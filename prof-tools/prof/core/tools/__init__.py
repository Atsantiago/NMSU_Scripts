"""
Core Tools Package

Specialized tools and utilities for Prof-Tools development and advanced functionality.
This package contains tools that extend the core functionality with specialized features.

Contents:
- dev_prefs: Developer preferences and settings management
- silent_updater: Background update checking system  
- version_utils_new: Experimental version utilities

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function

# Import main developer tools for easy access
try:
    from .dev_prefs import get_prefs, is_dev_mode_enabled, should_show_dev_features
    from .silent_updater import configure_auto_updates, silently_check_for_updates, initialize_silent_updates
except ImportError:
    # Handle case where tools aren't available yet
    pass

__all__ = [
    'get_prefs',
    'is_dev_mode_enabled',
    'should_show_dev_features',
    'configure_auto_updates',
    'silently_check_for_updates',
    'initialize_silent_updates'
]
