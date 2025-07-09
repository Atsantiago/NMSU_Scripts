"""
Simple Import Test for Prof-Tools
This can be run from Maya's script editor to test if the fixes work.
"""

import sys
import os

# Add prof-tools directory to path (adjust path as needed)
prof_tools_path = r"d:\Alexander Santiago\Documents\Code\Github-Repos\NMSU_Scripts\prof-tools"
if prof_tools_path not in sys.path:
    sys.path.insert(0, prof_tools_path)

print("=== Prof-Tools Import Test ===")

try:
    print("1. Testing prof module import...")
    import prof
    print("   ✓ SUCCESS: prof module imported")
    print("   Version: {}".format(prof.get_version()))
except Exception as e:
    print("   ✗ FAILED: {}".format(e))

try:
    print("2. Testing setup module import...")
    from prof.core.setup import ProfToolsSetup, launcher_entry_point
    print("   ✓ SUCCESS: setup module imported")
except Exception as e:
    print("   ✗ FAILED: {}".format(e))

try:
    print("3. Testing ProfToolsSetup class...")
    setup = ProfToolsSetup()
    print("   ✓ SUCCESS: ProfToolsSetup instance created")
    print("   Version: {}".format(setup.version))
    print("   Platform: {}".format(setup.platform))
    
    # Check methods
    methods = ['install_package', 'uninstall_package', 'run_only']
    for method in methods:
        if hasattr(setup, method) and callable(getattr(setup, method)):
            print("   ✓ Method '{}' is callable".format(method))
        else:
            print("   ✗ Method '{}' issue".format(method))
            
except Exception as e:
    print("   ✗ FAILED: {}".format(e))

try:
    print("4. Testing launcher_entry_point...")
    if callable(launcher_entry_point):
        print("   ✓ SUCCESS: launcher_entry_point is callable")
    else:
        print("   ✗ FAILED: launcher_entry_point is not callable")
except Exception as e:
    print("   ✗ FAILED: {}".format(e))

try:
    print("5. Testing UI builder...")
    from prof.ui import builder
    print("   ✓ SUCCESS: UI builder imported")
except Exception as e:
    print("   ✗ FAILED: {}".format(e))

print("=== Test Complete ===")
