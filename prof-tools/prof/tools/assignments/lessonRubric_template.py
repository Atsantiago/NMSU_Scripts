"""
Prof-Tools Lesson Rubric Template

A comprehensive grading rubric system for Maya assignments that provides:
- 5-tier scoring system (No Marks to Full Marks)
- Configurable percentage scoring with dropdown and manual entry
- Auto-calculation based on criteria with manual override capability
- Empty file detection and scoring
- Robust UI with table format and auto-generated comments

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function

import logging
import math
from collections import OrderedDict

try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

class LessonRubric(object):
    """
    Main rubric class for grading Maya assignments.
    Provides a comprehensive scoring system with UI.
    """
    
    # Scoring system configuration
    SCORE_LEVELS = OrderedDict([
        ('No Marks', {'min': 0, 'max': 5, 'default': 0}),
        ('Low Marks', {'min': 6, 'max': 15, 'default': 10}),
        ('Partial Marks', {'min': 16, 'max': 45, 'default': 30}),
        ('High Marks', {'min': 46, 'max': 75, 'default': 50}),
        ('Full Marks', {'min': 76, 'max': 100, 'default': 85})
    ])
    
    PERCENTAGE_OPTIONS = [0, 10, 30, 50, 70, 85, 95, 100]
    
    def __init__(self, assignment_name="Assignment", total_points=10):
        """
        Initialize the rubric with assignment details.
        
        Args:
            assignment_name (str): Name of the assignment
            total_points (int): Total points for the assignment (default: 10)
        """
        self.assignment_name = assignment_name
        self.total_points = total_points
        self.criteria = OrderedDict()
        self.window_name = "lessonRubricWindow"
        self.ui_elements = {}
        self.is_empty_file = False
        
        # Check if Maya file is empty
        self._check_empty_file()
        
    def add_criterion(self, name, point_value, description=""):
        """
        Add a grading criterion to the rubric.
        
        Args:
            name (str): Name of the criterion
            point_value (float): Point value for this criterion
            description (str): Description of the criterion
        """
        self.criteria[name] = {
            'point_value': point_value,
            'description': description,
            'percentage': 10 if self.is_empty_file else 85,  # Default to Low Marks for empty file
            'score': 0.0,
            'comments': "",
            'manual_override': False
        }
        
    def _check_empty_file(self):
        """Check if the current Maya file is empty or has minimal content."""
        if not MAYA_AVAILABLE:
            return
            
        try:
            # Check for various Maya objects that indicate content
            all_objects = cmds.ls(dag=True, long=True)
            
            # Filter out default Maya objects
            default_objects = [
                'persp', 'top', 'front', 'side',  # Default cameras
                'perspShape', 'topShape', 'frontShape', 'sideShape',  # Camera shapes
                'defaultLightSet', 'defaultObjectSet',  # Default sets
                'initialShadingGroup', 'initialParticleSE', 'initialMaterialInfo',  # Default shading
                'lambert1', 'particleCloud1',  # Default materials
                'time1', 'sequenceManager1', 'renderPartition', 'renderGlobalsList1',
                'defaultRenderLayer', 'globalRender1', 'defaultResolution',
                'hardwareRenderGlobals', 'characterPartition', 'defaultHardwareRenderGlobals'
            ]
            
            # Remove default objects from the list
            content_objects = [obj for obj in all_objects 
                             if not any(default in obj for default in default_objects)]
            
            # If we have 5 or fewer non-default objects, consider it empty
            self.is_empty_file = len(content_objects) <= 5
            
            if self.is_empty_file:
                logger.info("Empty or minimal Maya file detected")
                
        except Exception as e:
            logger.warning("Could not check file content: %s", e)
            self.is_empty_file = False
    
    def _get_score_level_for_percentage(self, percentage):
        """
        Determine which score level a percentage falls into.
        
        Args:
            percentage (float): Percentage score
            
        Returns:
            str: Score level name
        """
        for level, data in self.SCORE_LEVELS.items():
            if data['min'] <= percentage <= data['max']:
                return level
        return 'No Marks'
    
    def _calculate_criterion_score(self, criterion_name):
        """
        Calculate the point score for a criterion based on percentage.
        
        Args:
            criterion_name (str): Name of the criterion
            
        Returns:
            float: Calculated score
        """
        if criterion_name not in self.criteria:
            return 0.0
            
        criterion = self.criteria[criterion_name]
        percentage = criterion['percentage']
        point_value = criterion['point_value']
        
        # Calculate score as percentage of point value
        score = (percentage / 100.0) * point_value
        return round(score, 2)
    
    def _generate_comments(self, criterion_name):
        """
        Generate auto-comments based on the score level.
        
        Args:
            criterion_name (str): Name of the criterion
            
        Returns:
            str: Generated comments
        """
        if criterion_name not in self.criteria:
            return ""
            
        criterion = self.criteria[criterion_name]
        percentage = criterion['percentage']
        level = self._get_score_level_for_percentage(percentage)
        
        comments = {
            'No Marks': "Criterion not met or not attempted.",
            'Low Marks': "Minimal effort shown, significant improvements needed.",
            'Partial Marks': "Basic requirements met, some areas need improvement.",
            'High Marks': "Good work with minor areas for improvement.",
            'Full Marks': "Excellent work, all requirements exceeded."
        }
        
        base_comment = comments.get(level, "")
        
        if self.is_empty_file:
            base_comment = "Empty or minimal file detected. " + base_comment
            
        return base_comment
    
    def calculate_total_score(self):
        """
        Calculate the total assignment score.
        
        Returns:
            float: Total score rounded to nearest tenth
        """
        total = 0.0
        for criterion_name, criterion in self.criteria.items():
            if criterion['manual_override']:
                total += criterion['score']
            else:
                total += self._calculate_criterion_score(criterion_name)
        
        # Round up to nearest tenth
        return math.ceil(total * 10) / 10.0
    
    def show_rubric_ui(self):
        """Display the rubric grading UI."""
        if not MAYA_AVAILABLE:
            logger.error("Maya not available for UI display")
            return
            
        self._create_rubric_window()
    
    def _create_rubric_window(self):
        """Create the main rubric window UI."""
        # Delete existing window if it exists
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)
        
        # Create main window
        self.ui_elements['window'] = cmds.window(
            self.window_name,
            title=f"Grading Rubric - {self.assignment_name}",
            widthHeight=(800, 600),
            resizeToFitChildren=True,
            sizeable=True
        )
        
        # Main layout
        main_layout = cmds.columnLayout(
            adjustableColumn=True,
            columnOffset=('both', 10),
            rowSpacing=10,
            parent=self.ui_elements['window']
        )
        
        # Header
        cmds.text(
            label=f"Assignment: {self.assignment_name}",
            font="boldLabelFont",
            height=30,
            parent=main_layout
        )
        
        cmds.text(
            label=f"Total Points: {self.total_points}",
            font="smallPlainLabelFont",
            parent=main_layout
        )
        
        if self.is_empty_file:
            cmds.text(
                label="⚠️ Empty or minimal file detected - scores defaulted to Low Marks",
                backgroundColor=(1.0, 0.8, 0.0),
                parent=main_layout
            )
        
        cmds.separator(height=10, parent=main_layout)
        
        # Create criteria table
        self._create_criteria_table(main_layout)
        
        # Total score section
        cmds.separator(height=15, parent=main_layout)
        
        total_layout = cmds.rowLayout(
            numberOfColumns=3,
            columnAlign=[(1, 'left'), (2, 'center'), (3, 'right')],
            columnWidth=[(1, 200), (2, 200), (3, 200)],
            parent=main_layout
        )
        
        cmds.text(label="", parent=total_layout)  # Spacer
        
        self.ui_elements['total_score'] = cmds.text(
            label=f"Total Grade: {self.calculate_total_score():.1f}/{self.total_points}",
            font="boldLabelFont",
            parent=total_layout
        )
        
        cmds.text(label="", parent=total_layout)  # Spacer
        
        # Buttons
        cmds.setParent(main_layout)
        button_layout = cmds.rowLayout(
            numberOfColumns=3,
            columnAlign=[(1, 'center'), (2, 'center'), (3, 'center')],
            parent=main_layout
        )
        
        cmds.button(
            label="Recalculate",
            command=lambda *args: self._update_all_scores(),
            parent=button_layout
        )
        
        cmds.button(
            label="Export Results",
            command=lambda *args: self._export_results(),
            parent=button_layout
        )
        
        cmds.button(
            label="Close",
            command=lambda *args: cmds.deleteUI(self.window_name, window=True),
            parent=button_layout
        )
        
        # Show window
        cmds.showWindow(self.ui_elements['window'])
    
    def _create_criteria_table(self, parent):
        """Create the criteria scoring table."""
        # Table header
        header_layout = cmds.rowLayout(
            numberOfColumns=4,
            columnAlign=[(1, 'left'), (2, 'center'), (3, 'center'), (4, 'right')],
            columnWidth=[(1, 150), (2, 120), (3, 280), (4, 120)],
            backgroundColor=(0.3, 0.3, 0.3),
            parent=parent
        )
        
        cmds.text(label="Criteria", font="boldLabelFont", parent=header_layout)
        cmds.text(label="Score %", font="boldLabelFont", parent=header_layout)
        cmds.text(label="Performance Level", font="boldLabelFont", parent=header_layout)
        cmds.text(label="Points", font="boldLabelFont", parent=header_layout)
        
        cmds.setParent(parent)
        
        # Create rows for each criterion
        for criterion_name, criterion_data in self.criteria.items():
            self._create_criterion_row(parent, criterion_name, criterion_data)
    
    def _create_criterion_row(self, parent, criterion_name, criterion_data):
        """Create a single criterion row in the table."""
        # Main criterion row
        row_layout = cmds.rowLayout(
            numberOfColumns=4,
            columnAlign=[(1, 'left'), (2, 'center'), (3, 'center'), (4, 'right')],
            columnWidth=[(1, 150), (2, 120), (3, 280), (4, 120)],
            parent=parent
        )
        
        # Criterion name
        cmds.text(label=criterion_name, parent=row_layout)
        
        # Score percentage dropdown/field
        percentage_field = cmds.intFieldGrp(
            numberOfFields=1,
            label="",
            value1=criterion_data['percentage'],
            changeCommand=lambda: self._on_percentage_change(criterion_name),
            parent=row_layout
        )
        self.ui_elements[f"{criterion_name}_percentage"] = percentage_field
        
        # Performance level indicators
        level_layout = cmds.rowLayout(
            numberOfColumns=5,
            columnAlign=[(i, 'center') for i in range(1, 6)],
            parent=row_layout
        )
        
        current_level = self._get_score_level_for_percentage(criterion_data['percentage'])
        for level_name in self.SCORE_LEVELS.keys():
            color = (0.4, 0.7, 0.4) if level_name == current_level else (0.6, 0.6, 0.6)
            cmds.text(
                label=level_name.split()[0],  # Show just first word
                backgroundColor=color,
                parent=level_layout
            )
        
        cmds.setParent(row_layout)
        
        # Points display
        calculated_score = self._calculate_criterion_score(criterion_name)
        points_text = cmds.text(
            label=f"{calculated_score:.1f}/{criterion_data['point_value']:.1f}",
            parent=row_layout
        )
        self.ui_elements[f"{criterion_name}_points"] = points_text
        
        # Comments row
        cmds.setParent(parent)
        comment_layout = cmds.columnLayout(
            adjustableColumn=True,
            columnOffset=('left', 20),
            parent=parent
        )
        
        comments = self._generate_comments(criterion_name)
        cmds.text(
            label=f"Comments: {comments}",
            font="smallPlainLabelFont",
            align="left",
            parent=comment_layout
        )
        
        cmds.separator(height=5, parent=parent)
    
    def _on_percentage_change(self, criterion_name):
        """Handle percentage change for a criterion."""
        if criterion_name not in self.ui_elements:
            return
            
        field = self.ui_elements[f"{criterion_name}_percentage"]
        new_percentage = cmds.intFieldGrp(field, query=True, value1=True)
        
        # Clamp percentage between 0 and 100
        new_percentage = max(0, min(100, new_percentage))
        cmds.intFieldGrp(field, edit=True, value1=new_percentage)
        
        # Update criterion data
        self.criteria[criterion_name]['percentage'] = new_percentage
        self.criteria[criterion_name]['comments'] = self._generate_comments(criterion_name)
        
        # Update displays
        self._update_criterion_display(criterion_name)
        self._update_total_score_display()
    
    def _update_criterion_display(self, criterion_name):
        """Update the display for a specific criterion."""
        if f"{criterion_name}_points" in self.ui_elements:
            calculated_score = self._calculate_criterion_score(criterion_name)
            point_value = self.criteria[criterion_name]['point_value']
            
            cmds.text(
                self.ui_elements[f"{criterion_name}_points"],
                edit=True,
                label=f"{calculated_score:.1f}/{point_value:.1f}"
            )
    
    def _update_total_score_display(self):
        """Update the total score display."""
        if 'total_score' in self.ui_elements:
            total = self.calculate_total_score()
            cmds.text(
                self.ui_elements['total_score'],
                edit=True,
                label=f"Total Grade: {total:.1f}/{self.total_points}"
            )
    
    def _update_all_scores(self):
        """Recalculate and update all scores and displays."""
        for criterion_name in self.criteria.keys():
            self._update_criterion_display(criterion_name)
        self._update_total_score_display()
    
    def _export_results(self):
        """Export grading results to a text format."""
        results = []
        results.append(f"Grading Results for: {self.assignment_name}")
        results.append("=" * 50)
        results.append("")
        
        for criterion_name, criterion_data in self.criteria.items():
            score = self._calculate_criterion_score(criterion_name)
            percentage = criterion_data['percentage']
            level = self._get_score_level_for_percentage(percentage)
            
            results.append(f"Criterion: {criterion_name}")
            results.append(f"  Score: {score:.1f}/{criterion_data['point_value']:.1f} ({percentage}%)")
            results.append(f"  Level: {level}")
            results.append(f"  Comments: {self._generate_comments(criterion_name)}")
            results.append("")
        
        total_score = self.calculate_total_score()
        results.append(f"TOTAL GRADE: {total_score:.1f}/{self.total_points}")
        results.append("")
        
        if self.is_empty_file:
            results.append("Note: Empty or minimal file detected")
        
        # Display results in a scroll field window
        self._show_export_window("\n".join(results))
    
    def _show_export_window(self, content):
        """Show export results in a new window."""
        export_window = "exportWindow"
        
        if cmds.window(export_window, exists=True):
            cmds.deleteUI(export_window, window=True)
        
        window = cmds.window(
            export_window,
            title="Exported Grading Results",
            widthHeight=(600, 400)
        )
        
        layout = cmds.columnLayout(adjustableColumn=True, parent=window)
        
        cmds.scrollField(
            text=content,
            editable=False,
            wordWrap=True,
            height=350,
            parent=layout
        )
        
        cmds.button(
            label="Close",
            command=lambda *args: cmds.deleteUI(export_window, window=True),
            parent=layout
        )
        
        cmds.showWindow(window)


def create_sample_rubric():
    """
    Create a sample rubric for demonstration purposes.
    This can be customized for specific assignments.
    """
    # Get current file name for assignment name
    assignment_name = "Sample Assignment"
    if MAYA_AVAILABLE:
        try:
            scene_name = cmds.file(query=True, sceneName=True, shortName=True)
            if scene_name:
                assignment_name = scene_name.rsplit('.', 1)[0]  # Remove extension
        except:
            pass
    
    # Create rubric instance
    rubric = LessonRubric(assignment_name=assignment_name, total_points=10)
    
    # Add sample criteria (customize these for your assignment)
    rubric.add_criterion("Technical Execution", 3.0, "Proper modeling techniques and clean geometry")
    rubric.add_criterion("Creative Design", 2.5, "Originality and artistic vision")
    rubric.add_criterion("File Organization", 1.5, "Proper naming, grouping, and scene structure")
    rubric.add_criterion("Following Instructions", 2.0, "Adherence to assignment requirements")
    rubric.add_criterion("Presentation Quality", 1.0, "Final render quality and composition")
    
    # Show the rubric UI
    rubric.show_rubric_ui()
    
    return rubric


if __name__ == "__main__":
    # When run directly, create and show sample rubric
    if MAYA_AVAILABLE:
        create_sample_rubric()
    else:
        print("Maya not available - cannot display UI")
