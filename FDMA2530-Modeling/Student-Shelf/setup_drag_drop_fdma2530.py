"""
FDMA 2530 Shelf Installer v1.2.4 - JSON CONFIGURATION APPROACH
================================================================
Dynamic shelf creation from JSON configuration on GitHub
Cross-platform compatible: Windows, macOS, Linux
Maya versions: 2016-2025+ | Python 2/3 compatible
"""

import os
import sys
import tempfile
import importlib
import json

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import maya.cmds as cmds
import maya.mel as mel

__version__ = "1.2.4"

# Configuration URLs
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
CONFIG_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/shelf_config.json"
LOADER_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/utilities/cache_loader.py"
SHELF_NAME = "FDMA_2530"

# Visual status button colors (Maya RGB values)
BUTTON_COLORS = {
    'up_to_date': [0.5, 0.5, 0.5],        # Gray
    'updates_available': [0.2, 0.8, 0.2], # Green
    'update_failed': [0.8, 0.2, 0.2],     # Red
    'checking': [0.8, 0.8, 0.2]           # Yellow
}

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

def update_button_visual_status(label, status):
    """Set backgroundColor on the first shelfButton whose label matches *label*"""
    try:
        if not cmds.shelfLayout(SHELF_NAME, exists=True):
            return
        for btn in cmds.shelfLayout(SHELF_NAME, q=True, childArray=True) or []:
            if cmds.objectTypeUI(btn) == 'shelfButton' and cmds.shelfButton(btn, q=True, label=True) == label:
                cmds.shelfButton(btn, e=True, backgroundColor=BUTTON_COLORS.get(status, [0.5, 0.5, 0.5]))
                break
    except RuntimeError:
        pass

def viewport_yellow_alert(msg):
    """Single-shot yellow banner in lower-left of viewport"""
    if not hasattr(viewport_yellow_alert, '_fired'):
        viewport_yellow_alert._fired = False
    
    if not viewport_yellow_alert._fired:
        cmds.inViewMessage(
            amg='<span style="color:#FFF00">{}</span>'.format(msg),
            pos='botLeft',
            fade=True,
            alpha=0.95,
            dragKill=False,
            fadeStayTime=3000
        )
        viewport_yellow_alert._fired = True

def download_json_config():
    """Download and parse the JSON configuration file"""
    try:
        print("Downloading shelf configuration from GitHub...")
        config_content = safe_download(CONFIG_URL)
        if not config_content:
            return None
        
        # Parse JSON configuration
        config = json.loads(config_content)
        print("Configuration loaded successfully. Version: " + config['shelf_info']['version'])
        return config
        
    except Exception as e:
        cmds.warning("Failed to load configuration: " + str(e))
        return None

def cleanup_existing_shelf(shelf_name):
    """Clean up existing shelf"""
    try:
        if cmds.shelfLayout(shelf_name, exists=True):
            cmds.deleteUI(shelf_name, layout=True)
            print("Removed existing shelf: " + shelf_name)
        return True
    except Exception as e:
        print("Shelf cleanup warning: " + str(e))
        return True

def create_button_command(script_url):
    """Create a self-contained button command that downloads and executes a script"""
    command_template = '''
# Auto-generated button command for: {script_url}
import sys
import tempfile
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

def execute_script():
    """Download and execute script with proper namespace handling"""
    try:
        url = "{script_url}"
        response = urlopen(url, timeout=15)
        content = response.read()
        if sys.version_info[0] >= 3 and isinstance(content, bytes):
            content = content.decode("utf-8")
        
        # Create a proper execution namespace that persists in Maya
        execution_namespace = globals().copy()
        execution_namespace.update(locals())
        
        # Execute the script in the correct namespace
        exec(content, execution_namespace, execution_namespace)
        
        # Try to call common entry point functions
        for func_name in ['build_gui_ats_cmi_modeling_checklist', 'main', 'run', 'start']:
            if func_name in execution_namespace:
                execution_namespace[func_name]()
                print("Script executed successfully via: " + func_name)
                return
        
        print("Script executed successfully!")
        
    except Exception as e:
        import maya.cmds as cmds
        cmds.warning("Failed to execute script: " + str(e))
        import traceback
        print(traceback.format_exc())

execute_script()
'''
    return command_template.format(script_url=script_url)

