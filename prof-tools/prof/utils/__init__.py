"""
Prof-Tools Utils Module
Utility functions and helper classes for prof-tools package.

This module provides cross-platform utilities, file operations, and common
helper functions used throughout the prof-tools system.
"""

# Python 2/3 compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import logging

# Configure logging for utils module
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Utils module metadata
__version__ = "0.1.0"
__author__ = "Alexander T. Santiago - https://github.com/Atsantiago"

# Cross-platform constants
PLATFORM_WINDOWS = 'win32'
PLATFORM_MAC = 'darwin'
PLATFORM_LINUX = 'linux'

def get_platform():
    """
    Get the current platform identifier.
    
    Returns:
        str: Platform identifier ('windows', 'mac', 'linux', or 'unknown')
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
    Check if running on Windows platform.
    
    Returns:
        bool: True if Windows, False otherwise
    """
    return get_platform() == 'windows'

def is_mac():
    """
    Check if running on macOS platform.
    
    Returns:
        bool: True if macOS, False otherwise
    """
    return get_platform() == 'mac'

def is_linux():
    """
    Check if running on Linux platform.
    
    Returns:
        bool: True if Linux, False otherwise
    """
    return get_platform() == 'linux'

def safe_path_join(*paths):
    """
    Safely join path components using os.path.join with normalization.
    
    Args:
        *paths: Path components to join
        
    Returns:
        str: Normalized cross-platform path
    """
    if not paths:
        return ""
    
    try:
        path = os.path.join(*paths)
        return os.path.normpath(path)
    except Exception as e:
        logger.error("Failed to join paths {}: {}".format(paths, str(e)))
        return ""

def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to directory
        
    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            logger.debug("Created directory: {}".format(directory_path))
        return True
    except Exception as e:
        logger.error("Failed to create directory '{}': {}".format(directory_path, str(e)))
        return False

def safe_file_read(file_path, encoding='utf-8'):
    """
    Safely read a file with proper error handling.
    
    Args:
        file_path (str): Path to file to read
        encoding (str): File encoding (default: utf-8)
        
    Returns:
        str: File contents or empty string if failed
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error("Failed to read file '{}': {}".format(file_path, str(e)))
        return ""

def safe_file_write(file_path, content, encoding='utf-8'):
    """
    Safely write content to a file with proper error handling.
    
    Args:
        file_path (str): Path to file to write
        content (str): Content to write
        encoding (str): File encoding (default: utf-8)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not ensure_directory_exists(directory):
            return False
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        logger.debug("Successfully wrote file: {}".format(file_path))
        return True
    except Exception as e:
        logger.error("Failed to write file '{}': {}".format(file_path, str(e)))
        return False

def get_user_documents_path():
    """
    Get the user's Documents directory path in a cross-platform way.
    
    Returns:
        str: Path to user's Documents directory
    """
    try:
        if is_windows():
            return os.path.join(os.path.expanduser("~"), "Documents")
        elif is_mac():
            return os.path.join(os.path.expanduser("~"), "Documents")
        else:  # Linux and others
            return os.path.expanduser("~")
    except Exception as e:
        logger.error("Failed to get user documents path: {}".format(str(e)))
        return os.path.expanduser("~")

def log_utils_info(message):
    """
    Log an info message to the utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.info(message)

def log_utils_warning(message):
    """
    Log a warning message to the utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.warning(message)

def log_utils_error(message):
    """
    Log an error message to the utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.error(message)

# Initialize utils module
def _initialize_utils_module():
    """
    Initialize the utils module with platform detection and logging setup.
    """
    try:
        platform = get_platform()
        log_utils_info("Prof-Tools utils module initialized on platform: {}".format(platform))
    except Exception as e:
        log_utils_error("Failed to initialize utils module: {}".format(str(e)))
        raise

# Automatic initialization
_initialize_utils_module()

# Public API
__all__ = [
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
