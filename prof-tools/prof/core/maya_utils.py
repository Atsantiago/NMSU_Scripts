"""
Prof-Tools Maya Utilities
Maya environment utilities and helper functions for prof-tools package.

This module provides Maya-specific utilities for UI operations, scene management,
and Maya environment integration.
"""

# Python 2/3 compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

# Configure logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Maya availability check
MAYA_AVAILABLE = False
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    # Create dummy modules for non-Maya environments
    class DummyMayaModule:
        def __getattr__(self, name):
            def dummy_function(*args, **kwargs):
                raise RuntimeError("Maya not available - cannot execute Maya commands")
            return dummy_function
    
    cmds = DummyMayaModule()
    mel = DummyMayaModule()

def is_maya_available():
    """
    Check if Maya is available in the current environment.
    
    Returns:
        bool: True if Maya is available, False otherwise
    """
    return MAYA_AVAILABLE

def get_maya_version():
    """
    Get the current Maya version.
    
    Returns:
        str: Maya version string, or empty string if not available
    """
    if not is_maya_available():
        return ""
    
    try:
        return cmds.about(version=True)
    except Exception as e:
        logger.error("Failed to get Maya version: {}".format(str(e)))
        return ""

def get_maya_build_info():
    """
    Get Maya build information.
    
    Returns:
        dict: Dictionary containing Maya build information
    """
    if not is_maya_available():
        return {}
    
    try:
        return {
            'version': cmds.about(version=True),
            'build_date': cmds.about(buildDate=True),
            'operating_system': cmds.about(operatingSystem=True),
            'api_version': cmds.about(apiVersion=True),
            'product': cmds.about(product=True),
            'is_batch_mode': cmds.about(batch=True)
        }
    except Exception as e:
        logger.error("Failed to get Maya build info: {}".format(str(e)))
        return {}

def is_maya_batch_mode():
    """
    Check if Maya is running in batch mode (no GUI).
    
    Returns:
        bool: True if in batch mode, False otherwise
    """
    if not is_maya_available():
        return False
    
    try:
        return cmds.about(batch=True)
    except Exception:
        return False

def get_maya_main_window():
    """
    Get Maya's main window for UI parenting.
    
    Returns:
        str: Maya main window name, or empty string if not available
    """
    if not is_maya_available() or is_maya_batch_mode():
        return ""
    
    try:
        return mel.eval('global string $gMainWindow; $tmp = $gMainWindow;')
    except Exception as e:
        logger.error("Failed to get Maya main window: {}".format(str(e)))
        return ""

def safe_maya_command(command_func, *args, **kwargs):
    """
    Safely execute a Maya command with error handling.
    
    Args:
        command_func: Maya command function to execute
        *args: Positional arguments for the command
        **kwargs: Keyword arguments for the command
        
    Returns:
        tuple: (success, result) where success is bool and result is command output or error message
    """
    if not is_maya_available():
        return False, "Maya not available"
    
    try:
        result = command_func(*args, **kwargs)
        return True, result
    except Exception as e:
        error_msg = "Maya command failed: {}".format(str(e))
        logger.error(error_msg)
        return False, error_msg

def show_maya_dialog(title, message, button_labels=None):
    """
    Show a dialog in Maya with proper error handling.
    
    Args:
        title (str): Dialog title
        message (str): Dialog message
        button_labels (list): List of button labels (default: ["OK"])
        
    Returns:
        str: Selected button label, or empty string if failed
    """
    if not is_maya_available() or is_maya_batch_mode():
        # Fallback to console output if no UI available
        print("{}: {}".format(title, message))
        return ""
    
    if button_labels is None:
        button_labels = ["OK"]
    
    try:
        result = cmds.confirmDialog(
            title=title,
            message=message,
            button=button_labels,
            defaultButton=button_labels[0] if button_labels else "OK"
        )
        return result
    except Exception as e:
        logger.error("Failed to show Maya dialog: {}".format(str(e)))
        # Fallback to console
        print("{}: {}".format(title, message))
        return ""

def show_maya_warning(message, title="Prof-Tools Warning"):
    """
    Show a warning dialog in Maya.
    
    Args:
        message (str): Warning message
        title (str): Dialog title
    """
    show_maya_dialog(title, message, ["OK"])

