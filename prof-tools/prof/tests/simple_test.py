#!/usr/bin/env python3
"""
Simple test to check if our Maya path mocking works
"""
import os
import sys
import tempfile

# Add the prof package to the path - go up to the prof-tools directory
current_dir = os.path.dirname(os.path.abspath(__file__))
prof_tools_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, prof_tools_dir)

from prof.core.setup import ProfToolsSetup

def test_maya_path_mocking():
    """Test if we can successfully mock the Maya documents path"""
    
    # Create test directory with maya structure
    with tempfile.TemporaryDirectory() as test_dir:
        print(f"Test directory: {test_dir}")
        
        # The get_maya_documents_path() normally returns ~/Documents/maya
        # When we mock it to return test_dir, then Maya versions should be directly in test_dir
        # So the structure should be: test_dir/2023 not test_dir/maya/2023
        
        # Create a Maya version directory directly in test_dir
        version_dir = os.path.join(test_dir, "2023")
        scripts_dir = os.path.join(version_dir, "scripts")
        prefs_dir = os.path.join(version_dir, "prefs") 
        
        os.makedirs(scripts_dir)
        os.makedirs(prefs_dir)
        
        # Create userSetup files
        with open(os.path.join(scripts_dir, "userSetup.py"), "w") as f:
            f.write("# Test userSetup.py")
        with open(os.path.join(scripts_dir, "userSetup.mel"), "w") as f:
            f.write("// Test userSetup.mel")
        
        print(f"Created Maya version structure: {version_dir}")
        print(f"Test dir contents: {os.listdir(test_dir)}")
        print(f"Version dir contents: {os.listdir(version_dir)}")
        
        # Test without mocking first
        setup = ProfToolsSetup()
        normal_path = setup.get_maya_documents_path()
        print(f"Normal Maya documents path: {normal_path}")
        
        # Now try mocking
        original_method = ProfToolsSetup.get_maya_documents_path
        
        try:
            # Mock the method to return our test directory
            ProfToolsSetup.get_maya_documents_path = lambda self: test_dir
            
            # Create new setup instance
            mocked_setup = ProfToolsSetup()
            mocked_path = mocked_setup.get_maya_documents_path()
            print(f"Mocked Maya documents path: {mocked_path}")
            
            if mocked_path == test_dir:
                print("✓ Mocking successful!")
                
                # Now test Maya version detection
                maya_dirs = mocked_setup.get_available_maya_preferences_dirs()
                print(f"Found Maya dirs with mocking: {maya_dirs}")
                
                if "2023" in maya_dirs:
                    print("✓ Maya version detection works with mocking!")
                    return True
                else:
                    print("✗ Maya version detection failed with mocking")
                    return False
            else:
                print(f"✗ Mocking failed - expected {test_dir}, got {mocked_path}")
                return False
                
        finally:
            # Restore original method
            ProfToolsSetup.get_maya_documents_path = original_method

if __name__ == "__main__":
    success = test_maya_path_mocking()
    print(f"Test result: {'PASS' if success else 'FAIL'}")
