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

def safe_download(url):
    """Download content with basic error handling"""
    try:
        response = urlopen(url, timeout=15)
        content = response.read()
        
        # Handle Python 3 encoding
        if sys.version_info[0] >= 3 and isinstance(content, bytes):
            content = content.decode("utf-8")
        
        return content
    except Exception as e:
        cmds.warning("Download failed: " + str(e))
        return None

def safe_write(path, content):
    """Write file with directory creation and encoding handling"""
    # Create directory if needed
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Write with appropriate encoding
    if sys.version_info[0] >= 3:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        # Python 2 - use codecs for UTF-8
        import codecs
        with codecs.open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# ============================================================================
# INSTALLATION FUNCTIONS
# ============================================================================

def install_permanent():
    """Install shelf permanently with essential error handling"""
    try:
        script_dir, shelf_dir = get_maya_directories()
        
        # Remove existing shelf UI and files
        if cmds.shelfLayout(SHELF_NAME, exists=True):
            cmds.deleteUI(SHELF_NAME)
            print("Removed existing shelf UI")
        mel.eval(f'deleteShelfTab "{SHELF_NAME}"')  # Clean preferences
        
        # Delete existing shelf MEL file
        shelf_path = os.path.join(shelf_dir, "shelf_FDMA_2530.mel")
        if os.path.exists(shelf_path):
            os.remove(shelf_path)
            print("Removed existing shelf file")
        
        # Clean preferences (from search result [11])
        mel.eval('evalDeferred("deleteShelfTab FDMA_2530")')
        
        # Download and install cache_loader
        loader_content = safe_download(LOADER_URL)
        if not loader_content:
            return False
        
        loader_path = os.path.join(script_dir, "utilities", "cache_loader.py")
        safe_write(loader_path, loader_content)
                    
        # Download and install shelf
        shelf_content = safe_download(SHELF_URL)
        if not shelf_content:
            return False
        
        shelf_path = os.path.join(shelf_dir, "shelf_FDMA_2530.mel")
        safe_write(shelf_path, shelf_content)
        
        # Load shelf in Maya
        shelf_path_mel = shelf_path.replace("\\", "/")  # MEL needs forward slashes
        mel.eval('loadNewShelf "{}"'.format(shelf_path_mel))
        
        return True
        
    except Exception as e:
        cmds.warning("Installation failed: " + str(e))
        return False

def install_temporary():
    """Install shelf temporarily for current session"""
    try:
        temp_dir = tempfile.gettempdir()
        
        # Remove existing temporary shelf
        if cmds.shelfLayout(SHELF_NAME, exists=True):
            cmds.deleteUI(SHELF_NAME)
            print("Removed existing temporary shelf UI")
        mel.eval(f'deleteShelfTab "{SHELF_NAME}"')  # Clean preferences
        
        # Clean temporary preferences
        mel.eval('evalDeferred("deleteShelfTab FDMA_2530")')

        # Download and cache loader
        loader_content = safe_download(LOADER_URL)
        if not loader_content:
            return False
        
        loader_path = os.path.join(temp_dir, "cache_loader.py")
        safe_write(loader_path, loader_content)
        

        # Add temp directory to Python path
        if temp_dir not in sys.path:
            sys.path.insert(0, temp_dir)
        
        # Download and install shelf temporarily
        shelf_content = safe_download(SHELF_URL)
        if not shelf_content:
            return False
        
        shelf_path = os.path.join(temp_dir, "shelf_FDMA_2530.mel")
        safe_write(shelf_path, shelf_content)
        
        # Load shelf in Maya
        shelf_path_mel = shelf_path.replace("\\", "/")
        mel.eval('loadNewShelf "{}"'.format(shelf_path_mel))
        
        return True
        
    except Exception as e:
        cmds.warning("Temporary installation failed: " + str(e))
        return False

# ============================================================================
# USER INTERFACE
# ============================================================================

def show_install_dialog():
    """Simple installation dialog"""
    choice = cmds.confirmDialog(
        title="FDMA 2530 Shelf Installer v{}".format(__version__),
        message=(
            "Choose installation type:\n\n"
            "INSTALL SHELF:\n"
            "• Permanent installation for all Maya sessions\n"
            "• Includes smart caching for fast loading\n\n"
            "LOAD ONCE:\n"
            "• Temporary installation for current session only\n"
            "• Perfect for testing\n\n"
            "Platform: {} | Python: {}.{}"
        ).format(
            "Windows" if sys.platform.startswith("win") else
            "macOS" if sys.platform.startswith("darwin") else "Linux",
            sys.version_info[0], sys.version_info[1]
        ),
        button=["Install Shelf", "Load Once", "Cancel"],
        defaultButton="Install Shelf",
        cancelButton="Cancel",
        dismissString="Cancel"
    )
    
    if choice == "Install Shelf":
        if install_permanent():
            cmds.confirmDialog(
                title="Installation Successful",
                message=(
                    "FDMA 2530 shelf installed successfully!\n\n"
                    "The shelf is now available in all Maya sessions.\n"
                ),
                button=["Great!"]
            )
        else:
            cmds.confirmDialog(
                title="Installation Failed",
                message=(
                    "Installation failed. Please check:\n"
                    "• Internet connection\n"
                    "• GitHub access\n"
                    "• Maya console for detailed errors\n\n"
                    "Contact: asanti89@nmsu.edu"
                ),
                button=["OK"]
            )
    
    elif choice == "Load Once":
        if install_temporary():
            cmds.confirmDialog(
                title="Temporary Load Successful",
                message=(
                    "FDMA 2530 shelf loaded for this session!\n\n"
                    "The shelf will be removed when Maya closes.\n"
                    "To make it permanent, run installer again."
                ),
                button=["Got it!"]
            )
        else:
            cmds.confirmDialog(
                title="Temporary Load Failed",
                message=(
                    "Temporary load failed. Please check:\n"
                    "• Internet connection\n"
                    "• GitHub access\n"
                    "• Maya console for detailed errors\n\n"
                    "Contact: asanti89@nmsu.edu"
                ),
                button=["OK"]
            )

# ============================================================================
# MAYA DRAG-AND-DROP ENTRY POINT
# ============================================================================

def onMayaDroppedPythonFile(*args):
    """
    Maya drag-and-drop entry point.
    
    This function is called automatically when the Python file is
    dragged and dropped into Maya's viewport.
    """
    try:
        show_install_dialog()
    except Exception as e:
        cmds.warning("Installer error: " + str(e))
        # Show emergency dialog
        try:
            cmds.confirmDialog(
                title="Installer Error",
                message=(
                    "The installer encountered an error.\n\n"
                    "Error: {}\n\n"
                    "Contact: asanti89@nmsu.edu"
                ).format(str(e)),
                button=["OK"]
            )
        except:
            print("CRITICAL INSTALLER ERROR: {}".format(str(e)))

# ============================================================================
# DIRECT EXECUTION SUPPORT
# ============================================================================

if __name__ == "__main__":
    # Support direct execution for testing
    onMayaDroppedPythonFile()
