"""
Prof-Tools Menu Builder

Creates the Prof-Tools dropdown menu in Maya, with sections for grading
tools and a Help menu for version info and update checking.
"""

from __future__ import absolute_import, division, print_function

import logging
import maya.cmds as cmds
import maya.mel as mel

from prof import __version__
from prof.core.updater import check_for_updates

# Set up logging for this module
logging.basicConfig()
logger = logging.getLogger("prof_menu_builder")
logger.setLevel(logging.INFO)

# Menu labels
MENU_NAME     = "ProfTools"
MENU_LABEL    = "Prof-Tools"
GRADING_LABEL = "Grading Tools"
HELP_LABEL    = "Help"

def build_menu():
    """
    Create or rebuild the Prof-Tools menu in Maya's main window.
    """
    _delete_existing_menu()

    # Get Maya main window for parenting
    main_win = mel.eval('global string $gMainWindow; $tmp = $gMainWindow;')

    # Create the top-level Prof-Tools menu
    menu = cmds.menu(MENU_NAME, label=MENU_LABEL, parent=main_win, tearOff=True)

    _build_grading_section(menu)   # add grading tools section
    _build_developer_section(menu) # add developer tools section (if enabled)
    _build_help_section(menu)      # add help section

    logger.info("Prof-Tools menu created")
    return True  # <— Add this line

def _delete_existing_menu():
    """
    Remove any existing Prof-Tools menu before rebuilding.
    """
    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME)
        logger.debug("Removed existing Prof-Tools menu")

def _build_grading_section(parent_menu):
    """
    Add the 'Grading Tools' submenu with empty placeholders for each class.
    """
    # Open Grading Tools submenu
    grading = cmds.menuItem(
        label=GRADING_LABEL,
        subMenu=True,
        tearOff=True,
        parent=parent_menu
    )

    # Assignment Grading Rubric
    cmds.menuItem(
        label="Assignment Grading Rubric",
        parent=grading,
        command=lambda *args: _open_grading_rubric()
    )
    
    cmds.menuItem(divider=True, parent=grading)

    # FDMA 1510 placeholder
    fdma1510 = cmds.menuItem(
        label="FDMA 1510",
        subMenu=True,
        tearOff=True,
        parent=grading
    )
    cmds.menuItem(label="(no tools yet)", enable=False, parent=fdma1510)
    cmds.setParent('..', menu=True)  # close FDMA 1510 submenu

    # FDMA 2530 submenu
    fdma2530 = cmds.menuItem(
        label="FDMA 2530",
        subMenu=True,
        tearOff=True,
        parent=grading
    )
    cmds.menuItem(
        label="U01_L01_Primitives",
        parent=fdma2530,
        command=lambda *args: _open_u01_ss01_rubric()
    )
    cmds.setParent('..', menu=True)  # close FDMA 2530 submenu

    cmds.setParent('..', menu=True)    # close Grading Tools submenu

