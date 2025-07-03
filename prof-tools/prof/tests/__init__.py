"""
Prof-Tools Tests Module
Unit tests and testing utilities for prof-tools package.

This module provides testing framework integration and utilities for
validating prof-tools functionality in Maya environments.
"""

# Python 2/3 compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import unittest
import logging

# Configure logging for tests module
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Tests module metadata
__version__ = "0.1.0"
__author__ = "Alexander T. Santiago - https://github.com/Atsantiago"

def is_maya_available():
    """
    Check if Maya is available for testing.
    
    Returns:
        bool: True if Maya is available, False otherwise
    """
    try:
        import maya.cmds
        return True
    except ImportError:
        return False

def get_test_data_path():
    """
    Get the path to test data directory.
    
    Returns:
        str: Path to test data directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'data')

def ensure_test_data_exists():
    """
    Ensure test data directory exists.
    
    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    try:
        test_data_path = get_test_data_path()
        if not os.path.exists(test_data_path):
            os.makedirs(test_data_path)
            logger.info("Created test data directory: {}".format(test_data_path))
        return True
    except Exception as e:
        logger.error("Failed to create test data directory: {}".format(str(e)))
        return False

class ProfToolsTestCase(unittest.TestCase):
    """
    Base test case class for prof-tools tests.
    Provides common setup and utilities for testing prof-tools functionality.
    """
    
    def setUp(self):
        """Set up test case with common initialization."""
        self.maya_available = is_maya_available()
        self.test_data_path = get_test_data_path()
        ensure_test_data_exists()
    
    def tearDown(self):
        """Clean up after test case."""
        pass
    
    def skipIfMayaNotAvailable(self):
        """Skip test if Maya is not available."""
        if not self.maya_available:
            self.skipTest("Maya not available for testing")
    
    def assertMayaAvailable(self):
        """Assert that Maya is available for testing."""
        self.assertTrue(self.maya_available, "Maya must be available for this test")

def run_all_tests():
    """
    Run all prof-tools tests.
    
    Returns:
        unittest.TestResult: Test results
    """
    try:
        # Discover tests in this directory
        current_dir = os.path.dirname(__file__)
        suite = unittest.TestLoader().discover(current_dir, pattern='test_*.py')
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        logger.info("Test run completed. Tests run: {}, Failures: {}, Errors: {}".format(
            result.testsRun, len(result.failures), len(result.errors)
        ))
        
        return result
        
    except Exception as e:
        logger.error("Failed to run tests: {}".format(str(e)))
        return None

def run_maya_tests():
    """
    Run only tests that require Maya.
    
    Returns:
        unittest.TestResult: Test results
    """
    if not is_maya_available():
        logger.warning("Maya not available - skipping Maya-specific tests")
        return None
    
    try:
        # This would discover and run only Maya-specific tests
        # Implementation would filter for tests that inherit from ProfToolsTestCase
        # and use Maya functionality
        current_dir = os.path.dirname(__file__)
        suite = unittest.TestLoader().discover(current_dir, pattern='test_maya_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        logger.info("Maya test run completed. Tests run: {}, Failures: {}, Errors: {}".format(
            result.testsRun, len(result.failures), len(result.errors)
        ))
        
        return result
        
    except Exception as e:
        logger.error("Failed to run Maya tests: {}".format(str(e)))
        return None

def log_tests_info(message):
    """
    Log an info message to the tests logger.
    
    Args:
        message (str): Message to log
    """
    logger.info(message)

def log_tests_warning(message):
    """
    Log a warning message to the tests logger.
    
    Args:
        message (str): Message to log
    """
    logger.warning(message)

def log_tests_error(message):
    """
    Log an error message to the tests logger.
    
    Args:
        message (str): Message to log
    """
    logger.error(message)

# Initialize tests module
def _initialize_tests_module():
    """
    Initialize the tests module with environment setup.
    """
    try:
        maya_status = "available" if is_maya_available() else "not available"
        log_tests_info("Prof-Tools tests module initialized - Maya: {}".format(maya_status))
        
        # Ensure test data directory exists
        ensure_test_data_exists()
        
    except Exception as e:
        log_tests_error("Failed to initialize tests module: {}".format(str(e)))
        raise

# Automatic initialization
_initialize_tests_module()

# Public API
__all__ = [
    'ProfToolsTestCase',
    'is_maya_available',
    'get_test_data_path',
    'ensure_test_data_exists',
    'run_all_tests',
    'run_maya_tests',
    'log_tests_info',
    'log_tests_warning',
    'log_tests_error'
]
