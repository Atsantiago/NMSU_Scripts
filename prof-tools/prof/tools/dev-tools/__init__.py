"""
Developer Tools for Prof-Tools

This package contains tools and utilities specifically for Prof-Tools development,
testing, and maintenance. These tools are separate from the main user-facing
functionality.

Contents:
- dev_prefs: Developer preferences and settings management
- silent_updater: Background update checking system
- version_utils_new: Enhanced version utilities (development)

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function

# Import main developer tools for easy access
try:
    from .dev_prefs import get_prefs, is_dev_mode_enabled
    from .silent_updater import configure_auto_updates, silently_check_for_updates
except ImportError:
    # Handle case where files haven't been moved yet
    pass

__all__ = [
    'get_prefs',
    'is_dev_mode_enabled', 
    'configure_auto_updates',
    'silently_check_for_updates'
]
