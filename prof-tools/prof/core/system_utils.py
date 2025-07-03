"""
Prof-Tools System Utilities
Cross-platform system utilities for prof-tools package.

This module provides system-level utilities for file operations, path handling,
and environment detection across Windows, macOS, and Linux platforms.
"""

# Python 2/3 compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import platform
import logging
from prof.utils import (
    get_platform, is_windows, is_mac, is_linux,
    safe_path_join, ensure_directory_exists,
    safe_file_read, safe_file_write,
    get_user_documents_path
)

# Configure logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# System constants
MAYA_FOLDER_NAME = "maya"
MAYA_MODULES_FOLDER = "modules"
MAYA_PREFS_FOLDER = "prefs"
MAYA_SCRIPTS_FOLDER = "scripts"
USERSETUP_FILE_NAME = "userSetup.mel"

def get_system_info():
    """
    Get comprehensive system information.
    
    Returns:
        dict: Dictionary containing system information
    """
    try:
        return {
            'platform': get_platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'is_windows': is_windows(),
            'is_mac': is_mac(),
            'is_linux': is_linux()
        }
    except Exception as e:
        logger.error("Failed to get system info: {}".format(str(e)))
        return {}

def get_maya_documents_path():
    """
    Get the Maya documents directory path for the current platform.
    
    Returns:
        str: Path to Maya documents directory
    """
    try:
        documents_path = get_user_documents_path()
        return safe_path_join(documents_path, MAYA_FOLDER_NAME)
    except Exception as e:
        logger.error("Failed to get Maya documents path: {}".format(str(e)))
        return ""

def get_maya_modules_path():
    """
    Get the Maya modules directory path.
    
    Returns:
        str: Path to Maya modules directory
    """
    try:
        maya_docs = get_maya_documents_path()
        return safe_path_join(maya_docs, MAYA_MODULES_FOLDER)
    except Exception as e:
        logger.error("Failed to get Maya modules path: {}".format(str(e)))
        return ""

def get_maya_scripts_path():
    """
    Get the Maya scripts directory path.
    
    Returns:
        str: Path to Maya scripts directory
    """
    try:
        maya_docs = get_maya_documents_path()
        prefs_path = safe_path_join(maya_docs, MAYA_PREFS_FOLDER)
        return safe_path_join(prefs_path, MAYA_SCRIPTS_FOLDER)
    except Exception as e:
        logger.error("Failed to get Maya scripts path: {}".format(str(e)))
        return ""

def get_usersetup_mel_path():
    """
    Get the path to the userSetup.mel file.
    
    Returns:
        str: Path to userSetup.mel file
    """
    try:
        scripts_path = get_maya_scripts_path()
        return safe_path_join(scripts_path, USERSETUP_FILE_NAME)
    except Exception as e:
        logger.error("Failed to get userSetup.mel path: {}".format(str(e)))
        return ""

def ensure_maya_directories():
    """
    Ensure all necessary Maya directories exist.
    
    Returns:
        bool: True if all directories exist or were created, False otherwise
    """
    try:
        directories = [
            get_maya_documents_path(),
            get_maya_modules_path(),
            get_maya_scripts_path()
        ]
        
        success = True
        for directory in directories:
            if directory and not ensure_directory_exists(directory):
                success = False
        
        return success
        
    except Exception as e:
        logger.error("Failed to ensure Maya directories: {}".format(str(e)))
        return False

def read_usersetup_mel():
    """
    Read the contents of userSetup.mel file.
    
    Returns:
        str: Contents of userSetup.mel file, or empty string if failed
    """
    try:
        usersetup_path = get_usersetup_mel_path()
        if not usersetup_path or not os.path.exists(usersetup_path):
            return ""
        
        return safe_file_read(usersetup_path)
        
    except Exception as e:
        logger.error("Failed to read userSetup.mel: {}".format(str(e)))
        return ""

