"""
FDMA 2530 Shelf Installer v2.0.0 - OPTIMIZED ZIP DOWNLOAD
=========================================================
Drag-and-drop installer for FDMA 2530 student shelf system.
Fast ZIP-based installation following GT Tools architecture.

Cross-platform compatible: Windows, macOS, Linux
Maya versions: 2016-2025+ | Python 2/3 compatible
"""

import os
import sys
import shutil
import tempfile
import zipfile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import maya.cmds as cmds
import maya.mel as mel

__version__ = "2.0.0"

# Configuration - GitHub repository ZIP download
REPO_ZIP_URL = "https://github.com/Atsantiago/NMSU_Scripts/archive/refs/heads/master.zip"

def safe_download(url, timeout=30):
    """Download content from URL with error handling"""
    try:
        response = urlopen(url, timeout=timeout)
        content = response.read()
        return content
    except Exception as e:
        print("Download failed for {0}: {1}".format(url, e))
        return None

def get_scripts_directory():
    """Get Maya user scripts directory"""
    return cmds.internalVar(userScriptDir=True)

def download_and_extract_package(target_dir):
    """Download repo ZIP and extract FDMA 2530 package files"""
    print("Downloading FDMA 2530 shelf package...")
    
    try:
        # Download ZIP file
        zip_data = safe_download(REPO_ZIP_URL)
        if not zip_data:
            print("Failed to download package ZIP")
            return False
        
        # Create temporary ZIP file
        temp_zip_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                temp_zip.write(zip_data)
                temp_zip_path = temp_zip.name
            
            # Extract ZIP contents
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                # Extract all files to temp directory first
                temp_extract_dir = tempfile.mkdtemp(prefix="fdma_extract_")
                zip_ref.extractall(temp_extract_dir)
                
                # Find the extracted repo directory
                extracted_repo = None
                for item in os.listdir(temp_extract_dir):
                    if item.startswith("NMSU_Scripts-"):
                        extracted_repo = os.path.join(temp_extract_dir, item)
                        break
                
                if not extracted_repo:
                    print("Could not find extracted repository")
                    return False
                
                # Source paths in extracted repo
                source_package = os.path.join(extracted_repo, "FDMA2530-Modeling", "Student-Shelf", "fdma_shelf")
                source_config = os.path.join(extracted_repo, "FDMA2530-Modeling", "Student-Shelf", "shelf_config.json")
                
                # Target paths
                target_package = os.path.join(target_dir, "fdma_shelf")
                target_config = os.path.join(target_dir, "shelf_config.json")
                
                # Copy package directory
                if os.path.exists(source_package):
                    if os.path.exists(target_package):
                        shutil.rmtree(target_package)
                    shutil.copytree(source_package, target_package)
                    print("Copied fdma_shelf package")
                else:
                    print("Warning: fdma_shelf package not found in ZIP")
                
                # Copy config file
                if os.path.exists(source_config):
                    shutil.copy2(source_config, target_config)
                    print("Copied shelf_config.json")
                else:
                    print("Warning: shelf_config.json not found in ZIP")
                
                # Clean up temp extraction directory
                shutil.rmtree(temp_extract_dir)
            
            print("Package extraction completed successfully!")
            return True
            
        finally:
            # Clean up temp ZIP file
            if temp_zip_path and os.path.exists(temp_zip_path):
                os.unlink(temp_zip_path)
        
    except Exception as e:
        print("ZIP download/extract failed: {0}".format(e))
        import traceback
        print(traceback.format_exc())
        return False

