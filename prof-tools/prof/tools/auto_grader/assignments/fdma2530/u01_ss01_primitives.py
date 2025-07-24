"""
FDMA 2530 - U01_SS01: Primitives Assignment Rubric

Assignment: Introduction to 3D modeling using primitive shapes
Focus: File organization, basic modeling principles, and technical execution

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric
import re


# ==============================================================================
# RUBRIC CONFIGURATION - Easy to modify criteria and points
# ==============================================================================

# Assignment Details
ASSIGNMENT_TITLE = "FDMA 2530 - U01_SS01"
PROJECT_NAME = "Primitive Modeling"
TOTAL_POINTS = 10

# Criteria Definition - Modify this list to add/remove/change criteria
RUBRIC_CRITERIA = [
    {
        "name": "File Names",
        "points": 2.0,
        "description": "Proper naming conventions for Maya scene file and project structure",
        "validation_function": "validate_file_name"
    },
    {
        "name": "Outliner Organization",
        "points": 2.0,
        "description": "Clean hierarchy, proper grouping, and logical object naming in Maya's Outliner",
        "validation_function": "validate_outliner_organization"
    },
    {
        "name": "Primitive Design Principles",
        "points": 2.0,
        "description": "Effective use of primitive shapes with attention to proportion, balance, and composition",
        "validation_function": "validate_primitive_design_principles"
    },
    {
        "name": "Technical Execution",
        "points": 2.0,
        "description": "Proper modeling techniques, clean geometry, and appropriate use of Maya tools",
        "validation_function": "validate_technical_execution"
    },
    {
        "name": "Perceived Effort/ Professionalism",
        "points": 2.0,
        "description": "Overall quality, attention to detail, and demonstration of effort and professional standards",
        "validation_function": "validate_effort_professionalism"
    }
]


# ==============================================================================
# MAIN RUBRIC CREATION FUNCTION
# ==============================================================================

def create_u01_ss01_rubric():
    """
    Create the FDMA 2530 U01_SS01 Primitives assignment rubric.
    
    Assignment Overview:
    - Students create basic 3D models using primitive shapes
    - Focus on proper file naming, organization, and technical execution
    - Introduction to design principles and professionalism standards
    """
    # Get current file name for assignment context
    file_name = "Primitives"
    if MAYA_AVAILABLE:
        try:
            scene_name = cmds.file(query=True, sceneName=True, shortName=True)
            if scene_name:
                file_name = scene_name.rsplit('.', 1)[0]
        except:
            pass
    
    assignment_name = f"{ASSIGNMENT_TITLE}: {file_name}"
    
    # Create rubric instance
    rubric = LessonRubric(
        assignment_name=assignment_name,
        assignment_display_name=file_name,
        total_points=TOTAL_POINTS,
        project_name=PROJECT_NAME
    )
    
    # Add all criteria from configuration
    for criterion in RUBRIC_CRITERIA:
        rubric.add_criterion(
            criterion["name"],
            criterion["points"],
            criterion["description"]
        )
    
    # Run validation logic for each criterion
    validation_results = {}
    for criterion in RUBRIC_CRITERIA:
        validation_func = globals().get(criterion["validation_function"])
        if validation_func:
            if criterion["validation_function"] == "validate_file_name":
                score, comments = validation_func(file_name)
            else:
                score, comments = validation_func()
            validation_results[criterion["name"]] = (score, comments)
    
    # Apply validation results to rubric
    for criterion_name, (score, comments) in validation_results.items():
        rubric.criteria[criterion_name]["percentage"] = score
        rubric.criteria[criterion_name]["comments"] = comments
        rubric.criteria[criterion_name]["manual_override"] = False
    
    # Show the rubric UI
    rubric.show_rubric_ui()
    
    return rubric


# ==============================================================================
# VALIDATION FUNCTIONS
# ==============================================================================

def validate_file_name(file_name):
    """
    Validate FDMA 2530 U01_SS01 file naming convention.
    
    Expected format: "XX_U01_SS01_V01_ZZ" OR "XX_U01_SS01_V01.ZZZZ"
    Where:
    - XX/XXX: Student initials (2-3 letters)
    - U01: Unit number (must be exactly "U01")
    - SS01: SoftSkill number (must be exactly "SS01") 
    - V##: Version number (must start with "V" + numbers)
    - ZZ/ZZZZ: Iteration number (optional, can be _## or .####)
    
    Scoring: 0 errors = 100%, 1 error = 90%, 2 errors = 70%, 3+ errors = 50%
    
    Args:
        file_name (str): The file name to validate
        
    Returns:
        tuple: (score_percentage, comments)
            score_percentage: 0-100 based on file name compliance
            comments: Detailed feedback about the file name
    """
    if not file_name or file_name.strip() == "":
        return (0, "No file name found.")
    
    # Remove common Maya file extensions for analysis
    clean_name = file_name
    for ext in ['.ma', '.mb', '.mayaAscii', '.mayaBinary']:
        if clean_name.lower().endswith(ext.lower()):
            clean_name = clean_name[:-len(ext)]
            break
    
    # Define the regex pattern for the expected format
    # Pattern breakdown:
    # ^([A-Za-z]{2,3})    - 2-3 initials at start
    # _                   - required underscore
    # (U\d+)              - Unit (should be U01)
    # _                   - required underscore  
    # (SS\d+)             - SoftSkill (should be SS01)
    # _                   - required underscore
    # (V\d+)              - Version (must start with V)
    # (?:_(\d+)|\.(\d+))? - optional iteration: either _## or .####
    # $                   - end of string
    pattern = r'^([A-Za-z]{2,3})_(U\d+)_(SS\d+)_(V\d+)(?:_(\d+)|\.(\d+))?$'
    
    match = re.match(pattern, clean_name)
    
    if not match:
        # Check for common structural issues and provide specific feedback
        structural_errors = []
        
        if '_' not in clean_name:
            structural_errors.append("Missing required underscores between components")
        
        if not re.search(r'^[A-Za-z]{2,3}_', clean_name):
            structural_errors.append("Should start with 2-3 letter initials followed by underscore")
        
        if 'U01' not in clean_name:
            structural_errors.append("Missing required unit number 'U01'")
        
        if 'SS01' not in clean_name:
            structural_errors.append("Missing required SoftSkill number 'SS01'")
        
        if not re.search(r'_V\d+', clean_name):
            structural_errors.append("Missing required version number (format: _V##)")
        
        # Score based on number of structural errors (these are major)
        error_count = len(structural_errors)
        if error_count >= 3:
            score = 50
        elif error_count == 2:
            score = 70
        elif error_count == 1:
            score = 90
        else:
            score = 70  # Format is wrong but structure might be okay
        
        # Generate specific error feedback
        if error_count > 0:
            comments = f"File name has {error_count} structural error(s): {'; '.join(structural_errors)}. Expected format: XX_U01_SS01_V##[_##|.####]"
        else:
            comments = "File name format incorrect. Expected: XX_U01_SS01_V##[_##|.####]"
        
        return (score, comments)
    
    # Extract components
    initials, unit, softskill, version, iter_underscore, iter_dot = match.groups()
    
    # Validate each component and collect specific errors
    errors = []
    
    # Check unit number (most critical)
    if unit != 'U01':
        errors.append(f"Unit number should be 'U01', found '{unit}'")
    
    # Check SoftSkill number (most critical)  
    if softskill != 'SS01':
        errors.append(f"SoftSkill number should be 'SS01', found '{softskill}'")
    
    # Check version format (must start with V)
    if not version.startswith('V'):
        errors.append(f"Version should start with 'V', found '{version}'")
    
    # Iteration number validation (if present)
    iteration_num = iter_underscore or iter_dot
    if iteration_num:
        try:
            iter_int = int(iteration_num)
            if iter_int < 1:
                errors.append("Iteration number should start from 01 (or 0001)")
        except ValueError:
            errors.append("Iteration number should be numeric")
    
    # Calculate score based on number of errors
    error_count = len(errors)
    if error_count == 0:
        score = 100
    elif error_count == 1:
        score = 90
    elif error_count == 2:
        score = 70
    else:  # 3 or more errors
        score = 50
    
    # Generate specific feedback comments
    if error_count == 0:
        if iteration_num:
            comments = f"Perfect file naming! Format: {initials}_{unit}_{softskill}_{version} with iteration {iteration_num}."
        else:
            comments = f"Perfect file naming! Format: {initials}_{unit}_{softskill}_{version}."
    elif error_count == 1:
        comments = f"Good file naming with 1 error: {errors[0]}"
    elif error_count == 2:
        comments = f"File naming has 2 errors: {errors[0]}; {errors[1]}"
    else:
        comments = f"File naming has {error_count} errors: {'; '.join(errors)}"
    
    return (score, comments)


def validate_outliner_organization():
    """
    Validate Maya Outliner organization and hierarchy.
    
    Checks for:
    - Clean hierarchy structure
    - Proper grouping of objects
    - Logical object naming conventions
    - No unnecessary empty groups
    
    Scoring: 0 errors = 100%, 1 error = 90%, 2 errors = 70%, 3+ errors = 50%
    
    Returns:
        tuple: (score_percentage, comments)
    """
    # TODO: Implement outliner validation logic
    return (85, "Manual evaluation required for Outliner Organization.")


def validate_primitive_design_principles():
    """
    Validate design principles in primitive modeling.
    
    Checks for:
    - Effective use of primitive shapes
    - Attention to proportion and balance
    - Good composition principles
    - Creative use of basic forms
    
    Scoring: 0 errors = 100%, 1 error = 90%, 2 errors = 70%, 3+ errors = 50%
    
    Returns:
        tuple: (score_percentage, comments)
    """
    # TODO: Implement design principles validation logic
    return (85, "Manual evaluation required for Primitive Design Principles.")


def validate_technical_execution():
    """
    Validate technical execution of modeling work.
    
    Checks for:
    - Proper modeling techniques
    - Clean geometry (no overlapping faces, proper normals)
    - Appropriate use of Maya tools
    - No construction history issues
    
    Scoring: 0 errors = 100%, 1 error = 90%, 2 errors = 70%, 3+ errors = 50%
    
    Returns:
        tuple: (score_percentage, comments)
    """
    # TODO: Implement technical execution validation logic
    return (85, "Manual evaluation required for Technical Execution.")


def validate_effort_professionalism():
    """
    Validate overall effort and professionalism.
    
    Checks for:
    - Overall quality and attention to detail
    - Demonstration of effort beyond minimum requirements
    - Professional presentation and finish
    - Evidence of learning and skill application
    
    Scoring: 0 errors = 100%, 1 error = 90%, 2 errors = 70%, 3+ errors = 50%
    
    Returns:
        tuple: (score_percentage, comments)
    """
    # TODO: Implement effort/professionalism validation logic
    return (85, "Manual evaluation required for Perceived Effort/Professionalism.")


if __name__ == "__main__":
    # When run directly, create and show the rubric
    if MAYA_AVAILABLE:
        create_u01_ss01_rubric()
    else:
        print("Maya not available - cannot display UI")
