"""
Prof-Tools Tools Module
Grading logic and rubric systems for prof-tools package.

This module contains the core grading engine, rubric configurations,
and assignment-specific grading tools for Maya instructor workflows.
"""

# Python 2/3 compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

# Configure logging for tools module
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Tools module metadata
__version__ = "0.1.0"
__author__ = "Alexander T. Santiago - https://github.com/Atsantiago"

# Module constants
FDMA_1510_COURSE_CODE = "fdma1510"
FDMA_2530_COURSE_CODE = "fdma2530"

# Course information
COURSE_INFO = {
    FDMA_1510_COURSE_CODE: {
        'name': 'FDMA 1510 - Intro 3D Animation',
        'description': 'Basic 3D modeling and animation projects',
        'assignments': []  # Will be populated as assignments are added
    },
    FDMA_2530_COURSE_CODE: {
        'name': 'FDMA 2530 - Modeling',
        'description': 'Advanced character and environment modeling',
        'assignments': []  # Will be populated as assignments are added
    }
}

def get_course_info(course_code):
    """
    Get information about a specific course.
    
    Args:
        course_code (str): Course code (e.g., 'fdma1510', 'fdma2530')
        
    Returns:
        dict: Course information or empty dict if not found
    """
    return COURSE_INFO.get(course_code, {})

def get_available_courses():
    """
    Get list of available course codes.
    
    Returns:
        list: List of available course codes
    """
    return list(COURSE_INFO.keys())

def get_course_display_name(course_code):
    """
    Get display name for a course.
    
    Args:
        course_code (str): Course code
        
    Returns:
        str: Course display name or empty string if not found
    """
    course_info = get_course_info(course_code)
    return course_info.get('name', '')

def is_valid_course_code(course_code):
    """
    Check if a course code is valid.
    
    Args:
        course_code (str): Course code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return course_code in COURSE_INFO

def log_tools_info(message):
    """
    Log an info message to the tools logger.
    
    Args:
        message (str): Message to log
    """
    logger.info(message)

def log_tools_warning(message):
    """
    Log a warning message to the tools logger.
    
    Args:
        message (str): Message to log
    """
    logger.warning(message)

def log_tools_error(message):
    """
    Log an error message to the tools logger.
    
    Args:
        message (str): Message to log
    """
    logger.error(message)

# Initialize tools module
def _initialize_tools_module():
    """
    Initialize the tools module with course setup and logging.
    """
    try:
        course_count = len(COURSE_INFO)
        log_tools_info("Prof-Tools tools module initialized with {} courses".format(course_count))
        
        # Log available courses
        for code, info in COURSE_INFO.items():
            log_tools_info("Loaded course: {} - {}".format(code, info['name']))
            
    except Exception as e:
        log_tools_error("Failed to initialize tools module: {}".format(str(e)))
        raise

# Automatic initialization
_initialize_tools_module()

# Public API
__all__ = [
    'FDMA_1510_COURSE_CODE',
    'FDMA_2530_COURSE_CODE',
    'COURSE_INFO',
    'get_course_info',
    'get_available_courses',
    'get_course_display_name',
    'is_valid_course_code',
    'log_tools_info',
    'log_tools_warning',
    'log_tools_error'
]