def show_maya_error(message, title="Prof-Tools Error"):
    """
    Show an error dialog in Maya.
    
    Args:
        message (str): Error message
        title (str): Dialog title
    """
    show_maya_dialog(title, message, ["OK"])

def show_maya_info(message, title="Prof-Tools Info"):
    """
    Show an info dialog in Maya.
    
    Args:
        message (str): Info message
        title (str): Dialog title
    """
    show_maya_dialog(title, message, ["OK"])

def get_current_scene_file():
    """
    Get the current Maya scene file path.
    
    Returns:
        str: Current scene file path, or empty string if not available
    """
    if not is_maya_available():
        return ""
    
    try:
        scene_name = cmds.file(query=True, sceneName=True)
        return scene_name if scene_name else ""
    except Exception as e:
        logger.error("Failed to get current scene file: {}".format(str(e)))
        return ""

def is_scene_modified():
    """
    Check if the current Maya scene has unsaved changes.
    
    Returns:
        bool: True if scene is modified, False otherwise
    """
    if not is_maya_available():
        return False
    
    try:
        return cmds.file(query=True, modified=True)
    except Exception as e:
        logger.error("Failed to check if scene is modified: {}".format(str(e)))
        return False

def get_maya_preferences_dir():
    """
    Get Maya's preferences directory.
    
    Returns:
        str: Maya preferences directory path
    """
    if not is_maya_available():
        return ""
    
    try:
        return cmds.internalVar(userPrefDir=True)
    except Exception as e:
        logger.error("Failed to get Maya preferences directory: {}".format(str(e)))
        return ""

def get_maya_app_dir():
    """
    Get Maya's application directory.
    
    Returns:
        str: Maya application directory path
    """
    if not is_maya_available():
        return ""
    
    try:
        return cmds.internalVar(userAppDir=True)
    except Exception as e:
        logger.error("Failed to get Maya application directory: {}".format(str(e)))
        return ""

def cleanup_maya_ui(ui_name):
    """
    Safely cleanup Maya UI elements.
    
    Args:
        ui_name (str): Name of UI element to cleanup
        
    Returns:
        bool: True if cleanup successful, False otherwise
    """
    if not is_maya_available():
        return False
    
    try:
        # Check if it's a window
        if cmds.window(ui_name, exists=True):
            cmds.deleteUI(ui_name, window=True)
            logger.debug("Cleaned up Maya window: {}".format(ui_name))
            return True
        
        # Check if it's a menu
        elif cmds.menu(ui_name, exists=True):
            cmds.deleteUI(ui_name)
            logger.debug("Cleaned up Maya menu: {}".format(ui_name))
            return True
        
        return True  # Nothing to cleanup is also success
        
    except Exception as e:
        logger.error("Failed to cleanup Maya UI '{}': {}".format(ui_name, str(e)))
        return False

def log_maya_info(message):
    """
    Log an info message to the Maya utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.info(message)

def log_maya_warning(message):
    """
    Log a warning message to the Maya utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.warning(message)

def log_maya_error(message):
    """
    Log an error message to the Maya utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.error(message)

# Initialize Maya utils
try:
    if is_maya_available():
        maya_info = get_maya_build_info()
        version = maya_info.get('version', 'Unknown')
        batch_mode = maya_info.get('is_batch_mode', False)
        log_maya_info("Maya utilities initialized - Version: {}, Batch mode: {}".format(version, batch_mode))
    else:
        log_maya_warning("Maya utilities initialized without Maya environment")
except Exception as e:
    log_maya_error("Failed to initialize Maya utilities: {}".format(str(e)))

# Public API
__all__ = [
    'is_maya_available',
    'get_maya_version',
    'get_maya_build_info',
    'is_maya_batch_mode',
    'get_maya_main_window',
    'safe_maya_command',
    'show_maya_dialog',
    'show_maya_warning',
    'show_maya_error',
    'show_maya_info',
    'get_current_scene_file',
    'is_scene_modified',
    'get_maya_preferences_dir',
    'get_maya_app_dir',
    'cleanup_maya_ui',
    'log_maya_info',
    'log_maya_warning',
    'log_maya_error'
]
