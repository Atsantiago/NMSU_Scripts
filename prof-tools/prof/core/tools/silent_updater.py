"""
Silent Update Checker for Prof-Tools

Inspired by GT Tools' silent update system. Checks for updates in the background
without interrupting the user's workflow, and only shows notifications when
updates are actually available.

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function

import logging
import threading
import sys

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

def silently_check_for_updates():
    """
    Silently check for updates in the background.
    Only shows UI if an update is actually available.
    
    This function:
    1. Checks if auto-update is enabled
    2. Checks if it's time to update based on interval
    3. Runs update check in background thread
    4. Only shows update dialog if update is available
    """
    from prof.core.tools.dev_prefs import get_prefs
    
    prefs = get_prefs()
    
    # Check if auto-update is enabled
    if not prefs.is_auto_check_enabled():
        logger.debug("Auto-check disabled, skipping silent update check")
        return
    
    # Check if it's time to update
    if not prefs.should_check_for_updates():
        logger.debug("Not time to check for updates yet")
        return
    
    logger.info("Starting silent update check...")
    
    def _check_for_updates_threaded():
        """
        Internal function to check for updates in a separate thread.
        This prevents blocking Maya's UI during the network request.
        """
        try:
            from prof.core.updater import get_latest_version, compare_versions
            from prof.core.version_utils import get_prof_tools_version
            
            # Get current and latest versions
            current_version = get_prof_tools_version()
            if not current_version:
                logger.debug("Could not determine current version")
                return
            
            # Include test versions if dev mode is enabled
            include_test = prefs.is_dev_mode_enabled() and prefs.includes_test_versions()
            latest_version = get_latest_version(include_test=include_test)
            
            if not latest_version:
                logger.debug("Could not determine latest version")
                return
            
            # Update last check date
            prefs.set_last_check_date()
            
            # Compare versions
            if compare_versions(current_version, latest_version, include_test_versions=include_test):
                # Update available - show notification
                _show_update_notification(current_version, latest_version, include_test)
            else:
                logger.debug("No updates available (current: %s, latest: %s)", current_version, latest_version)
                
        except Exception as e:
            logger.debug("Silent update check failed: %s", e)
    
    def _maya_execute_update_check():
        """Maya-specific function to execute update check using deferred execution."""
        if MAYA_AVAILABLE:
            # Use Maya's executeDeferred to run in main thread when idle
            cmds.evalDeferred(lambda: _check_for_updates_threaded())
        else:
            # Direct execution if not in Maya
            _check_for_updates_threaded()
    
    try:
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=_maya_execute_update_check)
        thread.daemon = True  # Don't prevent Maya from closing
        thread.start()
    except Exception as e:
        logger.debug("Could not start update check thread: %s", e)


def _show_update_notification(current_version, latest_version, is_test_version):
    """
    Show a non-intrusive update notification.
    
    Args:
        current_version (str): Current version
        latest_version (str): Latest available version  
        is_test_version (bool): Whether the latest version is a test version
    """
    if not MAYA_AVAILABLE:
        print("Prof-Tools update available: {} -> {}".format(current_version, latest_version))
        return
    
    try:
        from prof.core.version_utils import is_test_version as check_test_version
        
        # Determine version type
        version_type = "test version" if check_test_version(latest_version) else "stable version"
        
        # Create message
        if is_test_version:
            title = "Prof-Tools Test Update Available"
            message = (
                "A new test version of Prof-Tools is available:\n\n"
                "Current: {}\n"
                "Available: {} ({})\n\n"
                "⚠️ Test versions are for development and testing.\n"
                "Open update manager?"
            ).format(current_version, latest_version, version_type)
        else:
            title = "Prof-Tools Update Available"
            message = (
                "A new version of Prof-Tools is available:\n\n"
                "Current: {}\n"
                "Available: {}\n\n"
                "Open update manager?"
            ).format(current_version, latest_version)
        
        # Show dialog
        result = cmds.confirmDialog(
            title=title,
            message=message,
            button=["Open Update Manager", "Remind Me Later", "Don't Ask Again"],
            defaultButton="Open Update Manager",
            cancelButton="Remind Me Later",
            dismissString="Remind Me Later"
        )
        
        if result == "Open Update Manager":
            _open_update_manager(include_test_versions=is_test_version)
        elif result == "Don't Ask Again":
            # Disable auto-check
            from prof.core.tools.dev_prefs import get_prefs
            prefs = get_prefs()
            prefs.set_auto_check_enabled(False)
            cmds.inViewMessage(
                amg='Auto-check for updates <span style="color:#FF0000;">disabled</span>. Re-enable in Help menu.',
                pos='botLeft', fade=True, alpha=0.9
            )
        
    except Exception as e:
        logger.error("Could not show update notification: %s", e)


def _open_update_manager(include_test_versions=False):
    """
    Open the update manager dialog.
    
    Args:
        include_test_versions (bool): Whether to include test versions
    """
    try:
        if include_test_versions:
            from prof.core.updater import check_for_test_updates
            check_for_test_updates()
        else:
            from prof.core.updater import check_for_updates
            check_for_updates()
    except Exception as e:
        logger.error("Could not open update manager: %s", e)


def configure_auto_updates():
    """
    Show a dialog to configure auto-update settings.
    Inspired by GT Tools' preference configuration.
    """
    if not MAYA_AVAILABLE:
        logger.warning("Auto-update configuration requires Maya")
        return
    
    from prof.core.tools.dev_prefs import get_prefs
    prefs = get_prefs()
    
    # Get current settings
    auto_enabled = prefs.is_auto_check_enabled()
    interval_days = prefs.get_check_interval_days()
    include_test = prefs.includes_test_versions()
    
    # Interval options (similar to GT Tools)
    interval_options = {
        1: "Daily",
        3: "Every 3 days", 
        7: "Weekly",
        14: "Every 2 weeks",
        30: "Monthly",
        90: "Every 3 months",
        180: "Every 6 months",
        365: "Yearly"
    }
    
    # Find current interval display name
    current_interval_name = interval_options.get(interval_days, "{} days".format(interval_days))
    
    try:
        # Create configuration dialog
        window_name = "profToolsAutoUpdateConfig"
        
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)
        
        window = cmds.window(
            window_name,
            title="Prof-Tools Auto-Update Configuration",
            widthHeight=(400, 250),
            resizeToFitChildren=True,
            sizeable=False
        )
        
        main_layout = cmds.columnLayout(adjustableColumn=True, parent=window)
        
        # Header
        cmds.text(
            label="Configure Automatic Update Checking",
            font="boldLabelFont",
            height=30,
            parent=main_layout
        )
        
        cmds.separator(height=10, parent=main_layout)
        
        # Auto-check toggle
        auto_check_layout = cmds.rowLayout(
            numberOfColumns=2,
            columnAlign=[(1, 'left'), (2, 'left')],
            columnWidth=[(1, 200), (2, 150)],
            parent=main_layout
        )
        
        cmds.text(label="Enable Auto-Check:", parent=auto_check_layout)
        auto_checkbox = cmds.checkBox(
            label="",
            value=auto_enabled,
            parent=auto_check_layout
        )
        
        cmds.setParent(main_layout)
        
        # Interval setting
        interval_layout = cmds.rowLayout(
            numberOfColumns=2,
            columnAlign=[(1, 'left'), (2, 'left')],
            columnWidth=[(1, 200), (2, 150)],
            parent=main_layout
        )
        
        cmds.text(label="Check Interval:", parent=interval_layout)
        interval_button = cmds.button(
            label=current_interval_name,
            width=150,
            command=lambda *args: _cycle_interval(interval_button, prefs),
            parent=interval_layout
        )
        
        cmds.setParent(main_layout)
        
        # Test versions toggle (only show if dev mode is enabled)
        test_checkbox = None
        if prefs.is_dev_mode_enabled():
            test_layout = cmds.rowLayout(
                numberOfColumns=2,
                columnAlign=[(1, 'left'), (2, 'left')],
                columnWidth=[(1, 200), (2, 150)],
                parent=main_layout
            )
            
            cmds.text(label="Include Test Versions:", parent=test_layout)
            test_checkbox = cmds.checkBox(
                label="(Dev Mode Only)",
                value=include_test,
                parent=test_layout
            )
            
            cmds.setParent(main_layout)
        
        cmds.separator(height=15, parent=main_layout)
        
        # Buttons
        button_layout = cmds.rowLayout(
            numberOfColumns=3,
            columnAlign=[(1, 'center'), (2, 'center'), (3, 'center')],
            columnWidth=[(1, 120), (2, 120), (3, 120)],
            parent=main_layout
        )
        
        cmds.button(
            label="Apply",
            command=lambda *args: _apply_auto_update_settings(
                window, prefs, auto_checkbox, test_checkbox
            ),
            parent=button_layout
        )
        
        cmds.button(
            label="Test Now",
            command=lambda *args: _test_update_check(),
            parent=button_layout
        )
        
        cmds.button(
            label="Cancel",
            command=lambda *args: cmds.deleteUI(window, window=True),
            parent=button_layout
        )
        
        cmds.showWindow(window)
        
    except Exception as e:
        logger.error("Could not create auto-update configuration dialog: %s", e)


def _cycle_interval(button, prefs):
    """Cycle through available interval options."""
    interval_options = [1, 3, 7, 14, 30, 90, 180, 365]
    interval_names = {
        1: "Daily",
        3: "Every 3 days",
        7: "Weekly", 
        14: "Every 2 weeks",
        30: "Monthly",
        90: "Every 3 months",
        180: "Every 6 months", 
        365: "Yearly"
    }
    
    current = prefs.get_check_interval_days()
    try:
        current_index = interval_options.index(current)
        next_index = (current_index + 1) % len(interval_options)
    except ValueError:
        next_index = 0
    
    new_interval = interval_options[next_index]
    new_name = interval_names[new_interval]
    
    cmds.button(button, edit=True, label=new_name)
    prefs.set_check_interval_days(new_interval)


def _apply_auto_update_settings(window, prefs, auto_checkbox, test_checkbox):
    """Apply the auto-update settings."""
    try:
        # Get values
        auto_enabled = cmds.checkBox(auto_checkbox, query=True, value=True)
        test_enabled = False
        if test_checkbox:
            test_enabled = cmds.checkBox(test_checkbox, query=True, value=True)
        
        # Apply settings
        prefs.set_auto_check_enabled(auto_enabled)
        prefs.set_include_test_versions(test_enabled)
        
        # Show feedback
        status = "enabled" if auto_enabled else "disabled"
        cmds.inViewMessage(
            amg='Auto-update checking <span style="color:#00FF00;">{}</span>'.format(status),
            pos='botLeft', fade=True, alpha=0.9
        )
        
        # Close window
        cmds.deleteUI(window, window=True)
        
    except Exception as e:
        logger.error("Could not apply auto-update settings: %s", e)


def _test_update_check():
    """Test the update checking system immediately."""
    try:
        from prof.core.tools.dev_prefs import get_prefs
        prefs = get_prefs()
        
        # Force an immediate check
        prefs.set_last_check_date(None)  # Reset last check date
        silently_check_for_updates()
        
        cmds.inViewMessage(
            amg='Update check <span style="color:#00FF00;">triggered</span>',
            pos='botLeft', fade=True, alpha=0.9
        )
        
    except Exception as e:
        logger.error("Could not test update check: %s", e)


def initialize_silent_updates():
    """
    Initialize the silent update system for automatic background checking.
    
    This function is called during package initialization to set up 
    automatic update checking based on user preferences. If developer 
    mode is enabled and auto-updates are configured, it will start 
    background checking.
    
    Safe to call multiple times - will not create duplicate checkers.
    """
    try:
        from prof.core.tools.dev_prefs import get_prefs
        
        prefs = get_prefs()
        
        # Only initialize if developer mode is enabled and auto-updates are on
        if prefs.is_dev_mode_enabled() and prefs.is_auto_check_enabled():
            logger.debug("Initializing silent update system...")
            
            # Check if we should perform an update check based on interval
            if prefs.should_check_for_updates():
                logger.debug("Starting background update check...")
                silently_check_for_updates()
            else:
                logger.debug("Update check not needed yet (within check interval)")
        else:
            logger.debug("Silent updates not enabled (dev mode: %s, auto-update: %s)", 
                        prefs.is_dev_mode_enabled(), prefs.is_auto_check_enabled())
            
    except ImportError as e:
        logger.debug("Could not import dependencies for silent updates: %s", e)
    except Exception as e:
        logger.error("Failed to initialize silent updates: %s", e)


if __name__ == "__main__":
    # Test the silent update system
    configure_auto_updates()
