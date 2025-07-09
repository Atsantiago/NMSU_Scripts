"""
Prof-Tools Core Module
Core functionality for prof-tools including installation, setup, and system utilities.
"""

# Python 2/3 compatibility imports
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import logging

# Configure logging for core module
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Core module metadata - version comes from main prof module
try:
    from prof import __version__
except ImportError:
    # Fallback if prof module not available
    __version__ = "0.1.0"
    
__author__ = "Alexander T. Santiago - https://github.com/Atsantiago"

# Module constants following GT-Tools patterns
PACKAGE_NAME = "prof-tools"
PACKAGE_MAIN_MODULE = "prof"
PACKAGE_ENTRY_LINE = 'python("import prof.ui.builder as _p; _p.build_menu()");'

# Cross-platform path constants
DOCUMENTS_FOLDER_NAME = "Documents"
MAYA_FOLDER_NAME = "maya"
PREFS_FOLDER_NAME = "prefs"
SCRIPTS_FOLDER_NAME = "scripts"
USERSETUP_FILE_NAME = "userSetup.mel"

# Installation constants
INSTALL_DIRECTORY_NAME = "prof-tools"
INSTALL_PACKAGE_NAME = "prof"

def get_core_version():
    """
    Returns the core module version string
    
    Returns:
        str: Core module version
    """
    return __version__

def get_package_constants():
    """
    Returns package constants for installation and setup
    
    Returns:
        dict: Dictionary containing package constants
    """
    return {
        'package_name': PACKAGE_NAME,
        'main_module': PACKAGE_MAIN_MODULE,
        'entry_line': PACKAGE_ENTRY_LINE,
        'install_dir': INSTALL_DIRECTORY_NAME,
        'install_package': INSTALL_PACKAGE_NAME
    }

def is_maya_available():
    """
    Checks if Maya is available in the current environment
    
    Returns:
        bool: True if Maya is available, False otherwise
    """
    try:
        import maya.cmds
        return True
    except ImportError:
        return False

def get_maya_version():
    """
    Gets the current Maya version if available
    
    Returns:
        str: Maya version string, or empty string if not available
    """
    if not is_maya_available():
        return ""
    
    try:
        import maya.cmds as cmds
        return cmds.about(version=True)
    except Exception:
        return ""

def log_info(msg):
    """
    Logs an info message to the core logger
    
    Args:
        msg (str): Message to log
    """
    logger.info(msg)

def log_warning(msg):
    """
    Logs a warning message to the core logger
    
    Args:
        msg (str): Message to log
    """
    logger.warning(msg)

def log_error(msg):
    """
    Logs an error message to the core logger
    
    Args:
        msg (str): Message to log
    """
    logger.error(msg)

# Python version compatibility check (following GT-Tools pattern)
def check_python_compatibility():
    """
    Checks if the current Python version is compatible with prof-tools
    
    Returns:
        bool: True if compatible, False otherwise
    """
    if sys.version_info.major < 3:
        user_version = "{}.{}.{}".format(
            sys.version_info.major, 
            sys.version_info.minor, 
            sys.version_info.micro
        )
        error_msg = "Incompatible Python Version. Expected Python 3+. Found: {}".format(user_version)
        error_msg += "\nFor Python 2 support, use an older version of Prof-Tools."
        log_error(error_msg)
        return False
    return True

# Initialize core module
try:
    if not check_python_compatibility():
        raise ImportError("Python version incompatibility detected")
    log_info("Prof-Tools core module initialized successfully")
except Exception as e:
    log_error("Failed to initialize prof-tools core module: {}".format(str(e)))
    raise
