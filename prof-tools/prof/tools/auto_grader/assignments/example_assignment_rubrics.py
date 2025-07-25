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
    Show a dialog to select which assignment rubric to open.
    
    This function provides a simple interface for instructors to choose
    which assignment they want to grade.
    """
    if not MAYA_AVAILABLE:
        print("Maya not available - cannot display dialog")
        return
    
    # Create selection dialog
    result = cmds.confirmDialog(
        title="Select Assignment to Grade",
        message="Which assignment would you like to grade?",
        button=["FDMA 2530 - U01_SS01 Primitives", "Cancel"],
        defaultButton="FDMA 2530 - U01_SS01 Primitives",
        cancelButton="Cancel",
        dismissString="Cancel"
    )
    
    if result == "FDMA 2530 - U01_SS01 Primitives":
        try:
            from prof.tools.auto_grader.assignments.fdma2530.u01_ss01_primitives import create_u01_ss01_rubric
            create_u01_ss01_rubric()
        except Exception as e:
            cmds.confirmDialog(
                title="Error",
                message=f"Failed to open FDMA 2530 U01_SS01 rubric: {str(e)}",
                button=["OK"]
            )
    # Add more assignment options here as they are developed


if __name__ == "__main__":
    # Test the dialog when run directly
    grade_current_assignment()
