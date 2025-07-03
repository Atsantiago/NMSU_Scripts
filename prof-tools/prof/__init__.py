"""
Prof-Tools for Maya - Instructor Grading and Utility Tools

A comprehensive suite of tools for grading and managing Maya assignments.

Defines core metadata, versioning, and compatibility checks for the Prof-Tools Maya instructor toolkit.
"""

# Python 2/3 compatibility imports
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
import logging

# Python version compatibility check
if sys.version_info.major < 3:
    user_version = "{}.{}.{}".format(
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro
    )
    error = (
        "Incompatible Python Version. Expected to find 3+. "
        "Found version: " + user_version + ".\n"
        "For Python 2, use an older version of Prof-Tools. "
        "(e.g. older Maya versions)\n"
    )
    raise ImportError(error)

# Package metadata and versioning
__version_tuple__ = (0, 1, 0)      # MAJOR, MINOR, PATCH
__version_suffix__ = ''            # e.g. '-alpha', '-beta', '-rc1'
__version__ = '.'.join(map(str, __version_tuple__)) + __version_suffix__

__title__ = 'Prof-Tools'
__author__ = 'Alexander T. Santiago - https://github.com/Atsantiago'
__description__ = 'Maya instructor tools for grading and assignment management'
__license__ = 'MIT'
__url__ = 'https://github.com/Atsantiago/NMSU_Scripts'

# Public API
__all__ = [
    '__version__',
    '__version_tuple__',
    '__title__',
    '__author__',
    '__description__',
    '__license__',
    '__url__',
    'get_version',
    'get_version_info',
    'get_package_path',
    'is_maya_available'
]

# Configure package logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_version():
    """
    Returns the current version string.
    Returns:
        str: Version string (e.g. "0.1.0")
    """
    return __version__

def get_version_info():
    """
    Returns detailed version and package information.
    Returns:
        dict: Dictionary containing version metadata
    """
    return {
        'version': __version__,
        'version_tuple': __version_tuple__,
        'title': __title__,
        'author': __author__,
        'description': __description__,
        'license': __license__,
        'url': __url__
    }

def get_package_path():
    """
    Returns the absolute path to this package directory.
    Returns:
        str: Path to the prof package directory
    """
    return os.path.dirname(os.path.abspath(__file__))

def is_maya_available():
    """
    Checks if Maya Python modules are available in the current environment.
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
    Gets the current Maya version if available.
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

def get_python_version():
    """
    Gets the current Python version information.
    Returns:
        dict: Dictionary containing Python version info
    """
    return {
        'version': sys.version,
        'version_info': sys.version_info,
        'major': sys.version_info.major,
        'minor': sys.version_info.minor,
        'micro': sys.version_info.micro
    }

def check_python_compatibility():
    """
    Checks if the current Python version is compatible with prof-tools.
    Returns:
        bool: True if compatible, False otherwise
    """
    if sys.version_info.major < 3:
        user_version = "{}.{}.{}".format(
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro
        )
        error_msg = (
            "Incompatible Python Version. Expected Python 3+. "
            "Found: " + user_version + "."
        )
        logger.error(error_msg)
        return False
    return True

def check_maya_compatibility():
    """
    Checks if Maya is available and compatible.
    Returns:
        bool: True if Maya is available and compatible, False otherwise
    """
    if not is_maya_available():
        logger.warning(
            "Maya Python modules not available. Some features may be limited."
        )
        return False
    try:
        maya_version = get_maya_version()
        if maya_version:
            logger.info("Maya version detected: {}".format(maya_version))
            return True
        else:
            logger.warning("Could not determine Maya version.")
            return False
    except Exception as e:
        logger.error("Error checking Maya compatibility: {}".format(e))
        return False

def get_system_info():
    """
    Returns system information for debugging and support.
    Returns:
        dict: Dictionary containing system information
    """
    return {
        'platform': sys.platform,
        'python_version': get_python_version(),
        'maya_version': get_maya_version(),
        'maya_available': is_maya_available(),
        'package_path': get_package_path(),
        'prof_tools_version': get_version()
    }

def _initialize_package():
    """
    Initialize the prof-tools package with compatibility checks.
    Called automatically on import.
    """
    try:
        if not check_python_compatibility():
            raise ImportError("Python version incompatibility detected")
        check_maya_compatibility()
        logger.info("Prof-Tools package initialized successfully (v{})".format(__version__))
    except Exception as e:
        logger.error("Failed to initialize prof-tools package: {}".format(e))
        raise

# Automatic initialization when package is imported
_initialize_package()
