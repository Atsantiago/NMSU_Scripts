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
def _safe_write(path, data):
    """Write *data* (str) to *path*, creating folders as needed."""
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    # ADD ENCODING PARAMETER
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(data)

# ===========================================================================
# USER INTERFACE
# ===========================================================================
def _show_install_dialog():
    # Replace Unicode arrows with ASCII equivalents
    message=(
        "Choose installation type:\n\n"
        "- Install Shelf: Permanent installation\n"  
        "- Load Once: Temporary for this session\n"  
        "- Cancel: Do nothing"
    )


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
