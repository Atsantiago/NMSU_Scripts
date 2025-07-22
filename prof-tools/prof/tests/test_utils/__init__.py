"""
Test utilities and helpers for Prof-Tools testing.

This module provides common utilities, mock data, and helpers for testing:
- Maya testing utilities
- Mock data generators
- Common test fixtures
- Test environment setup
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from unittest.mock import MagicMock, patch

def mock_maya_cmds():
    """
    Create a mock Maya cmds module for testing UI components without Maya.
    
    Returns:
        MagicMock: Mock cmds module with common Maya UI functions
    """
    cmds_mock = MagicMock()
    
    # Mock common UI functions
    cmds_mock.window.return_value = "test_window"
    cmds_mock.window.exists.return_value = False
    cmds_mock.columnLayout.return_value = "test_layout"
    cmds_mock.button.return_value = "test_button"
    cmds_mock.text.return_value = "test_text"
    cmds_mock.checkBox.return_value = "test_checkbox"
    cmds_mock.confirmDialog.return_value = "OK"
    
    return cmds_mock

def maya_not_available():
    """
    Decorator to simulate Maya not being available for testing.
    
    This is useful for testing fallback behavior when Maya is not installed.
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with patch.dict('sys.modules', {'maya': None, 'maya.cmds': None}):
                return test_func(*args, **kwargs)
        return wrapper
    return decorator

class MockManifestData:
    """Mock data for testing version manifest functionality."""
    
    STABLE_MANIFEST = {
        "current_version": "0.2.12",
        "releases": [
            {"version": "0.2.12", "release_date": "2025-01-15"},
            {"version": "0.2.11", "release_date": "2025-01-01"}
        ]
    }
    
    TEST_MANIFEST = {
        "current_version": "0.2.12",
        "releases": [
            {"version": "0.2.12.1", "release_date": "2025-01-20"},
            {"version": "0.2.12", "release_date": "2025-01-15"},
            {"version": "0.2.11", "release_date": "2025-01-01"}
        ]
    }
