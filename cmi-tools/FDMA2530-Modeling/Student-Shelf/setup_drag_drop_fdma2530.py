"""
CMI Tools Shelf Installer - OPTIMIZED ZIP DOWNLOAD
========================================================
Drag-and-drop installer for CMI Tools student shelf system.
Fast ZIP-based installation following GT Tools architecture.

Cross-platform compatible: Windows, macOS, Linux
Maya versions: 2016-2025+ | Python 2/3 compatible

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
"""

import os
import sys
import shutil
import tempfile
import zipfile
import json

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import maya.cmds as cmds

# Configuration - GitHub repository ZIP download
REPO_ZIP_URL = "https://github.com/Atsantiago/NMSU_Scripts/archive/refs/heads/master.zip"

def get_cmi_tools_root():
    """Get the cmi-tools root directory path"""
    maya_app_dir = cmds.internalVar(userAppDir=True)
    return os.path.join(maya_app_dir, "cmi-tools").replace('\\', '/')

def get_modules_dir():
    """Get Maya modules directory path"""
    maya_app_dir = cmds.internalVar(userAppDir=True)
    modules_dir = os.path.join(maya_app_dir, "modules")
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
    return modules_dir

def safe_download(url, timeout=30):
    """Download content from URL with error handling"""
    try:
        response = urlopen(url, timeout=timeout)
        content = response.read()
        return content
    except Exception as e:
        print("Download failed: {0}".format(e))
        return None

def get_latest_release_info():
    """Return (version, download_url, description) from the releases.json manifest on GitHub."""
    manifest_url = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/cmi-tools/FDMA2530-Modeling/releases.json"
    try:
        response = urlopen(manifest_url, timeout=30)
        manifest = json.loads(response.read().decode("utf-8"))
        current_version = manifest["current_version"]
        for release in manifest["releases"]:
            if release["version"] == current_version:
                return release["version"], release["download_url"], release["description"]
        # Fallback: use first release if current_version not found
        if manifest["releases"]:
            latest = manifest["releases"][0]
            return latest["version"], latest["download_url"], latest["description"]
    except Exception as e:
        print("Failed to fetch latest release info: {0}".format(e))
    return None, None, None