def _build_developer_section(parent_menu):
    """
    Add the 'Developer Tools' submenu to the main menu (only shown if dev mode is enabled).
    """
    from prof.core.tools.dev_prefs import should_show_dev_features, get_prefs
    from prof.core.version_utils import get_prof_tools_version, is_test_version
    
    if should_show_dev_features():
        # Add divider before developer tools
        cmds.menuItem(divider=True, parent=parent_menu)
        
        # Check for temporary installation status
        prefs = get_prefs()
        current_version = get_prof_tools_version()
        temp_status = ""
        
        if prefs.is_temp_install_active():
            temp_info = prefs.get_temp_install_info()
            temp_version = temp_info.get("version", "unknown")
            temp_status = " (Test {} temp)".format(temp_version)
        elif is_test_version(current_version):
            temp_status = " (Test {} permanent)".format(current_version)
        
        # Developer submenu at main menu level
        dev_submenu = cmds.menuItem(
            label="Developer Tools{}".format(temp_status),
            subMenu=True,
            tearOff=True,
            parent=parent_menu
        )
        
        # Show installation status
        if prefs.is_temp_install_active():
            temp_info = prefs.get_temp_install_info()
            temp_version = temp_info.get("version", "unknown")
            stable_version = temp_info.get("stable_version", "unknown")
            
            cmds.menuItem(
                label="Status: Test {} Temporarily Installed".format(temp_version),
                parent=dev_submenu,
                enable=False  # Disabled - just a status indicator
            )
            cmds.menuItem(
                label="Will revert to {} on restart".format(stable_version),
                parent=dev_submenu,
                enable=False  # Disabled - just a status indicator
            )
            cmds.menuItem(divider=True, parent=dev_submenu)
        elif is_test_version(current_version):
            cmds.menuItem(
                label="Status: Test {} Permanently Installed".format(current_version),
                parent=dev_submenu,
                enable=False  # Disabled - just a status indicator
            )
            cmds.menuItem(
                label="Use 'Revert to Stable' to downgrade",
                parent=dev_submenu,
                enable=False  # Disabled - just a status indicator
            )
            cmds.menuItem(divider=True, parent=dev_submenu)
        
        # Check for test updates - moved here from help menu
        cmds.menuItem(
            label="Check for Test Updates…",
            parent=dev_submenu,
            command=lambda *args: _check_for_test_updates()
        )
        
        cmds.menuItem(divider=True, parent=dev_submenu)
        
        cmds.menuItem(
            label="Configure Auto-Updates…",
            parent=dev_submenu,
            command=lambda *args: _configure_auto_updates()
        )
        
        cmds.menuItem(
            label="Test Silent Update Check",
            parent=dev_submenu,
            command=lambda *args: _test_silent_update()
        )
        
        cmds.menuItem(divider=True, parent=dev_submenu)
        
        # Conditional menu items based on installation status
        if prefs.is_temp_install_active():
            cmds.menuItem(
                label="Install Different Test Version…",
                parent=dev_submenu,
                command=lambda *args: _install_test_version_temporarily()
            )
        else:
            cmds.menuItem(
                label="Install Test Version Temporarily…",
                parent=dev_submenu,
                command=lambda *args: _install_test_version_temporarily()
            )
        
        # Revert option - enabled if any test version is active
        has_test_version = prefs.is_temp_install_active() or is_test_version(current_version)
        cmds.menuItem(
            label="Revert to Stable Version",
            parent=dev_submenu,
            command=lambda *args: _revert_to_stable(),
            enable=has_test_version
        )
        
        cmds.setParent('..', menu=True)  # close Developer Tools submenu

def _build_help_section(parent_menu):
    """
    Add the 'Help' submenu with version info, update checking, and helpful links.
    Enhanced to provide more useful information for instructors.
    """
    # Open Help submenu
    help_menu = cmds.menuItem(
        label=HELP_LABEL,
        subMenu=True,
        tearOff=True,
        parent=parent_menu
    )

    # About Prof-Tools
    cmds.menuItem(
        label="About Prof-Tools",
        parent=help_menu,
        command=lambda *args: _show_about_dialog()
    )
    
    # Divider before version
    cmds.menuItem(divider=True, parent=help_menu)

    # Display current version (show full version including test component if active)
    from prof.core.tools.dev_prefs import get_prefs
    prefs = get_prefs()
    
    if prefs.is_temp_install_active():
        temp_info = prefs.get_temp_install_info()
        temp_version = temp_info.get("version", __version__)
        version_label = "Version: {} (Test)".format(temp_version)
    else:
        version_label = "Version: {}".format(__version__)
    
    cmds.menuItem(
        label=version_label,
        enable=False,
        parent=help_menu
    )

    # Divider before update section
    cmds.menuItem(divider=True, parent=help_menu)

    # Command to check for updates (uses new dialog)
    cmds.menuItem(
        label="Check for Updates…",
        parent=help_menu,
        command=lambda *args: check_for_updates()
    )
    
    # Toggle developer mode
    cmds.menuItem(divider=True, parent=help_menu)
    
    from prof.core.tools.dev_prefs import is_dev_mode_enabled
    dev_mode_label = "Disable Developer Mode" if is_dev_mode_enabled() else "Enable Developer Mode"
    cmds.menuItem(
        label=dev_mode_label,
        parent=help_menu,
        command=lambda *args: _toggle_developer_mode()
    )
    
    # Divider before links
    cmds.menuItem(divider=True, parent=help_menu)
    
    # GitHub repository
    cmds.menuItem(
        label="View Source Code",
        parent=help_menu,
        command=lambda *args: _open_github()
    )
    
    cmds.setParent('..', menu=True)  # close Help submenu
    cmds.setParent('..', menu=True)  # close main Prof-Tools menu


