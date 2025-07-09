#!/usr/bin/env python
"""
Temporary test script to verify version loading works correctly.
This will be deleted after testing.
"""

import sys
import os

# Add prof-tools to path
prof_tools_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, prof_tools_path)

print("Testing Prof-Tools versioning system...")
print("=" * 50)

# Test version_utils directly
try:
    from prof.core.version_utils import get_prof_tools_version, get_version_tuple
    
    version = get_prof_tools_version()
    version_tuple = get_version_tuple()
    
    print("✓ Version from version_utils.get_prof_tools_version(): {}".format(version))
    print("✓ Version tuple from version_utils.get_version_tuple(): {}".format(version_tuple))
    
except Exception as e:
    print("✗ Error testing version_utils: {}".format(e))

# Test main prof module version
try:
    from prof import __version__, get_version
    
    print("✓ Version from prof.__version__: {}".format(__version__))
    print("✓ Version from prof.get_version(): {}".format(get_version()))
    
except Exception as e:
    print("✗ Error testing prof module: {}".format(e))

# Test updater functions
try:
    from prof.core.updater import get_latest_version, compare_versions
    
    latest = get_latest_version()
    print("✓ Latest version from updater.get_latest_version(): {}".format(latest))
    
    if latest and version:
        is_newer = compare_versions(version, latest)
        print("✓ Version comparison ({} vs {}): newer available = {}".format(version, latest, is_newer))
    
except Exception as e:
    print("✗ Error testing updater: {}".format(e))

print("=" * 50)
print("Version testing complete!")