def create_update_button_command(script_url):
    """Specialized command for the Update button with correct deferred rebuild."""
    return '''
import sys, hashlib, os, json, tempfile
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import maya.cmds as cmds
import maya.utils

# Helper to change button color
update_button_visual_status = globals().get('update_button_visual_status')

label = "Update"
if update_button_visual_status:
    update_button_visual_status(label, "checking")

def safe_download(url):
    try:
        data = urlopen(url, timeout=15).read()
        if sys.version_info[0] >= 3 and isinstance(data, bytes):
            data = data.decode("utf-8")
        return data
    except Exception as e:
        cmds.warning("Download failed: " + str(e))
        return None

def show_up_to_date_message():
    cmds.inViewMessage(
        amg='<span style="color:#FFCC00">You are already on the latest version</span>',
        pos='botLeft', fade=True, alpha=0.9, dragKill=False, fadeStayTime=3000
    )

def show_update_confirmation_dialog():
    choice = cmds.confirmDialog(
        title='New Updates Available',
        message='New Updates Available. Would you like to update the shelf?',
        button=['Yes', 'No'], defaultButton='Yes', cancelButton='No'
    )
    return choice == 'Yes'

def rebuild_shelf(latest_config):
    """Deferred function to safely delete and recreate the shelf."""
    try:
        # Parse new config
        config = json.loads(latest_config)
        shelf_name = config['shelf_info']['name']

        # Delete old shelf
        if cmds.shelfLayout(shelf_name, exists=True):
            cmds.deleteUI(shelf_name, layout=True)

        # Dynamically load and run the installer script
        installer_url = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/setup_drag_drop_fdma2530.py"
        installer_code = safe_download(installer_url)
        if installer_code:
            exec(installer_code, globals())
            # Recreate permanently-installed shelf
            install_permanent()

    except Exception as e:
        cmds.warning("Deferred shelf rebuild failed: " + str(e))
        if update_button_visual_status:
            update_button_visual_status(label, "update_failed")
        return

    # On success, update cache and button color
    cache_path = os.path.join(cmds.internalVar(userScriptDir=True), "shelf_config_cache.json")
    with open(cache_path, "w") as f:
        f.write(latest_config)
    if update_button_visual_status:
        update_button_visual_status(label, "up_to_date")

# Main update logic
try:
    config_url = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/shelf_config.json"
    latest = safe_download(config_url)
    if not latest:
        raise RuntimeError("No data")

    # Load installed config
    cache_path = os.path.join(cmds.internalVar(userScriptDir=True), "shelf_config_cache.json")
    installed = ""
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            installed = f.read()

    # Compare hashes
    upd_needed = hashlib.md5(latest.encode("utf-8")).hexdigest() != hashlib.md5(installed.encode("utf-8")).hexdigest()

    if upd_needed:
        if update_button_visual_status:
            update_button_visual_status(label, "updates_available")
        if show_update_confirmation_dialog():
            # Defer the actual shelf delete/create to avoid crashes
            maya.utils.executeDeferred(lambda: rebuild_shelf(latest))
        else:
            # Keep green as reminder
            pass
    else:
        show_up_to_date_message()
        if update_button_visual_status:
            update_button_visual_status(label, "up_to_date")

except Exception as err:
    cmds.warning("Update check failed: " + str(err))
    if update_button_visual_status:
        update_button_visual_status(label, "update_failed")
'''.format(script_url)


