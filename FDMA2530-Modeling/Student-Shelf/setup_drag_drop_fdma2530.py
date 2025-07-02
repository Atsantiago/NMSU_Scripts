"""
FDMA 2530 Shelf Installer v2.0.0 - GT TOOLS STYLE APPROACH
===========================================================
Drag-and-drop installer for FDMA 2530 student shelf system.
Follows GT Tools architecture for reliable installation and updates.

Cross-platform compatible: Windows, macOS, Linux
Maya versions: 2016-2025+ | Python 2/3 compatible
"""

import os
import sys
import shutil
import tempfile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import maya.cmds as cmds
import maya.mel as mel

__version__ = "2.0.0"

# Configuration URLs - GitHub repository paths
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
PACKAGE_BASE_URL = REPO_RAW + "FDMA2530-Modeling/Student-Shelf/"

# Files to download and install
REQUIRED_FILES = {
    "fdma_shelf/__init__.py": PACKAGE_BASE_URL + "fdma_shelf/__init__.py",
    "fdma_shelf/shelf/__init__.py": PACKAGE_BASE_URL + "fdma_shelf/shelf/__init__.py", 
    "fdma_shelf/shelf/builder.py": PACKAGE_BASE_URL + "fdma_shelf/shelf/builder.py",
    "fdma_shelf/utils/__init__.py": PACKAGE_BASE_URL + "fdma_shelf/utils/__init__.py",
    "fdma_shelf/utils/cache.py": PACKAGE_BASE_URL + "fdma_shelf/utils/cache.py",
    "fdma_shelf/utils/downloader.py": PACKAGE_BASE_URL + "fdma_shelf/utils/downloader.py",
    "fdma_shelf/utils/system_utils.py": PACKAGE_BASE_URL + "fdma_shelf/utils/system_utils.py",
    "fdma_shelf/utils/updater.py": PACKAGE_BASE_URL + "fdma_shelf/utils/updater.py",
    "fdma_shelf/tools/__init__.py": PACKAGE_BASE_URL + "fdma_shelf/tools/__init__.py",
    "fdma_shelf/tools/checklist.py": PACKAGE_BASE_URL + "fdma_shelf/tools/checklist.py",
    "fdma_shelf/tools/TEMP_humanBody_import.py": PACKAGE_BASE_URL + "fdma_shelf/tools/TEMP_humanBody_import.py",
    "shelf_config.json": PACKAGE_BASE_URL + "shelf_config.json"
}

def safe_download(url, timeout=15):
    """Download content from URL with error handling"""
    try:
        response = urlopen(url, timeout=timeout)
        content = response.read()
        if sys.version_info[0] >= 3 and isinstance(content, bytes):
            content = content.decode("utf-8")
        return content
    except Exception as e:
        print("Download failed for {0}: {1}".format(url, e))
        return None

def safe_write_file(path, content):
    """Write content to file with directory creation"""
    try:
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
        return True
    except Exception as e:
        print("Failed to write file {0}: {1}".format(path, e))
        return False

def get_scripts_directory():
    """Get Maya user scripts directory"""
    return cmds.internalVar(userScriptDir=True)

def download_package_files(target_dir, use_temp=False):
    """Download all package files to target directory"""
    print("Downloading FDMA 2530 shelf package files...")
    
    failed_downloads = []
    
    for relative_path, url in REQUIRED_FILES.items():
        print("Downloading: {0}".format(relative_path))
        content = safe_download(url)
        
        if content is None:
            failed_downloads.append(relative_path)
            continue
        
        full_path = os.path.join(target_dir, relative_path)
        if not safe_write_file(full_path, content):
            failed_downloads.append(relative_path)
    
    if failed_downloads:
        print("Failed to download: {0}".format(", ".join(failed_downloads)))
        return False
    
    print("Package download completed successfully!")
    return True

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
            elif skip_section and line.strip().startswith("except"):
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
    
    if removed_items:
        print("Removed: {0}".format(", ".join(removed_items)))
    
    return True

def install_permanent():
    """Install FDMA 2530 shelf system permanently"""
    scripts_dir = get_scripts_directory()
    print("Installing to: {0}".format(scripts_dir))
    
    # Download package files
    if not download_package_files(scripts_dir):
        return False
    
    # Update userSetup.py
    if not modify_user_setup(scripts_dir):
        print("Warning: userSetup.py modification failed")
    
    # Import and create shelf immediately
    try:
        # Add scripts dir to path if not already there
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        # Import and build shelf
        import fdma_shelf
        fdma_shelf.build_shelf(startup=False)
        
        print("FDMA 2530 shelf created successfully!")
        return True
        
    except Exception as e:
        print("Failed to create shelf: {0}".format(e))
        return False

def install_temporary():
    """Install FDMA 2530 shelf system temporarily (session only)"""
    temp_dir = tempfile.mkdtemp(prefix="fdma_shelf_")
    print("Installing temporarily to: {0}".format(temp_dir))
    
    # Download package files to temp directory
    if not download_package_files(temp_dir):
        return False
    
    try:
        # Add temp dir to Python path
        if temp_dir not in sys.path:
            sys.path.insert(0, temp_dir)
        
        # Import and build shelf
        import fdma_shelf
        fdma_shelf.build_shelf(startup=False)
        
        print("FDMA 2530 shelf created temporarily!")
        return True
        
    except Exception as e:
        print("Failed to create temporary shelf: {0}".format(e))
        return False

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
        message="Install Shelf: Permanent installation\nLoad Once: Temporary installation (session only)\nUninstall: Remove FDMA 2530 shelf system",
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
