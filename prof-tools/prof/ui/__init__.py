"""
Prof-Tools UI Module
User interface components for prof-tools including menu builders, dialog systems, and Maya UI integration.

This module handles all user-facing interface elements within Maya, providing a clean
and consistent interface for instructor grading tools.
"""

# Python 2/3 compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import logging

# Configure logging for UI module
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# UI module metadata - version comes from main prof module
try:
    from prof import __version__
except ImportError:
    # Fallback if prof module not available
    __version__ = "0.1.0"
__author__ = "Alexander T. Santiago - https://github.com/Atsantiago"

# UI module constants
UI_WINDOW_PREFIX = "ProfTools"
UI_MENU_NAME = "ProfTools"
UI_MENU_LABEL = "Prof-Tools"

# Maya UI availability check
def is_maya_ui_available():
    """
    Checks if Maya UI components are available in the current environment.
    
    Returns:
        bool: True if Maya UI is available, False otherwise
    """
    try:
        import maya.cmds as cmds
        import maya.mel as mel
        # Test if we can access Maya's main window
        try:
            main_window = mel.eval('global string $gMainWindow; $tmp = $gMainWindow;')
            return main_window is not None and main_window != ""
        except Exception:
            return False
    except ImportError:
        return False

def get_maya_main_window():
    """
    Gets Maya's main window for UI parenting.
    
    Returns:
        str: Maya main window name, or empty string if not available
    """
    if not is_maya_ui_available():
        return ""
    
    try:
        import maya.mel as mel
        return mel.eval('global string $gMainWindow; $tmp = $gMainWindow;')
    except Exception:
        return ""

def cleanup_existing_ui(window_name):
    """
    Safely cleanup existing UI elements with the given name.
    
    Args:
        window_name (str): Name of the window/UI element to cleanup
    """
    if not is_maya_ui_available():
        return
    
    try:
        import maya.cmds as cmds
        
        # Check if it's a window
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)
            logger.debug("Cleaned up existing window: {}".format(window_name))
        
        # Check if it's a menu
        elif cmds.menu(window_name, exists=True):
            cmds.deleteUI(window_name)
            logger.debug("Cleaned up existing menu: {}".format(window_name))
            
    except Exception as e:
        logger.warning("Failed to cleanup UI element '{}': {}".format(window_name, str(e)))

def log_ui_info(message):
    """
    Logs an info message to the UI logger.
    
    Args:
        message (str): Message to log
    """
    logger.info(message)

def log_ui_warning(message):
    """
    Logs a warning message to the UI logger.
    
    Args:
        message (str): Message to log
    """
    logger.warning(message)

def log_ui_error(message):
    """
    Logs an error message to the UI logger.
    
    Args:
        message (str): Message to log
    """
    logger.error(message)

def get_ui_constants():
    """
    Returns UI constants for use by UI components.
    
    Returns:
        dict: Dictionary containing UI constants
    """
    return {
        'window_prefix': UI_WINDOW_PREFIX,
        'menu_name': UI_MENU_NAME,
        'menu_label': UI_MENU_LABEL,
        'version': __version__,
        'author': __author__
    }

# Cross-platform UI utilities
def is_windows():
    """
    Checks if running on Windows platform.
    
    Returns:
        bool: True if Windows, False otherwise
    """
    return sys.platform.startswith('win')

def is_mac():
    """
    Checks if running on macOS platform.
    
    Returns:
        bool: True if macOS, False otherwise
    """
    return sys.platform.startswith('darwin')

def is_linux():
    """
    Checks if running on Linux platform.
    
    Returns:
        bool: True if Linux, False otherwise
    """
    return sys.platform.startswith('linux')

def get_platform_info():
    """
    Returns platform information for UI optimization.
    
    Returns:
        dict: Dictionary containing platform information
    """
    return {
        'platform': sys.platform,
        'is_windows': is_windows(),
        'is_mac': is_mac(),
        'is_linux': is_linux()
    }

# Module initialization
def _initialize_ui_module():
    """
    Initialize the UI module with necessary checks and setup.
    This function is called automatically when the module is imported.
    """
    try:
        # Check if Maya UI is available
        if is_maya_ui_available():
            log_ui_info("Maya UI environment detected and available")
        else:
            log_ui_warning("Maya UI environment not available - some features may be limited")
        
        # Log platform information
        platform_info = get_platform_info()
        log_ui_info("UI module initialized on platform: {}".format(platform_info['platform']))
        
        # Log successful initialization
        log_ui_info("Prof-Tools UI module initialized successfully (v{})".format(__version__))
        
    except Exception as e:
        log_ui_error("Failed to initialize UI module: {}".format(str(e)))
        raise

# Automatic initialization when module is imported
_initialize_ui_module()

# Import centralized version from package root
try:
    from prof import __version__
except ImportError:
    # Fallback if prof module not available
    __version__ = "0.1.0"

# Try to import update dialog module for UI functionality
try:
    from . import update_dialog
except ImportError:
    update_dialog = None
    logger.warning("Update dialog module not available")

# Make key functions available at package level
__all__ = [
    'is_maya_ui_available',
    'get_maya_main_window', 
    'cleanup_existing_ui',
    'get_ui_constants',
    'get_platform_info',
    'log_ui_info',
    'log_ui_warning',
    'log_ui_error',
    'update_dialog'  # Add update dialog module
]
