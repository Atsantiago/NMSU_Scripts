"""
FDMA 2530 Shelf Installer v1.2
===============================
Drag-and-drop this file into Maya's viewport to install/update the FDMA 2530 shelf system.
Provides Python 2/3 compatibility and user-friendly options.

Features:
- Install Shelf (persistent)
- Load Once (temporary session)
- Cancel
- Visual feedback with Maya dialogs
- Automatic dependency handling

Created by: Alexander T. Santiago
GitHub: github.com/atsantiago
Repository: https://github.com/Atsantiago/NMSU_Scripts
"""

from __future__ import print_function, absolute_import
import os
import sys
import traceback

# Python 2/3 compatibility
try:
    from urllib.request import urlopen  # Py3
except ImportError:
    from urllib2 import urlopen  # Py2

# Maya imports with error handling
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# ===========================================================================
# CONFIGURATION
# ===========================================================================
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
SHELF_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf_FDMA_2530.mel"
LOADER_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/utilities/cache_loader.py"

# ===========================================================================
# CORE FUNCTIONS
# ===========================================================================
def _maya_script_dir():
    """Get Maya's user script directory with Python 2/3 safety."""
    try:
        return cmds.internalVar(userScriptDir=True)
    except Exception:
        return os.path.join(os.path.expanduser('~'), 'maya', 'scripts')

def _install_files():
    """Download and install required files."""
    script_dir = _maya_script_dir()
    
    # Create utilities directory if needed
    util_dir = os.path.join(script_dir, 'utilities')
    if not os.path.exists(util_dir):
        os.makedirs(util_dir)
    
    # Download cache_loader.py
    loader_path = os.path.join(util_dir, 'cache_loader.py')
    with open(loader_path, 'wb') as f:
        f.write(urlopen(LOADER_URL).read())
    
    # Download shelf file
    shelf_dir = cmds.internalVar(userShelfDir=True)
    shelf_path = os.path.join(shelf_dir, 'shelf_FDMA_2530.mel')
    with open(shelf_path, 'wb') as f:
        f.write(urlopen(SHELF_URL).read())
    
    return shelf_path

def _load_temp_shelf():
    """Load shelf temporarily without installation."""
    temp_dir = tempfile.gettempdir()
    
    # Download loader to temp
    loader_path = os.path.join(temp_dir, 'cache_loader.py')
    with open(loader_path, 'wb') as f:
        f.write(urlopen(LOADER_URL).read())
    
    # Download shelf to temp
    shelf_path = os.path.join(temp_dir, 'shelf_FDMA_2530.mel')
    with open(shelf_path, 'wb') as f:
        f.write(urlopen(SHELF_URL).read())
    
    # Add temp to Python path
    if temp_dir not in sys.path:
        sys.path.insert(0, temp_dir)
    
    return shelf_path

# ===========================================================================
# USER INTERFACE
# ===========================================================================
def _show_install_dialog():
    """Style installation dialog."""
    choice = cmds.confirmDialog(
        title='FDMA 2530 Shelf Installer',
        message=(
            "Choose installation type:\n\n"
            "• Install Shelf - Permanent installation\n"
            "• Load Once - Temporary for this session\n"
            "• Cancel - Do nothing"
        ),
        button=['Install Shelf', 'Load Once', 'Cancel'],
        defaultButton='Install Shelf',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    
    if choice == 'Install Shelf':
        try:
            shelf_path = _install_files()
            cmds.confirmDialog(
                title='Success',
                message='Shelf installed successfully!\nRestart Maya to see changes.',
                button=['OK']
            )
            if MAYA_AVAILABLE:
                mel.eval('loadNewShelf "{0}"'.format(shelf_path.replace('\\', '/')))
        except Exception as e:
            cmds.confirmDialog(
                title='Error',
                message='Installation failed:\n{}'.format(str(e)),
                button=['OK']
            )
            print(traceback.format_exc())
    
    elif choice == 'Load Once':
        try:
            shelf_path = _load_temp_shelf()
            mel.eval('loadNewShelf "{0}"'.format(shelf_path.replace('\\', '/')))
            cmds.confirmDialog(
                title='Success',
                message='Shelf loaded temporarily!\nChanges will reset on Maya restart.',
                button=['OK']
            )
        except Exception as e:
            cmds.confirmDialog(
                title='Error',
                message='Temporary load failed:\n{}'.format(str(e)),
                button=['OK']
            )
            print(traceback.format_exc())

# ===========================================================================
# ENTRY POINT 
# ===========================================================================
def onMayaDroppedPythonFile(*args):
    """Maya drag-and-drop entry point."""
    if not MAYA_AVAILABLE:
        cmds.warning("Maya not detected - cannot install shelf")
        return
    
    # Python version check
    if sys.version_info[0] < 2:
        cmds.confirmDialog(
            title='Python Error',
            message='Python 2.7 or newer required',
            button=['OK']
        )
        return
    
    _show_install_dialog()

# CLI support
if __name__ == "__main__":
    onMayaDroppedPythonFile()