def _show_about_dialog():
    """Show an about dialog with Prof-Tools information."""
    about_message = (
        "Prof-Tools for Maya\n"
        "Version: {}\n\n"
        "A comprehensive suite of instructor tools for grading and managing "
        "Maya assignments across NMSU's FDMA animation courses.\n\n"
        "This toolset also aims to automate, enhance, and simplify "
        "common Maya tasks and workflows for advanced users.\n\n"
        "Designed for Maya users and instructors at NMSU's "
        "Creative Media Institute (CMI).\n\n"
        "Author: Alexander T. Santiago"
    ).format(__version__)
    
    result = cmds.confirmDialog(
        title="About Prof-Tools",
        message=about_message,
        button=["Alexander T. Santiago", "GitHub", "Close"],
        defaultButton="Close",
        cancelButton="Close",
        dismissString="Close"
    )
    
    # Handle button clicks to open links
    if result == "Alexander T. Santiago":
        _open_portfolio()
    elif result == "GitHub":
        _open_github()


def _open_portfolio():
    """Open Alexander's portfolio website."""
    import webbrowser
    try:
        webbrowser.open("https://atsantiago.artstation.com/resume")
        logger.info("Opened portfolio website")
    except Exception as e:
        logger.error("Failed to open portfolio: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to open resume/portfolio. Please visit:\nhttps://atsantiago.artstation.com/resume",
            button=["OK"]
        )


def _open_github():
    """Open the Prof-Tools GitHub repository."""
    import webbrowser
    try:
        webbrowser.open("https://github.com/Atsantiago/NMSU_Scripts")
        logger.info("Opened GitHub repository")
    except Exception as e:
        logger.error("Failed to open GitHub: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to open GitHub. Please visit:\nhttps://github.com/Atsantiago/NMSU_Scripts",
            button=["OK"]
        )


def _open_grading_rubric():
    """Open the assignment grading rubric system."""
    try:
        from prof.tools.auto_grader.assignments.assignment_rubrics_window import grade_current_assignment
        grade_current_assignment()
        logger.info("Opened grading rubric system")
    except Exception as e:
        logger.error("Failed to open grading rubric: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to open grading rubric. Please check the console for details.",
            button=["OK"]
        )


def _check_for_test_updates():
    """Check for test updates (MAJOR.MINOR.PATCH.TEST format) for development testing."""
    try:
        from prof.core.updater import check_for_test_updates
        check_for_test_updates()
        logger.info("Checked for test updates")
    except Exception as e:
        logger.error("Failed to check for test updates: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to check for test updates. Please check the console for details.",
            button=["OK"]
        )


def _toggle_developer_mode():
    """Toggle developer mode on/off and rebuild menu to show/hide dev features."""
    try:
        from prof.core.tools.dev_prefs import toggle_dev_mode
        new_state = toggle_dev_mode()
        
        # Rebuild menu to reflect new state
        build_menu()
        
        state_msg = "enabled" if new_state else "disabled"
        logger.info("Developer mode %s", state_msg)
        
    except Exception as e:
        logger.error("Failed to toggle developer mode: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to toggle developer mode. Please check the console for details.",
            button=["OK"]
        )


