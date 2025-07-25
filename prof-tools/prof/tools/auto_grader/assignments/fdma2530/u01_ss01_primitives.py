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
    5. No NURBS primitives (assignment requires polygon primitives only)
    
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
        
        # ========================================================================
        # First, identify all light transforms so we can exclude them from geometry checks
        # ========================================================================
        
        # Light types to check - using same approach as CMI-tools checklist.py
        maya_light_types = ['pointLight', 'directionalLight', 'spotLight', 'areaLight', 'volumeLight', 'ambientLight']
        arnold_light_types = ['aiAreaLight', 'aiSkyDomeLight', 'aiPhotometricLight', 'aiMeshLight', 'aiLightPortal']
        redshift_light_types = ['rsPhysicalLight', 'rsIESLight', 'rsPortalLight', 'rsDomeLight']
        
        all_light_shapes = []
        all_light_types = maya_light_types + arnold_light_types + redshift_light_types
        
        # Find all light shapes using the proven approach from CMI-tools
        for light_type in all_light_types:
            lights_of_type = cmds.ls(type=light_type) or []
            all_light_shapes.extend(lights_of_type)
        
        # Debug: Print all light shapes found for troubleshooting
        print(f"DEBUG: Found {len(all_light_shapes)} light shapes in scene: {all_light_shapes}")
        
        # Find the transform nodes that contain these light shapes
        light_transforms = []
        for light_shape in all_light_shapes:
            # Get the transform parent of each light shape
            light_parents = cmds.listRelatives(light_shape, parent=True, type='transform') or []
            if light_parents:
                light_transform = light_parents[0]
                if light_transform not in light_transforms:
                    light_transforms.append(light_transform)
                    print(f"DEBUG: Found light transform '{light_transform}' for light shape '{light_shape}'")
        
        print(f"DEBUG: Found {len(light_transforms)} unique light transforms: {light_transforms}")
        
        # ========================================================================
        # Check 1: Unparented Objects (excluding light transforms)
        # ========================================================================
        
        unparented_objects = []
        geo_dag_nodes = cmds.ls(geometry=True)
        
        print(f"DEBUG: Found {len(geo_dag_nodes)} geometry nodes: {geo_dag_nodes}")
        
        if geo_dag_nodes:
            for obj in geo_dag_nodes:
                try:
                    # Get the transform parent of this geometry node
                    geo_parents = cmds.listRelatives(obj, parent=True, type='transform') or []
                    if geo_parents:
                        geo_transform = geo_parents[0]
                        
                        # Skip if this geometry belongs to a light transform - lights should be handled separately
                        if geo_transform in light_transforms:
                            print(f"DEBUG: Skipping geometry '{obj}' because it belongs to light transform '{geo_transform}'")
                            continue
                        
                        # Check if the geometry's transform is unparented
                        transform_parents = cmds.listRelatives(geo_transform, parent=True, type='transform') or []
                        
                        if not transform_parents:
                            print(f"DEBUG: Found unparented geometry transform '{geo_transform}' for geometry '{obj}'")
                            if geo_transform not in unparented_objects:
                                unparented_objects.append(geo_transform)
                except Exception:
                    continue
        
        # ========================================================================
        # Check 2: Unparented Lights (these should always be grouped)
        # ========================================================================
        
        unparented_lights = []
        
        # Check which light transforms are unparented (at world level)
        for light_transform in light_transforms:
            # Check if light transform is at top level (no parent)
            transform_parents = cmds.listRelatives(light_transform, parent=True, type='transform') or []
            print(f"DEBUG: Light '{light_transform}' has parents: {transform_parents}")
            
            if not transform_parents:
                # Skip startup cameras that might contain light components
                if light_transform not in STARTUP_CAMERAS:
                    print(f"DEBUG: Adding '{light_transform}' to unparented lights list")
                    unparented_lights.append(light_transform)
                else:
                    print(f"DEBUG: Skipping startup camera '{light_transform}'")
        
        print(f"DEBUG: Final unparented lights list: {unparented_lights}")
        
        # Report unparented issues with specific feedback (no truncation)
        if unparented_objects or unparented_lights:
            error_parts = []
            if unparented_objects:
                error_parts.append(f"{len(unparented_objects)} unparented geometry object(s): {', '.join(unparented_objects)}")
            if unparented_lights:
                error_parts.append(f"{len(unparented_lights)} unparented light(s): {', '.join(unparented_lights)} (lights must be grouped)")
            
            errors.append("Found " + "; ".join(error_parts))
        
        # ========================================================================
        # Check 3: Light Organization (verify lights are in proper light groups)
        # ========================================================================
        # This checks that lights are not just grouped, but grouped with appropriate naming
        
        if light_transforms:
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
                
                # Check each light transform directly
                for light_transform in light_transforms:
                    # Check if this light transform is under any light group
                    if light_transform not in light_group_descendants and light_transform not in light_groups:
                        ungrouped_lights.append(light_transform)
                
                if ungrouped_lights:
                    warnings.append(f"Some lights may not be in proper light groups: {', '.join(ungrouped_lights)}")
        
        # ========================================================================
        # Check 4: Turntable_ROT group (geometry organization)
        # ========================================================================
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
        
        # ========================================================================
        # Check 5: Default Object Names (excluding startup cameras)
        # ========================================================================
        # Check for objects with default Maya names - these should be renamed descriptively
        
        offending_objects = []
        
        for obj in filtered_transforms:
            # Use set membership for O(1) lookup instead of list iteration
            for def_name in DEFAULT_OBJECT_NAMES:
                if obj.startswith(def_name):
                    offending_objects.append(obj)
                    break  # No need to check other default names for this object
        
        if offending_objects:
            errors.append(f"Found {len(offending_objects)} object(s) with default names: {', '.join(offending_objects)}")
        
        # ========================================================================
        # Check 6: NURBS Primitives Usage (should use polygon primitives only)
        # ========================================================================
        # This assignment is about polygon modeling - NURBS primitives should be penalized
        
        nurbs_objects = []
        # Check for NURBS surfaces and curves
        nurbs_surfaces = cmds.ls(type='nurbsSurface') or []
        nurbs_curves = cmds.ls(type='nurbsCurve') or []
        
        # Get transform parents of NURBS geometry
        for nurbs_surface in nurbs_surfaces:
            surface_transforms = cmds.listRelatives(nurbs_surface, parent=True, type='transform') or []
            for transform in surface_transforms:
                if transform not in nurbs_objects:
                    nurbs_objects.append(transform)
        
        for nurbs_curve in nurbs_curves:
            curve_transforms = cmds.listRelatives(nurbs_curve, parent=True, type='transform') or []
            for transform in curve_transforms:
                if transform not in nurbs_objects:
                    nurbs_objects.append(transform)
        
        if nurbs_objects:
            errors.append(f"Found {len(nurbs_objects)} NURBS object(s): {', '.join(nurbs_objects)} (assignment requires polygon primitives only)")
        
        # ========================================================================
        # Calculate score with weighted penalties based on issue types and severity
        # ========================================================================
        
        # Count specific error types for weighted scoring
        error_weight = 0
        total_warnings = len(warnings)
        
        # Count unparented objects (lights + geometry combined)
        total_unparented = len(unparented_objects) + len(unparented_lights)
        
        # Penalty 1: Unparented objects (weighted by severity)
        if total_unparented > 0:
            if total_unparented < 3:
                error_weight += 1  # Minor penalty for 1-2 unparented objects
            else:
                error_weight += 2  # Major penalty for 3+ unparented objects
        
        # Penalty 2: Light organization issues (strict but reasonable)
        if unparented_lights:
            # If lights are unparented, this is already counted above
            # But if there are light organization issues (from Check 2), add penalty
            pass
        elif "No light organization group found" in "; ".join(errors):
            error_weight += 1  # Missing light group structure
        
        # Penalty 3: Missing Turntable_ROT group
        if "No 'Turntable_ROT' group found" in "; ".join(errors):
            error_weight += 1
        
        # Penalty 4: Default object names (graduated penalties)
        default_name_objects = [err for err in errors if "default names" in err]
        if default_name_objects:
            # Extract count from error message
            import re
            match = re.search(r'Found (\d+) object\(s\) with default names', default_name_objects[0])
            if match:
                default_count = int(match.group(1))
                
                # Check if all defaults are lights (stricter penalty)
                light_defaults = [obj for obj in offending_objects if any(light_type in obj.lower() for light_type in ['light', 'directional', 'point', 'spot', 'area', 'volume', 'ambient'])]
                
                if len(light_defaults) == default_count and default_count > 0:
                    # All default names are lights - 85% score (15% penalty)
                    error_weight += 1.5
                elif default_count == 1:
                    # Single default name - 95% score (5% penalty)
                    error_weight += 0.5
                elif default_count <= 3:
                    # Few default names - moderate penalty
                    error_weight += 1
                else:
                    # Many default names - major penalty
                    error_weight += 2
        
        # Penalty 5: NURBS usage (major violation for this assignment)
        if nurbs_objects:
            error_weight += 2  # Major penalty for using wrong primitive type
        
        # Generate specific feedback based on issue types
        organizational_issues = []
        naming_issues = []
        other_issues = []
        
        # Categorize errors for more specific feedback
        for error in errors:
            if "unparented" in error.lower() or "turntable" in error.lower() or "light organization" in error.lower():
                organizational_issues.append(error)
            elif "default names" in error.lower():
                naming_issues.append(error)
            else:
                other_issues.append(error)
        
        # Convert error weight to score and generate targeted comments
        if error_weight == 0 and total_warnings == 0:
            score = 100
            comments = "Excellent outliner organization! All objects properly grouped and named."
        elif error_weight <= 0.5:
            score = 95
            if naming_issues and not organizational_issues:
                comments = f"Very good organization with minor naming issue: {'; '.join(naming_issues + warnings)}"
            elif organizational_issues and not naming_issues:
                comments = f"Very good naming with minor organizational issue: {'; '.join(organizational_issues + warnings)}"
            else:
                comments = f"Very good organization with minimal issues: {'; '.join(errors + warnings)}"
        elif error_weight <= 1.0:
            score = 90
            if naming_issues and not organizational_issues:
                comments = f"Good organization but naming needs attention: {'; '.join(naming_issues + warnings)}"
            elif organizational_issues and not naming_issues:
                comments = f"Good naming but organization needs attention: {'; '.join(organizational_issues + warnings)}"
            else:
                comments = f"Good outliner organization with minor issues: {'; '.join(errors + warnings)}"
        elif error_weight <= 1.5:
            score = 85
            if naming_issues and not organizational_issues:
                comments = f"Organization structure is good but naming needs improvement: {'; '.join(naming_issues + warnings)}"
            elif organizational_issues and not naming_issues:
                comments = f"Naming is good but organization needs improvement: {'; '.join(organizational_issues + warnings)}"
            else:
                comments = f"Both organization and naming need improvement: {'; '.join(errors + warnings)}"
        elif error_weight <= 2.0:
            score = 70
            if naming_issues and not organizational_issues:
                comments = f"Naming needs some work: {'; '.join(naming_issues + warnings)}"
            elif organizational_issues and not naming_issues:
                comments = f"Organization needs some work: {'; '.join(organizational_issues + warnings)}"
            else:
                comments = f"Both organization and naming need improvement: {'; '.join(errors + warnings)}"
        else:
            score = 50
            if naming_issues and not organizational_issues:
                comments = f"Poor naming with multiple issues (organization structure is present): {'; '.join(naming_issues + warnings)}"
            elif organizational_issues and not naming_issues:
                comments = f"Poor organization with multiple issues (naming is acceptable): {'; '.join(organizational_issues + warnings)}"
            else:
                comments = f"Poor organization with multiple issues in both structure and naming: {'; '.join(errors + warnings)}"
        
        return (score, comments)
        
    except Exception as e:
        return (50, f"Error validating outliner organization: {str(e)}")


