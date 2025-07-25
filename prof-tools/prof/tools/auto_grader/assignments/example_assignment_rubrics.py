"""
Assignment Grading Dialog System

Provides a dialog for selecting which assignment rubric to open.
This replaces the original example rubrics file and provides the
grade_current_assignment() function needed by the UI builder.

Author: Alexander T. Santiago
"""

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False


def grade_current_assignment():
    """
    Show a categorized assignment selection window with course sections.
    
    This function provides an organized interface for instructors to choose
    assignments by course, with expandable sections for future assignments.
    """
    if not MAYA_AVAILABLE:
        print("Maya not available - cannot display dialog")
        return
    
    # Create the main assignment selection window
    assignment_window = "assignmentSelectionWindow"
    
    if cmds.window(assignment_window, exists=True):
        cmds.deleteUI(assignment_window, window=True)
    
    window = cmds.window(
        assignment_window,
        title="Assignment Grading Rubrics",
        widthHeight=(450, 400),
        resizeToFitChildren=True,
        sizeable=True
    )
    
    # Main layout
    main_layout = cmds.columnLayout(
        adjustableColumn=True,
        columnAttach=('both', 20),
        parent=window
    )
    
    # Header
    cmds.text(
        label="Select Assignment to Grade",
        font="boldLabelFont",
        align="center",
        height=30,
        parent=main_layout
    )
    
    cmds.separator(height=15, parent=main_layout)
    
    # FDMA 1510 Section
    cmds.text(
        label="FDMA 1510 - Introduction to 3D Animation",
        font="boldLabelFont",
        align="left",
        backgroundColor=(0.3, 0.3, 0.4),
        height=25,
        parent=main_layout
    )
    
    fdma1510_frame = cmds.frameLayout(
        label="",
        borderStyle="in",
        collapsable=False,
        height=60,
        parent=main_layout
    )
    
    cmds.text(
        label="No assignments available yet",
        font="plainLabelFont",
        align="center",
        parent=fdma1510_frame
    )
    
    cmds.setParent(main_layout)
    cmds.separator(height=10, parent=main_layout)
    
    # FDMA 2530 Section
    cmds.text(
        label="FDMA 2530 - Introduction to Modeling",
        font="boldLabelFont", 
        align="left",
        backgroundColor=(0.3, 0.4, 0.3),
        height=25,
        parent=main_layout
    )
    
    fdma2530_frame = cmds.frameLayout(
        label="",
        borderStyle="in",
        collapsable=False,
        height=80,
        parent=main_layout
    )
    
    # FDMA 2530 assignments layout
    fdma2530_layout = cmds.rowLayout(
        numberOfColumns=3,
        columnAlign=[(1, 'center'), (2, 'center'), (3, 'center')],
        columnWidth=[(1, 120), (2, 120), (3, 120)],
        parent=fdma2530_frame
    )
    
    # U01_SS01 Primitives button
    cmds.button(
        label="U01_SS01\nPrimitives",
        height=45,
        width=110,
        command=lambda *args: _open_u01_ss01_primitives(assignment_window),
        parent=fdma2530_layout
    )
    
    # Placeholder buttons for future assignments
    cmds.button(
        label="U02_SS02\n(Coming Soon)",
        height=45,
        width=110,
        enable=False,
        parent=fdma2530_layout
    )
    
    cmds.button(
        label="U03_SS03\n(Coming Soon)",
        height=45,
        width=110,
        enable=False,
        parent=fdma2530_layout
    )
    
    cmds.setParent(main_layout)
    cmds.separator(height=10, parent=main_layout)
    
    # Custom Section
    cmds.text(
        label="Custom Rubrics",
        font="boldLabelFont",
        align="left", 
        backgroundColor=(0.4, 0.3, 0.3),
        height=25,
        parent=main_layout
    )
    
    custom_frame = cmds.frameLayout(
        label="",
        borderStyle="in",
        collapsable=False,
        height=60,
        parent=main_layout
    )
    
    cmds.text(
        label="Custom rubrics will be added here",
        font="plainLabelFont",
        align="center",
        parent=custom_frame
    )
    
    cmds.setParent(main_layout)
    cmds.separator(height=15, parent=main_layout)
    
    # Close button
    cmds.button(
        label="Close",
        height=35,
        width=100,
        command=lambda *args: cmds.deleteUI(assignment_window, window=True),
        parent=main_layout
    )
    
    cmds.showWindow(window)


def _open_u01_ss01_primitives(parent_window):
    """Open the U01_SS01 Primitives rubric and close the selection window."""
    try:
        from prof.tools.auto_grader.assignments.fdma2530.u01_ss01_primitives import create_u01_ss01_rubric
        create_u01_ss01_rubric()
        # Close the selection window
        if cmds.window(parent_window, exists=True):
            cmds.deleteUI(parent_window, window=True)
    except Exception as e:
        cmds.confirmDialog(
            title="Error",
            message=f"Failed to open U01_SS01 Primitives rubric: {str(e)}",
            button=["OK"]
        )


if __name__ == "__main__":
    # Test the dialog when run directly
    grade_current_assignment()