def write_usersetup_mel(content):
    """
    Write content to userSetup.mel file.
    
    Args:
        content (str): Content to write to userSetup.mel
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        usersetup_path = get_usersetup_mel_path()
        if not usersetup_path:
            return False
        
        # Ensure scripts directory exists
        scripts_dir = os.path.dirname(usersetup_path)
        if not ensure_directory_exists(scripts_dir):
            return False
        
        return safe_file_write(usersetup_path, content)
        
    except Exception as e:
        logger.error("Failed to write userSetup.mel: {}".format(str(e)))
        return False

def backup_usersetup_mel():
    """
    Create a backup of the userSetup.mel file.
    
    Returns:
        str: Path to backup file, or empty string if failed
    """
    try:
        usersetup_path = get_usersetup_mel_path()
        if not usersetup_path or not os.path.exists(usersetup_path):
            return ""
        
        # Create backup filename with timestamp
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = "userSetup_backup_{}.mel".format(timestamp)
        backup_path = safe_path_join(os.path.dirname(usersetup_path), backup_name)
        
        # Read original content and write to backup
        content = safe_file_read(usersetup_path)
        if content and safe_file_write(backup_path, content):
            logger.info("Created userSetup.mel backup: {}".format(backup_path))
            return backup_path
        
        return ""
        
    except Exception as e:
        logger.error("Failed to backup userSetup.mel: {}".format(str(e)))
        return ""

def get_environment_variables():
    """
    Get relevant environment variables for Maya and system information.
    
    Returns:
        dict: Dictionary of environment variables
    """
    try:
        env_vars = {}
        
        # Common environment variables
        vars_to_check = [
            'MAYA_APP_DIR',
            'MAYA_MODULE_PATH',
            'MAYA_SCRIPT_PATH',
            'PYTHONPATH',
            'PATH',
            'HOME',
            'USERPROFILE',
            'TEMP',
            'TMP'
        ]
        
        for var in vars_to_check:
            value = os.environ.get(var)
            if value is not None:
                env_vars[var] = value
        
        return env_vars
        
    except Exception as e:
        logger.error("Failed to get environment variables: {}".format(str(e)))
        return {}

def check_file_permissions(file_path):
    """
    Check file permissions for read/write access.
    
    Args:
        file_path (str): Path to file to check
        
    Returns:
        dict: Dictionary with permission information
    """
    try:
        if not os.path.exists(file_path):
            return {
                'exists': False,
                'readable': False,
                'writable': False,
                'executable': False
            }
        
        return {
            'exists': True,
            'readable': os.access(file_path, os.R_OK),
            'writable': os.access(file_path, os.W_OK),
            'executable': os.access(file_path, os.X_OK)
        }
        
    except Exception as e:
        logger.error("Failed to check file permissions for '{}': {}".format(file_path, str(e)))
        return {
            'exists': False,
            'readable': False,
            'writable': False,
            'executable': False,
            'error': str(e)
        }

def log_system_info(message):
    """
    Log an info message to the system utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.info(message)

def log_system_warning(message):
    """
    Log a warning message to the system utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.warning(message)

def log_system_error(message):
    """
    Log an error message to the system utils logger.
    
    Args:
        message (str): Message to log
    """
    logger.error(message)

# Initialize system utils
try:
    system_info = get_system_info()
    log_system_info("System utilities initialized on {} {}".format(
        system_info.get('system', 'Unknown'),
        system_info.get('release', '')
    ))
except Exception as e:
    log_system_error("Failed to initialize system utilities: {}".format(str(e)))
    raise

# Public API
__all__ = [
    'get_system_info',
    'get_maya_documents_path',
    'get_maya_modules_path', 
    'get_maya_scripts_path',
    'get_usersetup_mel_path',
    'ensure_maya_directories',
    'read_usersetup_mel',
    'write_usersetup_mel',
    'backup_usersetup_mel',
    'get_environment_variables',
    'check_file_permissions',
    'log_system_info',
    'log_system_warning',
    'log_system_error'
]
