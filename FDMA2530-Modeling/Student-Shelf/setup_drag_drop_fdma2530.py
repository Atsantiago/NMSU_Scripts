"""
FDMA 2530 Shelf Installer v1.2.1 - STREAMLINED VERSION
======================================================

Optimized drag-and-drop installer for Maya 2016-2025+ with essential
functionality.

Features:
- Fast installation with minimal overhead
- Python 2/3 compatibility across all Maya versions
- Essential error handling without complexity
- Cross-platform support (Windows, macOS, Linux)
- Clean, maintainable code following best practices

Created by: Alexander T. Santiago - asanti89@nmsu.edu
"""

import os
import sys
import tempfile

# Python 2/3 compatibility - minimal approach
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

# ============================================================================
# CONFIGURATION
# ============================================================================

__version__ = "1.2.1"

# Repository URLs
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
SHELF_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf_FDMA_2530.mel"
LOADER_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/utilities/cache_loader.py"
SHELF_NAME = "FDMA_2530"
# ============================================================================
# CORE UTILITIES
# ============================================================================

""""
def get_maya_directories():
    """Get Maya script and shelf directories with fallbacks"""
    try:
        script_dir = cmds.internalVar(userScriptDir=True)
        shelf_dir = cmds.internalVar(userShelfDir=True)
        return script_dir, shelf_dir
    except Exception:
        # Simple fallback for any Maya API failures
        if sys.platform.startswith("win"):
            base_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "maya")
        elif sys.platform.startswith("darwin"):
            base_dir = os.path.expanduser("~/Library/Preferences/Autodesk/maya")
        else:
            base_dir = os.path.expanduser("~/maya")
        
        script_dir = os.path.join(base_dir, "scripts")
        shelf_dir = os.path.join(base_dir, "prefs", "shelves")
        return script_dir, shelf_dir
"""
    
    def safe_download(url):
    try:
        response = urlopen(url, timeout=15)
        content = response.read()
        if sys.version_info[0] >= 3 and isinstance(content, bytes):
            content = content.decode("utf-8")
        return content
    except Exception as e:
        cmds.warning("Download failed: " + str(e))
        return None

def safe_write(path, content):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    if sys.version_info[0] >= 3:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        import codecs
        with codecs.open(path, 'w', encoding='utf-8') as f:
            f.write(content)

def cleanup_existing_shelf():
    """Clean up existing shelf using the working pattern"""
    try:
        # Use the working pattern from your old code
        if cmds.shelfLayout(SHELF_NAME, exists=True):
            cmds.deleteUI(SHELF_NAME, layout=True)  # KEY: layout=True parameter
            print("Removed existing shelf UI")
        return True
    except Exception as e:
        print("Shelf cleanup warning: " + str(e))
        return True  # Continue anyway

def load_and_show_shelf(shelf_path):
    """Load shelf and make it visible in the UI"""
    try:
        # Load the shelf
        shelf_path_mel = shelf_path.replace("\\", "/")
        mel.eval('loadNewShelf "{}"'.format(shelf_path_mel))
        
        # Get the main shelf tab layout
        shelf_tab_layout = mel.eval('$tempVar = $gShelfTopLevel')
        
        # Verify shelf loaded and make it visible
        if cmds.shelfLayout(SHELF_NAME, exists=True):
            # Select the shelf tab to make it visible
            if shelf_tab_layout:
                cmds.shelfTabLayout(shelf_tab_layout, edit=True, selectTab=SHELF_NAME)
            print("Shelf loaded and displayed successfully!")
            return True
        else:
            print("Shelf failed to load")
            return False
            
    except Exception as e:
        print("Error loading shelf: " + str(e))
        return False

def install_permanent():
    try:
        script_dir = cmds.internalVar(userScriptDir=True)
        shelf_dir = cmds.internalVar(userShelfDir=True)
        
        # Clean up existing shelf FIRST
        cleanup_existing_shelf()
        
        # Download cache_loader
        loader_content = safe_download(LOADER_URL)
        if not loader_content:
            return False
        
        loader_path = os.path.join(script_dir, "utilities", "cache_loader.py")
        safe_write(loader_path, loader_content)
        
        # Download shelf
        shelf_content = safe_download(SHELF_URL)
        if not shelf_content:
            return False
        
        # Write shelf file
        shelf_path = os.path.join(shelf_dir, "shelf_FDMA_2530.mel")
        safe_write(shelf_path, shelf_content)
        
        # Load shelf and make it visible
        return load_and_show_shelf(shelf_path)
        
    except Exception as e:
        cmds.warning("Installation failed: " + str(e))
        return False

def install_temporary():
    try:
        temp_dir = tempfile.gettempdir()
        
        # Clean up existing shelf FIRST
        cleanup_existing_shelf()
        
        # Download cache_loader
        loader_content = safe_download(LOADER_URL)
        if not loader_content:
            return False
        
        loader_path = os.path.join(temp_dir, "cache_loader.py")
        safe_write(loader_path, loader_content)
        
        if temp_dir not in sys.path:
            sys.path.insert(0, temp_dir)
        
        # Download shelf
        shelf_content = safe_download(SHELF_URL)
        if not shelf_content:
            return False
        
        # Write temporary shelf file
        shelf_path = os.path.join(temp_dir, "shelf_FDMA_2530.mel")
        safe_write(shelf_path, shelf_content)
        
        # Load shelf and make it visible
        return load_and_show_shelf(shelf_path)
        
    except Exception as e:
        cmds.warning("Temporary installation failed: " + str(e))
        return False

def show_install_dialog():
    choice = cmds.confirmDialog(
        title="FDMA 2530 Shelf Installer v{}".format(__version__),
        message="Choose installation type:\n\nInstall Shelf: Permanent\nLoad Once: Temporary",
        button=["Install Shelf", "Load Once", "Cancel"],
        defaultButton="Install Shelf",
        cancelButton="Cancel"
    )
    
    if choice == "Install Shelf":
        if install_permanent():
            cmds.confirmDialog(title="Success", message="Shelf installed successfully!", button=["OK"])
        else:
            cmds.confirmDialog(title="Error", message="Installation failed.", button=["OK"])
    elif choice == "Load Once":
        if install_temporary():
            cmds.confirmDialog(title="Success", message="Shelf loaded temporarily!", button=["OK"])
        else:
            cmds.confirmDialog(title="Error", message="Temporary load failed.", button=["OK"])

def onMayaDroppedPythonFile(*args):
    try:
        show_install_dialog()
    except Exception as e:
        cmds.warning("Installer error: " + str(e))

if __name__ == "__main__":
    onMayaDroppedPythonFile()
