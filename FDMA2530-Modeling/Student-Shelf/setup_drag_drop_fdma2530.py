"""
FDMA 2530 Shelf Installer v1.2.3 
================================================================
Cross-platform compatible: Windows, macOS, Linux
Maya versions: 2016-2025+ | Python 2/3 compatible
Alexander Santiago 
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

__version__ = "1.2.3"

# Configuration
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
SHELF_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf_FDMA_2530.mel"
LOADER_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/utilities/cache_loader.py"
CHECKLIST_SCRIPT_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf-button-scripts/shelf_run-cmi_modeling_checklist.py"
UPDATE_SCRIPT_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf-button-scripts/update_shelf.py"
CHECKLIST_MAIN_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/core-scripts/cmi_modeling_checklist.py"
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

def create_shelf_with_working_buttons():
    """Create shelf with properly configured buttons that execute correctly"""
    try:
        # Get the shelf top level using Python - much more reliable
        gShelfTopLevel = mel.eval('global string $gShelfTopLevel; $temp = $gShelfTopLevel')
        
        # If still empty, force UI refresh and try again
        if not gShelfTopLevel:
            cmds.refresh(force=True)
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
        
        # FIXED Checklist button command that properly handles namespace issues
        checklist_command = '''
# Fixed namespace execution for Maya GUI scripts
import sys
import os
import tempfile
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

def execute_checklist_fixed():
    """Execute checklist with proper namespace handling"""
    try:
        # Download the main checklist script directly (not the loader)
        url = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/core-scripts/cmi_modeling_checklist.py"
        response = urlopen(url, timeout=15)
        content = response.read()
        if sys.version_info[0] >= 3 and isinstance(content, bytes):
            content = content.decode("utf-8")
        
        # Create a proper execution namespace that persists in Maya
        execution_namespace = globals().copy()
        execution_namespace.update(locals())
        
        # Execute the script in the correct namespace
        exec(content, execution_namespace, execution_namespace)
        
        # Call the main GUI function directly from the namespace
        if 'build_gui_ats_cmi_modeling_checklist' in execution_namespace:
            execution_namespace['build_gui_ats_cmi_modeling_checklist']()
            print("CMI Modeling Checklist loaded successfully!")
        else:
            print("Warning: GUI function not found in downloaded script")
        
    except Exception as e:
        import maya.cmds as cmds
        cmds.warning("Failed to load checklist: " + str(e))
        import traceback
        print(traceback.format_exc())

execute_checklist_fixed()
'''
        
        # FIXED Update button command
        update_command = '''
# Fixed namespace execution for update script
import sys
import os
import tempfile
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

def execute_update_fixed():
    """Execute update script with proper namespace handling"""
    try:
        # Download and execute the update script directly
        url = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/shelf-button-scripts/update_shelf.py"
        response = urlopen(url, timeout=15)
        content = response.read()
        if sys.version_info[0] >= 3 and isinstance(content, bytes):
            content = content.decode("utf-8")
        
        # Create a proper execution namespace
        execution_namespace = globals().copy()
        execution_namespace.update(locals())
        
        # Execute the script in the correct namespace
        exec(content, execution_namespace, execution_namespace)
        print("Update script executed successfully!")
        
    except Exception as e:
        import maya.cmds as cmds
        cmds.warning("Failed to load update script: " + str(e))
        import traceback
        print(traceback.format_exc())

execute_update_fixed()
'''
        
        # Add Checklist button 
        cmds.shelfButton(
            parent=shelf,
            label="Checklist",
            image1="checkboxOn.png",
            annotation="CMI Modeling Checklist v3.0",
            command=checklist_command
        )
        
        # Add separator
        cmds.separator(parent=shelf, width=12)
        
        # Add Update button 
        cmds.shelfButton(
            parent=shelf,
            label="Update", 
            image1="updateApp.png",
            annotation="FDMA 2530 Shelf Updater v1.3.1",
            command=update_command
        )
        
        print("Added shelf buttons with FIXED namespace-aware commands")
        
        # Activate the shelf
        if cmds.control(gShelfTopLevel, exists=True) and cmds.control(shelf, exists=True):
            cmds.tabLayout(gShelfTopLevel, edit=True, selectTab=shelf)
            print("FDMA_2530 shelf created and activated successfully")
        
        return True
        
    except Exception as e:
        cmds.warning("Failed to create shelf: " + str(e))
        import traceback
        print(traceback.format_exc())
        return False

def install_permanent():
    """Install shelf permanently with fixed button commands"""
    try:
        return create_shelf_with_working_buttons()
    except Exception as e:
        cmds.warning("Installation failed: " + str(e))
        return False

def install_temporary():
    """Install shelf temporarily with fixed button commands"""
    try:
        return create_shelf_with_working_buttons()
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
            cmds.confirmDialog(
                title="Success", 
                message="Shelf installed successfully!", 
                button=["OK"]
            )
        else:
            cmds.confirmDialog(title="Error", message="Installation failed.", button=["OK"])
    elif choice == "Load Once":
        if install_temporary():
            cmds.confirmDialog(
                title="Success", 
                message="Shelf loaded temporarily!", 
                button=["OK"]
            )
        else:
            cmds.confirmDialog(title="Error", message="Temporary load failed.", button=["OK"])

def force_reload_self():
    """Force reload this module to handle Maya's caching issue"""
    try:
        current_module = __name__
        if current_module in sys.modules:
            if sys.version_info[0] >= 3:
                importlib.reload(sys.modules[current_module])
            else:
                reload(sys.modules[current_module])
    except:
        pass

def onMayaDroppedPythonFile(*args):
    """Maya's drag-and-drop entry point"""
    try:
        force_reload_self()
        show_install_dialog()
    except Exception as e:
        cmds.warning("Installer error: " + str(e))
        import traceback
        print(traceback.format_exc())

# Execute if run directly (for testing)
if __name__ == "__main__":
    onMayaDroppedPythonFile()
