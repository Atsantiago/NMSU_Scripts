"""
Prof-Tools Update Dialog

Author: Alexander T. Santiago
Repository: https://github.com/Atsantiago/NMSU_Scripts
"""

from __future__ import absolute_import, division, print_function

import sys
import webbrowser
import logging

try:
    import maya.cmds as cmds
    import maya.OpenMayaUI as OpenMayaUI
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    OpenMayaUI = None
    MAYA_AVAILABLE = False

# Import version utilities
from ..core.version_utils import get_prof_tools_version
from ..core.updater import get_latest_version, compare_versions

# Configure logging
logger = logging.getLogger(__name__)

# Window constants
WINDOW_NAME = "prof_tools_update_dialog"
WINDOW_TITLE = "Prof-Tools Update Manager"
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 320

# Colors (Maya-friendly RGB values 0-1)
COLOR_BACKGROUND = (0.25, 0.25, 0.25)
COLOR_HEADER = (0.35, 0.35, 0.35)
COLOR_SUCCESS = (0.4, 0.7, 0.4)
COLOR_WARNING = (0.9, 0.7, 0.3)
COLOR_ERROR = (0.8, 0.4, 0.4)
COLOR_INFO = (0.5, 0.7, 0.9)
COLOR_TEXT = (0.9, 0.9, 0.9)


def show_update_dialog():
    """
    Show the Prof-Tools update dialog window.
    
    This is the main entry point for the update dialog system.
    Creates a professional dialog designed for advanced Maya users and instructors.
    """
    if not MAYA_AVAILABLE:
        print("Prof-Tools Update Dialog requires Maya environment")
        return
    
    # Close existing window if it exists
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)
    
    # Get version information
    current_version = get_prof_tools_version()
    latest_version = get_latest_version()
    
    # Determine update status
    if latest_version and compare_versions(current_version, latest_version):
        update_available = True
        status_message = "Update Available"
        status_color = COLOR_WARNING
    elif latest_version:
        update_available = False
        status_message = "Up to Date"
        status_color = COLOR_SUCCESS
    else:
        update_available = None
        status_message = "Unable to Check"
        status_color = COLOR_ERROR
        latest_version = "Unknown"
    
    # Create the main window
    window = cmds.window(
        WINDOW_NAME,
        title=WINDOW_TITLE,
        widthHeight=(WINDOW_WIDTH, WINDOW_HEIGHT),
        sizeable=False,
        minimizeButton=False,
        maximizeButton=False,
        titleBar=True,
        resizeToFitChildren=False
    )
    
    # Main layout
    main_layout = cmds.columnLayout(
        adjustableColumn=True,
        marginWidth=15,
        marginHeight=15,
        spacing=10,
        parent=window
    )
    
    # Build the UI sections
    _create_header_section(main_layout)
    _create_version_info_section(main_layout, current_version, latest_version, status_message, status_color)
    _create_details_section(main_layout, update_available, latest_version)
    _create_button_section(main_layout, update_available, latest_version)
    
    # Show window
    cmds.showWindow(window)
    
    # Set window properties
    cmds.window(window, edit=True, sizeable=False)
    
    return window


def _create_header_section(parent):
    """Create the header section with title and branding."""
    # Header background
    header_frame = cmds.frameLayout(
        label="",
        borderStyle="etchedIn",
        backgroundColor=COLOR_HEADER,
        marginWidth=5,
        marginHeight=8,
        parent=parent
    )
    
    cmds.columnLayout(adjustableColumn=True, spacing=5, parent=header_frame)
    
    # Title
    cmds.text(
        label="Prof-Tools Update Manager",
        font="boldLabelFont",
        height=25,
        backgroundColor=COLOR_HEADER,
        align="center"
    )
    
    # Subtitle
    cmds.text(
        label="Maya Instructor Tools for NMSU CMI",
        font="smallPlainLabelFont",
        height=20,
        align="center"
    )