def modify_user_setup(scripts_dir):
    """Add or update userSetup.py to bootstrap shelf creation"""
    user_setup_path = os.path.join(scripts_dir, "userSetup.py")
    
    # Bootstrap code to add
    bootstrap_code = """
# FDMA 2530 Shelf Auto-Loader v2.0.0
try:
    import fdma_shelf
    print("FDMA 2530 shelf system loaded successfully")
except ImportError as e:
    print("FDMA 2530 shelf system failed to load: {0}".format(e))
except Exception as e:
    print("FDMA 2530 shelf system error: {0}".format(e))
"""
    
    # Read existing userSetup.py if it exists
    existing_content = ""
    if os.path.exists(user_setup_path):
        try:
            with open(user_setup_path, 'r') as f:
                existing_content = f.read()
        except Exception:
            pass
    
    # Check if our bootstrap is already present
    if "FDMA 2530 Shelf Auto-Loader" in existing_content:
        print("userSetup.py already contains FDMA 2530 shelf bootstrap")
        return True
    
    # Add bootstrap to existing content
    updated_content = existing_content + bootstrap_code
    
    # Write updated userSetup.py
    try:
        with open(user_setup_path, 'w') as f:
            f.write(updated_content)
        print("Updated userSetup.py with FDMA 2530 shelf bootstrap")
        return True
    except Exception as e:
        print("Failed to update userSetup.py: {0}".format(e))
        return False

def remove_user_setup_bootstrap(scripts_dir):
    """Remove FDMA 2530 bootstrap from userSetup.py"""
    user_setup_path = os.path.join(scripts_dir, "userSetup.py")
    
    if not os.path.exists(user_setup_path):
        return True
    
    try:
        with open(user_setup_path, 'r') as f:
            content = f.read()
        
        # Remove our bootstrap section
        lines = content.split('\n')
        filtered_lines = []
        skip_section = False
        
        for line in lines:
            if "FDMA 2530 Shelf Auto-Loader" in line:
                skip_section = True
                continue
            elif skip_section and (line.strip().startswith("except") or line.strip() == ""):
                if not line.strip():
                    skip_section = False
                continue
            elif not skip_section:
                filtered_lines.append(line)
        
        updated_content = '\n'.join(filtered_lines)
        
        with open(user_setup_path, 'w') as f:
            f.write(updated_content)
        
        print("Removed FDMA 2530 bootstrap from userSetup.py")
        return True
        
    except Exception as e:
        print("Failed to update userSetup.py: {0}".format(e))
        return False

def remove_package(scripts_dir):
    """Remove FDMA 2530 package from scripts directory"""
    package_path = os.path.join(scripts_dir, "fdma_shelf")
    config_path = os.path.join(scripts_dir, "shelf_config.json")
    cache_path = os.path.join(scripts_dir, "shelf_config_cache.json")
    
    removed_items = []
    
    # Remove package directory
    if os.path.exists(package_path):
        try:
            shutil.rmtree(package_path)
            removed_items.append("fdma_shelf package")
        except Exception as e:
            print("Failed to remove package: {0}".format(e))
            return False
    
    # Remove config file
    if os.path.exists(config_path):
        try:
            os.remove(config_path)
            removed_items.append("shelf_config.json")
        except Exception as e:
            print("Failed to remove config: {0}".format(e))
    
    # Remove cache file
    if os.path.exists(cache_path):
        try:
            os.remove(cache_path)
            removed_items.append("cache file")
        except Exception as e:
            print("Failed to remove cache: {0}".format(e))
    
    if removed_items:
        print("Removed: {0}".format(", ".join(removed_items)))
    
    return True

def create_shelf_safely(scripts_dir):
    """Safely import and create the shelf"""
    try:
        # Ensure scripts directory is in Python path
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        # Clear any cached imports to avoid stale modules
        modules_to_clear = [name for name in sys.modules.keys() if name.startswith('fdma_shelf')]
        for module_name in modules_to_clear:
            del sys.modules[module_name]
        
        # Import the package
        import fdma_shelf
        
        # Verify the build_shelf function exists
        if not hasattr(fdma_shelf, 'build_shelf'):
            print("Error: fdma_shelf module exists but build_shelf function not found")
            print("Available attributes: {0}".format(dir(fdma_shelf)))
            return False
        
        # Create the shelf
        print("Creating FDMA 2530 shelf...")
        fdma_shelf.build_shelf(startup=False)
        
        print("FDMA 2530 shelf created successfully!")
        return True
        
    except ImportError as e:
        print("Failed to import fdma_shelf: {0}".format(e))
        return False
    except Exception as e:
        print("Failed to create shelf: {0}".format(e))
        import traceback
        print(traceback.format_exc())
        return False

