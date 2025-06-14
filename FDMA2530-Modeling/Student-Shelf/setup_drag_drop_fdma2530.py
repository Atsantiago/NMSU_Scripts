"""
FDMA 2530 Shelf Installer v1.3
===============================
Drag-and-drop installer for Maya 2016-2025+ with full Python 2/3 compatibility.
Created by: Alexander T. Santiago - asanti89@nmsu.edu
"""

from __future__ import print_function, absolute_import
import os
import sys
import traceback
import tempfile
import shutil

__version__ = "1.3"

# Python 2/3 compatibility for URL handling
try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, URLError

try:
    import maya.cmds as cmds
    import maya.mel as mel
except ImportError:
    raise RuntimeError("This script must be run within Maya")

# ------------------------------------------------------------------ constants
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
SHELF_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf_FDMA_2530.mel"
LOADER_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/utilities/cache_loader.py"

# ----------------------------------------------------------------- utilities
def get_maya_script_dir():
    """Get Maya scripts directory for current version"""
    try:
        return cmds.internalVar(userScriptDir=True)
    except Exception:
        if sys.platform.startswith("win32"):
            maya_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "maya")
        elif sys.platform.startswith("darwin"):
            maya_dir = os.path.expanduser("~/Library/Preferences/Autodesk/maya")
        else:
            maya_dir = os.path.expanduser("~/maya")
        return os.path.join(maya_dir, "scripts")


def get_user_shelf_dir():
    """Get shelf directory for current Maya version"""
    return cmds.internalVar(userShelfDir=True)

def safe_write_file(path, content):
    """Write file with Python 2/3 compatibility"""
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    try:
        import codecs
        with codecs.open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception:
        with open(path, 'w') as f:
            if sys.version_info[0] >= 3:
                f.write(content)
            else:
                f.write(content.encode('utf-8'))

def safe_download(url):
    """Download content with Maya version compatibility"""
    try:
        response = urlopen(url, timeout=15)
        content = response.read()
        
        if sys.version_info[0] >= 3:
            if isinstance(content, bytes):
                content = content.decode("utf-8")
        else:
            if hasattr(content, 'decode'):
                content = content.decode("utf-8")
                
        return content
    except URLError as e:
        cmds.warning("Network error: " + str(e))
        return None
    except Exception as e:
        cmds.warning("Download failed: " + str(e))
        return None

# ----------------------------------------------------------------- main logic
def install_permanent():
    """Install shelf permanently to user directory"""
    try:
        util_dir = os.path.join(get_maya_script_dir(), "utilities")
        if not os.path.exists(util_dir):
            os.makedirs(util_dir)

        loader_content = safe_download(LOADER_URL)
        if not loader_content:
            return False
        safe_write_file(os.path.join(util_dir, "cache_loader.py"), loader_content)

        shelf_content = safe_download(SHELF_URL)
        if not shelf_content:
            return False
        shelf_path = os.path.join(get_user_shelf_dir(), "shelf_FDMA_2530.mel")
        safe_write_file(shelf_path, shelf_content)

        mel.eval('loadNewShelf "{}"'.format(shelf_path.replace("\\", "/")))
        return True

    except Exception as e:
        cmds.warning("Installation failed: " + str(e))
        print(traceback.format_exc())
        return False

def install_temporary():
    """Load shelf temporarily for current session only"""
    try:
        temp_dir = tempfile.gettempdir()
        
        loader_content = safe_download(LOADER_URL)
        if not loader_content:
            return False
        loader_path = os.path.join(temp_dir, "cache_loader.py")
        safe_write_file(loader_path, loader_content)
        
        shelf_content = safe_download(SHELF_URL)
        if not shelf_content:
            return False
        shelf_path = os.path.join(temp_dir, "shelf_FDMA_2530.mel")
        safe_write_file(shelf_path, shelf_content)
        
        if temp_dir not in sys.path:
            sys.path.insert(0, temp_dir)
        
        mel.eval('loadNewShelf "{}"'.format(shelf_path.replace("\\", "/")))
        return True

    except Exception as e:
        cmds.warning("Temporary install failed: " + str(e))
        print(traceback.format_exc())
        return False

def show_install_dialog():
    """Display installation options to user"""
    choice = cmds.confirmDialog(
        title="FDMA 2530 Shelf Installer v{}".format(__version__),
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
            cmds.confirmDialog(
                title="Success", 
                message="FDMA 2530 shelf installed successfully!\nShelf will be available in future Maya sessions.", 
                button=["OK"]
            )
        else:
            cmds.confirmDialog(
                title="Error", 
                message="Installation failed. Check Script Editor for details.", 
                button=["OK"]
            )

    elif choice == "Load Once":
        if install_temporary():
            cmds.confirmDialog(
                title="Success", 
                message="FDMA 2530 shelf loaded temporarily!\nShelf will be removed when Maya closes.", 
                button=["OK"]
            )
        else:
            cmds.confirmDialog(
                title="Error", 
                message="Temporary load failed. Check Script Editor for details.", 
                button=["OK"]
            )

def onMayaDroppedPythonFile(*args):
    """Maya drag-and-drop entry point"""
    try:
        show_install_dialog()
    except Exception as e:
        cmds.warning("Installer error: " + str(e))
        print(traceback.format_exc())

if __name__ == "__main__":
    onMayaDroppedPythonFile()
