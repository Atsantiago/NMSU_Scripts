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
    from prof.tools.assignments.lessonRubric_template import LessonRubric  # Our custom rubric class
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
    Quick function to open a rubric for the current file with assignment type selection.
    
    FUNCTIONALITY:
    - Displays a dialog for instructors to choose assignment type
    - Automatically loads the appropriate rubric template
    - Provides fallback to sample rubric for custom assignments
    
    UI INTERACTION PATTERN:
    1. Maya's confirmDialog creates a button-based selection interface
    2. Button selection determines which rubric function to call
    3. Each rubric function handles its own UI creation and display
    
    EXTENSIBILITY:
    You can add new assignment types by:
    1. Adding a new button to the dialog
    2. Creating a corresponding elif condition
    3. Writing a new rubric creation function
    """
    if not MAYA_AVAILABLE:
        print("Maya required for grading functionality")
        return
    
    # Maya's confirmDialog creates a modal dialog with custom buttons
    # This provides an intuitive interface for assignment type selection
    result = cmds.confirmDialog(
        title="Select Assignment Type",
        message="What type of assignment would you like to grade?",
        button=["Modeling Basics", "Character", "Environment", "Custom"],  # Available options
        defaultButton="Custom",    # Default selection if user just presses Enter
        cancelButton="Custom",     # What to do if user cancels/closes dialog
        dismissString="Custom"     # What to return if dialog is dismissed
    )
    
    # Route to appropriate rubric based on user selection
    # Each condition calls a different rubric creation function
    if result == "Modeling Basics":
        return create_modeling_basics_rubric()
    elif result == "Character":
        return create_character_modeling_rubric()
    elif result == "Environment":
        return create_environment_modeling_rubric()
    else:
        # Default case: import and use the generic sample rubric
        # This allows for custom assignments or testing
        from prof.tools.assignments.lessonRubric_template import create_sample_rubric
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
   ✅ Good: "All objects named using camelCase convention"
   ❌ Poor: "Good naming"

2. INCLUDE TECHNICAL REQUIREMENTS:
   ✅ Good: "Polygon count between 1000-5000 faces"
   ❌ Poor: "Appropriate detail level"

3. SET CLEAR EXPECTATIONS:
   ✅ Good: "Clean quad topology with proper edge loops around joints"
   ❌ Poor: "Good topology"

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