def _configure_auto_updates():
    """Open the auto-update configuration dialog."""
    try:
        from prof.core.tools.silent_updater import configure_auto_updates
        configure_auto_updates()
        logger.info("Opened auto-update configuration")
    except Exception as e:
        logger.error("Failed to open auto-update configuration: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to open auto-update configuration. Please check the console for details.",
            button=["OK"]
        )


def _test_silent_update():
    """Test the silent update checking system."""
    try:
        from prof.core.tools.silent_updater import silently_check_for_updates
        silently_check_for_updates()
        logger.info("Triggered silent update check")
    except Exception as e:
        logger.error("Failed to test silent update: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to test silent update. Please check the console for details.",
            button=["OK"]
        )


def _install_test_version_temporarily():
    """Install a test version temporarily (reverts on Maya restart)."""
    try:
        from prof.core.version_utils import get_prof_tools_version, get_manifest_data
        from prof.core.updater import get_latest_version, _install_specific_version
        from prof.core.tools.dev_prefs import get_prefs
        
        # Get current version and available test versions
        current_version = get_prof_tools_version()
        manifest = get_manifest_data()
        
        if not manifest:
            cmds.confirmDialog(
                title="Error",
                message="Could not retrieve version information. Please check your internet connection.",
                button=["OK"]
            )
            return
        
        # Find test versions
        releases = manifest.get('releases', [])
        test_versions = []
        
        for release in releases:
            if release.get('test_version', False):
                test_versions.append(release.get('version'))
        
        if not test_versions:
            cmds.confirmDialog(
                title="No Test Versions",
                message="No test versions are currently available.",
                button=["OK"]
            )
            return
        
        # Sort test versions (newest first)
        test_versions.sort(key=lambda v: [int(x) for x in v.split('.')], reverse=True)
        
        # Show selection dialog
        if len(test_versions) == 1:
            selected_version = test_versions[0]
            message = "Install test version {} temporarily?\n\nThis will revert to version {} when Maya restarts.".format(
                selected_version, current_version
            )
        else:
            # For multiple versions, use the latest for now
            selected_version = test_versions[0]
            message = "Install latest test version {} temporarily?\n\nThis will revert to version {} when Maya restarts.\n\n(Multiple test versions available: {})".format(
                selected_version, current_version, ", ".join(test_versions)
            )
        
        result = cmds.confirmDialog(
            title="Install Test Version Temporarily",
            message=message,
            button=["Install", "Cancel"],
            defaultButton="Install",
            cancelButton="Cancel"
        )
        
        if result == "Install":
            # Check if there's already a temp installation
            prefs = get_prefs()
            if prefs.is_temp_install_active():
                temp_info = prefs.get_temp_install_info()
                current_temp = temp_info.get("version", "unknown")
                
                override_result = cmds.confirmDialog(
                    title="Temporary Installation Active",
                    message="Test version {} is already temporarily installed.\n\nReplace with version {}?".format(
                        current_temp, selected_version
                    ),
                    button=["Replace", "Cancel"],
                    defaultButton="Replace",
                    cancelButton="Cancel"
                )
                
                if override_result != "Replace":
                    return
            
            # Set up temporary installation tracking
            prefs.set_temp_install(selected_version, current_version)
            
            # Install the test version
            success = _install_specific_version(selected_version, temporary=True)
            
            if success:
                cmds.confirmDialog(
                    title="Installation Complete",
                    message="Test version {} installed temporarily.\n\nThis will automatically revert to {} when Maya restarts.\n\nUse 'Developer Tools > Revert to Stable Version' to revert immediately.".format(
                        selected_version, current_version
                    ),
                    button=["OK"]
                )
                logger.info("Temporarily installed test version %s", selected_version)
            else:
                prefs.clear_temp_install()
                cmds.confirmDialog(
                    title="Installation Failed",
                    message="Failed to install test version {}. Please check the console for details.".format(
                        selected_version
                    ),
                    button=["OK"]
                )
                logger.error("Failed to install test version %s", selected_version)
        
    except Exception as e:
        logger.error("Failed to install test version temporarily: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to install test version temporarily. Please check the console for details.",
            button=["OK"]
        )