def _create_version_info_section(parent, current_version, latest_version, status_message, status_color):
    """Create the version information section."""
    info_frame = cmds.frameLayout(
        label="Version Information",
        borderStyle="etchedIn",
        collapsable=False,
        marginWidth=5,
        marginHeight=5,
        parent=parent
    )
    
    info_layout = cmds.columnLayout(adjustableColumn=True, spacing=8, parent=info_frame)
    
    # Current version row
    cmds.rowLayout(
        numberOfColumns=2,
        columnWidth2=(150, 250),
        columnAlign2=("left", "left"),
        columnAttach2=("left", "left"),
        parent=info_layout
    )
    cmds.text(label="Installed Version:", font="boldLabelFont")
    cmds.text(label=f"v{current_version}", backgroundColor=COLOR_INFO)
    cmds.setParent("..")
    
    # Latest version row
    cmds.rowLayout(
        numberOfColumns=2,
        columnWidth2=(150, 250),
        columnAlign2=("left", "left"),
        columnAttach2=("left", "left"),
        parent=info_layout
    )
    cmds.text(label="Latest Release:", font="boldLabelFont")
    cmds.text(label=f"v{latest_version}")
    cmds.setParent("..")
    
    # Status row
    cmds.rowLayout(
        numberOfColumns=2,
        columnWidth2=(150, 250),
        columnAlign2=("left", "left"),
        columnAttach2=("left", "left"),
        parent=info_layout
    )
    cmds.text(label="Status:", font="boldLabelFont")
    cmds.text(label=status_message, backgroundColor=status_color)
    cmds.setParent("..")


def _create_details_section(parent, update_available, latest_version):
    """Create the details/changelog section."""
    if update_available is None:
        # Error state
        details_frame = cmds.frameLayout(
            label="Connection Status",
            borderStyle="etchedIn",
            collapsable=False,
            marginWidth=5,
            marginHeight=5,
            parent=parent
        )
        
        cmds.columnLayout(adjustableColumn=True, spacing=5, parent=details_frame)
        cmds.text(
            label="Unable to connect to update server.",
            backgroundColor=COLOR_ERROR,
            height=25,
            align="center"
        )
        cmds.text(
            label="Please check your internet connection and try again.",
            height=20,
            align="center"
        )
        
    elif update_available:
        # Update available
        details_frame = cmds.frameLayout(
            label=f"Update Details - v{latest_version}",
            borderStyle="etchedIn",
            collapsable=False,
            marginWidth=5,
            marginHeight=5,
            parent=parent
        )
        
        cmds.columnLayout(adjustableColumn=True, spacing=5, parent=details_frame)
        cmds.text(
            label="A new version of Prof-Tools is available!",
            backgroundColor=COLOR_WARNING,
            height=25,
            align="center"
        )
        cmds.text(
            label="Click 'Update Now' to automatically install the latest version.",
            height=20,
            align="center"
        )
        
    else:
        # Up to date
        details_frame = cmds.frameLayout(
            label="System Status",
            borderStyle="etchedIn",
            collapsable=False,
            marginWidth=5,
            marginHeight=5,
            parent=parent
        )
        
        cmds.columnLayout(adjustableColumn=True, spacing=5, parent=details_frame)
        cmds.text(
            label="Prof-Tools is up to date!",
            backgroundColor=COLOR_SUCCESS,
            height=25,
            align="center"
        )
        cmds.text(
            label="You have the latest version with all current features.",
            height=20,
            align="center"
        )


