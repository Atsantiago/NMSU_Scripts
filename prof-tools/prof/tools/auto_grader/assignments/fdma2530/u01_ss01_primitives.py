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
        "validation_function": "validate_file_name",
        "general_performance_comments": {
            100: "Perfect file naming! Follows the correct naming convention.",
            90: "Good file naming with 1 minor error. Review naming convention on Canvas.",
            70: "File naming has 2 errors. Check the required format: XX_U01_SS01_V##",
            50: "File naming has 3+ errors. Please review the naming instructions on Canvas carefully.",
            0: "No valid file name found or completely incorrect naming format."
        }
    },
    {
        "name": "Outliner Organization",
        "points": 2.0,
        "description": "Clean hierarchy, proper grouping, and logical object naming in the Outliner",
        "validation_function": "validate_outliner_organization",
        "general_performance_comments": {
            100: "Excellent outliner organization! Everything is named and grouped correctly.",
            90: "Good organization with 1 minor issue. Some grouping or naming issues.",
            70: "Some organization present but 2 areas need improvement (grouping/naming/hierarchy).",
            50: "Poor organization with 3+ issues. Review how to organize your scene on Canvas.",
            0: "No clear organization visible. No proper naming or grouping."
        }
    },
    {
        "name": "Primitive Design Principles",
        "points": 2.0,
        "description": "No modification of faces, edges, or verts.",
        "validation_function": "validate_primitive_design_principles",
        "general_performance_comments": {
            100: "Perfect adherence to primitive principles! No face/edge/vertex modifications detected.",
            90: "Excellent with 1 minor deviation from primitive principles.",
            70: "Good use of primitives but 2 areas show modified geometry.",
            50: "Multiple primitive violations detected (3+). Review assignment requirements on Canvas.",
            0: "Extensive geometry modifications. This should use only primitive shapes."
        }
    },
    {
        "name": "Technical Execution",
        "points": 2.0,
        "description": "Pivot points, duplication, and instances. Simplified complex shapes.",
        "validation_function": "validate_technical_execution",
        "general_performance_comments": {
            100: "Excellent technical execution! Proper pivot points, smart duplication/instancing used.",
            90: "Strong technical work with 1 minor area for improvement.",
            70: "Good technical foundation but 2 areas need attention (pivots/duplication/complexity).",
            50: "Basic technical execution with 3+ issues. Review technical tutorials on Canvas.",
            0: "Poor technical execution. Multiple fundamental issues need addressing."
        }
    },
    {
        "name": "Perceived Effort/ Professionalism",
        "points": 2.0,
        "description": "Project challenged student. Demonstration of effort and professional standards",
        "validation_function": "validate_effort_professionalism",
        "general_performance_comments": {
            100: "Outstanding effort and professionalism! Project shows creativity and exceeds expectations.",
            90: "Strong effort evident with professional presentation and 1 area to enhance.",
            70: "Adequate effort shown but project could demonstrate more challenge/professionalism.",
            50: "Minimal effort apparent. Project needs more development to show learning growth.",
            0: "Insufficient effort demonstrated. Project appears rushed or incomplete."
        }
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
    file_name = "Unknown File"
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
        # Get the validation function for this criterion
        validation_func = globals().get(criterion["validation_function"])
        
        # Determine validation arguments based on the function
        validation_args = []
        if criterion["validation_function"] == "validate_file_name":
            validation_args = [file_name]
        
        # Get performance comments for this criterion
        general_performance_comments = criterion.get("general_performance_comments", {})
        
        rubric.add_criterion(
            name=criterion["name"],
            point_value=criterion["points"],
            description=criterion["description"],
            validation_function=validation_func,
            validation_args=validation_args,
            general_performance_comments=general_performance_comments
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
        rubric.criteria[criterion_name]["validation_comments"] = comments  # Store original validation comments
        
        # Use enhanced comments logic for initial display (will default to validation comments only)
        enhanced_comments = rubric._create_enhanced_comments(criterion_name, score, comments)
        rubric.criteria[criterion_name]["comments"] = enhanced_comments
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
    1. No unparented objects (all objects should be in proper groups)
    2. Lights grouped together with "light" or "lights" in group name
    3. Turntable_ROT group containing polygon geometry or other groups
    4. No default object names (excluding startup cameras)
    
    Scoring: 0 errors = 100%, 1 error = 90%, 2 errors = 70%, 3+ errors = 50%
    
    Returns:
        tuple: (score_percentage, comments)
    """
    if not MAYA_AVAILABLE:
        return (0, "Maya not available for validation.")
    
    # Default object names to check for (excluding cameras) - optimized set for faster lookup
    DEFAULT_OBJECT_NAMES = {
        "nurbsSphere", "nurbsCube", "nurbsCylinder", "nurbsCone",
        "nurbsPlane", "nurbsTorus", "nurbsCircle", "nurbsSquare", 
        "pSphere", "pCube", "pCylinder", "pCone", "pPlane", "pTorus",
        "pPrism", "pPyramid", "pPipe", "pHelix", "pSolid", 
        "rsPhysicalLight", "rsIESLight", "rsPortalLight", "aiAreaLight",
        "rsDomeLight", "aiPhotometricLight", "aiLightPortal",
        "ambientLight", "directionalLight", "pointLight", "spotLight",
        "areaLight", "volumeLight"
    }
    
    # Startup cameras to exclude - optimized set for faster lookup
    STARTUP_CAMERAS = {"persp", "top", "front", "side"}
    
    errors = []
    warnings = []
    
    try:
        # Get all transforms once for efficiency
        all_transforms = cmds.ls(type='transform', long=False) or []
        
        # Filter out startup cameras early
        filtered_transforms = [obj for obj in all_transforms if obj not in STARTUP_CAMERAS]
        
        # Check 1: Unparented Objects (optimized approach)
        unparented_objects = []
        
        # Get all top-level transforms (objects with no parent)
        top_level_objects = cmds.ls(assemblies=True) or []
        
        # Filter out cameras and other non-geometry parents
        for obj in top_level_objects:
            if obj not in STARTUP_CAMERAS:
                # Check if this object or its children contain geometry
                descendants = cmds.listRelatives(obj, allDescendents=True, type='mesh') or []
                if descendants:
                    unparented_objects.append(obj)
        
        if unparented_objects:
            errors.append(f"Found {len(unparented_objects)} unparented object(s): {', '.join(unparented_objects[:3])}{'...' if len(unparented_objects) > 3 else ''}")
        
        # Check 2: Light Organization (optimized light detection)
        # Get all light types in one call
        all_lights = cmds.ls(type=['directionalLight', 'pointLight', 'spotLight', 'areaLight', 'volumeLight', 
                                   'ambientLight', 'aiAreaLight', 'aiPhotometricLight', 'aiLightPortal',
                                   'rsPhysicalLight', 'rsIESLight', 'rsPortalLight', 'rsDomeLight']) or []
        
        if all_lights:
            # Find light groups efficiently using pre-filtered transforms
            light_groups = [group for group in filtered_transforms if 'light' in group.lower()]
            
            if not light_groups:
                errors.append("No light organization group found (should contain 'light' or 'lights' in name)")
            else:
                # Check light grouping more efficiently
                ungrouped_lights = []
                
                # Build a set of all objects under light groups for fast lookup
                light_group_descendants = set()
                for light_group in light_groups:
                    descendants = cmds.listRelatives(light_group, allDescendents=True, type='transform') or []
                    light_group_descendants.update(descendants)
                
                # Check each light's transform
                for light in all_lights:
                    light_transforms = cmds.listRelatives(light, parent=True, type='transform') or []
                    if light_transforms:
                        light_transform = light_transforms[0]
                        # Check if this light transform is under any light group
                        if light_transform not in light_group_descendants and light_transform not in light_groups:
                            ungrouped_lights.append(light_transform)
                
                if ungrouped_lights:
                    warnings.append(f"Some lights may not be properly grouped: {', '.join(ungrouped_lights[:2])}{'...' if len(ungrouped_lights) > 2 else ''}")
        
        # Check 3: Turntable_ROT group (optimized search)
        turntable_groups = [transform for transform in filtered_transforms 
                           if 'turntable_rot' in transform.lower() or 'turntable' in transform.lower()]
        
        if not turntable_groups:
            errors.append("No 'Turntable_ROT' group found for geometry organization")
        else:
            # Check if turntable group has children efficiently
            has_geometry = any(cmds.listRelatives(group, children=True, type='transform') 
                             for group in turntable_groups)
            
            if not has_geometry:
                warnings.append("Turntable group exists but appears to be empty")
        
        # Check 4: Default Object Names (optimized with set lookup)
        offending_objects = []
        
        for obj in filtered_transforms:
            # Use set membership for O(1) lookup instead of list iteration
            for def_name in DEFAULT_OBJECT_NAMES:
                if obj.startswith(def_name):
                    offending_objects.append(obj)
                    break  # No need to check other default names for this object
        
        if offending_objects:
            errors.append(f"Found {len(offending_objects)} object(s) with default names: {', '.join(offending_objects[:3])}{'...' if len(offending_objects) > 3 else ''}")
        
        # Calculate score based on total issues
        total_errors = len(errors)
        total_warnings = len(warnings)
        
        if total_errors == 0 and total_warnings == 0:
            score = 100
            comments = "Excellent outliner organization! All objects properly grouped and named."
        elif total_errors == 0 and total_warnings <= 1:
            score = 90
            comments = f"Good organization with minor issues: {'; '.join(warnings)}"
        elif total_errors == 1 or (total_errors == 0 and total_warnings == 2):
            score = 70
            comments = f"Organization needs improvement: {'; '.join(errors + warnings)}"
        else:
            score = 50
            comments = f"Poor organization with multiple issues: {'; '.join(errors + warnings)}"
        
        return (score, comments)
        
    except Exception as e:
        return (50, f"Error validating outliner organization: {str(e)}")


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