def install_permanent():
    """Install FDMA 2530 shelf system permanently"""
    scripts_dir = get_scripts_directory()
    print("Installing permanently to: {0}".format(scripts_dir))
    
    # Download and extract package files
    if not download_and_extract_package(scripts_dir):
        return False
    
    # Update userSetup.py
    if not modify_user_setup(scripts_dir):
        print("Warning: userSetup.py modification failed")
    
    # Create shelf immediately
    return create_shelf_safely(scripts_dir)

def install_temporary():
    """Install FDMA 2530 shelf system temporarily (session only)"""
    temp_dir = tempfile.mkdtemp(prefix="fdma_shelf_")
    print("Installing temporarily to: {0}".format(temp_dir))
    
    # Download and extract package files to temp directory
    if not download_and_extract_package(temp_dir):
        return False
    
    # Create shelf immediately
    return create_shelf_safely(temp_dir)

def uninstall():
    """Uninstall FDMA 2530 shelf system"""
    scripts_dir = get_scripts_directory()
    
    # Remove shelf from Maya if it exists
    try:
        if cmds.shelfLayout("FDMA_2530", exists=True):
            cmds.deleteUI("FDMA_2530", layout=True)
            print("Removed FDMA_2530 shelf from Maya")
    except Exception:
        pass
    
    # Remove package files
    if not remove_package(scripts_dir):
        return False
    
    # Remove userSetup.py bootstrap
    if not remove_user_setup_bootstrap(scripts_dir):
        print("Warning: userSetup.py cleanup failed")
    
    print("FDMA 2530 shelf system uninstalled successfully!")
    return True

def show_install_dialog():
    """Show installation dialog"""
    choice = cmds.confirmDialog(
        title="FDMA 2530 Shelf Installer v{0}".format(__version__),
        message="FDMA 2530 Shelf Installation\n\nChoose installation type:\n\nInstall Shelf: Permanent installation with auto-startup\nLoad Once: Temporary installation (session only)\nUninstall: Remove FDMA 2530 shelf system",
        button=["Install Shelf", "Load Once", "Uninstall", "Cancel"],
        defaultButton="Install Shelf",
        cancelButton="Cancel"
    )
    
    if choice == "Install Shelf":
        if install_permanent():
            cmds.confirmDialog(
                title="Success",
                message="FDMA 2530 shelf installed successfully!\n\nThe shelf will automatically load when Maya starts.\nUse the Update button to check for new tools and features.",
                button=["OK"]
            )
        else:
            cmds.confirmDialog(
                title="Error", 
                message="Installation failed. Check the Script Editor for details.",
                button=["OK"]
            )
    
    elif choice == "Load Once":
        if install_temporary():
            cmds.confirmDialog(
                title="Success",
                message="FDMA 2530 shelf loaded temporarily!\n\nThe shelf will be removed when Maya closes.\nFor permanent installation, run the installer again.",
                button=["OK"]
            )
        else:
            cmds.confirmDialog(
                title="Error",
                message="Temporary installation failed. Check the Script Editor for details.",
                button=["OK"]
            )
    
    elif choice == "Uninstall":
        confirm = cmds.confirmDialog(
            title="Confirm Uninstall",
            message="This will remove the FDMA 2530 shelf system completely.\n\nAre you sure you want to continue?",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No"
        )
        
        if confirm == "Yes":
            if uninstall():
                cmds.confirmDialog(
                    title="Uninstalled",
                    message="FDMA 2530 shelf system has been removed successfully.",
                    button=["OK"]
                )
            else:
                cmds.confirmDialog(
                    title="Error",
                    message="Uninstall failed. Check the Script Editor for details.",
                    button=["OK"]
                )

def onMayaDroppedPythonFile(*args):
    """Maya drag-and-drop entry point"""
    try:
        show_install_dialog()
    except Exception as e:
        cmds.warning("Installer error: {0}".format(e))
        import traceback
        print(traceback.format_exc())

# Execute if run directly (for testing)
if __name__ == "__main__":
    onMayaDroppedPythonFile()