def _revert_to_stable():
    """Revert from test version to stable version."""
    try:
        from prof.core.tools.dev_prefs import get_prefs
        from prof.core.version_utils import get_prof_tools_version, is_test_version
        from prof.core.updater import perform_automatic_update
        
        prefs = get_prefs()
        current_version = get_prof_tools_version()
        
        # Check if we have a temporary installation
        if prefs.is_temp_install_active():
            temp_info = prefs.get_temp_install_info()
            stable_version = temp_info.get("stable_version", "unknown")
            
            result = cmds.confirmDialog(
                title="Revert to Stable",
                message="Revert from temporary test version to stable version {}?".format(stable_version),
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No"
            )
            
            if result == "Yes":
                prefs.clear_temp_install()
                cmds.confirmDialog(
                    title="Reverted",
                    message="Reverted to stable version. Please restart Maya to complete the process.",
                    button=["OK"]
                )
                logger.info("Reverted from temporary test version to stable version")
        
        # Check if we have a permanently installed test version
        elif is_test_version(current_version):
            # Get stable version from manifest
            from prof.core.version_utils import get_manifest_data
            manifest = get_manifest_data()
            stable_version = manifest.get('current_version', 'latest stable') if manifest else 'latest stable'
            
            result = cmds.confirmDialog(
                title="Revert to Stable",
                message="You have test version {} permanently installed.\n\nRevert to stable version {}?\n\nThis will download and install the stable version.".format(
                    current_version, stable_version
                ),
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No"
            )
            
            if result == "Yes":
                # Remove the installed version file to revert to manifest version
                try:
                    from prof.core.version_utils import get_current_file_directory, clear_version_cache
                    import os
                    current_dir = get_current_file_directory()
                    version_file = os.path.join(current_dir, '..', 'installed_version.txt')
                    if os.path.exists(version_file):
                        os.remove(version_file)
                        logger.info("Removed installed version file")
                        # Clear cache so the manifest version is used immediately
                        clear_version_cache()
                        logger.debug("Cleared version cache after removing version file")
                except Exception as e:
                    logger.warning("Could not remove installed version file: %s", e)
                
                # Install the stable version
                success = perform_automatic_update(include_test_versions=False)
                
                if success:
                    cmds.confirmDialog(
                        title="Reverted to Stable",
                        message="Successfully reverted to stable version {}.\n\nThe menu has been refreshed.".format(stable_version),
                        button=["OK"]
                    )
                    logger.info("Successfully reverted from permanent test version to stable")
                else:
                    cmds.confirmDialog(
                        title="Reversion Failed",
                        message="Failed to revert to stable version. Please try updating manually or check the console for details.",
                        button=["OK"]
                    )
        else:
            cmds.confirmDialog(
                title="No Test Version",
                message="No test version installation found. You are already running a stable version ({}).".format(current_version),
                button=["OK"]
            )
            
    except Exception as e:
        logger.error("Failed to revert to stable version: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to revert to stable version. Please check the console for details.",
            button=["OK"]
        )


def _open_u01_ss01_rubric():
    """Open the FDMA 2530 U01_SS01 Primitives assignment rubric."""
    try:
        from prof.tools.auto_grader.assignments.fdma2530.u01_ss01_primitives import create_u01_ss01_rubric
        create_u01_ss01_rubric()
        logger.info("Opened FDMA 2530 U01_SS01 Primitives rubric")
    except Exception as e:
        logger.error("Failed to open U01_SS01 rubric: %s", e)
        cmds.confirmDialog(
            title="Error",
            message="Failed to open U01_SS01 rubric. Please check the console for details.",
            button=["OK"]
        )


if __name__ == "__main__":
    # When run directly in Maya script editor, build the menu
    logger.setLevel(logging.DEBUG)
    build_menu()
