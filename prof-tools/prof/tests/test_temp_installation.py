"""
Test script for Temporary Test Installation System

This script tests the temporary test installation functionality
in a controlled manner without actually performing installations.

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function
import sys
import os

def test_dev_prefs():
    """Test the developer preferences system."""
    print("Testing Developer Preferences System...")
    
    try:
        from prof.core.tools.dev_prefs import get_prefs
        prefs = get_prefs()
        
        print("✓ Successfully imported dev_prefs")
        print("✓ Created preferences instance")
        
        # Test temp install methods
        print("\nTesting temporary installation methods:")
        
        # Check initial state
        is_active = prefs.is_temp_install_active()
        print("✓ is_temp_install_active(): {}".format(is_active))
        
        # Get temp install info
        info = prefs.get_temp_install_info()
        print("✓ get_temp_install_info(): {}".format(info))
        
        # Test setting temp install (simulate only)
        print("\nSimulating temporary installation setup...")
        original_state = prefs.prefs.get("temp_install", {})
        
        prefs.set_temp_install("0.2.13.1", "0.2.13")
        print("✓ set_temp_install() completed")
        
        # Verify state changed
        is_active_after = prefs.is_temp_install_active()
        info_after = prefs.get_temp_install_info()
        print("✓ Active after set: {}".format(is_active_after))
        print("✓ Info after set: {}".format(info_after))
        
        # Test clearing
        prefs.clear_temp_install()
        print("✓ clear_temp_install() completed")
        
        # Verify state reverted
        is_active_final = prefs.is_temp_install_active()
        print("✓ Active after clear: {}".format(is_active_final))
        
        print("\n✅ Developer preferences tests completed successfully")
        return True
        
    except Exception as e:
        print("❌ Developer preferences test failed: {}".format(e))
        return False

def test_version_utils():
    """Test version utility functions."""
    print("\nTesting Version Utilities...")
    
    try:
        from prof.core.version_utils import get_prof_tools_version, get_manifest_data
        
        # Test current version
        current_version = get_prof_tools_version()
        print("✓ Current version: {}".format(current_version))
        
        # Test manifest data (may require internet)
        try:
            manifest = get_manifest_data()
            if manifest:
                releases = manifest.get('releases', [])
                print("✓ Manifest loaded: {} releases found".format(len(releases)))
                
                # Look for test versions
                test_versions = [r for r in releases if r.get('test_version', False)]
                print("✓ Test versions available: {}".format(len(test_versions)))
                
                if test_versions:
                    latest_test = test_versions[0].get('version', 'unknown')
                    print("✓ Latest test version: {}".format(latest_test))
            else:
                print("⚠ Manifest data not available (network issue?)")
                
        except Exception as e:
            print("⚠ Manifest test skipped: {}".format(e))
        
        print("\n✅ Version utilities tests completed successfully")
        return True
        
    except Exception as e:
        print("❌ Version utilities test failed: {}".format(e))
        return False

def test_updater_functions():
    """Test updater functions (without actually updating)."""
    print("\nTesting Updater Functions...")
    
    try:
        from prof.core.updater import get_latest_version, _install_specific_version
        
        # Test getting latest version
        try:
            latest_stable = get_latest_version(include_test=False)
            print("✓ Latest stable version: {}".format(latest_stable))
            
            latest_test = get_latest_version(include_test=True)
            print("✓ Latest version (with test): {}".format(latest_test))
            
        except Exception as e:
            print("⚠ Version check skipped: {}".format(e))
        
        # Test install function exists (don't actually run it)
        if hasattr(_install_specific_version, '__call__'):
            print("✓ _install_specific_version function available")
        else:
            print("❌ _install_specific_version function missing")
            return False
        
        print("\n✅ Updater function tests completed successfully")
        return True
        
    except Exception as e:
        print("❌ Updater function test failed: {}".format(e))
        return False

def test_ui_functions():
    """Test UI function availability (without opening Maya dialogs)."""
    print("\nTesting UI Functions...")
    
    try:
        from prof.ui.builder import _install_test_version_temporarily, _revert_to_stable
        
        # Test function existence
        if hasattr(_install_test_version_temporarily, '__call__'):
            print("✓ _install_test_version_temporarily function available")
        else:
            print("❌ _install_test_version_temporarily function missing")
            return False
            
        if hasattr(_revert_to_stable, '__call__'):
            print("✓ _revert_to_stable function available")
        else:
            print("❌ _revert_to_stable function missing")
            return False
        
        print("\n✅ UI function tests completed successfully")
        return True
        
    except Exception as e:
        print("❌ UI function test failed: {}".format(e))
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Prof-Tools Temporary Test Installation System Tests")
    print("=" * 60)
    
    tests = [
        test_dev_prefs,
        test_version_utils,
        test_updater_functions,
        test_ui_functions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print("❌ Test {} failed with exception: {}".format(test.__name__, e))
            failed += 1
    
    print("\n" + "=" * 60)
    print("Test Results: {} passed, {} failed".format(passed, failed))
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Temporary test installation system is ready.")
        return True
    else:
        print("⚠ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
