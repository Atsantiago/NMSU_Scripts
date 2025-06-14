"""
system_utils.py - Cross-platform OS detection
"""

import sys

def is_windows():
    return sys.platform.startswith("win32")

def is_macos():
    return sys.platform.startswith("darwin")

def is_linux():
    return sys.platform.startswith("linux")
