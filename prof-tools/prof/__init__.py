"""
Prof-Tools for Maya - Instructor Grading and Utility Tools
A comprehensive suite of tools for grading and managing Maya assignments.

Python 2/3 compatibility patterns following GT-Tools MIT license approach.
"""

# Python 2/3 compatibility imports
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys

# Python version compatibility check (following GT-Tools pattern)
if sys.version_info.major < 3:
    # String formatting for this error should remain compatible to Python 2 to guarantee feedback
    user_version = "{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    error = "Incompatible Python Version. Expected to find 3+. Found version: " + user_version
    error += " For Python 2, use an older version of Prof-Tools. (e.g. older Maya versions)\n"
    raise ImportError(error)

# Package metadata and versioning
__version_tuple__ = (0, 1, 0)   # MAJOR, MINOR, PATCH
__version_suffix__ = ''         # e.g. '-alpha', '-beta', '-rc1'
__version__ = '.'.join(map(str, __version_tuple__)) + __version_suffix__

__title__ = 'Prof-Tools'
__author__ = 'Alexander T. Santiago - https://github.com/Atsantiago'
__description__ = 'Maya instructor tools for grading and assignment management'
__license__ = 'MIT'

# Package metadata
__all__ = [
    '__version__',
    '__version_tuple__',
    '__title__',
    '__author__',
    '__description__',
    '__license__'
]

def get_version():
    """
    Returns the current version string
    
    Returns:
        str: Version string (e.g. "0.1.0")
    """
    return __version__

def get_version_info():
    """
    Returns detailed version information
    
    Returns:
        dict: Dictionary containing version metadata
    """
    return {
        'version': __version__,
        'version_tuple': __version_tuple__,
        'title': __title__,
        'author': __author__,
        'description': __description__,
        'license': __license__
    }

def get_package_path():
    """
    Returns the path to this package
    
    Returns:
        str: Path to the prof package directory
    """
    import os
    return os.path.dirname(__file__)

# Initialize package logging (following GT-Tools pattern)
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
