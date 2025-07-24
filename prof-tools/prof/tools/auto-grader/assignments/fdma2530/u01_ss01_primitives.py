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

# Import the base rubric template
from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric


def create_u01_ss01_rubric():
    """
    Create the FDMA 2530 U01_SS01 Primitives assignment rubric.
    
    Assignment Overview:
    - Students create basic 3D models using primitive shapes
    - Focus on proper file naming, organization, and technical execution
    - Introduction to design principles and professionalism standards
    
    Total Points: 10 (5 criteria × 2 points each)
    """
    # Get current file name for assignment context
    assignment_name = "FDMA 2530 - U01_SS01: Primitives"
    if MAYA_AVAILABLE:
        try:
            scene_name = cmds.file(query=True, sceneName=True, shortName=True)
            if scene_name:
                # Use the Maya file name but keep the assignment context
                assignment_name = f"FDMA 2530 - U01_SS01: {scene_name.rsplit('.', 1)[0]}"
        except:
            pass
    
    # Create rubric instance - 5 criteria × 2 points = 10 total points
    rubric = LessonRubric(assignment_name=assignment_name, total_points=10)
    
    # Add the 5 criteria (2 points each)
    rubric.add_criterion(
        "File Names", 
        2.0, 
        "Proper naming conventions for Maya scene file and project structure"
    )
    
    rubric.add_criterion(
        "Outliner Organization", 
        2.0, 
        "Clean hierarchy, proper grouping, and logical object naming in Maya's Outliner"
    )
    
    rubric.add_criterion(
        "Primitive Design Principles", 
        2.0, 
        "Effective use of primitive shapes with attention to proportion, balance, and composition"
    )
    
    rubric.add_criterion(
        "Technical Execution", 
        2.0, 
        "Proper modeling techniques, clean geometry, and appropriate use of Maya tools"
    )
    
    rubric.add_criterion(
        "Perceived Effort/ Professionalism", 
        2.0, 
        "Overall quality, attention to detail, and demonstration of effort and professional standards"
    )
    
    # Show the rubric UI
    rubric.show_rubric_ui()
    
    return rubric


if __name__ == "__main__":
    # When run directly, create and show the rubric
    if MAYA_AVAILABLE:
        create_u01_ss01_rubric()
    else:
        print("Maya not available - cannot display UI")
