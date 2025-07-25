"""
Test script to verify prof-tools installer correctly finds Maya version-specific userSetup paths
"""

import sys
import os
import tempfile
import shutil
import unittest

# Add prof-tools to path for testing
current_dir = os.path.dirname(os.path.abspath(__file__))
prof_dir = os.path.dirname(current_dir)  # Go up one level to prof/
prof_tools_root = os.path.dirname(prof_dir)  # Go up one more level to prof-tools/

if prof_tools_root not in sys.path:
    sys.path.insert(0, prof_tools_root)
if prof_dir not in sys.path:
    sys.path.insert(0, prof_dir)

from prof.core.setup import ProfToolsSetup

class TestUserSetupPaths(unittest.TestCase):
    """Test that installer correctly identifies Maya version-specific userSetup paths"""
    
    def setUp(self):
        """Set up test environment with mock Maya directories"""
        self.test_dir = tempfile.mkdtemp()
        
        # Important: get_maya_documents_path() normally returns ~/Documents/maya
        # When we mock it to return test_dir, the Maya versions should be directly in test_dir
        # So structure should be: test_dir/2022, test_dir/2023, etc.
        # NOT test_dir/maya/2022, test_dir/maya/2023, etc.
        
        # Create mock Maya version directories directly in test_dir
        self.maya_versions = ["2022", "2023", "2024", "2025"]
        for version in self.maya_versions:
            version_dir = os.path.join(self.test_dir, version)
            scripts_dir = os.path.join(version_dir, "scripts")
            prefs_dir = os.path.join(version_dir, "prefs")
            
            os.makedirs(scripts_dir)
            os.makedirs(prefs_dir)
            
            # Create some userSetup files
            usersetup_py = os.path.join(scripts_dir, "userSetup.py")
            usersetup_mel = os.path.join(scripts_dir, "userSetup.mel")
            
            with open(usersetup_py, 'w') as f:
                f.write("# Test userSetup.py for Maya {}\n".format(version))
            
            with open(usersetup_mel, 'w') as f:
                f.write("// Test userSetup.mel for Maya {}\n".format(version))
        
        # Also create a non-Maya directory that should be ignored
        non_maya_dir = os.path.join(self.test_dir, "notmaya")
        os.makedirs(non_maya_dir)
        
        # Create a year folder without Maya structure (should be ignored)
        fake_year_dir = os.path.join(self.test_dir, "2026")
        os.makedirs(fake_year_dir)
        
        # Mock the setup class to use our test directory
        # The get_maya_documents_path should return the test directory directly
        self.original_get_maya_documents_path = ProfToolsSetup.get_maya_documents_path
        test_dir = self.test_dir  # Capture in local variable for lambda
        ProfToolsSetup.get_maya_documents_path = lambda self: test_dir
        
        self.setup = ProfToolsSetup()
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original method
        ProfToolsSetup.get_maya_documents_path = self.original_get_maya_documents_path
        
        # Remove test directory
        shutil.rmtree(self.test_dir)
    
    def test_finds_maya_version_directories(self):
        """Test that setup correctly finds Maya version directories"""
        print(f"Test directory: {self.test_dir}")
        print(f"Test dir exists: {os.path.exists(self.test_dir)}")
        
        # List contents of test directory
        if os.path.exists(self.test_dir):
            print(f"Test dir contents: {os.listdir(self.test_dir)}")
        
        maya_dirs = self.setup.get_available_maya_preferences_dirs()
        print(f"Found Maya dirs: {maya_dirs}")
        
        # Should find all our mock Maya versions
        self.assertEqual(len(maya_dirs), len(self.maya_versions))
        
        for version in self.maya_versions:
            self.assertIn(version, maya_dirs)
            expected_path = os.path.join(self.test_dir, version)
            self.assertEqual(maya_dirs[version], expected_path)
        
        # Should not find non-Maya directories
        self.assertNotIn("notmaya", maya_dirs)
        self.assertNotIn("2026", maya_dirs)  # No Maya structure
    
    def test_usersetup_paths_are_version_specific(self):
        """Test that userSetup paths are correctly version-specific"""
        usersetup_files = self.setup.get_all_usersetup_files(only_existing=True)
        
        # Should find both .py and .mel files for each Maya version
        expected_count = len(self.maya_versions) * 2  # 2 files per version
        self.assertEqual(len(usersetup_files), expected_count)
        
        # Verify paths are correctly structured
        for version in self.maya_versions:
            expected_py_path = os.path.join(self.test_dir, version, "scripts", "userSetup.py")
            expected_mel_path = os.path.join(self.test_dir, version, "scripts", "userSetup.mel")
            
            self.assertIn(expected_py_path, usersetup_files)
            self.assertIn(expected_mel_path, usersetup_files)
    
    def test_usersetup_path_structure(self):
        """Test that userSetup paths follow correct Maya structure"""
        maya_dirs = self.setup.get_available_maya_preferences_dirs()
        
        for version, version_path in maya_dirs.items():
            # In our mock, path should be: {test_dir}/{version}
            # (in real Maya it would be ~/Documents/maya/{version})
            expected_path = os.path.join(self.test_dir, version)
            self.assertEqual(version_path, expected_path)
            
            # Scripts directory should be: {version_path}/scripts
            scripts_dir = os.path.join(version_path, "scripts")
            self.assertTrue(os.path.exists(scripts_dir))
            
            # userSetup files should be in scripts directory
            usersetup_py = os.path.join(scripts_dir, "userSetup.py")
            usersetup_mel = os.path.join(scripts_dir, "userSetup.mel")
            
            self.assertTrue(os.path.exists(usersetup_py))
            self.assertTrue(os.path.exists(usersetup_mel))
    
    def test_ignores_invalid_maya_directories(self):
        """Test that setup ignores directories that don't look like Maya versions"""
        # Create some invalid directories
        invalid_dirs = ["abc", "20", "202", "20222", "2024.5", "maya"]
        
        for invalid_dir in invalid_dirs:
            invalid_path = os.path.join(self.test_dir, invalid_dir)
            os.makedirs(invalid_path)
        
        maya_dirs = self.setup.get_available_maya_preferences_dirs()
        
        # Should still only find valid Maya versions
        self.assertEqual(len(maya_dirs), len(self.maya_versions))
        
        for invalid_dir in invalid_dirs:
            self.assertNotIn(invalid_dir, maya_dirs)
    
    def test_handles_missing_maya_directory(self):
        """Test that setup handles missing Maya base directory gracefully"""
        # Mock a non-existent Maya directory
        ProfToolsSetup.get_maya_documents_path = lambda self: "/non/existent/path"
        
        setup = ProfToolsSetup()
        maya_dirs = setup.get_available_maya_preferences_dirs()
        
        # Should return empty dict when Maya directory doesn't exist
        self.assertEqual(len(maya_dirs), 0)
        self.assertIsInstance(maya_dirs, dict)

def run_tests():
    """Run the userSetup path tests"""
    print("=" * 60)
    print("Testing Prof-Tools Installer Maya Version Detection")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUserSetupPaths)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED - Installer correctly finds Maya version-specific paths!")
        print("Key validations:")
        print("- Finds all Maya version directories (2022, 2023, 2024, 2025)")
        print("- Creates correct version-specific userSetup paths")
        print("- Ignores invalid directories")
        print("- Handles missing Maya directories gracefully")
        print("- Follows proper Maya directory structure: ~/maya/{version}/scripts/")
    else:
        print("✗ SOME TESTS FAILED - Check installer implementation")
        for failure in result.failures:
            print("FAILURE:", failure[0])
            print(failure[1])
        for error in result.errors:
            print("ERROR:", error[0])
            print(error[1])
    
    print("=" * 60)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
