"""
Example: Custom Assignment Rubric

This example shows how to create a custom rubric for a specific assignment
using the lessonRubric_template. This can be copied and modified for each
individual lesson/assignment.

LEARNING OBJECTIVES:
- Understand how to import and use the LessonRubric class
- Learn to create custom grading criteria with appropriate point values
- See how to structure rubrics for different assignment types
- Understand how point values should distribute across criteria

USAGE PATTERNS:
1. Copy this file and rename it for your specific assignment
2. Modify the criteria and point values as needed
3. Customize the comments and descriptions for your requirements
4. Run the script to display the grading rubric

TECHNICAL CONCEPTS DEMONSTRATED:
- Maya integration checking (MAYA_AVAILABLE flag)
- Error handling for missing dependencies
- Function-based rubric creation for reusability
- UI integration with Maya's command system
- Point distribution strategies for fair grading

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function

# Import handling with graceful fallback for non-Maya environments
try:
    import maya.cmds as cmds  # Maya's command interface for UI and scene operations
    from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric  # Our custom rubric class
    MAYA_AVAILABLE = True  # Flag to track if Maya is available for UI operations
except ImportError:
    # Graceful handling when Maya is not available (e.g., during development/testing)
    MAYA_AVAILABLE = False
    print("Maya not available - this example requires Maya")

def create_modeling_basics_rubric():
    """
    Example rubric for a basic 3D modeling assignment.
    
    LEARNING FOCUS: Fundamental 3D modeling skills and best practices
    
    POINT DISTRIBUTION STRATEGY:
    - Technical skills (4.5 pts): Core modeling and cleanup
    - Organization (3.0 pts): Naming, grouping, requirements  
    - Creativity (2.5 pts): Going beyond minimum requirements
    Total: 10 points (standard for all assignments)
    
    CUSTOMIZATION NOTES:
    - Adjust point values based on assignment complexity
    - Modify descriptions to match specific requirements
    - Add/remove criteria as needed for your assignment
    
    Returns:
        LessonRubric: Configured rubric ready for grading, or None if Maya unavailable
    """
    # Early return if Maya is not available (prevents errors)
    if not MAYA_AVAILABLE:
        return None
    
    # Attempt to get assignment name from current Maya scene file
    # This creates a connection between the rubric and the student's work
    assignment_name = "Modeling Basics Assignment"  # Default fallback name
    try:
        # Query Maya for the current scene file name
        scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        if scene_name:
            # Remove file extension to get clean assignment name
            assignment_name = scene_name.rsplit('.', 1)[0]  # rsplit from right, limit to 1 split
    except:
        # If anything goes wrong, use the default name (fail safely)
        pass
    
    # Create rubric instance with standardized 10-point total
    # All assignments use 10 points for consistency across courses
    rubric = LessonRubric(assignment_name=assignment_name, total_points=10)
    
    # Add criteria specific to this assignment
    # IMPORTANT: Point values should add up to the total_points (10)
    # Each criterion includes: name, point_value, description
    
    # TECHNICAL MODELING CRITERIA (4.5 points total)
    rubric.add_criterion(
        "Basic Shapes Modeling",  # Criterion name (appears in UI)
        point_value=2.5,          # Points possible (2.5 out of 10 total)
        description="Created required primitive shapes with proper proportions"  # Detailed description
    )
    
    rubric.add_criterion(
        "Mesh Cleanup", 
        point_value=2.0,
        description="Clean geometry, proper edge flow, no overlapping faces"
    )
    
    # ORGANIZATION AND WORKFLOW CRITERIA (3.0 points total)
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
    
    # REQUIREMENTS AND STANDARDS CRITERIA (2.0 points total)
    rubric.add_criterion(
        "Technical Requirements", 
        point_value=2.0,
        description="Met all technical specifications (poly count, size, etc.)"
    )
    
    # CREATIVITY AND POLISH CRITERIA (0.5 points total)
    rubric.add_criterion(
        "Creative Execution", 
        point_value=0.5,
        description="Shows creativity within assignment parameters"
    )
    
    # Display the interactive grading interface
    rubric.show_rubric_ui()
    return rubric  # Return rubric object for further manipulation if needed

def create_character_modeling_rubric():
    """
    Example rubric for a character modeling assignment.
    
    LEARNING FOCUS: Advanced modeling with emphasis on topology and anatomy
    
    POINT DISTRIBUTION STRATEGY:
    - Anatomical accuracy (5.5 pts): Proportions and topology quality
    - Technical execution (2.0 pts): Modeling techniques and detail
    - Reference and organization (1.5 pts): Research and file management
    Total: 10 points
    
    ADVANCED CONCEPTS:
    - Higher point values for complex skills (topology, anatomy)
    - Emphasis on animation-ready geometry
    - Professional workflow considerations
    """
    if not MAYA_AVAILABLE:
        return None
    
    # Same pattern for getting assignment name from Maya scene
    assignment_name = "Character Modeling Assignment"
    try:
        scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        if scene_name:
            assignment_name = scene_name.rsplit('.', 1)[0]
    except:
        pass
    
    rubric = LessonRubric(assignment_name=assignment_name, total_points=10)
    
    # CHARACTER-SPECIFIC CRITERIA with higher complexity weighting
    
    # ANATOMICAL ACCURACY (highest weight for advanced skill)
    rubric.add_criterion(
        "Character Proportions", 
        point_value=3.0,  # Largest point value - most important skill
        description="Accurate human/character proportions and anatomy"
    )
    
    # TECHNICAL TOPOLOGY (critical for animation pipeline)
    rubric.add_criterion(
        "Topology Quality", 
        point_value=2.5,  # High value for technical excellence
        description="Proper edge loops for animation, clean quad topology"
    )
    
    # DETAIL AND REFINEMENT
    rubric.add_criterion(
        "Detail Level", 
        point_value=2.0,
        description="Appropriate level of detail for assignment requirements"
    )
    
    # RESEARCH AND REFERENCE SKILLS
    rubric.add_criterion(
        "Reference Usage", 
        point_value=1.0,
        description="Effective use of reference images and accuracy to concept"
    )
    
    # TECHNICAL WORKFLOW
    rubric.add_criterion(
        "Technical Execution", 
        point_value=1.0,
        description="Proper modeling techniques, clean construction history"
    )
    
    # PROFESSIONAL PRACTICES
    rubric.add_criterion(
        "File Management", 
        point_value=0.5,  # Lower weight but still important
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
    Main entry point for assignment grading selection.
    
    FUNCTIONALITY:
    - Creates a comprehensive dialog with sections for each course
    - Provides organized access to all available rubrics
    - Allows users to access rubrics through menu or dialog
    
    TECHNICAL APPROACH:
    - Uses Maya's window system for better layout control
    - Sections separated by visual dividers
    - Consistent with Maya UI patterns and prof-tools design
    """
    if not MAYA_AVAILABLE:
        print("Maya not available - cannot display assignment selection")
        return None
    
    # Create assignment selection window
    window_name = "assignmentGradingWindow"
    
    # Clean up any existing window
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)
    
    # Create main window
    window = cmds.window(
        window_name,
        title="Assignment Grading Rubric",
        widthHeight=(400, 300),
        resizeToFitChildren=True,
        sizeable=False
    )
    
    # Main layout
    main_layout = cmds.columnLayout(
        adjustableColumn=True,
        columnAttach=('both', 20),
        parent=window
    )
    
    # Header
    cmds.text(
        label="Select an Assignment to Grade",
        font="boldLabelFont",
        align="center",
        height=30,
        parent=main_layout
    )
    
    cmds.separator(height=15, parent=main_layout)
    
    # FDMA 1510 Section
    cmds.text(
        label="FDMA 1510",
        font="boldLabelFont",
        align="left",
        parent=main_layout
    )
    
    fdma1510_layout = cmds.rowColumnLayout(
        numberOfColumns=1,
        columnAlign=[(1, 'left')],
        columnWidth=[(1, 350)],
        parent=main_layout
    )
    
    cmds.text(label="(No assignments available yet)", enable=False, parent=fdma1510_layout)
    
    cmds.setParent(main_layout)
    cmds.separator(height=15, parent=main_layout)
    
    # FDMA 2530 Section  
    cmds.text(
        label="FDMA 2530",
        font="boldLabelFont",
        align="left",
        parent=main_layout
    )
    
    fdma2530_layout = cmds.rowColumnLayout(
        numberOfColumns=1,
        columnAlign=[(1, 'left')],
        columnWidth=[(1, 350)],
        parent=main_layout
    )
    
    cmds.button(
        label="U01_L01_Primitives",
        command=lambda *args: _select_and_close_assignment("u01_ss01", window_name),
        height=30,
        parent=fdma2530_layout
    )
    
    cmds.setParent(main_layout)
    cmds.separator(height=15, parent=main_layout)
    
    # Custom Section
    cmds.text(
        label="General",
        font="boldLabelFont", 
        align="left",
        parent=main_layout
    )
    
    general_layout = cmds.rowColumnLayout(
        numberOfColumns=1,
        columnAlign=[(1, 'left')],
        columnWidth=[(1, 350)],
        parent=main_layout
    )
    
    cmds.button(
        label="Custom",
        command=lambda *args: _select_and_close_assignment("custom", window_name),
        height=30,
        parent=general_layout
    )
    
    cmds.setParent(main_layout)
    cmds.separator(height=20, parent=main_layout)
    
    # Cancel button
    cmds.button(
        label="Cancel",
        command=lambda *args: cmds.deleteUI(window_name, window=True),
        height=35,
        width=100,
        parent=main_layout
    )
    
    cmds.separator(height=10, parent=main_layout)
    
    # Show window
    cmds.showWindow(window)


