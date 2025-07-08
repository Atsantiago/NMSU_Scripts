"""
FDMA 2530 System Utilities
=================================

Cross-platform OS detection utilities for Maya shelf systems.
Optimized for speed and simplicity across all Maya versions (2016-2025+).

Part of the fdma_shelf package ecosystem.
"""

import sys
import os
import json

# ============================================================================
# VERSION INFORMATION
# ============================================================================

try:
    from .utils.version_utils import get_fdma2530_version
    __version__ = get_fdma2530_version()
except (ImportError, Exception):
    __version__ = "unknown"

# ============================================================================
# CORE OS DETECTION FUNCTIONS
# ============================================================================

def is_windows():
    """
    Check if running on Windows.
    
    Returns:
        bool: True if Windows, False otherwise
    """
    return sys.platform.startswith("win")

def is_macos():
    """
    Check if running on macOS.
    
    Returns:
        bool: True if macOS, False otherwise
    """
    return sys.platform.startswith("darwin")

def is_linux():
    """
    Check if running on Linux.
    
    Returns:
        bool: True if Linux, False otherwise
    """
    return sys.platform.startswith("linux")

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_os_name():
    """
    Get the operating system name as a string.
    
    Returns:
        str: 'windows', 'macos', 'linux', or 'unknown'
    """
    if is_windows():
        return 'windows'
    elif is_macos():
        return 'macos'
    elif is_linux():
        return 'linux'
    else:
        return 'unknown'

def get_platform_info():
    """
    Get basic platform information for diagnostics.
    
    Returns:
        dict: Platform information including OS name and Python version
    """
    return {
        'os_name': get_os_name(),
        'platform': sys.platform,
        'python_version': "{}.{}.{}".format(*sys.version_info[:3])
    }

# ============================================================================
# MODULE INFORMATION
# ============================================================================

# Display module info when run directly
if __name__ == "__main__":
    print("FDMA 2530 System Utilities v{}".format(__version__))
    info = get_platform_info()
    print("Platform: {} ({})".format(info['os_name'].title(), info['platform']))
    print("Python: {}".format(info['python_version']))
