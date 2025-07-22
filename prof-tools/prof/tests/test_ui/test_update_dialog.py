"""
Test the update dialog UI functionality.

This module tests the update dialog UI components, with proper mocking
for Maya cmds when Maya is not available.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add prof-tools to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from prof.tests import ProfToolsTestCase
from prof.tests.test_utils import mock_maya_cmds, MockManifestData


class TestUpdateDialog(ProfToolsTestCase):
    """Test update dialog functionality."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.maya_cmds_mock = mock_maya_cmds()

    @patch('prof.ui.update_dialog.MAYA_AVAILABLE', True)
    @patch('prof.ui.update_dialog.cmds')
    def test_show_update_dialog_with_mock_maya(self, mock_cmds):
        """Test showing update dialog with mocked Maya cmds."""
        mock_cmds.window.return_value = "test_window"
        mock_cmds.window.exists.return_value = False
        
        from prof.ui.update_dialog import show_update_dialog
        
        # This should not raise an exception
        result = show_update_dialog()
        
        # Verify Maya UI functions were called
        mock_cmds.window.assert_called()
        mock_cmds.showWindow.assert_called()

    @patch('prof.ui.update_dialog.MAYA_AVAILABLE', False)
    def test_show_update_dialog_without_maya(self):
        """Test update dialog behavior when Maya is not available."""
        from prof.ui.update_dialog import show_update_dialog
        
        # Should return early when Maya is not available
        result = show_update_dialog()
        self.assertIsNone(result)

    @patch('prof.ui.update_dialog.get_latest_version')
    @patch('prof.ui.update_dialog.get_prof_tools_version')
    def test_version_comparison_logic(self, mock_current_version, mock_latest_version):
        """Test the version comparison logic in update dialog."""
        # Mock version functions
        mock_current_version.return_value = "0.2.12"
        mock_latest_version.return_value = "0.2.12.1"
        
        from prof.ui.update_dialog import is_testing_temp_versions
        from prof.core.updater import compare_versions
        
        # Test with test versions enabled
        include_test = True
        result = compare_versions("0.2.12", "0.2.12.1", include_test)
        self.assertTrue(result, "Test version should be considered newer")

    def test_dev_mode_utilities(self):
        """Test developer mode utility functions."""
        from prof.ui.update_dialog import (
            is_dev_mode_enabled,
            set_dev_mode,
            is_testing_temp_versions,
            set_testing_temp_versions
        )
        
        # Test dev mode toggle
        original_dev_mode = is_dev_mode_enabled()
        set_dev_mode(not original_dev_mode)
        self.assertEqual(is_dev_mode_enabled(), not original_dev_mode)
        set_dev_mode(original_dev_mode)  # Restore
        
        # Test test versions toggle
        original_test_mode = is_testing_temp_versions()
        set_testing_temp_versions(not original_test_mode)
        self.assertEqual(is_testing_temp_versions(), not original_test_mode)
        set_testing_temp_versions(original_test_mode)  # Restore

    @patch('prof.ui.update_dialog.MAYA_AVAILABLE', True)
    @patch('prof.ui.update_dialog.cmds')
    def test_checkbox_toggle_behavior(self, mock_cmds):
        """Test the test version checkbox toggle behavior."""
        from prof.ui.update_dialog import _on_test_version_toggle
        
        # Mock the in-view message function
        mock_cmds.inViewMessage = MagicMock()
        
        # Test enabling test versions
        with patch('prof.ui.update_dialog._refresh_update_dialog') as mock_refresh:
            _on_test_version_toggle(True)
            mock_refresh.assert_called_once()
        
        # Test disabling test versions
        with patch('prof.ui.update_dialog._refresh_update_dialog') as mock_refresh:
            _on_test_version_toggle(False)
            mock_refresh.assert_called_once()


class TestUpdateDialogErrorHandling(ProfToolsTestCase):
    """Test error handling in update dialog."""

    @patch('prof.ui.update_dialog.MAYA_AVAILABLE', True)
    @patch('prof.ui.update_dialog.cmds')
    def test_error_handling_in_toggle(self, mock_cmds):
        """Test error handling in checkbox toggle function."""
        from prof.ui.update_dialog import _on_test_version_toggle
        
        # Mock an error in the refresh function
        with patch('prof.ui.update_dialog._refresh_update_dialog', side_effect=Exception("Test error")):
            # This should not raise an exception due to error handling
            try:
                _on_test_version_toggle(True)
            except Exception:
                self.fail("_on_test_version_toggle should handle exceptions gracefully")

    @patch('prof.ui.update_dialog.get_latest_version', return_value=None)
    def test_update_dialog_with_no_version_data(self, mock_get_version):
        """Test update dialog behavior when version data is unavailable."""
        from prof.ui.update_dialog import show_update_dialog
        
        with patch('prof.ui.update_dialog.MAYA_AVAILABLE', True):
            with patch('prof.ui.update_dialog.cmds', mock_maya_cmds()):
                # Should handle missing version data gracefully
                result = show_update_dialog()
                # The function should complete without errors


if __name__ == '__main__':
    unittest.main()
