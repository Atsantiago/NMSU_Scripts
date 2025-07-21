"""
Prof-Tools Assignment Tools

This module contains assignment-specific grading and evaluation tools
for Maya courses at NMSU's Creative Media Institute.
"""

from __future__ import absolute_import

# Import the lesson rubric template when Maya is available
try:
    from .lessonRubric_template import LessonRubric, create_sample_rubric
    __all__ = ['LessonRubric', 'create_sample_rubric']
except ImportError:
    # Maya not available - define empty exports
    __all__ = []

__author__ = "Alexander T. Santiago"
__version__ = "0.2.4"
