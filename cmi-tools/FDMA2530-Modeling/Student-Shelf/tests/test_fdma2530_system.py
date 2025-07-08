"""
Comprehensive Tests for FDMA2530 Maya Shelf System
==================================================

Test suite for all components of the FDMA2530 modeling shelf system.
Can be run in VS Code or any Python environment.

Author: Alexander T. Santiago
Created: 2025-07-08
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add the parent directories to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestVersionUtils(unittest.TestCase):
    """Test fdma_shelf.utils.version_utils module"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear any cached imports to ensure fresh imports in tests
        modules_to_clear = [name for name in sys.modules.keys() if name.startswith('fdma_shelf')]
        for module_name in modules_to_clear:
            if module_name in sys.modules:
                del sys.modules[module_name]
    
    def test_version_validation(self):
        """Test semantic version validation"""
        try:
            from fdma_shelf.utils.version_utils import is_valid_semantic_version
            
            # Valid versions
            self.assertTrue(is_valid_semantic_version("1.0.0"))
            self.assertTrue(is_valid_semantic_version("2.1.3"))
            self.assertTrue(is_valid_semantic_version("10.20.30"))
            self.assertTrue(is_valid_semantic_version("1.0.0-alpha"))
            self.assertTrue(is_valid_semantic_version("1.0.0+build.1"))
            
            # Invalid versions
            self.assertFalse(is_valid_semantic_version("1.0"))
            self.assertFalse(is_valid_semantic_version("invalid"))
            self.assertFalse(is_valid_semantic_version(""))
            self.assertFalse(is_valid_semantic_version(None))
            self.assertFalse(is_valid_semantic_version(123))
            
        except ImportError as e:
            self.skipTest(f"Could not import version_utils: {e}")
    
    def test_version_comparison(self):
        """Test semantic version comparison"""
        try:
            from fdma_shelf.utils.version_utils import compare_versions
            
            # Test basic comparisons
            self.assertEqual(compare_versions("1.0.0", "2.0.0"), -1)
            self.assertEqual(compare_versions("2.0.0", "1.0.0"), 1)
            self.assertEqual(compare_versions("1.0.0", "1.0.0"), 0)
            
            # Test pre-release versions
            self.assertEqual(compare_versions("1.0.0-alpha", "1.0.0"), -1)
            self.assertEqual(compare_versions("1.0.0", "1.0.0-alpha"), 1)
            
        except ImportError as e:
            self.skipTest(f"Could not import version_utils: {e}")
    
    def test_version_parsing(self):
        """Test semantic version parsing"""
        try:
            from fdma_shelf.utils.version_utils import parse_semantic_version
            
            # Test basic version parsing
            result = parse_semantic_version("1.2.3")
            expected = {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': None, 'build': None}
            self.assertEqual(result, expected)
            
            # Test version with pre-release and build
            result = parse_semantic_version("1.2.3-alpha.1+build.2")
            expected = {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': 'alpha.1', 'build': 'build.2'}
            self.assertEqual(result, expected)
            
            # Test invalid version
            with self.assertRaises(ValueError):
                parse_semantic_version("invalid")
                
        except ImportError as e:
            self.skipTest(f"Could not import version_utils: {e}")


class TestShelfBuilder(unittest.TestCase):
    """Test fdma_shelf.shelf.builder module"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Maya commands
        self.mock_cmds = Mock()
        sys.modules['maya.cmds'] = self.mock_cmds
        sys.modules['maya.mel'] = Mock()
        sys.modules['maya.utils'] = Mock()
    
    def test_config_reading(self):
        """Test shelf configuration reading"""
        try:
            from fdma_shelf.shelf.builder import _read_json
            
            # Create a temporary config file
            test_config = {
                "shelf_info": {"name": "TEST_SHELF"},
                "buttons": [{"type": "button", "label": "Test"}]
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(test_config, f)
                temp_path = f.name
            
            try:
                result = _read_json(temp_path)
                self.assertEqual(result["shelf_info"]["name"], "TEST_SHELF")
                self.assertEqual(len(result["buttons"]), 1)
            finally:
                os.unlink(temp_path)
                
        except ImportError as e:
            self.skipTest(f"Could not import shelf.builder: {e}")
    
    def test_version_token_expansion(self):
        """Test version token expansion in configuration"""
        try:
            from fdma_shelf.shelf.builder import _expand_version_tokens
            
            test_data = {
                "annotation": "Tool v{version}",
                "buttons": [
                    {"label": "Test {version}", "command": "print('{version}')"}
                ]
            }
            
            # Mock the version
            with patch('fdma_shelf.shelf.builder.PACKAGE_VERSION', '2.0.6'):
                result = _expand_version_tokens(test_data)
                self.assertEqual(result["annotation"], "Tool v2.0.6")
                self.assertEqual(result["buttons"][0]["label"], "Test 2.0.6")
                self.assertEqual(result["buttons"][0]["command"], "print('2.0.6')")
                
        except ImportError as e:
            self.skipTest(f"Could not import shelf.builder: {e}")
    
    def test_shelf_exists_check(self):
        """Test shelf existence checking"""
        try:
            from fdma_shelf.shelf.builder import _shelf_exists
            
            # Mock shelf exists
            self.mock_cmds.shelfLayout.return_value = True
            self.assertTrue(_shelf_exists("TEST_SHELF"))
            
            # Mock shelf doesn't exist
            self.mock_cmds.shelfLayout.return_value = False
            self.assertFalse(_shelf_exists("TEST_SHELF"))
            
        except ImportError as e:
            self.skipTest(f"Could not import shelf.builder: {e}")


class TestUpdater(unittest.TestCase):
    """Test fdma_shelf.utils.updater module"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Maya modules
        sys.modules['maya.cmds'] = Mock()
        sys.modules['maya.utils'] = Mock()
    
    def test_version_comparison(self):
        """Test version comparison logic in updater"""
        try:
            from fdma_shelf.utils.updater import _is_newer
            
            # Test newer version detection
            self.assertTrue(_is_newer("2.0.1", "2.0.0"))
            self.assertTrue(_is_newer("2.1.0", "2.0.9"))
            self.assertTrue(_is_newer("3.0.0", "2.9.9"))
            
            # Test same version
            self.assertFalse(_is_newer("2.0.0", "2.0.0"))
            
            # Test older version
            self.assertFalse(_is_newer("1.9.9", "2.0.0"))
            self.assertFalse(_is_newer("2.0.0", "2.0.1"))
            
        except ImportError as e:
            self.skipTest(f"Could not import updater: {e}")
    
    def test_cmi_tools_root_path(self):
        """Test CMI tools root directory detection"""
        try:
            from fdma_shelf.utils.updater import _get_cmi_tools_root
            
            # Test path generation
            root_path = _get_cmi_tools_root()
            self.assertIn("cmi-tools", root_path)
            self.assertTrue(root_path.endswith("cmi-tools"))
            
        except ImportError as e:
            self.skipTest(f"Could not import updater: {e}")
    
    @patch('fdma_shelf.utils.updater.urllib.request.urlopen')
    def test_manifest_reading(self, mock_urlopen):
        """Test manifest reading from GitHub"""
        try:
            from fdma_shelf.utils.updater import _get_releases_manifest
            
            # Mock response
            mock_response = Mock()
            mock_response.read.return_value = json.dumps({
                "current_version": "2.0.6",
                "releases": [{"version": "2.0.6", "download_url": "test_url"}]
            }).encode('utf-8')
            
            # Set up proper context manager
            mock_context = Mock()
            mock_context.__enter__ = Mock(return_value=mock_response)
            mock_context.__exit__ = Mock(return_value=None)
            mock_urlopen.return_value = mock_context
            
            result = _get_releases_manifest()
            self.assertEqual(result["current_version"], "2.0.6")
            self.assertEqual(len(result["releases"]), 1)
            
        except ImportError as e:
            self.skipTest(f"Could not import updater: {e}")


class TestInstaller(unittest.TestCase):
    """Test setup_drag_drop_fdma2530.py installer"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Maya commands
        self.mock_cmds = Mock()
        sys.modules['maya.cmds'] = self.mock_cmds
        
        # Add installer to path
        installer_path = os.path.join(os.path.dirname(__file__), '..', 'setup_drag_drop_fdma2530.py')
        if os.path.exists(installer_path):
            sys.path.insert(0, os.path.dirname(installer_path))
    
    def test_cmi_tools_root_detection(self):
        """Test CMI tools root directory detection"""
        try:
            import setup_drag_drop_fdma2530 as installer
            
            # Mock Maya internal variable
            self.mock_cmds.internalVar.return_value = "/test/maya/app/"
            
            root = installer.get_cmi_tools_root()
            self.assertIn("cmi-tools", root)
            
        except ImportError as e:
            self.skipTest(f"Could not import installer: {e}")
    
    def test_modules_directory_creation(self):
        """Test Maya modules directory handling"""
        try:
            import setup_drag_drop_fdma2530 as installer
            
            # Mock Maya internal variable
            self.mock_cmds.internalVar.return_value = "/test/maya/app/"
            
            with patch('os.path.exists', return_value=False), \
                 patch('os.makedirs') as mock_makedirs:
                
                modules_dir = installer.get_modules_dir()
                self.assertIn("modules", modules_dir)
                mock_makedirs.assert_called_once()
                
        except ImportError as e:
            self.skipTest(f"Could not import installer: {e}")
    
    @patch('setup_drag_drop_fdma2530.urlopen')
    def test_version_fetching(self, mock_urlopen):
        """Test latest version fetching from GitHub"""
        try:
            import setup_drag_drop_fdma2530 as installer
            
            # Mock response
            mock_response = Mock()
            mock_response.read.return_value = json.dumps({
                "current_version": "2.0.6"
            }).encode('utf-8')
            mock_urlopen.return_value = mock_response
            
            version = installer.get_latest_release_version()
            self.assertEqual(version, "2.0.6")
            
        except ImportError as e:
            self.skipTest(f"Could not import installer: {e}")


class TestShelfConfig(unittest.TestCase):
    """Test shelf_config.json configuration"""
    
    def test_config_file_validity(self):
        """Test that shelf_config.json is valid JSON"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'shelf_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                try:
                    config = json.load(f)
                    self.assertIn("shelf_info", config)
                    self.assertIn("buttons", config)
                except json.JSONDecodeError as e:
                    self.fail(f"shelf_config.json is not valid JSON: {e}")
        else:
            self.skipTest("shelf_config.json not found")
    
    def test_config_required_fields(self):
        """Test that shelf_config.json has required fields"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'shelf_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                
                # Check shelf_info
                shelf_info = config.get("shelf_info", {})
                self.assertIn("name", shelf_info)
                self.assertEqual(shelf_info["name"], "FDMA_2530")
                
                # Check buttons
                buttons = config.get("buttons", [])
                self.assertGreater(len(buttons), 0)
                
                # Check for Update button
                update_button = None
                for button in buttons:
                    if button.get("label") == "Update":
                        update_button = button
                        break
                
                self.assertIsNotNone(update_button, "Update button not found in config")
                self.assertIn("command", update_button)
        else:
            self.skipTest("shelf_config.json not found")
    
    def test_config_button_structure(self):
        """Test that buttons in shelf_config.json have proper structure"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'shelf_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                
                for button in config.get("buttons", []):
                    self.assertIn("type", button)
                    
                    if button["type"] == "button":
                        self.assertIn("label", button)
                        self.assertIn("enabled", button)
                    elif button["type"] == "separator":
                        self.assertIn("style", button)


class TestReleasesManifest(unittest.TestCase):
    """Test releases.json manifest file"""
    
    def test_manifest_validity(self):
        """Test that releases.json is valid JSON"""
        manifest_path = os.path.join(os.path.dirname(__file__), '..', '..', 'releases.json')
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                try:
                    manifest = json.load(f)
                    self.assertIn("current_version", manifest)
                    self.assertIn("releases", manifest)
                except json.JSONDecodeError as e:
                    self.fail(f"releases.json is not valid JSON: {e}")
        else:
            self.skipTest("releases.json not found")
    
    def test_manifest_required_fields(self):
        """Test that releases.json has required fields"""
        manifest_path = os.path.join(os.path.dirname(__file__), '..', '..', 'releases.json')
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
                # Check top-level fields
                required_fields = ["tool_name", "current_version", "description", "author", "releases"]
                for field in required_fields:
                    self.assertIn(field, manifest, f"Missing required field: {field}")
                
                # Check releases array
                releases = manifest.get("releases", [])
                self.assertGreater(len(releases), 0, "No releases found in manifest")
                
                # Check current version exists in releases
                current_version = manifest["current_version"]
                version_found = False
                for release in releases:
                    if release.get("version") == current_version:
                        version_found = True
                        break
                
                self.assertTrue(version_found, f"Current version {current_version} not found in releases")
        else:
            self.skipTest("releases.json not found")
    
    def test_manifest_download_urls(self):
        """Test that download URLs in releases.json are properly formatted"""
        manifest_path = os.path.join(os.path.dirname(__file__), '..', '..', 'releases.json')
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
                for release in manifest.get("releases", []):
                    download_url = release.get("download_url")
                    self.assertIsNotNone(download_url, "Missing download_url in release")
                    self.assertTrue(download_url.startswith("https://"), "Download URL should use HTTPS")
                    self.assertIn("github.com", download_url, "Download URL should be from GitHub")
        else:
            self.skipTest("releases.json not found")


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)