def create_shelf_from_json_config(config, use_temp=False):
    """Create shelf dynamically from JSON configuration"""
    try:
        # Get shelf configuration
        shelf_info = config['shelf_info']
        shelf_name = shelf_info['name']
        
        # Get the shelf top level using Python
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
        cleanup_existing_shelf(shelf_name)
        
        # Create new shelf with JSON configuration
        shelf = cmds.shelfLayout(
            shelf_name, 
            parent=gShelfTopLevel, 
            cellWidth=shelf_info.get('cell_width', 35),
            cellHeight=shelf_info.get('cell_height', 35)
        )
        print("Created shelf layout: " + shelf)
        
        # Make status functions available to button commands
        import __main__
        __main__.update_button_visual_status = update_button_visual_status
        __main__.viewport_yellow_alert = viewport_yellow_alert
        
        # Create buttons and separators from JSON configuration
        for item in config['buttons']:
            if not item.get('enabled', True):
                continue  # Skip disabled items
                
            if item['type'] == 'separator':
                cmds.separator(
                    parent=shelf,
                    style=item.get('style', 'shelf'),
                    hr=not item.get('horizontal', False)
                    )
                print("Added separator")
                
            elif item['type'] == 'button':
                # Create button command - special handling for Update button
                if item['label'] == 'Update':
                    button_command = create_update_button_command(item['script_url'])
                else:
                    button_command = create_button_command(item['script_url'])
                
                # Create the button
                button = cmds.shelfButton(
                    parent=shelf,
                    label=item['label'],
                    image1=item['icon'],
                    annotation=item['annotation'],
                    command=button_command,
                    width=item.get('width', 35),
                    height=item.get('height', 35)
                )
                print("Added button: " + item['label'])
        
        # Activate the shelf
        if cmds.control(gShelfTopLevel, exists=True) and cmds.control(shelf, exists=True):
            cmds.tabLayout(gShelfTopLevel, edit=True, selectTab=shelf)
            print("Shelf activated successfully: " + shelf_name)
        
        return True
        
    except Exception as e:
        cmds.warning("Failed to create shelf from JSON: " + str(e))
        import traceback
        print(traceback.format_exc())
        return False

def cache_json_config(config, use_temp=False):
    """Cache the JSON configuration for offline use and version comparison"""
    try:
        if use_temp:
            cache_dir = tempfile.gettempdir()
        else:
            cache_dir = cmds.internalVar(userScriptDir=True)
        
        config_cache_path = os.path.join(cache_dir, "shelf_config_cache.json")
        
        # Save the configuration with pretty formatting
        with open(config_cache_path, 'w') as f:
            json.dump(config, f, indent=2, sort_keys=True)
        
        print("Configuration cached at: " + config_cache_path)
        return config_cache_path
        
    except Exception as e:
        print("Failed to cache configuration: " + str(e))
        return None

def install_cache_system(use_temp=False):
    """Download and install the cache system (optional)"""
    try:
        if use_temp:
            install_dir = tempfile.gettempdir()
            if install_dir not in sys.path:
                sys.path.insert(0, install_dir)
        else:
            install_dir = cmds.internalVar(userScriptDir=True)
        
        utilities_dir = os.path.join(install_dir, "utilities")
        if not os.path.exists(utilities_dir):
            os.makedirs(utilities_dir)
        
        loader_content = safe_download(LOADER_URL)
        if loader_content:
            loader_path = os.path.join(utilities_dir, "cache_loader.py")
            safe_write(loader_path, loader_content)
            
            init_path = os.path.join(utilities_dir, "__init__.py")
            safe_write(init_path, "# Utilities package\n")
            
            print("Cache system installed at: " + utilities_dir)
            return True
        return False
        
    except Exception as e:
        print("Cache system installation failed: " + str(e))
        return False

def install_permanent():
    """Install shelf permanently with JSON configuration"""
    try:
        # Download JSON configuration
        config = download_json_config()
        if not config:
            return False
        
        # Install cache system (optional)
        install_cache_system(use_temp=False)
        
        # Cache the configuration
        cache_json_config(config, use_temp=False)
        
        # Create shelf from JSON configuration
        return create_shelf_from_json_config(config, use_temp=False)
        
    except Exception as e:
        cmds.warning("Installation failed: " + str(e))
        return False

def install_temporary():
    """Install shelf temporarily with JSON configuration"""
    try:
        # Download JSON configuration
        config = download_json_config()
        if not config:
            return False
        
        # Install cache system to temp (optional)
        install_cache_system(use_temp=True)
        
        # Cache the configuration
        cache_json_config(config, use_temp=True)
        
        # Create shelf from JSON configuration
        return create_shelf_from_json_config(config, use_temp=True)
        
    except Exception as e:
        cmds.warning("Temporary installation failed: " + str(e))
        return False

def show_install_dialog():
    """Show installation dialog with JSON configuration info"""
    choice = cmds.confirmDialog(
        title="FDMA 2530 Shelf Installer v{}".format(__version__),
        message="Choose installation type:\n\nInstall Shelf \nRun Only (Temporary) ",
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