def validate_primitive_design_principles():
    """
    Validate design principles in primitive modeling.
    
    Checks for:
    - Only Maya default polygon primitives are used (no edge/face/vertex modifications)
    - Students can scale, move, rotate, and alter initial primitive attributes
    - At least 10% of polygon objects should have modified utility helper node attributes
    - No extrusions, edge loops, or topology changes allowed
    
    Scoring: 0 violations = 100%, minor violations = 90%, moderate = 70%, major = 50%
    
    Returns:
        tuple: (score_percentage, comments)
    """
    if not MAYA_AVAILABLE:
        return (0, "Maya not available for validation.")
    
    try:
        # Get all polygon meshes in the scene
        all_meshes = cmds.ls(type='mesh') or []
        
        if not all_meshes:
            return (100, "No polygon objects found in scene to evaluate.")
        
        # Get transform parents for all meshes
        mesh_transforms = []
        for mesh in all_meshes:
            transforms = cmds.listRelatives(mesh, parent=True, type='transform') or []
            if transforms:
                mesh_transforms.append(transforms[0])
        
        print(f"DEBUG: Found {len(mesh_transforms)} polygon objects to check for primitive compliance")
        
        violations = []
        modified_attributes_count = 0
        total_primitives = 0
        
        # Define expected primitive topologies and vertex patterns
        primitive_topologies = {
            'pCube': {'vertices': 8, 'faces': 6, 'edges': 12},
            'pSphere': {'vertices': 382, 'faces': 760, 'edges': 1140},  # Default sphere (subdivisionsU=20, subdivisionsV=10)
            'pCylinder': {'vertices': 42, 'faces': 60, 'edges': 100},   # Default cylinder (subdivisionsAxis=20, subdivisionsHeight=1)
            'pCone': {'vertices': 22, 'faces': 40, 'edges': 60},        # Default cone (subdivisionsAxis=20, subdivisionsHeight=1)
            'pPlane': {'vertices': 4, 'faces': 1, 'edges': 4},          # Default plane (subdivisionsU=1, subdivisionsV=1)
            'pTorus': {'vertices': 400, 'faces': 400, 'edges': 800},    # Default torus (subdivisionsU=20, subdivisionsV=20)
        }
        
        # Define default vertex positions for Maya primitives (normalized)
        # These are the exact vertex positions Maya creates for default primitives
        default_vertex_positions = {
            'pCube': [
                (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5),
                (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5)
            ],
            'pPlane': [
                (-0.5, 0.0, 0.5), (0.5, 0.0, 0.5), (-0.5, 0.0, -0.5), (0.5, 0.0, -0.5)
            ]
            # For sphere, cylinder, cone, torus - we'll use topology + smoothness detection
            # since their vertex positions are more complex and parametric
        }
        
        def check_vertex_positions_match(mesh, primitive_type, tolerance=0.001):
            """
            Check if mesh vertex positions match default Maya primitive positions.
            Returns True if positions match (within tolerance), False if modified.
            """
            if primitive_type not in default_vertex_positions:
                return None  # Can't check this primitive type with vertex positions
            
            try:
                # Get current vertex positions
                vertex_count = cmds.polyEvaluate(mesh, vertex=True)
                expected_positions = default_vertex_positions[primitive_type]
                
                if vertex_count != len(expected_positions):
                    return False  # Wrong number of vertices
                
                # Get vertex positions in world space, then convert to object space
                current_positions = []
                for i in range(vertex_count):
                    pos = cmds.pointPosition(f"{mesh}.vtx[{i}]", world=True)
                    current_positions.append((pos[0], pos[1], pos[2]))
                
                # Get the transform to normalize positions
                transform = cmds.listRelatives(mesh, parent=True, type='transform')[0]
                
                # Get transform matrix to normalize positions
                try:
                    # Get bounding box to normalize scale
                    bbox = cmds.exactWorldBoundingBox(transform)
                    if bbox:
                        width = bbox[3] - bbox[0]
                        height = bbox[4] - bbox[1] 
                        depth = bbox[5] - bbox[2]
                        center_x = (bbox[0] + bbox[3]) / 2
                        center_y = (bbox[1] + bbox[4]) / 2
                        center_z = (bbox[2] + bbox[5]) / 2
                        
                        # Normalize current positions to -0.5 to 0.5 range like Maya defaults
                        normalized_positions = []
                        for pos in current_positions:
                            if width > tolerance: norm_x = (pos[0] - center_x) / width
                            else: norm_x = 0
                            if height > tolerance: norm_y = (pos[1] - center_y) / height  
                            else: norm_y = 0
                            if depth > tolerance: norm_z = (pos[2] - center_z) / depth
                            else: norm_z = 0
                            normalized_positions.append((norm_x, norm_y, norm_z))
                        
                        # Compare normalized positions to expected
                        for i, (curr, expected) in enumerate(zip(normalized_positions, expected_positions)):
                            diff_x = abs(curr[0] - expected[0])
                            diff_y = abs(curr[1] - expected[1]) 
                            diff_z = abs(curr[2] - expected[2])
                            if diff_x > tolerance or diff_y > tolerance or diff_z > tolerance:
                                return False
                        
                        return True
                except:
                    return None  # Can't determine due to transform issues
                    
            except Exception as e:
                print(f"DEBUG: Error checking vertex positions for {mesh}: {e}")
                return None
        
        def detect_smoothing_by_topology(mesh, primitive_type):
            """
            Detect if an object has been smoothed by analyzing topology patterns.
            Returns (is_smoothed, confidence_level)
            """
            try:
                vertex_count = cmds.polyEvaluate(mesh, vertex=True)
                face_count = cmds.polyEvaluate(mesh, face=True)
                edge_count = cmds.polyEvaluate(mesh, edge=True)
                
                # Known topology patterns for smoothed primitives (1 iteration)
                smoothed_topologies = {
                    'pCube': {'vertices': 26, 'faces': 24, 'edges': 48},      # Smoothed cube
                    'pSphere': {'vertices': 1522, 'faces': 1520, 'edges': 3040}, # Smoothed sphere (approx)
                    'pCylinder': {'vertices': 162, 'faces': 160, 'edges': 320},  # Smoothed cylinder (approx)
                    'pCone': {'vertices': 82, 'faces': 80, 'edges': 160},        # Smoothed cone (approx)
                    'pPlane': {'vertices': 9, 'faces': 4, 'edges': 12},          # Smoothed plane
                    'pTorus': {'vertices': 1600, 'faces': 1600, 'edges': 3200}   # Smoothed torus (approx)
                }
                
                expected_smooth = smoothed_topologies.get(primitive_type, {})
                if not expected_smooth:
                    return False, 0.0
                
                # Check if topology matches smoothed pattern (with some tolerance)
                vertex_match = abs(vertex_count - expected_smooth['vertices']) <= 2
                face_match = abs(face_count - expected_smooth['faces']) <= 2
                edge_match = abs(edge_count - expected_smooth['edges']) <= 4
                
                if vertex_match and face_match and edge_match:
                    return True, 0.9  # High confidence smoothed
                
                # Check for other smoothing indicators
                original_topo = primitive_topologies.get(primitive_type, {})
                if original_topo:
                    # If vertex count is significantly higher than original, likely smoothed
                    vertex_ratio = vertex_count / original_topo['vertices']
                    if vertex_ratio > 2.0:  # More than double the vertices
                        return True, 0.7  # Medium confidence smoothed
                
                return False, 0.0
                
            except Exception as e:
                print(f"DEBUG: Error detecting smoothing for {mesh}: {e}")
                return False, 0.0
        
        for transform in mesh_transforms:
            try:
                # Skip if this is a light transform
                children = cmds.listRelatives(transform, children=True, shapes=True) or []
                is_light = any(cmds.nodeType(child) in ['directionalLight', 'pointLight', 'spotLight', 'areaLight', 'volumeLight', 'ambientLight', 'aiAreaLight', 'aiSkyDomeLight', 'aiPhotometricLight', 'aiMeshLight', 'aiLightPortal', 'rsPhysicalLight', 'rsIESLight', 'rsPortalLight', 'rsDomeLight'] for child in children)
                
                if is_light:
                    continue
                
                # Get the mesh shape
                mesh_shapes = cmds.listRelatives(transform, children=True, type='mesh') or []
                if not mesh_shapes:
                    continue
                
                mesh = mesh_shapes[0]
                
                # Check if this looks like a primitive based on name
                primitive_type = None
                for prim_name in primitive_topologies.keys():
                    if transform.startswith(prim_name):
                        primitive_type = prim_name
                        break
                
                if not primitive_type:
                    # If name doesn't indicate primitive, check if it has construction history
                    history = cmds.listHistory(mesh, pruneDagObjects=True) or []
                    primitive_nodes = [node for node in history if cmds.nodeType(node).startswith('poly') and 'prim' in cmds.nodeType(node).lower()]
                    
                    if not primitive_nodes:
                        violations.append(f"'{transform}' does not appear to be a Maya primitive (no primitive construction history)")
                        continue
                    
                    # Try to determine primitive type from construction history
                    for node in primitive_nodes:
                        node_type = cmds.nodeType(node)
                        if 'Cube' in node_type:
                            primitive_type = 'pCube'
                        elif 'Sphere' in node_type:
                            primitive_type = 'pSphere'
                        elif 'Cylinder' in node_type:
                            primitive_type = 'pCylinder'
                        elif 'Cone' in node_type:
                            primitive_type = 'pCone'
                        elif 'Plane' in node_type:
                            primitive_type = 'pPlane'
                        elif 'Torus' in node_type:
                            primitive_type = 'pTorus'
                        break
                
                if not primitive_type:
                    violations.append(f"'{transform}' could not be identified as a Maya primitive")
                    continue
                
                total_primitives += 1
                
                # Check if topology has been modified
                vertex_count = cmds.polyEvaluate(mesh, vertex=True)
                face_count = cmds.polyEvaluate(mesh, face=True)
                edge_count = cmds.polyEvaluate(mesh, edge=True)
                
                print(f"DEBUG: {transform} ({primitive_type}) - V:{vertex_count}, F:{face_count}, E:{edge_count}")
                
                # For sphere, cylinder, cone, torus - check if attributes were modified
                expected_topology = primitive_topologies.get(primitive_type, {})
                
                # Check construction history for forbidden operations
                history = cmds.listHistory(mesh, pruneDagObjects=True) or []
                
                # Look for forbidden operations in construction history
                forbidden_operations = []
                
                for node in history:
                    node_type = cmds.nodeType(node)
                    
                    # Check for smoothing operations
                    if 'smooth' in node_type.lower() or node_type in ['polySmoothFace', 'polySmooth']:
                        forbidden_operations.append(f"Smooth operation ({node_type})")
                    
                    # Check for subdivision operations
                    elif 'subdiv' in node_type.lower() or node_type in ['polySubdFace', 'polySubdEdge']:
                        forbidden_operations.append(f"Subdivision operation ({node_type})")
                    
                    # Check for extrude operations
                    elif 'extrude' in node_type.lower() or node_type in ['polyExtrudeFace', 'polyExtrudeEdge', 'polyExtrudeVertex']:
                        forbidden_operations.append(f"Extrude operation ({node_type})")
                    
                    # Check for edge/face operations
                    elif node_type in ['polySplit', 'polySplitRing', 'polyConnectComponents', 'polyMergeVert', 'polyDeleteComponent']:
                        forbidden_operations.append(f"Topology modification ({node_type})")
                    
                    # Check for polyTweak nodes (vertex movement)
                    elif node_type == 'polyTweak':
                        # Check if any vertices were actually moved
                        try:
                            tweak_list = cmds.getAttr(f"{node}.tweak") or []
                            if tweak_list and len(tweak_list) > 0:
                                # Check if any tweaks are non-zero
                                has_tweaks = False
                                for tweak in tweak_list:
                                    if abs(tweak[0]) > 0.0001 or abs(tweak[1]) > 0.0001 or abs(tweak[2]) > 0.0001:
                                        has_tweaks = True
                                        break
                                if has_tweaks:
                                    forbidden_operations.append(f"Vertex movement (polyTweak)")
                        except:
                            # If we can't read the tweak data, assume it has tweaks
                            forbidden_operations.append(f"Vertex movement (polyTweak)")
                
                # Check for smooth preview (displaySmoothMesh attribute)
                try:
                    smooth_preview = cmds.getAttr(f"{mesh}.displaySmoothMesh")
                    if smooth_preview and smooth_preview > 0:
                        forbidden_operations.append("Smooth preview enabled (should be disabled)")
                except:
                    pass
                
                if forbidden_operations:
                    violations.append(f"'{transform}' has forbidden operations: {', '.join(forbidden_operations)}")
                    continue
                
                # Find the primitive creation node for attribute checking
                primitive_node = None
                for node in history:
                    node_type = cmds.nodeType(node)
                    if (primitive_type == 'pCube' and 'Cube' in node_type) or \
                       (primitive_type == 'pSphere' and 'Sphere' in node_type) or \
                       (primitive_type == 'pCylinder' and 'Cylinder' in node_type) or \
                       (primitive_type == 'pCone' and 'Cone' in node_type) or \
                       (primitive_type == 'pPlane' and 'Plane' in node_type) or \
                       (primitive_type == 'pTorus' and 'Torus' in node_type):
                        primitive_node = node
                        break
                
                if primitive_node:
                    # Check if attributes were modified from defaults (this is ENCOURAGED)
                    has_modified_attributes = False
                    
                    try:
                        if primitive_type == 'pSphere':
                            subdU = cmds.getAttr(f"{primitive_node}.subdivisionsU")
                            subdV = cmds.getAttr(f"{primitive_node}.subdivisionsV")
                            # Also check radius, start/end sweep angles
                            radius = cmds.getAttr(f"{primitive_node}.radius")
                            start_sweep = cmds.getAttr(f"{primitive_node}.startSweep")
                            end_sweep = cmds.getAttr(f"{primitive_node}.endSweep")
                            
                            if (subdU != 20 or subdV != 10 or radius != 1.0 or 
                                start_sweep != 0.0 or end_sweep != 360.0):
                                has_modified_attributes = True
                                
                        elif primitive_type == 'pCylinder':
                            subdAxis = cmds.getAttr(f"{primitive_node}.subdivisionsAxis")
                            subdHeight = cmds.getAttr(f"{primitive_node}.subdivisionsHeight")
                            subdCaps = cmds.getAttr(f"{primitive_node}.subdivisionsCAPS")
                            radius = cmds.getAttr(f"{primitive_node}.radius")
                            height = cmds.getAttr(f"{primitive_node}.height")
                            
                            if (subdAxis != 20 or subdHeight != 1 or subdCaps != 0 or 
                                radius != 1.0 or height != 2.0):
                                has_modified_attributes = True
                                
                        elif primitive_type == 'pCone':
                            subdAxis = cmds.getAttr(f"{primitive_node}.subdivisionsAxis")
                            subdHeight = cmds.getAttr(f"{primitive_node}.subdivisionsHeight")
                            subdCaps = cmds.getAttr(f"{primitive_node}.subdivisionsCaps")
                            radius = cmds.getAttr(f"{primitive_node}.radius")
                            height = cmds.getAttr(f"{primitive_node}.height")
                            
                            if (subdAxis != 20 or subdHeight != 1 or subdCaps != 0 or 
                                radius != 1.0 or height != 2.0):
                                has_modified_attributes = True
                                
                        elif primitive_type == 'pCube':
                            subdW = cmds.getAttr(f"{primitive_node}.subdivisionsWidth")
                            subdH = cmds.getAttr(f"{primitive_node}.subdivisionsHeight")
                            subdD = cmds.getAttr(f"{primitive_node}.subdivisionsDepth")
                            width = cmds.getAttr(f"{primitive_node}.width")
                            height = cmds.getAttr(f"{primitive_node}.height")
                            depth = cmds.getAttr(f"{primitive_node}.depth")
                            
                            if (subdW != 1 or subdH != 1 or subdD != 1 or 
                                width != 2.0 or height != 2.0 or depth != 2.0):
                                has_modified_attributes = True
                                
                        elif primitive_type == 'pPlane':
                            subdU = cmds.getAttr(f"{primitive_node}.subdivisionsU")
                            subdV = cmds.getAttr(f"{primitive_node}.subdivisionsV")
                            width = cmds.getAttr(f"{primitive_node}.width")
                            height = cmds.getAttr(f"{primitive_node}.height")
                            
                            if (subdU != 1 or subdV != 1 or width != 1.0 or height != 1.0):
                                has_modified_attributes = True
                                
                        elif primitive_type == 'pTorus':
                            subdU = cmds.getAttr(f"{primitive_node}.subdivisionsU")
                            subdV = cmds.getAttr(f"{primitive_node}.subdivisionsV")
                            radius = cmds.getAttr(f"{primitive_node}.radius")
                            section_radius = cmds.getAttr(f"{primitive_node}.sectionRadius")
                            
                            if (subdU != 20 or subdV != 20 or radius != 1.0 or section_radius != 0.5):
                                has_modified_attributes = True
                                
                    except Exception as attr_error:
                        print(f"DEBUG: Could not check all attributes for {transform}: {attr_error}")
                        # If we can't check some attributes, assume default behavior
                        pass
                    
                    if has_modified_attributes:
                        modified_attributes_count += 1
                        print(f"DEBUG: {transform} has modified primitive attributes (ENCOURAGED)")
                else:
                    # No construction history - can't verify attribute modifications
                    print(f"DEBUG: {transform} has no construction history - cannot verify attribute modifications")
                
                # Check for topology modifications - but allow legitimate attribute-based changes
                topology_violation = None
                
                # If we have the primitive node, calculate expected topology based on current attributes
                if primitive_node:
                    try:
                        expected_vertex_count = None
                        expected_face_count = None
                        
                        if primitive_type == 'pCube':
                            # For cubes: subdivisions add vertices/faces
                            subdW = cmds.getAttr(f"{primitive_node}.subdivisionsWidth")
                            subdH = cmds.getAttr(f"{primitive_node}.subdivisionsHeight") 
                            subdD = cmds.getAttr(f"{primitive_node}.subdivisionsDepth")
                            
                            # Calculate expected topology based on subdivisions
                            expected_vertex_count = (subdW + 1) * (subdH + 1) * (subdD + 1) - (subdW - 1) * (subdH - 1) * (subdD - 1)
                            expected_face_count = 2 * (subdW * subdH + subdH * subdD + subdD * subdW)
                            
                        elif primitive_type == 'pSphere':
                            # For spheres: topology depends on subdivisions
                            subdU = cmds.getAttr(f"{primitive_node}.subdivisionsU")
                            subdV = cmds.getAttr(f"{primitive_node}.subdivisionsV")
                            
                            # Sphere topology calculation (approximate)
                            expected_vertex_count = subdU * (subdV - 1) + 2
                            expected_face_count = subdU * (2 * subdV - 2)
                            
                        elif primitive_type == 'pCylinder':
                            # For cylinders: topology depends on subdivisions
                            subdAxis = cmds.getAttr(f"{primitive_node}.subdivisionsAxis")
                            subdHeight = cmds.getAttr(f"{primitive_node}.subdivisionsHeight")
                            
                            # Cylinder topology calculation
                            expected_vertex_count = subdAxis * (subdHeight + 1) + 2
                            expected_face_count = subdAxis * (subdHeight + 2)
                            
                        elif primitive_type == 'pCone':
                            # For cones: topology depends on subdivisions
                            subdAxis = cmds.getAttr(f"{primitive_node}.subdivisionsAxis")
                            subdHeight = cmds.getAttr(f"{primitive_node}.subdivisionsHeight")
                            
                            # Cone topology calculation
                            expected_vertex_count = subdAxis * subdHeight + subdAxis + 1
                            expected_face_count = subdAxis * (subdHeight + 1)
                            
                        elif primitive_type == 'pPlane':
                            # For planes: subdivisions add vertices/faces
                            subdU = cmds.getAttr(f"{primitive_node}.subdivisionsU")
                            subdV = cmds.getAttr(f"{primitive_node}.subdivisionsV")
                            
                            # Plane topology calculation
                            expected_vertex_count = (subdU + 1) * (subdV + 1)
                            expected_face_count = subdU * subdV
                            
                        elif primitive_type == 'pTorus':
                            # For torus: topology depends on subdivisions
                            subdU = cmds.getAttr(f"{primitive_node}.subdivisionsU")
                            subdV = cmds.getAttr(f"{primitive_node}.subdivisionsV")
                            
                            # Torus topology calculation
                            expected_vertex_count = subdU * subdV
                            expected_face_count = subdU * subdV
                        
                        # Check if actual topology matches expected (with tolerance for Maya calculation differences)
                        if expected_vertex_count is not None and expected_face_count is not None:
                            vertex_tolerance = max(2, int(expected_vertex_count * 0.05))  # 5% tolerance
                            face_tolerance = max(2, int(expected_face_count * 0.05))     # 5% tolerance
                            
                            if (abs(vertex_count - expected_vertex_count) > vertex_tolerance or 
                                abs(face_count - expected_face_count) > face_tolerance):
                                topology_violation = f"topology doesn't match expected values for current subdivisions (V:{vertex_count} vs {expected_vertex_count}, F:{face_count} vs {expected_face_count})"
                                
                            print(f"DEBUG: {transform} topology check - Expected V:{expected_vertex_count}, F:{expected_face_count} | Actual V:{vertex_count}, F:{face_count}")
                        
                    except Exception as e:
                        print(f"DEBUG: Could not calculate expected topology for {transform}: {e}")
                        # If we can't calculate expected topology, fall back to basic checks
                        pass
                
                # If no construction history, check against default topologies only
                elif primitive_type in primitive_topologies:
                    expected = primitive_topologies[primitive_type]
                    
                    # Only flag as violation if topology is way off from defaults (suggesting manual modification)
                    vertex_ratio = vertex_count / expected['vertices']
                    face_ratio = face_count / expected['faces']
                    
                    # Allow reasonable variations from attribute changes, but flag extreme differences
                    if vertex_ratio > 10 or vertex_ratio < 0.1 or face_ratio > 10 or face_ratio < 0.1:
                        topology_violation = f"topology significantly different from expected primitive (may indicate manual modifications or missing construction history)"
                
                # Check for obvious topology modifications (like extrusions, edge loops)
                # Look for non-manifold edges, ngons, or unusual topology patterns
                try:
                    # Check for ngons (faces with more than 4 sides)
                    ngons = []
                    for i in range(face_count):
                        face_verts = cmds.polyInfo(f"{mesh}.f[{i}]", faceToVertex=True)[0]
                        vert_count = len([x for x in face_verts.split() if x.isdigit()])
                        if vert_count > 4:
                            ngons.append(i)
                    
                    if ngons:
                        violations.append(f"'{transform}' contains {len(ngons)} ngon(s) - faces have been modified")
                    
                    # Check for triangles in objects that shouldn't have them
                    triangles = []
                    for i in range(face_count):
                        face_verts = cmds.polyInfo(f"{mesh}.f[{i}]", faceToVertex=True)[0]
                        vert_count = len([x for x in face_verts.split() if x.isdigit()])
                        if vert_count == 3:
                            triangles.append(i)
                    
                    # Cubes and planes shouldn't have triangles
                    if primitive_type in ['pCube', 'pPlane'] and triangles:
                        violations.append(f"'{transform}' contains triangulated faces - topology has been modified")
                        
                except Exception:
                    pass  # Skip topology checks if they fail
                
                # Add any topology violations to the main violations list
                if topology_violation:
                    violations.append(f"'{transform}' {topology_violation}")
                
                # Check for smoothing using topology patterns (even without construction history)
                is_smoothed, confidence = detect_smoothing_by_topology(mesh, primitive_type)
                if is_smoothed and confidence > 0.7:
                    violations.append(f"'{transform}' appears to have been smoothed (confidence: {confidence:.1f}) - smoothing is not allowed")
                    
            except Exception as e:
                print(f"DEBUG: Error checking {transform}: {e}")
                continue
        
        # Check for missing construction history as a warning (not a hard violation)
        history_warnings = []
        primitives_without_history = 0
        
        for transform in mesh_transforms:
            try:
                # Skip lights
                children = cmds.listRelatives(transform, children=True, shapes=True) or []
                is_light = any(cmds.nodeType(child) in ['directionalLight', 'pointLight', 'spotLight', 'areaLight', 'volumeLight', 'ambientLight', 'aiAreaLight', 'aiSkyDomeLight', 'aiPhotometricLight', 'aiMeshLight', 'aiLightPortal', 'rsPhysicalLight', 'rsIESLight', 'rsPortalLight', 'rsDomeLight'] for child in children)
                
                if is_light:
                    continue
                
                mesh_shapes = cmds.listRelatives(transform, children=True, type='mesh') or []
                if not mesh_shapes:
                    continue
                
                mesh = mesh_shapes[0]
                
                # Check if object appears to be a primitive but has no construction history
                history = cmds.listHistory(mesh, pruneDagObjects=True) or []
                primitive_creation_nodes = [node for node in history if any(prim_type in cmds.nodeType(node) for prim_type in ['Cube', 'Sphere', 'Cylinder', 'Cone', 'Plane', 'Torus'])]
                
                if not primitive_creation_nodes and any(transform.startswith(prim) for prim in primitive_topologies.keys()):
                    primitives_without_history += 1
                    
            except Exception:
                continue
        
        # Add warning if significant number of primitives have no history
        if primitives_without_history > 0:
            history_warnings.append(f"*** WARNING: {primitives_without_history} PRIMITIVE(S) MISSING CONSTRUCTION HISTORY - COMPLIANCE VERIFICATION LIMITED ***")
        
        # Calculate scores with enhanced logic
        major_violations = len(violations)
        attribute_modification_percentage = (modified_attributes_count / total_primitives * 100) if total_primitives > 0 else 0
        
        # Enhanced scoring logic that encourages attribute modifications while detecting violations
        if major_violations == 0:
            if attribute_modification_percentage >= 10:
                score = 100
                base_comment = f"Excellent primitive design! All {total_primitives} objects are unmodified Maya primitives. {modified_attributes_count} objects ({attribute_modification_percentage:.1f}%) have modified attributes - great creativity!"
            else:
                score = 95
                base_comment = f"Good primitive usage! All {total_primitives} objects are unmodified Maya primitives. Consider modifying attributes on more primitives for variety ({modified_attributes_count}/{total_primitives} currently have modified attributes)."
                
            # Add history warning if applicable
            if history_warnings:
                score = max(90, score - 5)  # Small penalty for missing history
                base_comment += f" {'; '.join(history_warnings)}"
                
            comments = base_comment
            
        elif major_violations <= 2:
            # Minor violations - check if they're mostly smoothing or topology issues
            smoothing_violations = [v for v in violations if 'smooth' in v.lower()]
            topology_violations = [v for v in violations if 'topology' in v.lower()]
            
            if smoothing_violations and not topology_violations:
                score = 60  # 10% penalty for smoothing (as requested)
                comments = f"Good primitive usage but smoothing detected (10% penalty): {'; '.join(smoothing_violations)}. Remember: only use unmodified Maya primitives (scaling, moving, rotating, and changing initial attributes is allowed)."
            else:
                score = 70
                comments = f"Some primitive violations found: {'; '.join(violations[:2])}. Remember: only use unmodified Maya primitives (scaling, moving, rotating, and changing initial attributes is allowed)."
                
        elif major_violations <= 5:
            score = 50
            comments = f"Multiple primitive violations detected: {'; '.join(violations[:3])}{'...' if len(violations) > 3 else ''}. Review assignment requirements - no edge/face/vertex modifications allowed."
        else:
            score = 25
            comments = f"Extensive primitive violations found ({major_violations} issues). This assignment requires using only unmodified Maya polygon primitives."
        
        # Add history warnings to comments if present (non-penalty)
        if history_warnings and major_violations > 0:
            comments += f" {'; '.join(history_warnings)}"
        
        print(f"DEBUG: Final primitive check - {total_primitives} primitives, {modified_attributes_count} with modified attributes ({attribute_modification_percentage:.1f}%), {major_violations} violations")
        
        return (score, comments)
        
    except Exception as e:
        return (50, f"Error validating primitive design principles: {str(e)}")


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
