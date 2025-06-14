"""
FDMA 2530 Shelf Installer v1.3
==============================
Drag-and-drop this file into Maya to install the FDMA 2530 shelf system.
Works on Windows, macOS, and Linux with Maya 2016-2025+.
"""

from __future__ import print_function, absolute_import
import os
import sys
import traceback
import tempfile
import shutil

# Python 2/3 compatibility
try:
    from urllib.request import urlopen  # Py3
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, URLError  # Py2

try:
    import maya.cmds as cmds
    import maya.mel as mel
except ImportError:
    raise RuntimeError("This script must be run within Maya")

# ========================================================================
# CONFIGURATION
# ========================================================================
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
SHELF_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf_FDMA_2530.mel"
LOADER_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/utilities/cache_loader.py"

# ========================================================================
# PATH UTILITIES
# ========================================================================
def get_maya_script_dir():
    """Get OS-specific Maya scripts directory"""
    if sys.platform.startswith("win32"):
        return os.path.join(os.environ["USERPROFILE"], "Documents", "maya")
    elif sys.platform.startswith("darwin"):
        return os.path.expanduser("~/Library/Preferences/Autodesk/maya")
    else:  # Linux
        return os.path.expanduser("~/maya")

def get_user_shelf_dir():
    """Get shelf directory for current Maya version"""
    return cmds.internalVar(userShelfDir=True)

# ========================================================================
# CORE INSTALLER FUNCTIONS
# ========================================================================
def _safe_download(url):
    """Download content with error handling"""
    try:
        response = urlopen(url, timeout=15)
        return response.read().decode("utf-8")
    except URLError as e:
        cmds.warning("Network error: " + str(e.reason))
        return None

def install_permanent():
    """Permanent installation"""
    try:
        # Create utilities directory
        util_dir = os.path.join(get_maya_script_dir(), "scripts", "utilities")
        os.makedirs(util_dir, exist_ok=True)

        # Install cache loader
        loader_content = _safe_download(LOADER_URL)
        if not loader_content:
            return False
        with open(os.path.join(util_dir, "cache_loader.py"), "w", encoding="utf-8") as f:
            f.write(loader_content)

        # Install shelf
        shelf_content = _safe_download(SHELF_URL)
        if not shelf_content:
            return False
        shelf_path = os.path.join(get_user_shelf_dir(), "shelf_FDMA_2530.mel")
        with open(shelf_path, "w", encoding="utf-8") as f:
            f.write(shelf_content)

        # Load shelf
        mel.eval('loadNewShelf "{}"'.format(shelf_path.replace("\\", "/")))
        return True

    except Exception as e:
        cmds.warning("Installation failed: " + str(e))
        return False

def install_temporary():
    """Temporary session installation"""
    try:
        temp_dir = tempfile.gettempdir()
        
        # Download loader
        loader_content = _safe_download(LOADER_URL)
        loader_path = os.path.join(temp_dir, "cache_loader.py")
        with open(loader_path, "w", encoding="utf-8") as f:
            f.write(loader_content)
        
        # Download shelf
        shelf_content = _safe_download(SHELF_URL)
        shelf_path = os.path.join(temp_dir, "shelf_FDMA_2530.mel")
        with open(shelf_path, "w", encoding="utf-8") as f:
            f.write(shelf_content)
        
        # Add to Python path and load
        sys.path.insert(0, temp_dir)
        mel.eval('loadNewShelf "{}"'.format(shelf_path.replace("\\", "/")))
        return True

    except Exception as e:
        cmds.warning("Temporary install failed: " + str(e))
        return False

# ========================================================================
# USER INTERFACE
# ========================================================================
def show_install_dialog():
    """GT-Tools style installation dialog"""
    choice = cmds.confirmDialog(
        title="FDMA 2530 Shelf Installer",
        message="Choose installation type:\n\n"
                "Install Shelf: Permanent installation\n"
                "Load Once: Temporary for this session\n"
                "Cancel: Do nothing",
        button=["Install Shelf", "Load Once", "Cancel"],
        defaultButton="Install Shelf",
        cancelButton="Cancel",
        dismissString="Cancel"
    )

    if choice == "Install Shelf":
        if install_permanent():
            cmds.confirmDialog(title="Success", message="Shelf installed!", button=["OK"])
        else:
            cmds.confirmDialog(title="Error", message="Installation failed!", button=["OK"])

    elif choice == "Load Once":
        if install_temporary():
            cmds.confirmDialog(title="Success", message="Shelf loaded!", button=["OK"])
        else:
            cmds.confirmDialog(title="Error", message="Load failed!", button=["OK"])

# ========================================================================
# ENTRY POINT
# ========================================================================
def onMayaDroppedPythonFile(*_):
    """Maya drag-and-drop handler"""
    show_install_dialog()

if __name__ == "__main__":
    onMayaDroppedPythonFile()