def download_and_extract_package(target_dir):
    """Download latest release ZIP and extract to cmi-tools structure (manifest-based)."""
    print("Downloading CMI Tools shelf package...")
    version, zip_url, _ = get_latest_release_info()
    if not zip_url:
        print("Could not determine latest release download URL.")
        return False
    try:
        zip_data = safe_download(zip_url)
        if not zip_data:
            return False
        
        # Create temp ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            temp_zip.write(zip_data)
            temp_zip_path = temp_zip.name
        
        try:
            # Extract ZIP
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                temp_extract_dir = tempfile.mkdtemp(prefix="cmi_extract_")
                zip_ref.extractall(temp_extract_dir)
                
                # Find extracted repo
                extracted_repo = None
                for item in os.listdir(temp_extract_dir):
                    if item.startswith("NMSU_Scripts-"):
                        extracted_repo = os.path.join(temp_extract_dir, item)
                        break
                
                if not extracted_repo:
                    print("Could not find extracted repository")
                    return False
                
                # Source paths
                student_shelf_path = os.path.join(extracted_repo, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf")
                source_package = os.path.join(student_shelf_path, "fdma_shelf")
                source_config = os.path.join(student_shelf_path, "shelf_config.json")
                
                # Create cmi-tools directory structure
                scripts_dir = os.path.join(target_dir, "scripts")
                icons_dir = os.path.join(target_dir, "icons") 
                shelves_dir = os.path.join(target_dir, "shelves")
                
                for dir_path in [scripts_dir, icons_dir, shelves_dir]:
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                
                # Copy package to scripts directory
                target_package = os.path.join(scripts_dir, "fdma_shelf")
                if os.path.exists(source_package):
                    if os.path.exists(target_package):
                        shutil.rmtree(target_package)
                    shutil.copytree(source_package, target_package)
                    print("Copied fdma_shelf package to scripts/")
                else:
                    print("Warning: fdma_shelf package not found in repository")
                    return False
                
                # Copy config to scripts directory
                if os.path.exists(source_config):
                    shutil.copy2(source_config, scripts_dir)
                    print("Copied shelf_config.json to scripts/")
                else:
                    print("Warning: shelf_config.json not found in repository")
                
                # Clean up temp extraction
                shutil.rmtree(temp_extract_dir)
            
            return True
            
        finally:
            os.unlink(temp_zip_path)
        
    except Exception as e:
        print("Package extraction failed: {0}".format(e))
        import traceback
        print(traceback.format_exc())
        return False

def create_module_file():
    """Create cmi-tools.mod file in Maya modules directory"""
    try:
        modules_dir = get_modules_dir()
        mod_file_path = os.path.join(modules_dir, "cmi-tools.mod")
        cmi_root = get_cmi_tools_root()
        
        mod_content = """+ cmi-tools 2.0.1 {cmi_root}
scripts: scripts
icons: icons
shelves: shelves
""".format(cmi_root=cmi_root)
        
        with open(mod_file_path, 'w') as f:
            f.write(mod_content)
        
        print("Created cmi-tools.mod in modules directory")
        return True
        
    except Exception as e:
        print("Failed to create module file: {0}".format(e))
        return False

def create_readme_file(target_dir):
    """Create README.md explaining the cmi-tools folder"""
    readme_content = """# CMI Tools for Maya - FDMA 2530 Shelf System

This folder contains the FDMA 2530 student modeling shelf system for Maya.

## Author & Creator

**Alexander T. Santiago**  
Email: asanti89@nmsu.edu  
Institution: New Mexico State University - Creative Media Institute  
Course: FDMA 2530 - 3D Modeling Fundamentals  

## About This System

The CMI Tools shelf system was designed specifically for FDMA 2530 students to provide:
- Streamlined modeling workflow tools
- Educational validation systems  
- Professional-grade tool organization
- Industry-standard Maya integration

## Folder Structure

- **scripts/**: Python packages and modules (fdma_shelf)
- **icons/**: Shelf button icons and UI graphics  
- **shelves/**: MEL shelf files (if any)
- **README.md**: This documentation file

## What This System Provides

The FDMA 2530 shelf includes tools for students:
- **CMI Modeling Checklist**: Comprehensive project validation system
- **Import Tools**: Reference geometry and asset management
- **Update System**: Automatic tool updates from GitHub
- **Educational Workflow**: Designed for Maya learning progression

## How It Works

This system uses Maya's professional module system to:
1. Add scripts/ to Maya's Python path automatically
2. Add icons/ to Maya's icon search path  
3. Load the shelf on Maya startup without userSetup.py modifications
4. Provide clean, professional tool organization

## For Students: Adding Personal Tools

To customize this system with your own tools:
1. Create new .py file in scripts/fdma_shelf/tools/
2. Add import to scripts/fdma_shelf/tools/__init__.py
3. Update scripts/shelf_config.json with new button configuration
4. Use semantic versioning for your tool versions

## Updating the System

The shelf includes an Update button that:
- Checks GitHub for new tool versions
- Downloads updates automatically
- Rebuilds the shelf without requiring Maya restart
- Preserves your personal customizations

## Uninstalling

To remove this system completely:
1. Delete this entire cmi-tools folder
2. Delete the cmi-tools.mod file from Maya's modules directory
3. Restart Maya

## Technical Details

- **Version**: 2.0.1
- **Compatibility**: Maya 2016-2025+
- **Platforms**: Windows, macOS, Linux
- **Architecture**: GT Tools-inspired professional structure
- **License**: Educational use for FDMA 2530 students

## Support

For technical support or feature requests:
- Check Maya Script Editor for detailed error messages
- Contact course instructor: Alexander T. Santiago
- Email: asanti89@nmsu.edu

## Acknowledgments

This system follows professional Maya tool development patterns
inspired by industry-standard tools like GT Tools while being
specifically designed for educational use in 3D modeling courses.

---
Created with care for FDMA 2530 students at NMSU Creative Media Institute.
"""
    
    try:
        readme_path = os.path.join(target_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print("Created README.md in cmi-tools directory")
        return True
    except Exception as e:
        print("Failed to create README: {0}".format(e))
        return False

def create_shelf_safely():
    """Import and create the shelf after module installation"""
    try:
        # Clear any existing fdma_shelf imports to ensure fresh load
        modules_to_clear = [name for name in sys.modules.keys() if name.startswith('fdma_shelf')]
        for module_name in modules_to_clear:
            del sys.modules[module_name]
        
        # Import the package (should now be in Maya's Python path via module)
        import fdma_shelf
        
        # Debug: Check what attributes are available
        print("fdma_shelf attributes: {0}".format(dir(fdma_shelf)))
        
        # Verify build_shelf exists
        if not hasattr(fdma_shelf, 'build_shelf'):
            print("Error: fdma_shelf.build_shelf not found")
            print("Available attributes: {0}".format([attr for attr in dir(fdma_shelf) if not attr.startswith('_')]))
            
            # Try importing builder directly as fallback
            try:
                from fdma_shelf.shelf.builder import build_shelf
                print("Successfully imported build_shelf directly from builder")
                build_shelf(startup=False)
                print("Shelf created successfully via direct import!")
                return True
            except ImportError as ie:
                print("Direct import also failed: {0}".format(ie))
                return False
        
        # Create the shelf using package function
        print("Creating FDMA 2530 shelf...")
        fdma_shelf.build_shelf(startup=False)
        print("Shelf created successfully!")
        return True
        
    except ImportError as e:
        print("Failed to import fdma_shelf: {0}".format(e))
        import traceback
        print(traceback.format_exc())
        return False
    except Exception as e:
        print("Failed to create shelf: {0}".format(e))
        import traceback
        print(traceback.format_exc())
        return False

def install_permanent():
    """Install cmi-tools module permanently"""
    cmi_root = get_cmi_tools_root()
    print("Installing to cmi-tools directory: {0}".format(cmi_root))
    
    # Create cmi-tools directory
    if not os.path.exists(cmi_root):
        os.makedirs(cmi_root)
    
    # Download and extract package
    if not download_and_extract_package(cmi_root):
        return False
    
    # Create module file
    if not create_module_file():
        return False
    
    # Create documentation
    if not create_readme_file(cmi_root):
        print("Warning: README creation failed")
    
    # Add scripts directory to Python path for immediate use
    scripts_dir = os.path.join(cmi_root, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    
    # Create shelf immediately
    return create_shelf_safely()

def install_temporary():
    """Install temporarily (just create shelf from temp location)"""
    temp_dir = tempfile.mkdtemp(prefix="cmi_temp_")
    print("Installing temporarily to: {0}".format(temp_dir))
    
    # Download to temp location
    if not download_and_extract_package(temp_dir):
        return False
    
    # Add temp scripts to Python path
    temp_scripts = os.path.join(temp_dir, "scripts")
    if temp_scripts not in sys.path:
        sys.path.insert(0, temp_scripts)
    
    # Create shelf
    return create_shelf_safely()

def uninstall():
    """Remove cmi-tools module system, MEL shelf, and prevent shelf recreation on Maya restart."""
    cmi_root = get_cmi_tools_root()
    modules_dir = get_modules_dir()
    mod_file = os.path.join(modules_dir, "cmi-tools.mod")
    # Remove shelf from Maya
    try:
        if cmds.shelfLayout("FDMA_2530", exists=True):
            cmds.deleteUI("FDMA_2530", layout=True)
            print("Removed FDMA_2530 shelf")
    except Exception:
        pass
    # Remove cmi-tools directory
    if os.path.exists(cmi_root):
        try:
            shutil.rmtree(cmi_root)
            print("Removed cmi-tools directory")
        except Exception as e:
            print("Failed to remove cmi-tools: {0}".format(e))
            return False
    # Remove module file
    if os.path.exists(mod_file):
        try:
            os.remove(mod_file)
            print("Removed cmi-tools.mod")
        except Exception as e:
            print("Failed to remove module file: {0}".format(e))
    # Remove MEL shelf file from Maya user prefs (cross-platform)
    try:
        import getpass
        user = getpass.getuser()
        # Maya user prefs root
        maya_root = os.path.expanduser('~/Documents/maya')
        if not os.path.exists(maya_root):
            maya_root = os.path.expanduser('~/maya')  # Linux/Mac alt
        # Try all major Maya versions (2016-2025+)
        for year in range(2016, 2030):
            shelf_path = os.path.join(maya_root, str(year), 'prefs', 'shelves', 'shelf_FDMA_2530.mel')
            if os.path.exists(shelf_path):
                try:
                    os.remove(shelf_path)
                    print(f"Removed shelf MEL: {shelf_path}")
                except Exception as e:
                    print(f"Failed to remove shelf MEL: {shelf_path} ({e})")
    except Exception as e:
        print(f"Error searching for Maya shelf MEL files: {e}")
    # Create uninstall marker to prevent shelf recreation
    marker = os.path.expanduser('~/.fdma2530_uninstalled')
    try:
        with open(marker, 'w') as f:
            f.write('uninstalled')
    except Exception as e:
        print("Failed to create uninstall marker: {0}".format(e))
    print("CMI Tools uninstalled successfully!")
    return True

def get_installed_package_version():
    """Try to get the installed fdma_shelf version, or return 'Unknown' if not available.
    Import is inside the function to avoid ModuleNotFoundError if fdma_shelf is not yet installed.
    """
    try:
        import fdma_shelf.utils.version_utils as vutils
        return vutils.get_fdma2530_version()
    except Exception:
        return "Unknown"

def show_install_dialog():
    """Show installation dialog"""
    version_str = get_installed_package_version()
    choice = cmds.confirmDialog(
        title="CMI Tools Installer v{0}".format(version_str),
        message="CMI Tools Installation\n\nChoose installation type:\n\nInstall Tools: Permanent installation using Maya modules\nLoad Once: Temporary installation (session only)\nUninstall: Remove CMI Tools",
        button=["Install", "Load Once", "Uninstall", "Cancel"],
        defaultButton="Install",
        cancelButton="Cancel"
    )
    
    if choice == "Install":
        if install_permanent():
            cmds.confirmDialog(
                title="Success",
                message="CMI Tools - FDMA 2530 Shelf installed successfully!\n\nThe shelf will automatically load when Maya starts.\n\nCreated by: Alexander T. Santiago",
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
                message="CMI Tools - FDMA 2530 shelf loaded temporarily!\n\nShelf will be removed when Maya closes.\nFor permanent installation, run installer again.",
                button=["OK"]
            )
        else:
            cmds.confirmDialog(
                title="Error",
                message="Temporary installation failed. Check Script Editor for details.",
                button=["OK"]
            )
    
    elif choice == "Uninstall":
        confirm = cmds.confirmDialog(
            title="Confirm Uninstall",
            message="Remove CMI Tools completely?",
            button=["Yes", "No"],
            defaultButton="No"
        )
        
        if confirm == "Yes":
            if uninstall():
                cmds.confirmDialog(
                    title="Uninstalled",
                    message="CMI Tools removed successfully.",
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

if __name__ == "__main__":
    onMayaDroppedPythonFile()
