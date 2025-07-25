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


# ==============================================================================
# RUBRIC CONFIGURATION - Scoring system and default settings
# ==============================================================================

# ==============================================================================
# RUBRIC CONFIGURATION - Scoring system and default settings
# ==============================================================================

class LessonRubric(object):
    """
    Main rubric class for grading Maya assignments.
    Provides a comprehensive scoring system with UI.
    """
    
    # Scoring system configuration - defines the 5-tier grading scale
    # Each level has a percentage range and default value for auto-scoring
    SCORE_LEVELS = OrderedDict([
        ('No Marks', {'min': 0, 'max': 0, 'default': 0}),        # 0%: Not attempted or completely wrong
        ('Low Marks', {'min': 1, 'max': 69, 'default': 65}),     # 1-69%: Minimal effort, major issues
        ('Partial Marks', {'min': 70, 'max': 84, 'default': 75}), # 70-84%: Basic requirements met
        ('High Marks', {'min': 85, 'max': 99, 'default': 95}),   # 85-99%: Good work, minor issues
        ('Full Marks', {'min': 100, 'max': 100, 'default': 100})   #100%: Excellent work, exceeds expectations
    ])
    
    # Common percentage values for quick selection in dropdowns
    PERCENTAGE_OPTIONS = [0, 10, 30, 50, 70, 85, 95, 100]


# ==============================================================================
# CORE RUBRIC CLASS - Initialization and utility methods
# ==============================================================================
    
    def __init__(self, assignment_name="Assignment", total_points=10, project_name=None, assignment_display_name=None):
        """
        Initialize the rubric with assignment details.
        
        Args:
            assignment_name (str): Name of the assignment (used for window title)
            total_points (int): Total points for the assignment (default: 10)
            project_name (str): Display name for the project (default: None, shows "Project Name")
            assignment_display_name (str): Name shown in assignment label (default: None, uses assignment_name)
        """
        # Initialize core instance variables
        self.assignment_name = assignment_name
        self.assignment_display_name = assignment_display_name if assignment_display_name else assignment_name
        self.total_points = total_points
        self.project_name = project_name if project_name else "Project Name"
        self.criteria = OrderedDict()  # Stores all grading criteria with their data
        self.window_name = "lessonRubricWindow"  # Unique identifier for Maya UI window
        self.ui_elements = {}  # Dictionary to store UI element references for updates
        self.is_empty_file = False  # Flag to track if Maya scene has minimal content
        
        # Automatically check if the current Maya file is empty/minimal
        # This affects default scoring (empty files get lower default scores)
        self._check_empty_file()
        
    def add_criterion(self, name, point_value, description="", validation_function=None, validation_args=None, general_performance_comments=None):
        """
        Add a grading criterion to the rubric.
        
        This method is designed to be flexible and work with various types of
        validation functions and argument structures for future compatibility.
        
        Args:
            name (str): Name of the criterion
            point_value (float): Point value for this criterion
            description (str): Description of the criterion
            validation_function (callable, optional): Function to validate this criterion.
                Can return (score, comments) tuple, just a score, or a dictionary
            validation_args (list/any, optional): Arguments to pass to the validation function.
                Can be a list of arguments, a single argument, or None
            general_performance_comments (dict, optional): Custom performance level comments for this criterion.
                Format: {score_range: "comment", ...} or {level_name: "comment", ...}
                Example: {100: "Perfect file naming!", 90: "Good naming with 1 error", 70: "2 errors found", 50: "3+ errors, review instructions"}
        """
        # Normalize validation_args to ensure consistency
        if validation_args is None:
            normalized_args = []
        elif isinstance(validation_args, list):
            normalized_args = validation_args
        else:
            # Single argument case - wrap in list for consistency
            normalized_args = [validation_args]
        
        # Create a new criterion entry with all necessary data
        # Each criterion tracks: points, description, current score percentage, 
        # calculated score, auto-generated comments, and manual override status
        self.criteria[name] = {
            'point_value': point_value,        # How many points this criterion is worth
            'description': description,        # Text description of what's being graded
            'percentage': 10 if self.is_empty_file else 85,  # Default score: low for empty files, high otherwise
            'score': 0.0,                     # Calculated point score (percentage * point_value)
            'comments': "",                   # Auto-generated feedback comments
            'manual_override': False,         # Whether instructor manually set the score
            'validation_function': validation_function,  # Function to re-run validation
            'validation_args': normalized_args,           # Arguments for validation function (normalized to list)
            'general_performance_comments': general_performance_comments or {}  # Custom performance level comments for this criterion
        }
    
    def add_validated_criterion(self, name, point_value, description="", validator=None, general_performance_comments=None, *args, **kwargs):
        """
        Convenience method for adding criteria with validation functions.
        Handles various validation function patterns automatically.
        
        Args:
            name (str): Name of the criterion
            point_value (float): Point value for this criterion  
            description (str): Description of the criterion
            validator (callable): Validation function (can be any callable)
            general_performance_comments (dict, optional): Custom performance level comments
            *args: Variable arguments to pass to validator
            **kwargs: Keyword arguments (special handling for common patterns)
        
        Example usage patterns:
            # Simple function with no args
            rubric.add_validated_criterion("Check Objects", 2.0, "Objects exist", check_objects_exist)
            
            # Function with positional args and custom comments
            general_performance_comments = {100: "Perfect!", 90: "1 error", 70: "2 errors", 50: "3+ errors"}
            rubric.add_validated_criterion("Check Count", 2.0, "Correct count", check_object_count, general_performance_comments, 5)
        """
        # Convert args to list for storage
        validation_args = list(args) if args else []
        
        # Handle common keyword arguments
        if kwargs:
            # Add kwargs as additional arguments (could be enhanced in future)
            for key, value in kwargs.items():
                validation_args.extend([key, value])
        
        # Use the standard add_criterion method
        self.add_criterion(name, point_value, description, validator, validation_args, general_performance_comments)
    
    def add_criteria_batch(self, criteria_list):
        """
        Add multiple criteria at once from a list of dictionaries.
        Makes it easy to set up complex rubrics with many validated criteria.
        
        Args:
            criteria_list (list): List of dictionaries, each containing criterion data.
                Each dict should have: name, point_value, description (optional),
                validation_function (optional), validation_args (optional)
        
        Example usage:
            criteria = [
                {
                    'name': 'Object Count',
                    'point_value': 2.0,
                    'description': 'Correct number of objects',
                    'validation_function': check_object_count,
                    'validation_args': [5]
                },
                {
                    'name': 'Naming Convention', 
                    'point_value': 1.0,
                    'description': 'Proper naming used',
                    'validation_function': check_naming
                    # validation_args not needed if function takes no args
                }
            ]
            rubric.add_criteria_batch(criteria)
        """
        for criterion_data in criteria_list:
            if not isinstance(criterion_data, dict):
                logger.warning(f"Skipping invalid criterion data: {criterion_data}")
                continue
                
            # Extract required fields
            name = criterion_data.get('name')
            point_value = criterion_data.get('point_value')
            
            if not name or point_value is None:
                logger.warning(f"Skipping criterion missing name or point_value: {criterion_data}")
                continue
            
            # Extract optional fields with defaults
            description = criterion_data.get('description', '')
            validation_function = criterion_data.get('validation_function')
            validation_args = criterion_data.get('validation_args')
            general_performance_comments = criterion_data.get('general_performance_comments')
            
            # Add the criterion
            self.add_criterion(name, point_value, description, validation_function, validation_args, general_performance_comments)
        
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
    

