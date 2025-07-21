"""
Example: Custom Assignment Rubric

This example shows how to create a custom rubric for a specific assignment
using the lessonRubric_template. This can be copied and modified for each
individual lesson/assignment.

Usage in Maya:
1. Copy this file and rename it for your specific assignment
2. Modify the criteria and point values as needed
3. Run the script to display the grading rubric

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function

try:
    import maya.cmds as cmds
    from prof.tools.assignments.lessonRubric_template import LessonRubric
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False
    print("Maya not available - this example requires Maya")

def create_modeling_basics_rubric():
    """
    Example rubric for a basic 3D modeling assignment.
    Customize this function for your specific assignment needs.
    """
    if not MAYA_AVAILABLE:
        return None
    
    # Get current file name for assignment name
    assignment_name = "Modeling Basics Assignment"
    try:
        scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        if scene_name:
            assignment_name = scene_name.rsplit('.', 1)[0]  # Remove extension
    except:
        pass
    
    # Create rubric with total points (always 10 for consistency)
    rubric = LessonRubric(assignment_name=assignment_name, total_points=10)
    
    # Add criteria specific to this assignment
    # Note: Point values should add up to the total_points (10)
    
    rubric.add_criterion(
        "Basic Shapes Modeling", 
        point_value=2.5,
        description="Created required primitive shapes with proper proportions"
    )
    
    rubric.add_criterion(
        "Mesh Cleanup", 
        point_value=2.0,
        description="Clean geometry, proper edge flow, no overlapping faces"
    )
    
    rubric.add_criterion(
        "Object Naming", 
        point_value=1.5,
        description="All objects properly named following naming conventions"
    )
    
    rubric.add_criterion(
        "Scene Organization", 
        point_value=1.5,
        description="Objects grouped logically, outliner is organized"
    )
    
    rubric.add_criterion(
        "Technical Requirements", 
        point_value=2.0,
        description="Met all technical specifications (poly count, size, etc.)"
    )
    
    rubric.add_criterion(
        "Creative Execution", 
        point_value=0.5,
        description="Shows creativity within assignment parameters"
    )
    
    # Display the rubric
    rubric.show_rubric_ui()
    return rubric

def create_character_modeling_rubric():
    """
    Example rubric for a character modeling assignment.
    More advanced criteria with different point distributions.
    """
    if not MAYA_AVAILABLE:
        return None
    
    assignment_name = "Character Modeling Assignment"
    try:
        scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        if scene_name:
            assignment_name = scene_name.rsplit('.', 1)[0]
    except:
        pass
    
    rubric = LessonRubric(assignment_name=assignment_name, total_points=10)
    
    # Character-specific criteria
    rubric.add_criterion(
        "Character Proportions", 
        point_value=3.0,
        description="Accurate human/character proportions and anatomy"
    )
    
    rubric.add_criterion(
        "Topology Quality", 
        point_value=2.5,
        description="Proper edge loops for animation, clean quad topology"
    )
    
    rubric.add_criterion(
        "Detail Level", 
        point_value=2.0,
        description="Appropriate level of detail for assignment requirements"
    )
    
    rubric.add_criterion(
        "Reference Usage", 
        point_value=1.0,
        description="Effective use of reference images and accuracy to concept"
    )
    
    rubric.add_criterion(
        "Technical Execution", 
        point_value=1.0,
        description="Proper modeling techniques, clean construction history"
    )
    
    rubric.add_criterion(
        "File Management", 
        point_value=0.5,
        description="Proper file structure, naming, and organization"
    )
    
    rubric.show_rubric_ui()
    return rubric

def create_environment_modeling_rubric():
    """
    Example rubric for an environment/scene modeling assignment.
    """
    if not MAYA_AVAILABLE:
        return None
    
    assignment_name = "Environment Modeling Assignment"
    try:
        scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        if scene_name:
            assignment_name = scene_name.rsplit('.', 1)[0]
    except:
        pass
    
    rubric = LessonRubric(assignment_name=assignment_name, total_points=10)
    
    # Environment-specific criteria
    rubric.add_criterion(
        "Scene Composition", 
        point_value=2.5,
        description="Strong overall composition and visual hierarchy"
    )
    
    rubric.add_criterion(
        "Asset Variety", 
        point_value=2.0,
        description="Good variety of objects and environmental elements"
    )
    
    rubric.add_criterion(
        "Scale & Proportions", 
        point_value=1.5,
        description="Realistic scale relationships between objects"
    )
    
    rubric.add_criterion(
        "Modeling Quality", 
        point_value=2.0,
        description="Clean geometry and appropriate polygon density"
    )
    
    rubric.add_criterion(
        "Level of Detail", 
        point_value=1.5,
        description="Appropriate detail level for viewing distance"
    )
    
    rubric.add_criterion(
        "Scene Organization", 
        point_value=0.5,
        description="Logical grouping and outliner organization"
    )
    
    rubric.show_rubric_ui()
    return rubric

# Example usage functions
def grade_current_assignment():
    """
    Quick function to open a basic rubric for the current file.
    Customize this to call the appropriate rubric function.
    """
    if not MAYA_AVAILABLE:
        print("Maya required for grading functionality")
        return
    
    # You can modify this to automatically detect assignment type
    # or present a choice dialog
    result = cmds.confirmDialog(
        title="Select Assignment Type",
        message="What type of assignment would you like to grade?",
        button=["Modeling Basics", "Character", "Environment", "Custom"],
        defaultButton="Custom",
        cancelButton="Custom",
        dismissString="Custom"
    )
    
    if result == "Modeling Basics":
        return create_modeling_basics_rubric()
    elif result == "Character":
        return create_character_modeling_rubric()
    elif result == "Environment":
        return create_environment_modeling_rubric()
    else:
        # Default to basic rubric
        from prof.tools.assignments.lessonRubric_template import create_sample_rubric
        return create_sample_rubric()

if __name__ == "__main__":
    # When run directly, show assignment type selection
    if MAYA_AVAILABLE:
        grade_current_assignment()
    else:
        print("This script requires Maya to run.")