def _select_and_close_assignment(assignment_type, window_name):
    """Helper function to handle assignment selection and window cleanup."""
    # Close the selection window
    cmds.deleteUI(window_name, window=True)
    
    # Route to appropriate rubric
    if assignment_type == "u01_ss01":
        from prof.tools.auto_grader.assignments.fdma2530.u01_ss01_primitives import create_u01_ss01_rubric
        return create_u01_ss01_rubric()
    else:
        # Default case: custom/sample rubric
        from prof.tools.auto_grader.assignments.lessonRubric_template import create_sample_rubric
        return create_sample_rubric()

if __name__ == "__main__":
    # When run directly, show assignment type selection
    # 
    # EXECUTION PATTERN:
    # This block only runs when the script is executed directly (not imported)
    # - Allows testing of rubric functionality
    # - Provides immediate access to grading interface
    # - Handles the Maya dependency gracefully
    #
    # USAGE SCENARIOS:
    # 1. Instructor runs script directly from Maya's script editor
    # 2. Script is executed via Maya's menu system  
    # 3. File is run from command line (will show error message)
    if MAYA_AVAILABLE:
        grade_current_assignment()  # Launch the assignment selection dialog
    else:
        print("This script requires Maya to run.")

"""
DEVELOPER GUIDE: Creating Custom Rubrics

This section provides guidance for instructors and developers who want to create
their own custom rubric templates.

BASIC RUBRIC CREATION PATTERN:
```python
def create_my_custom_rubric():
    # 1. Check Maya availability
    if not MAYA_AVAILABLE:
        return None
    
    # 2. Get assignment name (optional)
    assignment_name = "My Custom Assignment"
    
    # 3. Create rubric instance
    rubric = LessonRubric(assignment_name=assignment_name, total_points=10)
    
    # 4. Add criteria (must total 10 points)
    rubric.add_criterion("Criterion Name", point_value=X.X, description="...")
    
    # 5. Display the UI
    rubric.show_rubric_ui()
    return rubric
```

POINT DISTRIBUTION STRATEGIES:

1. EQUAL WEIGHTING: All criteria worth the same (e.g., 5 criteria × 2.0 points each)
   - Use when all skills are equally important
   - Good for foundational assignments

2. SKILL-BASED WEIGHTING: Higher points for more complex skills
   - Technical skills: 40-60% of total points
   - Creative/artistic: 20-30% of total points  
   - Organization/workflow: 10-20% of total points

3. LEARNING OBJECTIVE WEIGHTING: Points reflect lesson goals
   - Primary objective: 50-70% of points
   - Secondary objectives: 20-30% of points
   - Professional practices: 10-20% of points

CRITERIA WRITING BEST PRACTICES:

1. USE SPECIFIC, MEASURABLE LANGUAGE:
   Good: "All objects named using camelCase convention"
   Poor: "Good naming"

2. INCLUDE TECHNICAL REQUIREMENTS:
   Good: "Polygon count between 1000-5000 faces"
   Poor: "Appropriate detail level"

3. SET CLEAR EXPECTATIONS:
   Good: "Clean quad topology with proper edge loops around joints"
   Poor: "Good topology"

EXTENDING THE RUBRIC SYSTEM:

1. CUSTOM COMMENT GENERATION:
   Override the _generate_comments() method to create assignment-specific feedback

2. ADDITIONAL SCORING LEVELS:
   Modify SCORE_LEVELS to add new performance categories

3. AUTOMATED SCORING:
   Integrate with Maya scene analysis to auto-score technical criteria

4. EXPORT FORMATS:
   Extend _export_results() to support CSV, JSON, or LMS integration

TROUBLESHOOTING:

- Import errors: Ensure prof-tools is properly installed in Maya's Python path
- UI issues: Check that Maya version supports the cmds functions used
- Point totals: Always verify criteria points sum to total_points (usually 10)
- Performance: For large classes, consider batch processing multiple files

For more examples and advanced features, see the prof-tools documentation.
"""