# ==============================================================================
# CONTENT ANALYSIS AND FEEDBACK METHODS
# ==============================================================================

    def _get_score_level_for_percentage(self, percentage):
        """
        Determine which score level a percentage falls into.
        
        This maps percentage scores to descriptive level names:
        - 0%: "No Marks" 
        - 1-69%: "Low Marks"
        - 70-84%: "Partial Marks" 
        - 85-99%: "High Marks"
        - 100%: "Full Marks"
        
        Args:
            percentage (float): Percentage score (0-100)
            
        Returns:
            str: Score level name for display and comment generation
        """
        # Convert to int to ensure whole percentage comparison
        percentage = int(percentage)
        
        # New percentage-based ranges
        if percentage == 0:
            return 'No Marks'
        elif 1 <= percentage <= 69:
            return 'Low Marks'
        elif 70 <= percentage <= 84:
            return 'Partial Marks'
        elif 85 <= percentage <= 99:
            return 'High Marks'
        elif percentage == 100:
            return 'Full Marks'
        else:
            # Fallback for any unexpected values
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
        
        IMPORTANT: This method preserves existing comments from validation functions
        UNLESS the criterion has been manually overridden by the instructor.
        
        Args:
            criterion_name (str): Name of the criterion to generate comments for
            
        Returns:
            str: Generated feedback comment appropriate for the score level
        """
        if criterion_name not in self.criteria:
            return ""
            
        criterion = self.criteria[criterion_name]
        
        # If the criterion has been manually overridden, always generate fresh comments
        # based on the current performance level
        if criterion.get('manual_override', False):
            return self._generate_performance_level_comments(criterion_name, criterion['percentage'])
        
        # PRESERVE EXISTING COMMENTS: If comments already exist and the criterion hasn't
        # been manually overridden, return them instead of generating new generic ones.
        # This allows assignment-specific validation functions to provide detailed feedback
        # that won't be overwritten unless the instructor manually changes the score.
        existing_comments = criterion.get('comments', '').strip()
        if existing_comments:
            return existing_comments
        
        # Generate fresh comments based on performance level for new criteria
        return self._generate_performance_level_comments(criterion_name, criterion['percentage'])
    
    def _generate_performance_level_comments(self, criterion_name, percentage):
        """
        Generate comments specifically for a performance level based on percentage.
        
        This method uses criterion-specific performance comments when available,
        otherwise falls back to generic comments. This allows each criterion
        to have tailored feedback that matches its specific scoring criteria.
        
        Args:
            criterion_name (str): Name of the criterion
            percentage (float): Percentage score (0-100)
            
        Returns:
            str: Generated feedback comment appropriate for the score level and criterion
        """
        if criterion_name not in self.criteria:
            return ""
        
        criterion = self.criteria[criterion_name]
        general_performance_comments = criterion.get('general_performance_comments', {})
        
        # First, try to find criterion-specific comments
        if general_performance_comments:
            # Check for exact percentage match first
            if percentage in general_performance_comments:
                comment = general_performance_comments[percentage]
            else:
                # Check for range-based matches or closest match
                best_match = None
                best_diff = float('inf')
                
                for score_key, comment in general_performance_comments.items():
                    if isinstance(score_key, (int, float)):
                        diff = abs(percentage - score_key)
                        if diff < best_diff:
                            best_diff = diff
                            best_match = comment
                    elif isinstance(score_key, str):
                        # Handle level name keys like "Full Marks", "High Marks", etc.
                        level = self._get_score_level_for_percentage(percentage)
                        if score_key == level:
                            best_match = comment
                            break
                
                if best_match:
                    comment = best_match
                else:
                    # Fall back to generic comments if no criterion-specific match found
                    comment = self._get_generic_performance_comment(percentage)
            
            # Add empty file context if relevant
            if self.is_empty_file and "empty" not in comment.lower():
                comment = "Empty or minimal file detected. " + comment
                
            return comment
        
        # Fall back to generic comments if no criterion-specific comments defined
        return self._get_generic_performance_comment(percentage)
    
    def _get_generic_performance_comment(self, percentage):
        """
        Get generic performance comments based on score level.
        
        Args:
            percentage (float): Percentage score (0-100)
            
        Returns:
            str: Generic feedback comment for the performance level
        """
        level = self._get_score_level_for_percentage(percentage)
        
        # Standard generic comments for each performance level
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
    
    def _create_enhanced_comments(self, criterion_name, score_percentage, validation_comments):
        """
        Create enhanced comments with smart concatenation logic.
        
        Rules:
        1. By default, use specific validation comments only
        2. Only concatenate with performance comments when manually overridden
        3. For 100% scores, always use specific performance comment only
        4. Replace generic validation comments with performance comments
        
        Args:
            criterion_name (str): Name of the criterion
            score_percentage (float): Percentage score (0-100)
            validation_comments (str): Specific comments from validation function
            
        Returns:
            str: Appropriately formatted comments based on context
        """
        # Check if this criterion has been manually overridden
        is_manual_override = False
        if criterion_name in self.criteria:
            is_manual_override = self.criteria[criterion_name].get('manual_override', False)
        
        # Clean up validation comments
        validation_comments = validation_comments.strip() if validation_comments else ""
        
        # Get the general performance comment for this score level
        performance_comment = self._generate_performance_level_comments(criterion_name, score_percentage)
        
        # Rule 1: For 100% scores, always use specific performance comment only
        if score_percentage == 100:
            return performance_comment if performance_comment else validation_comments
        
        # Rule 2: Replace generic validation comments with performance comments
        if self._is_generic_validation_comment(validation_comments):
            return performance_comment if performance_comment else validation_comments
        
        # Rule 3: For manual overrides, concatenate performance + validation details
        if is_manual_override and validation_comments and performance_comment:
            return f"{performance_comment} | Details: {validation_comments}"
        
        # Rule 4: By default, use specific validation comments only
        return validation_comments if validation_comments else performance_comment
    
    def _is_generic_validation_comment(self, comment):
        """
        Check if a validation comment is generic (like "Auto-validation: 85%").
        
        Args:
            comment (str): Comment to check
            
        Returns:
            bool: True if comment appears to be generic/auto-generated
        """
        if not comment:
            return True
        
        comment_lower = comment.lower()
        generic_patterns = [
            "auto-validation:",
            "manual evaluation required",
            "validation error:",
            "no validation function",
            "todo:",
            "implement"
        ]
        
        return any(pattern in comment_lower for pattern in generic_patterns)
    

# ==============================================================================
# SCORING AND CALCULATION METHODS
# ==============================================================================

    def calculate_total_score(self):
        """
        Calculate the total assignment score by summing all criteria.
        
        Adds up the calculated scores from all criteria to get the final grade.
        Always calculates from current percentages to ensure dynamic updates.
        
        Returns:
            float: Total score rounded up to nearest tenth (e.g., 8.7 becomes 8.7, 8.71 becomes 8.8)
        """
        total = 0.0
        
        # Sum scores from all criteria - always calculate from current percentage
        # This ensures the total updates dynamically when percentages change
        for criterion_name, criterion in self.criteria.items():
            # Always use calculated score based on current percentage
            # This ensures total updates immediately when percentages change
            total += self._calculate_criterion_score(criterion_name)
        
        # Round up to nearest tenth for consistent grading
        # math.ceil(8.71 * 10) / 10.0 = math.ceil(87.1) / 10.0 = 88 / 10.0 = 8.8
        return math.ceil(total * 10) / 10.0
    
    def re_run_validations(self):
        """
        Re-run all validation functions to refresh scores and comments.
        
        This method is called by the Recalculate button to get fresh validation
        results, useful when the Maya scene has been modified or when the
        instructor wants to refresh all automatic validations.
        
        Only criteria that haven't been manually overridden will be updated.
        This method is designed to work with any rubric structure and handles
        various edge cases gracefully.
        
        Returns:
            int: Number of criteria that were successfully updated
        """
        updated_count = 0
        
        for criterion_name, criterion in self.criteria.items():
            # Skip criteria that have been manually overridden by the instructor
            if criterion.get('manual_override', False):
                logger.info(f"Skipping {criterion_name} - manually overridden")
                continue
                
            validation_function = criterion.get('validation_function')
            
            # Check if we have a valid validation function
            if not validation_function:
                logger.debug(f"No validation function for {criterion_name}")
                continue
                
            if not callable(validation_function):
                logger.warning(f"Validation function for {criterion_name} is not callable")
                continue
            
            try:
                validation_args = criterion.get('validation_args', [])
                
                # Handle different types of validation arguments
                if isinstance(validation_args, list):
                    # Standard case: list of arguments
                    if validation_args:
                        result = validation_function(*validation_args)
                    else:
                        result = validation_function()
                elif validation_args is not None:
                    # Single argument case (not in a list)
                    result = validation_function(validation_args)
                else:
                    # No arguments case
                    result = validation_function()
                
                # Handle different return types from validation functions
                if isinstance(result, tuple) and len(result) >= 2:
                    # Standard case: (score, comments) tuple
                    score, comments = result[0], result[1]
                elif isinstance(result, (int, float)):
                    # Score only case
                    score = result
                    comments = f"Auto-validation: {score}%"
                elif isinstance(result, dict):
                    # Dictionary return case
                    score = result.get('score', result.get('percentage', 85))
                    comments = result.get('comments', f"Auto-validation: {score}%")
                else:
                    logger.warning(f"Unexpected return type from {criterion_name} validation: {type(result)}")
                    continue
                
                # Validate score is within acceptable range
                if not isinstance(score, (int, float)) or score < 0 or score > 100:
                    logger.warning(f"Invalid score from {criterion_name} validation: {score}")
                    continue
                
                # Ensure comments is a string
                if not isinstance(comments, str):
                    comments = str(comments)
                
                # Update the criterion with fresh validation results
                criterion['percentage'] = float(score)
                
                # Store the original validation comments for potential later use
                criterion['validation_comments'] = comments
                
                # For automatic validation (not manual override), use enhanced comments logic
                enhanced_comments = self._create_enhanced_comments(criterion_name, float(score), comments)
                criterion['comments'] = enhanced_comments
                
                updated_count += 1
                
                logger.info(f"Updated {criterion_name}: {score}% - {enhanced_comments[:50]}...")
                
            except TypeError as e:
                logger.error(f"Type error re-running validation for {criterion_name}: {e}")
                logger.debug(f"Function: {validation_function}, Args: {validation_args}")
            except Exception as e:
                logger.error(f"Error re-running validation for {criterion_name}: {e}")
                # Keep existing values on error
        
        logger.info(f"Re-ran validations for {updated_count} criteria")
        return updated_count
    

# ==============================================================================
# UI CREATION AND DISPLAY METHODS
# ==============================================================================

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
            widthHeight=(670, 600),  # Further reduced width to fit optimized compact layout
            resizeToFitChildren=True,  # Auto-adjust if content is larger
            sizeable=True  # Allow user to resize window
        )
        
        # Main vertical layout container - all UI elements stack vertically
        # adjustableColumn=True makes the layout resize with the window
        main_layout = cmds.columnLayout(
            adjustableColumn=True,  # Automatically adjust width to fit window
            columnAttach=('both', 20),  # Add 20px margins on left and right
            parent=self.ui_elements['window']  # Attach to the main window
        )
        
        # Header section with assignment information
        self.ui_elements['assignment_display'] = cmds.text(
            label=f"Assignment: {self.assignment_display_name}",
            font="boldLabelFont",  # Use Maya's bold font for emphasis
            align="left",
            wordWrap=True,
            parent=main_layout
        )
        
        # Project name display - now customizable per assignment
        cmds.text(
            label=self.project_name,
            font="plainLabelFont",
            align="center",
            parent=main_layout
        )
        
        cmds.text(
            label=f"Total Points: {self.total_points}",
            font="plainLabelFont",  # Smaller font for secondary info
            align="center",
            parent=main_layout
        )
        
        # Warning message for empty files - helps instructors understand default scoring
        # Always create the warning element, but only show it when file is empty
        self.ui_elements['empty_file_warning'] = cmds.text(
            label="⚠️ Empty detected - scores defaulted to Low Marks",
            backgroundColor=(1.0, 0.8, 0.0),  # Yellow warning background (RGB values 0-1)
            visible=self.is_empty_file,  # Only visible when file is empty
            parent=main_layout
        )
        
        # Visual separator between header and content
        cmds.separator(height=10, parent=main_layout)
        
        # Create criteria table
        self._create_criteria_table(main_layout)
        
        # Total score section
        cmds.separator(height=15, parent=main_layout)
        
        # Calculate initial total and determine background color
        initial_total = self.calculate_total_score()
        if initial_total < 6.0:
            # Red for scores below 6
            total_background_color = (1.0, 0.3, 0.3)  # Red
        elif initial_total <= 7.5:
            # Muted yellow for scores between 6 and 7.5 (less bright than warning)
            total_background_color = (1.0, 0.9, 0.5)  # Muted yellow
        else:
            # Green for scores above 7.5 (same as performance level indicator)
            total_background_color = (0.4, 0.7, 0.4)  # Green
        
        self.ui_elements['total_score'] = cmds.text(
            label=f"Total Grade: {initial_total:.1f}/{self.total_points}",
            font="fixedWidthFont",  # Larger, more prominent font
            height=30,  # Taller text for better visibility
            align="center",  # Center the text within the element
            backgroundColor=total_background_color,  # Dynamic color based on score
            parent=main_layout
        )
        
        # Action buttons section with improved sizing and spacing
        cmds.setParent(main_layout)  # Return to main layout after creating other elements
        cmds.separator(height=15, parent=main_layout)  # Reduced separator for cleaner look
        
        button_layout = cmds.rowLayout(
            numberOfColumns=5,  # Five buttons in a horizontal row
            columnAlign=[(1, 'center'), (2, 'center'), (3, 'center'), (4, 'center'), (5, 'center')],  # Center-align all buttons
            adjustableColumn=True,  # Allow columns to expand to fill width
            columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2)],  # Small gaps between buttons
            parent=main_layout
        )
        
        # Select Assignment button - opens the assignment rubric selector window (moved to first position)
        cmds.button(
            label="Select Assignment",
            command=lambda *args: self._open_assignment_selector(),
            height=35,  # Larger button height for better usability
            parent=button_layout
        )
        
        # Refresh button - re-runs validation for current file and updates all scores
        cmds.button(
            label="Refresh",
            command=lambda *args: self._refresh_for_current_file(),
            height=35,  # Larger button height for better usability
            parent=button_layout
        )
        
        # Recalculate button - re-runs all validation functions and updates scores
        cmds.button(
            label="Recalculate",
            command=lambda *args: self._update_all_scores(),  # Lambda to handle Maya's callback format
            height=35,  # Larger button height for better usability
            parent=button_layout
        )
        
        # Export button - creates a text report of all scores and comments
        cmds.button(
            label="Export Results",
            command=lambda *args: self._export_results(),
            height=35,
            parent=button_layout
        )
        
        # Close button - safely closes the rubric window
        cmds.button(
            label="Close",
            command=lambda *args: cmds.deleteUI(self.window_name, window=True),
            height=35,
            parent=button_layout
        )
        
        # Add bottom padding to match left/right margins
        cmds.separator(height=20, parent=main_layout)
        
        # Show window
        cmds.showWindow(self.ui_elements['window'])
    
    def _create_criteria_table(self, parent):
        """
        Create the criteria scoring table using a robust hybrid of formLayout and rowLayout.
        This is the definitive solution for creating a clean, aligned, and spanning table.
        
        Args:
            parent: Maya UI parent element to attach the table to.
        """
        # 1. HEADER ROW: Use a simple rowLayout to define column headers and widths.
        header_layout = cmds.rowLayout(
            numberOfColumns=4,
            columnAlign=[(1, 'left'), (2, 'center'), (3, 'center'), (4, 'right')],
            columnWidth=[(1, 150), (2, 120), (3, 320), (4, 60)],
            backgroundColor=(0.3, 0.3, 0.3),
            parent=parent
        )
        cmds.text(label="Criteria", font="boldLabelFont")
        cmds.text(label="Score %", font="boldLabelFont")
        cmds.text(label="Performance Level", font="boldLabelFont")
        cmds.text(label="Points", font="boldLabelFont")
        
        cmds.setParent(parent)
        cmds.separator(height=5, style='none')

        # 2. CRITERIA ROWS: Loop and create a formLayout for each criterion.
        for criterion_name, criterion_data in self.criteria.items():
            self._create_criterion_form_row(parent, criterion_name, criterion_data)
            cmds.separator(height=10, style='in') # Visual separator between criteria

    def _create_criterion_form_row(self, parent, criterion_name, criterion_data):
        """
        Creates a single, robust criterion "row" using a formLayout.
        This allows for precise element positioning and true comment spanning.
        
        Args:
            parent: The parent UI element.
            criterion_name (str): The name of the criterion.
            criterion_data (dict): The data for the criterion.
        """
        # The formLayout acts as a container for one criterion's entire UI
        # Increased height to accommodate description, spacing between criteria and comments
        form = cmds.formLayout(height=125, parent=parent)

        # --- A. Create all UI Elements for this row ---
        
        # Top row elements
        crit_name_ui = cmds.text(label=criterion_name, align='left', width=150, wordWrap=True, height=30)
        score_layout = self._create_score_input_layout(criterion_name, criterion_data)
        perf_layout = self._create_performance_indicators_layout(criterion_name, criterion_data)
        points_layout = self._create_points_display_layout(criterion_name, criterion_data)

        # Description row element (new)
        description_text = criterion_data.get('description', '')
        description_ui = cmds.text(
            label=description_text, 
            align='left', 
            wordWrap=True, 
            font="plainLabelFont",
            backgroundColor=(0.25, 0.25, 0.25),
            height=20
        )

        # Bottom row elements (comments and copy button)
        # Use existing comments from validation functions if available, 
        # otherwise generate generic comments
        existing_comments = criterion_data.get('comments', '').strip()
        if not existing_comments:
            existing_comments = self._generate_comments(criterion_name)
        
        comment_field = cmds.scrollField(text=existing_comments, editable=True, wordWrap=True, height=40, font="plainLabelFont")
        copy_button = cmds.button(label="Copy", command=lambda *args, cn=criterion_name: self._copy_criterion_comment(cn), height=40, width=50)

        # Store UI elements that need updating
        self.ui_elements[f"{criterion_name}_comment_field"] = comment_field
        
        # --- B. Attach all elements within the formLayout ---
        
        cmds.formLayout(form, edit=True,
            # Consolidate all attachForm calls into a single list
            attachForm=[
                # Top row
                (crit_name_ui, 'top', 5), (crit_name_ui, 'left', 5),
                (score_layout, 'top', 5),
                (perf_layout, 'top', 5),
                (points_layout, 'top', 5), (points_layout, 'right', 5),
                
                # Description row
                (description_ui, 'left', 5), (description_ui, 'right', 5),
                
                # Bottom row
                (comment_field, 'left', 5),
                (copy_button, 'right', 5)
            ],
            # Consolidate all attachControl calls into a single list
            attachControl=[
                # Top row controls
                (score_layout, 'left', 5, crit_name_ui),
                (perf_layout, 'left', 5, score_layout),
                (points_layout, 'left', 5, perf_layout),
                
                # Description row positioning - below top row with some spacing
                (description_ui, 'top', 8, crit_name_ui),
                
                # Bottom row controls - below description with spacing
                (comment_field, 'top', 8, description_ui),
                (copy_button, 'top', 8, description_ui),
                
                # THE KEY TO SPANNING: Attach the right side of the comment field
                # to the left side of the copy button.
                (comment_field, 'right', 5, copy_button)
            ]
        )

    def _create_score_input_layout(self, criterion_name, criterion_data):
        """Helper to create the score input UI (dropdown + field)."""
        layout = cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 60), (2, 55)], width=120)  # Fixed width to match header
        
        dropdown = cmds.optionMenu(changeCommand=lambda sel: self._on_dropdown_change(criterion_name, sel))
        for p in self.PERCENTAGE_OPTIONS:
            cmds.menuItem(label=f"{p}%")
        cmds.menuItem(label="Custom")
        
        field = cmds.intField(value=criterion_data['percentage'], minValue=0, maxValue=100, changeCommand=lambda *args: self._on_percentage_field_change(criterion_name))
        
        # Store UI elements
        self.ui_elements[f"{criterion_name}_percentage_dropdown"] = dropdown
        self.ui_elements[f"{criterion_name}_percentage_field"] = field
        
        # Set initial dropdown value
        current_percentage = criterion_data['percentage']
        if current_percentage in self.PERCENTAGE_OPTIONS:
            cmds.optionMenu(dropdown, edit=True, select=self.PERCENTAGE_OPTIONS.index(current_percentage) + 1)
        else:
            cmds.optionMenu(dropdown, edit=True, select=len(self.PERCENTAGE_OPTIONS) + 1)
            
        cmds.setParent('..')
        return layout

    def _create_performance_indicators_layout(self, criterion_name, criterion_data):
        """Helper to create the performance level indicators with clickable buttons."""
        layout = cmds.rowLayout(numberOfColumns=5, columnAlign=[(i, 'center') for i in range(1, 6)], columnWidth=[(i, 60) for i in range(1, 6)], width=320)  # Fixed width to match header
        
        current_level = self._get_score_level_for_percentage(criterion_data['percentage'])
        for level_name in self.SCORE_LEVELS.keys():
            color = (0.4, 0.7, 0.4) if level_name == current_level else (0.6, 0.6, 0.6)
            # Create clickable button instead of text
            indicator = cmds.button(
                label=level_name.split()[0], 
                backgroundColor=color, 
                width=55, 
                height=25,
                command=lambda x, criterion=criterion_name, level=level_name: self._on_performance_indicator_click(criterion, level)
            )
            self.ui_elements[f"{criterion_name}_level_{level_name.split()[0]}"] = indicator
            
        cmds.setParent('..')
        return layout

    def _create_points_display_layout(self, criterion_name, criterion_data):
        """Helper to create the points display UI."""
        layout = cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 20), (2, 35)], width=60)  # Fixed width to match header
        
        calculated_score = self._calculate_criterion_score(criterion_name)
        cmds.text(label=f"{calculated_score:.1f}/")
        points_text = cmds.text(label=f"{criterion_data['point_value']:.1f}", font="boldLabelFont")
        
        # Store UI elements
        self.ui_elements[f"{criterion_name}_points"] = points_text
        self.ui_elements[f"{criterion_name}_points_layout"] = layout
        
        cmds.setParent('..')
        return layout
    

# ==============================================================================
# UI EVENT HANDLERS - User interaction callbacks
# ==============================================================================

    def _on_dropdown_change(self, criterion_name, selection):
        """Handle dropdown selection change for percentage."""
        # If "Custom" is selected, don't change the percentage field value
        if selection == "Custom":
            return  # Let user manually set their custom value
            
        # Extract percentage value from selection (e.g., "85%" -> 85)
        percentage_str = selection.replace('%', '')
        try:
            new_percentage = int(percentage_str)
            # Update the manual input field to match dropdown selection
            percentage_field = self.ui_elements[f"{criterion_name}_percentage_field"]
            cmds.intField(percentage_field, edit=True, value=new_percentage)
            # Update the criterion data and displays
            self._update_percentage_value(criterion_name, new_percentage)
        except ValueError:
            logger.warning(f"Invalid percentage selection: {selection}")
    
    def _on_performance_indicator_click(self, criterion_name, level_name):
        """Handle performance indicator button click."""
        # Get the default percentage for this performance level
        level_data = self.SCORE_LEVELS[level_name]
        default_percentage = level_data['default']
        
        # Update the percentage field to the default value for this level
        percentage_field = self.ui_elements[f"{criterion_name}_percentage_field"]
        cmds.intField(percentage_field, edit=True, value=default_percentage)
        
        # Update the dropdown to show "Custom" since we're setting a specific value
        dropdown = self.ui_elements[f"{criterion_name}_percentage_dropdown"]
        cmds.optionMenu(dropdown, edit=True, value="Custom")
        
        # Update the criterion data and displays
        # This will now generate performance-level appropriate comments
        self._update_percentage_value(criterion_name, default_percentage)
        
        logger.info(f"Set {criterion_name} to {default_percentage}% ({level_name})")
    
    def _on_percentage_field_change(self, criterion_name):
        """Handle manual percentage field change."""
        percentage_field = self.ui_elements[f"{criterion_name}_percentage_field"]
        new_percentage = cmds.intField(percentage_field, query=True, value=True)
        
        # Clamp percentage between 0 and 100
        new_percentage = max(0, min(100, new_percentage))
        cmds.intField(percentage_field, edit=True, value=new_percentage)
        
        # Update dropdown based on the value
        dropdown = self.ui_elements[f"{criterion_name}_percentage_dropdown"]
        if new_percentage in self.PERCENTAGE_OPTIONS:
            # If it matches a standard option, select that
            dropdown_index = self.PERCENTAGE_OPTIONS.index(new_percentage) + 1
            cmds.optionMenu(dropdown, edit=True, select=dropdown_index)
        else:
            # If it's a custom value, select "Custom"
            custom_index = len(self.PERCENTAGE_OPTIONS) + 1  # "Custom" is the last option
            cmds.optionMenu(dropdown, edit=True, select=custom_index)
        
        # Update the criterion data and displays
        self._update_percentage_value(criterion_name, new_percentage)
    
    def _update_percentage_value(self, criterion_name, new_percentage):
        """Update criterion percentage and refresh displays."""
        # Update criterion data
        self.criteria[criterion_name]['percentage'] = new_percentage
        
        # Calculate and update the score based on the new percentage
        # This ensures the individual criterion score is always in sync
        calculated_score = self._calculate_criterion_score(criterion_name)
        self.criteria[criterion_name]['score'] = calculated_score
        
        # Mark as manually adjusted first
        self.criteria[criterion_name]['manual_override'] = True
        
        # When user manually changes the percentage, we need to update comments appropriately
        # Get the existing validation comments to potentially concatenate with performance feedback
        existing_validation_comments = self.criteria[criterion_name].get('validation_comments', '')
        
        # Use enhanced comments logic which will concatenate for manual overrides
        enhanced_comments = self._create_enhanced_comments(criterion_name, new_percentage, existing_validation_comments)
        self.criteria[criterion_name]['comments'] = enhanced_comments
        
        # Update displays - this will refresh both the criterion display and total score
        self._update_criterion_display(criterion_name)
        self._update_total_score_display()
    
    def _on_percentage_change(self, criterion_name):
        """Legacy method - kept for backward compatibility if needed."""
        # This method is now replaced by the dropdown/field specific handlers
        pass
    
    def _update_criterion_display(self, criterion_name):
        """Update the display for a specific criterion."""
        if f"{criterion_name}_points_layout" in self.ui_elements:
            calculated_score = self._calculate_criterion_score(criterion_name)
            point_value = self.criteria[criterion_name]['point_value']
            
            # Update the points layout
            points_layout = self.ui_elements[f"{criterion_name}_points_layout"]
            
            # Delete existing children and recreate
            children = cmds.layout(points_layout, query=True, childArray=True)
            if children:
                for child in children:
                    cmds.deleteUI(child)
            
            # Recreate points display
            cmds.text(
                label=f"{calculated_score:.1f}/",
                parent=points_layout
            )
            
            cmds.text(
                label=f"{point_value:.1f}",
                font="boldLabelFont",
                parent=points_layout
            )
        
        # Update performance level indicators
        current_percentage = self.criteria[criterion_name]['percentage']
        current_level = self._get_score_level_for_percentage(current_percentage)
        
        for level_name in self.SCORE_LEVELS.keys():
            level_key = f"{criterion_name}_level_{level_name.split()[0]}"
            if level_key in self.ui_elements:
                color = (0.4, 0.7, 0.4) if level_name == current_level else (0.6, 0.6, 0.6)
                cmds.button(
                    self.ui_elements[level_key],
                    edit=True,
                    backgroundColor=color
                )
        
        # Update comment field if it exists
        if f"{criterion_name}_comment_field" in self.ui_elements:
            # Get existing comments from the criterion data, not from _generate_comments
            # This preserves specific validation function comments
            existing_comments = self.criteria[criterion_name].get('comments', '')
            if not existing_comments.strip():
                # Only generate generic comments if no specific comments exist
                existing_comments = self._generate_comments(criterion_name)
            
            cmds.scrollField(
                self.ui_elements[f"{criterion_name}_comment_field"],
                edit=True,
                text=existing_comments
            )
    
    def _update_total_score_display(self):
        """Update the total score display with dynamic background color."""
        if 'total_score' in self.ui_elements:
            total = self.calculate_total_score()
            
            # Determine background color based on score
            if total < 6.0:
                # Red for scores below 6
                background_color = (1.0, 0.3, 0.3)  # Red
            elif total <= 7.5:
                # Muted yellow for scores between 6 and 7.5 (less bright than warning)
                background_color = (1.0, 0.9, 0.5)  # Muted yellow
            else:
                # Green for scores above 7.5 (same as performance level indicator)
                background_color = (0.4, 0.7, 0.4)  # Green
            
            cmds.text(
                self.ui_elements['total_score'],
                edit=True,
                label=f"Total Grade: {total:.1f}/{self.total_points}",
                backgroundColor=background_color
            )
    
    def _update_all_scores(self):
        """
        Recalculate and update all scores and displays.
        
        This method is called by the Recalculate button and will:
        1. Ask user whether to preserve manual adjustments or recalculate everything
        2. Re-run validation functions based on user choice
        3. Update all UI displays with the new values
        """
        if not MAYA_AVAILABLE:
            # Fallback for non-Maya environments
            updated_count = self.re_run_validations()
            for criterion_name in self.criteria.keys():
                self._update_criterion_display(criterion_name)
            self._update_total_score_display()
            return
        
        # Check if there are any manual adjustments to preserve
        manual_adjustments = []
        for criterion_name, criterion in self.criteria.items():
            if criterion.get('manual_override', False):
                manual_adjustments.append(criterion_name)
        
        # Show different dialogs based on whether manual adjustments exist
        if manual_adjustments:
            # Show choice dialog when manual adjustments exist
            choice = cmds.confirmDialog(
                title="Recalculate Options",
                message=f"Found manual adjustments in {len(manual_adjustments)} criteria:\n• " + 
                       "\n• ".join(manual_adjustments) + 
                       "\n\nHow would you like to proceed?",
                button=["Keep Manual Adjustments", "Recalculate Everything", "Cancel"],
                defaultButton="Keep Manual Adjustments",
                cancelButton="Cancel",
                dismissString="Cancel"
            )
            
            if choice == "Cancel":
                return  # User cancelled, do nothing
            elif choice == "Recalculate Everything":
                # Reset all manual overrides and recalculate everything
                self._recalculate_all_criteria()
            else:  # "Keep Manual Adjustments"
                # Only recalculate non-manually adjusted criteria
                updated_count = self.re_run_validations()
                self._show_recalculate_results(updated_count, preserve_manual=True)
        else:
            # No manual adjustments - show simple confirmation
            choice = cmds.confirmDialog(
                title="Recalculate All Criteria",
                message="This will re-run all validation functions and update scores.\n\nProceed with recalculation?",
                button=["Recalculate", "Cancel"],
                defaultButton="Recalculate",
                cancelButton="Cancel",
                dismissString="Cancel"
            )
            
            if choice == "Cancel":
                return  # User cancelled, do nothing
            else:
                # Recalculate everything (no manual adjustments to worry about)
                self._recalculate_all_criteria()
        
        # Update all UI displays
        for criterion_name in self.criteria.keys():
            self._update_criterion_display(criterion_name)
        self._update_total_score_display()
    
    def _refresh_for_current_file(self):
        """
        Refresh the rubric for the current Maya file.
        
        This method completely reinitializes the rubric for the new file as if 
        the rubric was just opened fresh, including:
        1. Re-detecting if the current file is empty/minimal
        2. Getting the current Maya file name
        3. Updating the assignment name display
        4. Re-running all validation functions with fresh defaults
        5. Updating the empty file warning display
        6. Resetting all manual override flags
        
        This ensures the rubric behaves exactly like opening it fresh on the new file.
        """
        try:
            # STEP 1: Re-detect empty file status for the current scene
            # This is crucial for proper default scoring and warning display
            old_empty_status = self.is_empty_file
            self._check_empty_file()
            
            # STEP 2: Get current file name
            current_file = "Unknown File"
            try:
                scene_name = cmds.file(query=True, sceneName=True, shortName=True)
                if scene_name:
                    current_file = scene_name.rsplit('.', 1)[0]  # Remove extension
            except:
                pass
            
            # STEP 3: Update assignment name and display
            base_assignment = self.assignment_name.split(':')[0] if ':' in self.assignment_name else self.assignment_name
            self.assignment_name = f"{base_assignment}: {current_file}"
            self.assignment_display_name = current_file
            
            # Update window title if it exists
            if 'window' in self.ui_elements and cmds.window(self.ui_elements['window'], exists=True):
                cmds.window(self.ui_elements['window'], edit=True, title=f"Grading Rubric - {self.assignment_name}")
            
            # Update assignment name display in UI
            if 'assignment_display' in self.ui_elements:
                try:
                    cmds.text(
                        self.ui_elements['assignment_display'],
                        edit=True,
                        label=f"Assignment: {current_file}"
                    )
                except:
                    pass  # Field might not exist or be accessible
            
            # STEP 4: Update empty file warning display
            # We need to refresh the warning display when empty status changes
            self._update_empty_file_warning_display()
            
            # STEP 5: Reset all criteria with fresh defaults and validation
            total_updated = 0
            for criterion_name, criterion_data in self.criteria.items():
                # Reset manual override flag - treat as fresh rubric
                criterion_data['manual_override'] = False
                
                # Apply fresh default score based on current empty file status
                # This ensures proper default scoring for the new file context
                default_score = 10 if self.is_empty_file else 85
                criterion_data['percentage'] = default_score
                
                # Re-run validation function with new file context
                validation_func = criterion_data.get('validation_function')
                if validation_func:
                    try:
                        validation_args = criterion_data.get('validation_args', [])
                        # Update file name in args if this is a file validation
                        if validation_args and len(validation_args) > 0:
                            validation_args[0] = current_file
                        
                        if validation_args:
                            result = validation_func(*validation_args)
                        else:
                            result = validation_func()
                        
                        # Handle different validation function return types
                        if isinstance(result, tuple) and len(result) >= 2:
                            score, comments = result[0], result[1]
                        elif isinstance(result, (int, float)):
                            score = result
                            comments = f"Auto-validation: {score}%"
                        else:
                            # Keep defaults if validation returns unexpected format
                            continue
                        
                        # Update criterion data with validation results
                        criterion_data['percentage'] = score
                        criterion_data['validation_comments'] = comments
                        
                        # Create enhanced comments (will default to validation only since no manual override)
                        enhanced_comments = self._create_enhanced_comments(criterion_name, score, comments)
                        criterion_data['comments'] = enhanced_comments
                        
                        total_updated += 1
                        
                    except Exception as e:
                        print(f"Warning: Failed to update {criterion_name}: {e}")
                        # If validation fails, keep the fresh default score but generate default comments
                        criterion_data['comments'] = self._generate_comments(criterion_name)
                else:
                    # No validation function - just generate fresh default comments
                    criterion_data['comments'] = self._generate_comments(criterion_name)
            
            # STEP 6: Update all UI displays to reflect the refreshed state
            for criterion_name in self.criteria.keys():
                self._update_criterion_display(criterion_name)
            self._update_total_score_display()
            
            logger.info(f"Refreshed rubric for file: {current_file} (Empty: {self.is_empty_file}, Updated: {total_updated} criteria)")
            
        except Exception as e:
            logger.error(f"Failed to refresh rubric: {e}")
            if MAYA_AVAILABLE:
                cmds.confirmDialog(
                    title="Refresh Error",
                    message=f"Failed to refresh rubric: {str(e)}",
                    button=["OK"]
                )
    
    def _update_empty_file_warning_display(self):
        """
        Update the empty file warning display based on current file status.
        
        This method shows or hides the warning message that appears when
        an empty file is detected.
        """
        if not MAYA_AVAILABLE:
            return
            
        try:
            # Update the warning element visibility based on current empty file status
            if 'empty_file_warning' in self.ui_elements:
                cmds.text(
                    self.ui_elements['empty_file_warning'],
                    edit=True,
                    visible=self.is_empty_file
                )
                logger.info(f"Updated empty file warning visibility: {self.is_empty_file}")
            else:
                logger.warning("Empty file warning element not found in UI")
                
        except Exception as e:
            logger.warning(f"Could not update empty file warning display: {e}")
    
    def _recalculate_all_criteria(self):
        """
        Reset all manual overrides and recalculate all criteria from scratch.
        
        This completely resets the rubric to its initial validated state,
        discarding any manual adjustments made by the instructor.
        """
        recalculated_count = 0
        
        for criterion_name, criterion in self.criteria.items():
            # Reset manual override flag
            criterion['manual_override'] = False
            
            # Re-run validation if function exists
            validation_func = criterion.get('validation_function')
            validation_args = criterion.get('validation_args', [])
            
            if validation_func:
                try:
                    if validation_args:
                        score, comments = validation_func(*validation_args)
                    else:
                        score, comments = validation_func()
                    
                    # Update with fresh validation results
                    criterion['percentage'] = max(0, min(100, score))
                    
                    # Store the original validation comments
                    criterion['validation_comments'] = comments
                    
                    # For recalculation (resetting manual overrides), use enhanced comments logic
                    enhanced_comments = self._create_enhanced_comments(criterion_name, max(0, min(100, score)), comments)
                    criterion['comments'] = enhanced_comments
                    
                    recalculated_count += 1
                    
                except Exception as e:
                    # Keep existing values if validation fails
                    criterion['comments'] = f"Validation error: {str(e)}"
        
        self._show_recalculate_results(recalculated_count, preserve_manual=False)
    
    def _show_recalculate_results(self, updated_count, preserve_manual=True):
        """
        Show user feedback about recalculation results.
        
        Args:
            updated_count (int): Number of criteria that were updated
            preserve_manual (bool): Whether manual adjustments were preserved
        """
        if not MAYA_AVAILABLE:
            return
        
        if updated_count > 0:
            if preserve_manual:
                message = f"Re-ran validations for {updated_count} criteria.\nManually adjusted scores were preserved."
            else:
                message = f"Recalculated all {updated_count} criteria.\nAll manual adjustments were reset to validation results."
            
            """cmds.confirmDialog(
                title="Recalculation Complete",
                message=message,
                button=["OK"]
            )"""
        else:
            if preserve_manual:
                message = "All criteria have been manually adjusted or have no validation functions."
            else:
                message = "No criteria were updated - no validation functions available."
            
            """cmds.confirmDialog(
                title="No Updates",
                message=message,
                button=["OK"]
            )"""
    

# ==============================================================================
# EXPORT AND UTILITY METHODS
# ==============================================================================

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
            
            # Get current comments from UI field instead of stored data
            current_comments = ""
            if f"{criterion_name}_comment_field" in self.ui_elements:
                try:
                    current_comments = cmds.scrollField(
                        self.ui_elements[f"{criterion_name}_comment_field"],
                        query=True,
                        text=True
                    ).strip()
                except:
                    # Fallback to stored comments if UI read fails
                    current_comments = criterion_data.get('comments', '').strip()
            
            # If no current comments in UI, fallback to stored or generated comments
            if not current_comments:
                existing_comments = criterion_data.get('comments', '').strip()
                if not existing_comments:
                    current_comments = self._generate_comments(criterion_name)
                else:
                    current_comments = existing_comments
            
            results.append(f"  Comments: {current_comments}")
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
    
    def _open_assignment_selector(self):
        """
        Open the assignment grading rubric selector window.
        
        This allows instructors to easily switch between different assignments
        without having to go back through the Maya menu system.
        """
        try:
            from prof.tools.auto_grader.assignments.assignment_rubrics_window import grade_current_assignment
            grade_current_assignment()
            logger.info("Opened assignment rubric selector")
        except Exception as e:
            logger.error("Failed to open assignment selector: %s", e)
            if MAYA_AVAILABLE:
                cmds.confirmDialog(
                    title="Error",
                    message="Failed to open assignment selector. Please check the console for details.",
                    button=["OK"]
                )


# ==============================================================================
# SAMPLE RUBRIC CREATION - Template and example usage
# ==============================================================================

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
