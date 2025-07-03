"""
Prof-Tools Utils Module

Utility functions and helper classes for prof-tools package. Provides
cross-platform utilities, file operations, and common helper functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import logging

# Import centralized version from package root
from prof import __version__

# Configure logging for utils module
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Module metadata
__author__ = "Alexander T. Santiago - https://github.com/Atsantiago"

# Cross-platform constants
PLATFORM_WINDOWS = 'win32'
PLATFORM_MAC     = 'darwin'
PLATFORM_LINUX   = 'linux'

def get_platform():
    """
    Get the current platform identifier.
    Returns:
        str: 'windows', 'mac', 'linux', or 'unknown'
    """
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return 'unknown'

def is_windows():
    """
    Check if running on Windows.
    Returns:
        bool: True if Windows, else False
    """
    return get_platform() == 'windows'

def is_mac():
    """
    Check if running on macOS.
    Returns:
        bool: True if macOS, else False
    """
    return get_platform() == 'mac'

def is_linux():
    """
    Check if running on Linux.
    Returns:
        bool: True if Linux, else False
    """
    return get_platform() == 'linux'

def safe_path_join(*paths):
    """
    Safely join and normalize path components.
    Args:
        *paths: Path segments
    Returns:
        str: Normalized path or empty string on failure
    """
    if not paths:
        return ""
    try:
        return os.path.normpath(os.path.join(*paths))
    except Exception as e:
        logger.error("Failed to join paths %s: %s", paths, e)
        return ""

def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    Args:
        directory_path (str): Directory path
    Returns:
        bool: True if exists or created, else False
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            logger.debug("Created directory: %s", directory_path)
        return True
    except Exception as e:
        logger.error("Failed to create directory '%s': %s", directory_path, e)
        return False

def safe_file_read(file_path, encoding='utf-8'):
    """
    Read a file safely, returning its content or empty string.
    Args:
        file_path (str): Path to file
        encoding (str): File encoding
    Returns:
        str: File contents or '' on error
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error("Failed to read file '%s': %s", file_path, e)
        return ""

def safe_file_write(file_path, content, encoding='utf-8'):
    """
    Write content to a file safely.
    Args:
        file_path (str): File path
        content (str): Text to write
        encoding (str): File encoding
    Returns:
        bool: True on success, else False
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not ensure_directory_exists(directory):
            return False
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        logger.debug("Wrote file: %s", file_path)
        return True
    except Exception as e:
        logger.error("Failed to write file '%s': %s", file_path, e)
        return False

def get_user_documents_path():
    """
    Get the user's Documents directory path.
    Returns:
        str: Path to Documents or home folder on Linux
    """
    try:
        if is_windows() or is_mac():
            return os.path.join(os.path.expanduser("~"), "Documents")
        else:
            return os.path.expanduser("~")
    except Exception as e:
        logger.error("Failed to get user documents path: %s", e)
        return os.path.expanduser("~")

def log_utils_info(message):
    """
    Log an info message to the utils logger.
    Args:
        message (str): Message text
    """
    logger.info(message)

def log_utils_warning(message):
    """
    Log a warning message to the utils logger.
    Args:
        message (str): Message text
    """
    logger.warning(message)

def log_utils_error(message):
    """
    Log an error message to the utils logger.
    Args:
        message (str): Message text
    """
    logger.error(message)

def _initialize_utils_module():
    """
    Module initialization: log platform info.
    """
    try:
        platform = get_platform()
        log_utils_info("Prof-Tools utils initialized on: {}".format(platform))
    except Exception as e:
        log_utils_error("Utils initialization failed: {}".format(e))
        raise

# Automatically run initialization on import
_initialize_utils_module()

# Public API
__all__ = [
    '__version__',          # Central version from prof/__init__.py
    '__author__',
    'get_platform',
    'is_windows',
    'is_mac',
    'is_linux',
    'safe_path_join',
    'ensure_directory_exists',
    'safe_file_read',
    'safe_file_write',
    'get_user_documents_path',
    'log_utils_info',
    'log_utils_warning',
    'log_utils_error'
]
