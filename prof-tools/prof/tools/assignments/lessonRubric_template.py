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
    
    # Scoring system configuration - defines the 5-tier grading scale
    # Each level has a percentage range and default value for auto-scoring
    SCORE_LEVELS = OrderedDict([
        ('No Marks', {'min': 0, 'max': 5, 'default': 0}),        # 0-5%: Not attempted or completely wrong
        ('Low Marks', {'min': 6, 'max': 15, 'default': 10}),     # 6-15%: Minimal effort, major issues
        ('Partial Marks', {'min': 16, 'max': 45, 'default': 30}), # 16-45%: Basic requirements met
        ('High Marks', {'min': 46, 'max': 75, 'default': 50}),   # 46-75%: Good work, minor issues
        ('Full Marks', {'min': 76, 'max': 100, 'default': 85})   # 76-100%: Excellent work, exceeds expectations
    ])
    
    # Common percentage values for quick selection in dropdowns
    PERCENTAGE_OPTIONS = [0, 10, 30, 50, 70, 85, 95, 100]
    
    def __init__(self, assignment_name="Assignment", total_points=10):
        """
        Initialize the rubric with assignment details.
        
        Args:
            assignment_name (str): Name of the assignment
            total_points (int): Total points for the assignment (default: 10)
        """
        # Initialize core instance variables
        self.assignment_name = assignment_name
        self.total_points = total_points
        self.criteria = OrderedDict()  # Stores all grading criteria with their data
        self.window_name = "lessonRubricWindow"  # Unique identifier for Maya UI window
        self.ui_elements = {}  # Dictionary to store UI element references for updates
        self.is_empty_file = False  # Flag to track if Maya scene has minimal content
        
        # Automatically check if the current Maya file is empty/minimal
        # This affects default scoring (empty files get lower default scores)
        self._check_empty_file()
        
    def add_criterion(self, name, point_value, description=""):
        """
        Add a grading criterion to the rubric.
        
        Args:
            name (str): Name of the criterion
            point_value (float): Point value for this criterion
            description (str): Description of the criterion
        """
        # Create a new criterion entry with all necessary data
        # Each criterion tracks: points, description, current score percentage, 
        # calculated score, auto-generated comments, and manual override status
        self.criteria[name] = {
            'point_value': point_value,        # How many points this criterion is worth
            'description': description,        # Text description of what's being graded
            'percentage': 10 if self.is_empty_file else 85,  # Default score: low for empty files, high otherwise
            'score': 0.0,                     # Calculated point score (percentage * point_value)
            'comments': "",                   # Auto-generated feedback comments
            'manual_override': False          # Whether instructor manually set the score
        }
        
    def _check_empty_file(self):
        """
        Check if the current Maya file is empty or has minimal content.
        
        This method examines the Maya scene to determine if it contains meaningful work.
        Empty or minimal files get lower default scores to encourage substantial work.
        
        The detection works by:
        1. Getting a list of all objects in the scene
        2. Filtering out Maya's default objects (cameras, lights, materials, etc.)
        3. Counting remaining user-created content
        4. If 5 or fewer objects remain, consider the file "empty"
        """
        if not MAYA_AVAILABLE:
            return
            
        try:
            # Get all objects in the Maya scene (DAG = Directed Acyclic Graph objects)
            # This includes transforms, shapes, cameras, lights, etc.
            all_objects = cmds.ls(dag=True, long=True)
            
            # List of default Maya objects that exist in every new scene
            # These don't count as "user content" for grading purposes
            default_objects = [
                'persp', 'top', 'front', 'side',  # Default camera transforms
                'perspShape', 'topShape', 'frontShape', 'sideShape',  # Default camera shapes
                'defaultLightSet', 'defaultObjectSet',  # Default selection sets
                'initialShadingGroup', 'initialParticleSE', 'initialMaterialInfo',  # Default shading nodes
                'lambert1', 'particleCloud1',  # Default materials
                'time1', 'sequenceManager1', 'renderPartition', 'renderGlobalsList1',  # Animation/render nodes
                'defaultRenderLayer', 'globalRender1', 'defaultResolution',  # Render settings
                'hardwareRenderGlobals', 'characterPartition', 'defaultHardwareRenderGlobals'  # More defaults
            ]
            
            # Filter out default objects - only count user-created content
            # Uses 'any()' to check if any default object name appears in the full object path
            content_objects = [obj for obj in all_objects 
                             if not any(default in obj for default in default_objects)]
            
            # Threshold: 5 or fewer user objects = "empty" file
            # This accounts for minimal work like a single primitive shape
            self.is_empty_file = len(content_objects) <= 5
            
            if self.is_empty_file:
                logger.info("Empty or minimal Maya file detected")
                
        except Exception as e:
            # If anything goes wrong, assume file is not empty (fail safely)
            logger.warning("Could not check file content: %s", e)
            self.is_empty_file = False
    
    def _get_score_level_for_percentage(self, percentage):
        """
        Determine which score level a percentage falls into.
        
        This maps percentage scores to descriptive level names:
        - 0-5%: "No Marks" 
        - 6-15%: "Low Marks"
        - 16-45%: "Partial Marks" 
        - 46-75%: "High Marks"
        - 76-100%: "Full Marks"
        
        Args:
            percentage (float): Percentage score (0-100)
            
        Returns:
            str: Score level name for display and comment generation
        """
        # Iterate through score levels to find which range the percentage fits
        for level, data in self.SCORE_LEVELS.items():
            if data['min'] <= percentage <= data['max']:
                return level
        # Fallback if percentage is outside expected ranges
        return 'No Marks'
    
    def _calculate_criterion_score(self, criterion_name):
        """
        Calculate the point score for a criterion based on percentage.
        
        Converts percentage score to actual points by multiplying:
        final_score = (percentage / 100) * max_points_for_criterion
        
        Example: If criterion is worth 3.0 points and student scores 70%:
        final_score = (70 / 100) * 3.0 = 2.1 points
        
        Args:
            criterion_name (str): Name of the criterion to calculate
            
        Returns:
            float: Calculated score rounded to 2 decimal places
        """
        if criterion_name not in self.criteria:
            return 0.0
            
        criterion = self.criteria[criterion_name]
        percentage = criterion['percentage']  # Student's percentage score (0-100)
        point_value = criterion['point_value']  # Maximum points possible for this criterion
        
        # Convert percentage to decimal and multiply by max points
        score = (percentage / 100.0) * point_value
        return round(score, 2)  # Round to 2 decimal places for clean display
    
    def _generate_comments(self, criterion_name):
        """
        Generate auto-comments based on the score level.
        
        Creates standardized feedback comments that correspond to the student's
        performance level. This provides consistent, helpful feedback across
        all assignments and instructors.
        
        Args:
            criterion_name (str): Name of the criterion to generate comments for
            
        Returns:
            str: Generated feedback comment appropriate for the score level
        """
        if criterion_name not in self.criteria:
            return ""
            
        criterion = self.criteria[criterion_name]
        percentage = criterion['percentage']
        level = self._get_score_level_for_percentage(percentage)
        
        # Standard comments for each performance level
        # These can be customized per assignment by overriding this method
        comments = {
            'No Marks': "Criterion not met or not attempted.",
            'Low Marks': "Minimal effort shown, significant improvements needed.",
            'Partial Marks': "Basic requirements met, some areas need improvement.",
            'High Marks': "Good work with minor areas for improvement.",
            'Full Marks': "Excellent work, all requirements exceeded."
        }
        
        base_comment = comments.get(level, "")
        
        # Add special note for empty files to provide specific guidance
        if self.is_empty_file:
            base_comment = "Empty or minimal file detected. " + base_comment
            
        return base_comment
    
    def calculate_total_score(self):
        """
        Calculate the total assignment score by summing all criteria.
        
        Adds up the calculated scores from all criteria to get the final grade.
        Supports both auto-calculated scores and manual overrides set by instructors.
        
        Returns:
            float: Total score rounded up to nearest tenth (e.g., 8.7 becomes 8.7, 8.71 becomes 8.8)
        """
        total = 0.0
        
        # Sum scores from all criteria
        for criterion_name, criterion in self.criteria.items():
            if criterion['manual_override']:
                # Use manually entered score if instructor override is active
                total += criterion['score']
            else:
                # Use calculated score based on percentage
                total += self._calculate_criterion_score(criterion_name)
        
        # Round up to nearest tenth for consistent grading
        # math.ceil(8.71 * 10) / 10.0 = math.ceil(87.1) / 10.0 = 88 / 10.0 = 8.8
        return math.ceil(total * 10) / 10.0
    
    def show_rubric_ui(self):
        """Display the rubric grading UI."""
        if not MAYA_AVAILABLE:
            logger.error("Maya not available for UI display")
            return
            
        self._create_rubric_window()
    
    def _create_rubric_window(self):
        """
        Create the main rubric window UI using Maya's cmds interface.
        
        This builds the complete grading interface including:
        - Header with assignment info and empty file warnings
        - Criteria table with score inputs and performance indicators  
        - Total score display
        - Action buttons (Recalculate, Export, Close)
        
        The UI is built hierarchically using Maya's layout system:
        Window -> ColumnLayout (main) -> Various child layouts and controls
        """
        # Clean up any existing window to prevent conflicts
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)
        
        # Create main window with appropriate size for content
        # widthHeight sets initial size, sizeable=True allows user resizing
        self.ui_elements['window'] = cmds.window(
            self.window_name,
            title=f"Grading Rubric - {self.assignment_name}",
            widthHeight=(720, 800),  # Compact width matching table layout + padding
            resizeToFitChildren=True,  # Auto-adjust if content is larger
            sizeable=True  # Allow user to resize window
        )
        
        # Main vertical layout container - all UI elements stack vertically
        # adjustableColumn=True makes the layout resize with the window
        main_layout = cmds.columnLayout(
            adjustableColumn=True,  # Automatically adjust width to fit window
            parent=self.ui_elements['window']  # Attach to the main window
        )
        
        # Header section with assignment information
        cmds.text(
            label=f"Assignment: {self.assignment_name}",
            font="fixedWidthFont",  # Use Maya's larger fixed-width font for emphasis
            align="left",
            wordWrap=True,
            parent=main_layout
        )
        
        cmds.text(
            label=f"Total Points: {self.total_points}",
            font="smallPlainLabelFont",  # Smaller font for secondary info
            parent=main_layout
        )
        
        # Warning message for empty files - helps instructors understand default scoring
        if self.is_empty_file:
            cmds.text(
                label="⚠️ Empty or minimal file detected - scores defaulted to Low Marks",
                backgroundColor=(1.0, 0.8, 0.0),  # Yellow warning background (RGB values 0-1)
                parent=main_layout
            )
        
        # Visual separator between header and content
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
            font="fixedWidthFont",
            parent=total_layout
        )
        
        cmds.text(label="", parent=total_layout)  # Spacer
        
        # Action buttons section with improved sizing and spacing
        cmds.setParent(main_layout)  # Return to main layout after creating other elements
        button_layout = cmds.rowLayout(
            numberOfColumns=3,  # Three buttons in a horizontal row
            columnAlign=[(1, 'center'), (2, 'center'), (3, 'center')],  # Center-align all buttons
            columnWidth=[(1, 200), (2, 200), (3, 200)],  # Fixed width for each button column
            columnAttach=[(1, 'left', 20), (2, 'both', 10), (3, 'right', 20)],  # Add padding
            parent=main_layout
        )
        
        # Recalculate button - updates all scores and displays
        cmds.button(
            label="Recalculate",
            command=lambda *args: self._update_all_scores(),  # Lambda to handle Maya's callback format
            height=35,  # Larger button height for better usability
            width=180,  # Fixed width for consistency
            parent=button_layout
        )
        
        # Export button - creates a text report of all scores and comments
        cmds.button(
            label="Export Results",
            command=lambda *args: self._export_results(),
            height=35,
            width=180,
            parent=button_layout
        )
        
        # Close button - safely closes the rubric window
        cmds.button(
            label="Close",
            command=lambda *args: cmds.deleteUI(self.window_name, window=True),
            height=35,
            width=180,
            parent=button_layout
        )
        
        # Show window
        cmds.showWindow(self.ui_elements['window'])
    
    def _create_criteria_table(self, parent):
        """
        Create the criteria scoring table with headers and data rows.
        
        Builds a table-like interface showing:
        - Criterion name
        - Score percentage input field  
        - Performance level indicators (visual feedback)
        - Calculated points display
        - Editable comments field with copy functionality
        
        Args:
            parent: Maya UI parent element to attach the table to
        """
        # Table header row with column labels and styling
        header_layout = cmds.rowLayout(
            numberOfColumns=4,  # Four main columns for the table
            columnAlign=[(1, 'left'), (2, 'center'), (3, 'center'), (4, 'right')],  # Text alignment per column
            columnWidth=[(1, 150), (2, 120), (3, 280), (4, 120)],  # Fixed widths for consistent layout
            backgroundColor=(0.3, 0.3, 0.3),  # Dark gray header background for contrast
            parent=parent
        )
        
        # Column headers using larger bold font to distinguish from data
        cmds.text(label="Criteria", font="fixedWidthFont", parent=header_layout)
        cmds.text(label="Score %", font="fixedWidthFont", parent=header_layout)
        cmds.text(label="Performance Level", font="fixedWidthFont", parent=header_layout)
        cmds.text(label="Points", font="fixedWidthFont", parent=header_layout)
        
        cmds.setParent(parent)  # Return to parent for adding data rows
        
        # Create individual rows for each criterion
        # Each criterion gets its own row with input fields and displays
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
            parent=parent
        )
        
        # Comments header with copy button
        header_layout = cmds.rowLayout(
            numberOfColumns=2,
            columnAlign=[(1, 'left'), (2, 'right')],
            columnWidth=[(1, 500), (2, 100)],
            parent=comment_layout
        )
        
        cmds.text(
            label="Comments:",
            font="boldLabelFont",
            align="left",
            parent=header_layout
        )
        
        cmds.button(
            label="Copy",
            command=lambda *args, cn=criterion_name: self._copy_criterion_comment(cn),
            height=20,
            width=80,
            parent=header_layout
        )
        
        cmds.setParent(comment_layout)
        
        # Copyable comments field
        comments = self._generate_comments(criterion_name)
        comment_field = cmds.scrollField(
            text=comments,
            editable=True,
            wordWrap=True,
            height=40,
            font="smallPlainLabelFont",
            parent=comment_layout
        )
        self.ui_elements[f"{criterion_name}_comment_field"] = comment_field
        
        cmds.separator(height=8, parent=parent)
    
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
        
        # Update comment field if it exists
        if f"{criterion_name}_comment_field" in self.ui_elements:
            comments = self._generate_comments(criterion_name)
            cmds.scrollField(
                self.ui_elements[f"{criterion_name}_comment_field"],
                edit=True,
                text=comments
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
            widthHeight=(700, 500)
        )
        
        layout = cmds.columnLayout(adjustableColumn=True, parent=window)
        
        cmds.scrollField(
            text=content,
            editable=True,
            wordWrap=True,
            height=420,
            parent=layout
        )
        
        button_layout = cmds.rowLayout(
            numberOfColumns=2,
            columnAlign=[(1, 'center'), (2, 'center')],
            columnWidth=[(1, 200), (2, 200)],
            parent=layout
        )
        
        cmds.button(
            label="Copy All Text",
            command=lambda *args: self._copy_to_clipboard(content),
            height=35,
            width=180,
            parent=button_layout
        )
        
        cmds.button(
            label="Close",
            command=lambda *args: cmds.deleteUI(export_window, window=True),
            height=35,
            width=180,
            parent=button_layout
        )
        
        cmds.showWindow(window)
    
    def _copy_to_clipboard(self, text):
        """
        Copy text to system clipboard with cross-platform support.
        
        This method handles clipboard operations across different operating systems:
        - Windows: Uses 'clip' command
        - macOS: Uses 'pbcopy' command  
        - Linux: Uses 'xclip' or 'xsel' command
        
        TECHNICAL IMPLEMENTATION:
        - subprocess.Popen creates a new process for the clipboard command
        - stdin=subprocess.PIPE allows us to send text to the command
        - text=True ensures proper text encoding
        - communicate() sends the text and waits for completion
        
        ERROR HANDLING:
        - Graceful fallback if clipboard commands are not available
        - User feedback via Maya dialogs for success/failure
        - Logging for debugging clipboard issues
        
        Args:
            text (str): Text content to copy to clipboard
        """
        try:
            # Maya's cmdFileOutput - attempt to use Maya's internal clipboard
            # (This is mostly for compatibility, actual copying happens below)
            cmds.cmdFileOutput(open=True)
            cmds.cmdFileOutput(close=True)
            
            # Import subprocess for cross-platform clipboard support
            import subprocess
            import sys
            
            # Platform-specific clipboard commands
            if sys.platform == "win32":
                # Windows: 'clip' command reads from stdin and copies to clipboard
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, text=True, shell=True)
                process.communicate(input=text)
            elif sys.platform == "darwin":
                # macOS: 'pbcopy' (pasteboard copy) is the standard clipboard command
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
                process.communicate(input=text)
            else:
                # Linux: Try xclip first (most common), fall back to xsel
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE, text=True)
                    process.communicate(input=text)
                except FileNotFoundError:
                    # Fallback to xsel if xclip is not available
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE, text=True)
                    process.communicate(input=text)
            
            # Show success dialog to confirm the operation worked
            cmds.confirmDialog(
                title="Copy Successful",
                message="Grading results copied to clipboard!",
                button=["OK"]
            )
            
        except Exception as e:
            # If clipboard copying fails, inform user and suggest manual copy
            logger.warning(f"Could not copy to clipboard: {e}")
            cmds.confirmDialog(
                title="Copy Failed",
                message="Could not copy to clipboard. Please select and copy the text manually.",
                button=["OK"]
            )
    
    def _copy_criterion_comment(self, criterion_name):
        """Copy a specific criterion's comment to clipboard."""
        if f"{criterion_name}_comment_field" in self.ui_elements:
            comment_text = cmds.scrollField(
                self.ui_elements[f"{criterion_name}_comment_field"],
                query=True,
                text=True
            )
            self._copy_to_clipboard(f"{criterion_name}: {comment_text}")

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
