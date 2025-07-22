"""
Test the version utilities functionality.

This module tests the core version management functionality of Prof-Tools,
including version parsing, comparison, and manifest handling.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add prof-tools to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from prof.tests import ProfToolsTestCase
from prof.tests.test_utils import MockManifestData
from prof.core.version_utils import (
    get_prof_tools_version,
    parse_semantic_version,
    compare_versions_extended,
    is_valid_semantic_version
)


class TestVersionUtils(ProfToolsTestCase):
    """Test version utility functions."""

    def test_get_version_returns_string(self):
        """Test that get_prof_tools_version returns a string."""
        version = get_prof_tools_version()
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)

    def test_parse_semantic_version_valid(self):
        """Test parsing valid semantic version strings."""
        # Test stable version
        result = parse_semantic_version("1.2.3")
        expected = {
            'major': 1,
            'minor': 2,
            'patch': 3,
            'test': None,
            'prerelease': None,
            'build': None,
            'is_test_version': False
        }
        self.assertEqual(result, expected)

    def test_parse_semantic_version_test_version(self):
        """Test parsing test version strings."""
        result = parse_semantic_version("1.2.3.4")
        expected = {
            'major': 1,
            'minor': 2,
            'patch': 3,
            'test': 4,
            'prerelease': None,
            'build': None,
            'is_test_version': True
        }
        self.assertEqual(result, expected)

    def test_is_valid_semantic_version(self):
        """Test version string validation."""
        # Valid versions
        self.assertTrue(is_valid_semantic_version("1.0.0"))
        self.assertTrue(is_valid_semantic_version("0.2.12"))
        self.assertTrue(is_valid_semantic_version("1.2.3.4"))
        
        # Invalid versions
        self.assertFalse(is_valid_semantic_version("1.0"))
        self.assertFalse(is_valid_semantic_version("invalid"))
        self.assertFalse(is_valid_semantic_version(""))

    def test_compare_versions_extended(self):
        """Test extended version comparison with test versions."""
        # Test version should be newer than stable
        self.assertTrue(compare_versions_extended("0.2.12", "0.2.12.1", True))
        
        # Test version should not be considered when disabled
        self.assertFalse(compare_versions_extended("0.2.12", "0.2.12.1", False))
        
        # Next stable should be newer than test
        self.assertTrue(compare_versions_extended("0.2.12.1", "0.2.13", True))
        
        # Same versions should not be newer
        self.assertFalse(compare_versions_extended("1.0.0", "1.0.0", True))

    @patch('prof.core.version_utils.get_manifest_data')
    def test_get_version_with_mock_manifest(self, mock_manifest):
        """Test version retrieval with mocked manifest data."""
        mock_manifest.return_value = MockManifestData.STABLE_MANIFEST
        
        # The get_prof_tools_version should return current_version from manifest
        # Note: This test assumes the function uses manifest data
        # Actual implementation may vary
        version = get_prof_tools_version()
        self.assertIsInstance(version, str)


class TestVersionComparison(ProfToolsTestCase):
    """Test version comparison edge cases."""

    def test_version_precedence_order(self):
        """Test that version precedence follows the correct order."""
        versions = [
            "0.2.11",      # Older stable
            "0.2.12",      # Current stable
            "0.2.12.1",    # Test version 1
            "0.2.12.2",    # Test version 2
            "0.2.13"       # Next stable
        ]
        
        # Each version should be newer than the previous one
        for i in range(len(versions) - 1):
            current = versions[i]
            next_version = versions[i + 1]
            
            with self.subTest(current=current, next_version=next_version):
                self.assertTrue(
                    compare_versions_extended(current, next_version, True),
                    f"{next_version} should be newer than {current}"
                )

    def test_test_version_exclusion(self):
        """Test that test versions are excluded when include_test=False."""
        # Test version should not be considered newer when disabled
        self.assertFalse(compare_versions_extended("0.2.12", "0.2.12.1", False))
        
        # But stable version should still work
        self.assertTrue(compare_versions_extended("0.2.11", "0.2.12", False))


if __name__ == '__main__':
    unittest.main()