def _create_button_section(parent, update_available, latest_version):
    """Create the action buttons section."""
    button_layout = cmds.rowLayout(
        numberOfColumns=3,
        columnWidth3=(120, 120, 120),
        columnAlign3=("center", "center", "center"),
        columnAttach3=("both", "both", "both"),
        columnOffset3=(5, 5, 5),
        parent=parent
    )
    
    # Refresh button (always available)
    cmds.button(
        label="Refresh",
        height=35,
        backgroundColor=COLOR_INFO,
        command=lambda *args: _refresh_update_dialog(),
        annotation="Check for updates again"
    )
    
    # Update/View button (context-dependent)
    if update_available:
        cmds.button(
            label="Update Now",
            height=35,
            backgroundColor=COLOR_WARNING,
            command=lambda *args: _launch_update_process(),
            annotation=f"Automatically download and install v{latest_version}"
        )
    else:
        cmds.button(
            label="View Releases",
            height=35,
            backgroundColor=COLOR_INFO,
            command=lambda *args: _view_releases(),
            annotation="View all releases on GitHub"
        )
    
    # Close button (always available)
    cmds.button(
        label="Close",
        height=35,
        command=lambda *args: _close_update_dialog(),
        annotation="Close this dialog"
    )


def _refresh_update_dialog():
    """Refresh the update dialog with latest information."""
    logger.info("Refreshing update dialog...")
    show_update_dialog()


def _launch_update_process():
    """Launch the automatic update process."""
    try:
        # Ask user for confirmation
        result = cmds.confirmDialog(
            title="Update Prof-Tools",
            message="Would you like to update now?\n\nThis will download and install the latest version automatically.",
            button=["Update Now", "Cancel"],
            defaultButton="Update Now",
            cancelButton="Cancel",
            dismissString="Cancel"
        )
        
        if result == "Update Now":
            logger.info("Starting automatic update process...")
            
            # Import the update function
            from ..core.updater import perform_automatic_update
            
            # Show progress message
            progress_dialog = cmds.confirmDialog(
                title="Updating Prof-Tools",
                message="Downloading and installing update...\nThis may take a few moments.",
                button=["Please Wait..."],
                defaultButton="Please Wait..."
            )
            
            # Perform the update
            success = perform_automatic_update()
            
            # Close the update dialog first
            _close_update_dialog()
            
            if success:
                # Show success message
                cmds.confirmDialog(
                    title="Update Complete",
                    message="Prof-Tools has been updated successfully!\n\nThe menu has been refreshed with the latest version.",
                    button=["OK"],
                    defaultButton="OK"
                )
            else:
                # Show error and offer manual option
                result = cmds.confirmDialog(
                    title="Update Failed",
                    message="Automatic update failed. Would you like to download manually?",
                    button=["Open Downloads", "Cancel"],
                    defaultButton="Open Downloads",
                    cancelButton="Cancel"
                )
                
                if result == "Open Downloads":
                    repo_url = "https://github.com/Atsantiago/NMSU_Scripts"
                    releases_url = repo_url + "/releases"
                    webbrowser.open(releases_url)
        
    except Exception as e:
        logger.error("Update process failed: %s", e)
        cmds.confirmDialog(
            title="Update Error",
            message="Update process failed: {}".format(str(e)),
            button=["OK"],
            defaultButton="OK"
        )


def _view_releases():
    """Open the releases page to view all releases."""
    try:
        repo_url = "https://github.com/Atsantiago/NMSU_Scripts"
        releases_url = repo_url + "/releases"
        webbrowser.open(releases_url)
        logger.info("Opened releases page for viewing")
        
    except Exception as e:
        logger.error("Failed to open releases page: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to open the releases page. Please visit:\nhttps://github.com/Atsantiago/NMSU_Scripts/releases",
            button=["OK"],
            defaultButton="OK"
        )


def _close_update_dialog():
    """Close the update dialog window."""
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)


# Convenience functions for integration
def check_for_updates_with_dialog():
    """
    Check for updates and show the dialog.
    
    This is the main function that should be called from the Prof-Tools menu
    or other parts of the system to show the update dialog.
    """
    show_update_dialog()


if __name__ == "__main__":
    # For testing outside of Prof-Tools context
    if MAYA_AVAILABLE:
        show_update_dialog()
    else:
        print("This module requires Maya to run")
