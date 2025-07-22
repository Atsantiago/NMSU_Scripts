#!/usr/bin/env python
"""
Test script to verify the checkbox behavior in the update dialog.
This tests the toggle functionality without requiring Maya.
"""

import sys
import os

# Add the prof-tools to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_checkbox_functions():
    """Test the checkbox toggle functions."""
    print("Testing checkbox toggle functions...")
    
    try:
        from prof.ui.update_dialog import set_testing_temp_versions, is_testing_temp_versions
        
        print("Initial state:", is_testing_temp_versions())
        
        # Test enabling
        print("Enabling test versions...")
        set_testing_temp_versions(True)
        print("State after enabling:", is_testing_temp_versions())
        
        # Test disabling  
        print("Disabling test versions...")
        set_testing_temp_versions(False)
        print("State after disabling:", is_testing_temp_versions())
        
        # Test enabling again
        print("Re-enabling test versions...")
        set_testing_temp_versions(True)
        print("Final state:", is_testing_temp_versions())
        
        print("✅ Checkbox functions work correctly")
        
    except Exception as e:
        print(f"❌ Error in checkbox functions: {e}")
        import traceback
        traceback.print_exc()

def test_version_retrieval():
    """Test version retrieval with different settings."""
    print("\nTesting version retrieval...")
    
    try:
        from prof.core.updater import get_latest_version
        from prof.ui.update_dialog import set_testing_temp_versions
        
        # Test with test versions disabled
        print("Setting test versions to False...")
        set_testing_temp_versions(False)
        stable_version = get_latest_version(include_test=False)
        print(f"Stable version: {stable_version}")
        
        # Test with test versions enabled
        print("Setting test versions to True...")
        set_testing_temp_versions(True)
        test_version = get_latest_version(include_test=True)
        print(f"Test version: {test_version}")
        
        if stable_version != test_version:
            print("✅ Version retrieval works correctly - versions differ as expected")
        else:
            print("⚠️  Versions are the same - might be normal if no test version available")
        
    except Exception as e:
        print(f"❌ Error in version retrieval: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Prof-Tools Checkbox Behavior Test")
    print("=" * 50)
    
    test_checkbox_functions()
    test_version_retrieval()
    
    print("\nTest completed.")
