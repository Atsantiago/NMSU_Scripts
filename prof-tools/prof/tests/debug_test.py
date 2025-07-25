#!/usr/bin/env python3
"""
Quick debug test to understand what's happening with Maya directory detection
"""
import os
import sys
import tempfile

# Add the prof package to the path - go up to the prof-tools directory
current_dir = os.path.dirname(os.path.abspath(__file__))
prof_tools_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, prof_tools_dir)

from prof.core.setup import ProfToolsSetup

def debug_maya_detection():
    # Create a temporary test directory
    with tempfile.TemporaryDirectory() as test_dir:
        print(f"Test directory: {test_dir}")
        
        # Create mock Maya directory structure
        mock_maya_dir = os.path.join(test_dir, "Maya")
        os.makedirs(mock_maya_dir)
        print(f"Created Maya directory: {mock_maya_dir}")
        
        # Create some Maya version directories
        versions = ["2022", "2023", "2024", "2025"]
        for version in versions:
            version_dir = os.path.join(mock_maya_dir, version)
            scripts_dir = os.path.join(version_dir, "scripts")
            prefs_dir = os.path.join(version_dir, "prefs")
            
            os.makedirs(scripts_dir)
            os.makedirs(prefs_dir)
            
            # Create userSetup files
            with open(os.path.join(scripts_dir, "userSetup.py"), "w") as f:
                f.write("# Test userSetup.py")
            with open(os.path.join(scripts_dir, "userSetup.mel"), "w") as f:
                f.write("// Test userSetup.mel")
            
            print(f"Created Maya {version} structure at {version_dir}")
        
        print(f"Maya directory contents: {os.listdir(mock_maya_dir)}")
        
        # Test Setup with mock Maya directory  
        # First try without overriding to see what the setup finds by default
        setup = ProfToolsSetup()
        
        print(f"Setup Maya documents path: {setup.get_maya_documents_path()}")
        
        try:
            maya_dirs = setup.get_available_maya_preferences_dirs()
            print(f"Found Maya directories: {maya_dirs}")
            print(f"Found {len(maya_dirs)} Maya installations")
            
            usersetup_files = setup.get_all_usersetup_files()
            print(f"Found userSetup files: {usersetup_files}")
            print(f"Found {len(usersetup_files)} userSetup files")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_maya_detection()
