#!/usr/bin/env python
"""
Prof-Tools Installation Diagnostics
Run this script in Maya to diagnose prof-tools installation issues.
"""

import os
import sys

def diagnose_prof_tools_installation():
    """Diagnose prof-tools installation and persistence issues"""
    
    print("=" * 60)
    print("PROF-TOOLS INSTALLATION DIAGNOSTICS")
    print("=" * 60)
    
    # 1. Check Maya preferences directories
    print("\n1. MAYA PREFERENCES DIRECTORIES:")
    maya_docs_path = os.path.join(os.path.expanduser("~"), "Documents", "maya")
    print("   Maya documents path: {}".format(maya_docs_path))
    print("   Exists: {}".format(os.path.exists(maya_docs_path)))
    
    if os.path.exists(maya_docs_path):
        maya_versions = []
        for folder in os.listdir(maya_docs_path):
            if folder.isdigit() and len(folder) == 4:
                full_path = os.path.join(maya_docs_path, folder)
                if os.path.isdir(full_path):
                    maya_versions.append((folder, full_path))
        
        print("   Found Maya versions: {}".format([v[0] for v in maya_versions]))
        
        # Check userSetup.mel files
        print("\n2. USERSETUP.MEL FILES:")
        for version, version_path in maya_versions:
            scripts_dir = os.path.join(version_path, "scripts")
            usersetup_path = os.path.join(scripts_dir, "userSetup.mel")
            print("   Maya {}: {}".format(version, usersetup_path))
            print("      Scripts dir exists: {}".format(os.path.exists(scripts_dir)))
            print("      userSetup.mel exists: {}".format(os.path.exists(usersetup_path)))
            
            if os.path.exists(usersetup_path):
                with open(usersetup_path, 'r') as f:
                    content = f.read()
                has_prof_entry = "prof" in content.lower()
                print("      Has prof-tools entry: {}".format(has_prof_entry))
                if has_prof_entry:
                    print("      Content preview:")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'prof' in line.lower():
                            print("         Line {}: {}".format(i+1, line.strip()))
    
    # 3. Check prof-tools installation
    print("\n3. PROF-TOOLS INSTALLATION:")
    prof_tools_path = os.path.join(maya_docs_path, "prof-tools")
    print("   Installation path: {}".format(prof_tools_path))
    print("   Exists: {}".format(os.path.exists(prof_tools_path)))
    
    if os.path.exists(prof_tools_path):
        prof_module_path = os.path.join(prof_tools_path, "prof")
        print("   Prof module path: {}".format(prof_module_path))
        print("   Prof module exists: {}".format(os.path.exists(prof_module_path)))
        
        if os.path.exists(prof_module_path):
            init_file = os.path.join(prof_module_path, "__init__.py")
            print("   __init__.py exists: {}".format(os.path.exists(init_file)))
            
            ui_builder_path = os.path.join(prof_module_path, "ui", "builder.py")
            print("   UI builder exists: {}".format(os.path.exists(ui_builder_path)))
    
    # 4. Check Python path
    print("\n4. PYTHON PATH:")
    print("   Current sys.path entries:")
    for i, path in enumerate(sys.path):
        print("      {}: {}".format(i, path))
    
    prof_tools_in_path = prof_tools_path in sys.path
    print("   Prof-tools path in sys.path: {}".format(prof_tools_in_path))
    
    # 5. Test import
    print("\n5. IMPORT TEST:")
    if not prof_tools_in_path and os.path.exists(prof_tools_path):
        print("   Adding prof-tools to sys.path...")
        sys.path.insert(0, prof_tools_path)
    
    try:
        import prof
        print("   ✓ Successfully imported prof module")
        print("   Prof version: {}".format(getattr(prof, '__version__', 'Unknown')))
    except ImportError as e:
        print("   ✗ Failed to import prof module: {}".format(e))
    
    try:
        import prof.ui.builder
        print("   ✓ Successfully imported prof.ui.builder")
    except ImportError as e:
        print("   ✗ Failed to import prof.ui.builder: {}".format(e))
    
    # 6. Menu test
    print("\n6. MENU BUILD TEST:")
    try:
        import maya.cmds as cmds
        # Check if menu already exists
        if cmds.menu("ProfTools", exists=True):
            print("   Prof-Tools menu already exists!")
        else:
            from prof.ui import builder
            result = builder.build_menu()
            if result:
                print("   ✓ Successfully built prof-tools menu")
            else:
                print("   ✗ Failed to build prof-tools menu")
    except Exception as e:
        print("   ✗ Menu build failed: {}".format(e))
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_prof_tools_installation()