"""
Prof-Tools Tests Module

Unit tests and testing utilities for prof-tools package. Provides
testing framework integration and utilities for validating prof-tools
functionality in Maya environments.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import unittest
import logging

# Import centralized version from package root
from prof import __version__

# Configure logging for tests module
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Module metadata
__author__ = "Alexander T. Santiago - https://github.com/Atsantiago"

def is_maya_available():
    """
    Check if Maya is available for testing.
    Returns:
        bool: True if Maya modules can be imported, False otherwise
    """
    try:
        import maya.cmds
        return True
    except ImportError:
        return False

def get_test_data_path():
    """
    Get the path to the test data directory.
    Returns:
        str: Path to test data directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'data')

def ensure_test_data_exists():
    """
    Ensure the test data directory exists, creating it if necessary.
    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    try:
        test_data_path = get_test_data_path()
        if not os.path.exists(test_data_path):
            os.makedirs(test_data_path)
            logger.info("Created test data directory: %s", test_data_path)
        return True
    except Exception as e:
        logger.error("Failed to create test data directory: %s", e)
        return False

class ProfToolsTestCase(unittest.TestCase):
    """
    Base test case class for prof-tools tests. Provides common setup
    and utilities for testing prof-tools functionality.
    """

    def setUp(self):
        """Initialize test case environment."""
        self.maya_available = is_maya_available()
        self.test_data_path = get_test_data_path()
        ensure_test_data_exists()

    def tearDown(self):
        """Clean up after test."""
        pass

    def skipIfMayaNotAvailable(self):
        """Skip test if Maya is not available."""
        if not self.maya_available:
            self.skipTest("Maya not available for testing")

    def assertMayaAvailable(self):
        """Assert that Maya is available for this test."""
        self.assertTrue(self.maya_available, "Maya must be available for this test")

def run_all_tests():
    """
    Discover and run all prof-tools tests in this directory.
    Returns:
        unittest.TestResult: Test results object
    """
    try:
        current_dir = os.path.dirname(__file__)
        suite = unittest.TestLoader().discover(current_dir, pattern='test_*.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        logger.info(
            "Test run completed. Tests run: %d, Failures: %d, Errors: %d",
            result.testsRun, len(result.failures), len(result.errors)
        )
        return result
    except Exception as e:
        logger.error("Failed to run tests: %s", e)
        return None

def run_maya_tests():
    """
    Discover and run only Maya-specific tests (pattern 'test_maya_*.py').
    Returns:
        unittest.TestResult: Test results object or None if Maya unavailable
    """
    if not is_maya_available():
        logger.warning("Maya not available - skipping Maya-specific tests")
        return None
    try:
        current_dir = os.path.dirname(__file__)
        suite = unittest.TestLoader().discover(current_dir, pattern='test_maya_*.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        logger.info(
            "Maya test run completed. Tests run: %d, Failures: %d, Errors: %d",
            result.testsRun, len(result.failures), len(result.errors)
        )
        return result
    except Exception as e:
        logger.error("Failed to run Maya tests: %s", e)
        return None

def log_tests_info(message):
    """
    Log an informational message to the tests logger.
    Args:
        message (str): Message text
    """
    logger.info(message)

def log_tests_warning(message):
    """
    Log a warning message to the tests logger.
    Args:
        message (str): Message text
    """
    logger.warning(message)

def log_tests_error(message):
    """
    Log an error message to the tests logger.
    Args:
        message (str): Message text
    """
    logger.error(message)

def _initialize_tests_module():
    """
    Initialize the tests module by reporting the environment and
    ensuring test data directory exists.
    """
    try:
        maya_status = "available" if is_maya_available() else "not available"
        log_tests_info("Prof-Tools tests module initialized - Maya: %s", maya_status)
        ensure_test_data_exists()
    except Exception as e:
        log_tests_error("Failed to initialize tests module: %s", e)
        raise

# Automatically initialize when module is imported
_initialize_tests_module()

# Public API
__all__ = [
    '__version__',          # Central version from prof/__init__.py
    '__author__',
    'is_maya_available',
    'get_test_data_path',
    'ensure_test_data_exists',
    'ProfToolsTestCase',
    'run_all_tests',
    'run_maya_tests',
    'log_tests_info',
    'log_tests_warning',
    'log_tests_error'
]
