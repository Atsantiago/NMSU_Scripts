"""
FDMA 2530 Shelf Installer v1.3.0 - COMPLETE DRAG-DROP SOLUTION
================================================================
Handles Maya UI timing, module reloading, and robust shelf creation
Cross-platform compatible: Windows, macOS, Linux
Maya versions: 2016-2025+ | Python 2/3 compatible
"""

import os
import sys
import tempfile
import importlib

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import maya.cmds as cmds
import maya.mel as mel

__version__ = "1.3.0"

# Configuration
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
SHELF_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf_FDMA_2530.mel"
LOADER_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/utilities/cache_loader.py"
SHELF_NAME = "FDMA_2530"

def safe_download(url):
    """Download content from URL with error handling"""
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
    """Write content to file with directory creation"""
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
    """Clean up existing shelf"""
    try:
        if cmds.shelfLayout(SHELF_NAME, exists=True):
            cmds.deleteUI(SHELF_NAME, layout=True)
            print("Removed existing shelf UI")
        return True
    except Exception as e:
        print("Shelf cleanup warning: " + str(e))
        return True

def create_shelf_directly():
    """Create shelf directly in Python - bypasses MEL timing issues"""
    try:
        # Get the shelf top level using Python - much more reliable
        gShelfTopLevel = mel.eval('global string $gShelfTopLevel; $temp = $gShelfTopLevel')
        
        # If still empty, force UI refresh and try again
        if not gShelfTopLevel:
            cmds.refresh(force=True)
            # Process any pending idle events
            try:
                import maya.utils
                maya.utils.processIdleEvents()
            except:
                pass
            gShelfTopLevel = mel.eval('global string $gShelfTopLevel; $temp = $gShelfTopLevel')
        
        if not gShelfTopLevel:
            cmds.warning("Maya shelf system not ready")
            return False
        
        print("Using shelf parent: " + gShelfTopLevel)
        
        # Remove existing shelf
        cleanup_existing_shelf()
        
        # Create new shelf
        shelf = cmds.shelfLayout(SHELF_NAME, parent=gShelfTopLevel, cellWidth=35, cellHeight=35)
        print("Created shelf layout: " + shelf)
        
        # Add Checklist button
        cmds.shelfButton(
            parent=shelf,
            label="Checklist",
            image1="checkboxOn.png",
            annotation="CMI Modeling Checklist v3.0",
            command='python("from utilities.cache_loader import load_execute; load_execute(\'https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/core-scripts/cmi_modeling_checklist.py\', \'checklist.py\')")'
        )
        
        # Add separator
        cmds.separator(parent=shelf, width=12)
        
        # Add Update button
        cmds.shelfButton(
            parent=shelf,
            label="Update", 
            image1="updateApp.png",
            annotation="FDMA 2530 Shelf Updater v1.2.1",
            command='python("from utilities.cache_loader import load_execute; load_execute(\'https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/shelf-button-scripts/update_shelf.py\', \'update.py\')")'
        )
        
        print("Added shelf buttons")
        
        # Activate the shelf
        if cmds.control(gShelfTopLevel, exists=True) and cmds.control(shelf, exists=True):
            cmds.tabLayout(gShelfTopLevel, edit=True, selectTab=shelf)
            print("FDMA_2530 shelf created and activated successfully")
        
        return True
        
    except Exception as e:
        cmds.warning("Failed to create shelf: " + str(e))
        return False

def install_cache_loader(use_temp=False):
    """Download and install the cache_loader utility"""
    try:
        # Download cache_loader
        loader_content = safe_download(LOADER_URL)
        if not loader_content:
            return False
        
        if use_temp:
            # Temporary installation
            temp_dir = tempfile.gettempdir()
            loader_path = os.path.join(temp_dir, "utilities", "cache_loader.py")
            if temp_dir not in sys.path:
                sys.path.insert(0, temp_dir)
        else:
            # Permanent installation
            script_dir = cmds.internalVar(userScriptDir=True)
            loader_path = os.path.join(script_dir, "utilities", "cache_loader.py")
        
        safe_write(loader_path, loader_content)
        print("Cache loader installed at: " + loader_path)
        return True
        
    except Exception as e:
        cmds.warning("Cache loader installation failed: " + str(e))
        return False

def install_permanent():
    """Install shelf permanently"""
    try:
        # Install cache loader
        if not install_cache_loader(use_temp=False):
            return False
        
        # Create shelf directly in Python
        return create_shelf_directly()
        
    except Exception as e:
        cmds.warning("Installation failed: " + str(e))
        return False

def install_temporary():
    """Install shelf temporarily"""
    try:
        # Install cache loader to temp directory
        if not install_cache_loader(use_temp=True):
            return False
        
        # Create shelf directly in Python
        return create_shelf_directly()
        
    except Exception as e:
        cmds.warning("Temporary installation failed: " + str(e))
        return False

def show_install_dialog():
    """Show installation dialog"""
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

def force_reload_self():
    """Force reload this module to handle Maya's caching issue"""
    try:
        # Get the current module name
        current_module = __name__
        if current_module in sys.modules:
            if sys.version_info[0] >= 3:
                importlib.reload(sys.modules[current_module])
            else:
                reload(sys.modules[current_module])
    except:
        pass  # Ignore reload errors

def onMayaDroppedPythonFile(*args):
    """Maya's drag-and-drop entry point"""
    try:
        # Force reload to handle Maya's caching bug
        force_reload_self()
        
        # Show installation dialog
        show_install_dialog()
        
    except Exception as e:
        cmds.warning("Installer error: " + str(e))
        import traceback
        print(traceback.format_exc())

# Execute if run directly (for testing)
if __name__ == "__main__":
    onMayaDroppedPythonFile()
