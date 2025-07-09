"""
<<<<<<< HEAD
CMI Tools Shelf Installer - OPTIMIZED ZIP DOWNLOAD
========================================================
Drag-and-drop installer for CMI Tools student shelf system.
Fast ZIP-based installation following GT Tools architecture.
Cross-platform compatible: Windows, macOS, Linux
Maya versions: 2016-2025+ | Python 2/3 compatible
Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
"""
=======
CMI Tools – FDMA 2530 Shelf Installer
=====================================================

Drag-and-drop script that installs or loads the FDMA 2530 student
shelf.  Key features:

• Downloads the repository as a ZIP (fast, no git required).  
• Copies `fdma_shelf`, `shelf_config.json`, **and `releases.json`**  
  so version_utils can find the manifest.  
• Reads `current_version` from the manifest – no hard-coded numbers.  
• Creates a Maya `.mod` file so the shelf auto-loads.  
• Works on Windows / macOS / Linux, Maya 2016-2025, Py 2/3.  

Author:  Alexander T. Santiago   •   asanti89@nmsu.edu
"""

from __future__ import absolute_import, print_function

import json
import logging
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
import os
import shutil
import sys
import tempfile
import zipfile
import json
try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen
import maya.cmds as cmds
<<<<<<< HEAD
import maya.utils
=======

# ---------------------------------------------------------------------------
# Configuration / constants
# ---------------------------------------------------------------------------
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af

REPO_ZIP_URL = (
    "https://github.com/Atsantiago/NMSU_Scripts/archive/refs/heads/master.zip"
)
MODULE_NAME = "cmi-tools"
SHELF_NAME = "FDMA_2530"
FALLBACK_VERSION = "2.0.1"

# Will be filled after the manifest is read
CURRENT_VERSION = FALLBACK_VERSION

# Logging
logging.basicConfig()
LOG = logging.getLogger("fdma2530_installer")
LOG.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Helper paths
# ---------------------------------------------------------------------------

def get_maya_app_dir():
    """Return Maya's *user* application directory (~/maya/20xx/)."""
    return cmds.internalVar(userAppDir=True)

def get_cmi_root():
    """cmi-tools installation root inside the Maya user directory."""
    return os.path.join(get_maya_app_dir(), MODULE_NAME).replace("\\", "/")

def get_modules_dir():
    """Maya modules folder; create it if missing."""
    path = os.path.join(get_maya_app_dir(), "modules")
    if not os.path.exists(path):
        os.makedirs(path)
    return path

# ---------------------------------------------------------------------------
# Download / extract helpers
# ---------------------------------------------------------------------------

def safe_download(url, timeout=30):
    """Return raw bytes from *url* or None on failure."""
    try:
        LOG.info("Downloading %s …", url)
        return urlopen(url, timeout=timeout).read()
    except Exception as exc:
        LOG.error("Download failed: %s", exc)
        return None

<<<<<<< HEAD
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

def get_latest_release_version():
    """Return the latest release version from the releases.json manifest on GitHub."""
    manifest_url = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/cmi-tools/FDMA2530-Modeling/releases.json"
    try:
        response = urlopen(manifest_url, timeout=30)
        manifest = json.loads(response.read().decode("utf-8"))
        return manifest.get("current_version", "Unknown")
    except Exception as e:
        print("Failed to fetch latest release version: {0}".format(e))
        return "Unknown"

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
            # Copy releases.json to fdma_shelf package directory for version detection
            source_manifest = os.path.join(os.path.dirname(student_shelf_path), "releases.json")
            target_manifest = os.path.join(target_package, "releases.json")
            if os.path.exists(source_manifest):
                shutil.copy2(source_manifest, target_manifest)
                print("Copied releases.json to fdma_shelf package directory")
            else:
                print("Warning: releases.json not found in repository")
            # Clean up temp extraction
            shutil.rmtree(temp_extract_dir)
            return True
        finally:
            os.unlink(temp_zip_path)
    except Exception as e:
        print("Package extraction failed: {0}".format(e))
        import traceback
        print(traceback.format_exc())
=======
def _find_repo_root(extract_dir):
    """Return the …/NMSU_Scripts-xxxx root inside *extract_dir*."""
    for name in os.listdir(extract_dir):
        if name.startswith("NMSU_Scripts-"):
            return os.path.join(extract_dir, name)
    return None

def _read_manifest_version(manifest_path):
    """Return *current_version* from a manifest JSON file."""
    try:
        with open(manifest_path, "r") as fin:
            data = json.load(fin)
        return data.get("current_version", FALLBACK_VERSION)
    except Exception as exc:
        LOG.warning("Could not read manifest version: %s", exc)
        return FALLBACK_VERSION

def get_version_from_repo():
    """
    Download repo and read version from manifest without installing.
    Used to show correct version in dialog title.
    """
    global CURRENT_VERSION
    
    zip_bytes = safe_download(REPO_ZIP_URL)
    if not zip_bytes:
        return FALLBACK_VERSION

    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    tmp_zip.write(zip_bytes)
    tmp_zip.close()

    try:
        with zipfile.ZipFile(tmp_zip.name, "r") as zf:
            extract_dir = tempfile.mkdtemp(prefix="cmi_version_check_")
            zf.extractall(extract_dir)

        repo_root = _find_repo_root(extract_dir)
        if not repo_root:
            return FALLBACK_VERSION

        manifest_path = os.path.join(
            repo_root, "cmi-tools", "FDMA2530-Modeling", "releases.json"
        )
        
        if os.path.exists(manifest_path):
            version = _read_manifest_version(manifest_path)
            CURRENT_VERSION = version
            return version
        
        return FALLBACK_VERSION
        
    except Exception as exc:
        LOG.warning("Failed to read version from repo: %s", exc)
        return FALLBACK_VERSION
    finally:
        # Cleanup temp files
        if os.path.exists(tmp_zip.name):
            os.unlink(tmp_zip.name)
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

def download_and_extract_package(target_dir):
    """
    Download the repository ZIP and copy everything we need into
    *target_dir*/scripts | icons | shelves.
    """
    global CURRENT_VERSION

    zip_bytes = safe_download(REPO_ZIP_URL)
    if not zip_bytes:
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
        return False

    # Write the ZIP to a temp file
    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    tmp_zip.write(zip_bytes)
    tmp_zip.close()

    try:
<<<<<<< HEAD
        modules_dir = get_modules_dir()
        mod_file_path = os.path.join(modules_dir, "cmi-tools.mod")
        cmi_root = get_cmi_tools_root()
        # Use the latest version from releases.json
        latest_version = get_latest_release_version()
        if latest_version == "Unknown":
            latest_version = "2.0.6"  # Fallback to current version
        mod_content = """+ cmi-tools {version} {cmi_root}
scripts: scripts
icons: icons
shelves: shelves
""".format(version=latest_version, cmi_root=cmi_root)
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
=======
        with zipfile.ZipFile(tmp_zip.name, "r") as zf:
            extract_dir = tempfile.mkdtemp(prefix="cmi_extract_")
            zf.extractall(extract_dir)

        repo_root = _find_repo_root(extract_dir)
        if not repo_root:
            LOG.error("Repository root not found in ZIP")
            return False

        # Source locations inside the repo
        shelf_dir = os.path.join(
            repo_root, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf"
        )
        src_pkg = os.path.join(shelf_dir, "fdma_shelf")
        src_cfg = os.path.join(shelf_dir, "shelf_config.json")
        src_manifest = os.path.join(
            repo_root, "cmi-tools", "FDMA2530-Modeling", "releases.json"
        )

        # Verify all required files exist
        if not os.path.exists(src_pkg):
            LOG.error("fdma_shelf package not found at %s", src_pkg)
            return False
        if not os.path.exists(src_cfg):
            LOG.error("shelf_config.json not found at %s", src_cfg)
            return False
        if not os.path.exists(src_manifest):
            LOG.error("releases.json not found at %s", src_manifest)
            return False

        # Destination folders
        scripts_dir = os.path.join(target_dir, "scripts")
        icons_dir = os.path.join(target_dir, "icons")
        shelves_dir = os.path.join(target_dir, "shelves")
        for path in (scripts_dir, icons_dir, shelves_dir):
            if not os.path.exists(path):
                os.makedirs(path)

        # Copy the fdma_shelf package
        dst_pkg = os.path.join(scripts_dir, "fdma_shelf")
        if os.path.exists(dst_pkg):
            shutil.rmtree(dst_pkg)
        shutil.copytree(src_pkg, dst_pkg)
        LOG.info("Copied fdma_shelf → %s", dst_pkg)

        # Copy shelf_config.json
        shutil.copy2(src_cfg, scripts_dir)
        LOG.info("Copied shelf_config.json")

        # Copy releases.json (manifest) and read version
        shutil.copy2(src_manifest, scripts_dir)
        LOG.info("Copied releases.json")
        CURRENT_VERSION = _read_manifest_version(src_manifest)
        LOG.info("Detected version %s from manifest", CURRENT_VERSION)

        return True
    except Exception as exc:
        LOG.error("Package extraction failed: %s", exc, exc_info=True)
        return False
    finally:
        # Cleanup temp files
        if os.path.exists(tmp_zip.name):
            os.unlink(tmp_zip.name)
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

# ---------------------------------------------------------------------------
# Module / README creation
# ---------------------------------------------------------------------------

def create_module_file():
    """Write a cmi-tools.mod file for Maya's module system."""
    try:
        mod_path = os.path.join(get_modules_dir(), "cmi-tools.mod")
        cmi_root = get_cmi_root()
        content = (
            "+ {name} {ver} {root}\n"
            "scripts: scripts\n"
            "icons:   icons\n"
            "shelves: shelves\n"
        ).format(name=MODULE_NAME, ver=CURRENT_VERSION, root=cmi_root)
        with open(mod_path, "w") as fout:
            fout.write(content)
        LOG.info("Created module file %s", mod_path)
        return True
    except Exception as exc:
        LOG.error("Failed to create .mod file: %s", exc)
        return False

def create_readme_file(target_dir):
    """Generate a small README including the correct version."""
    readme_path = os.path.join(target_dir, "README.md")
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
    try:
        with open(readme_path, "w") as fout:
            fout.write(
                "# CMI Tools – FDMA 2530 Shelf\n\n"
                "*Version:* {ver}\n\n"
                "This folder was generated by the drag-and-drop installer. "
                "It contains the `fdma_shelf` package, icons and shelf "
                "configuration used by students in FDMA 2530.\n"
                "\nCreated by Alexander T. Santiago\n".format(ver=CURRENT_VERSION)
            )
        LOG.info("Created README.md")
        return True
    except Exception as exc:
        LOG.warning("README creation failed: %s", exc)
        return False

<<<<<<< HEAD
def create_shelf_safely():
    """Import and create shelf with marker check"""
    try:
        # Check for and remove uninstall marker first
        marker = os.path.expanduser('~/.fdma2530_uninstalled')
        if os.path.exists(marker):
            os.remove(marker)
            
        # Clear any existing fdma_shelf imports to ensure fresh load
        modules_to_clear = [name for name in sys.modules.keys() if name.startswith('fdma_shelf')]
        for module_name in modules_to_clear:
            del sys.modules[module_name]
        
        # Try importing builder directly first (most reliable)
        try:
            from fdma_shelf.shelf.builder import build_shelf
            result = build_shelf(startup=False)
            if result:
                print("Shelf created successfully!")
                return True
            else:
                return False
        except ImportError as ie:
            pass
            
        # Fallback: try package import
        try:
            import fdma_shelf
            
            # Verify build_shelf exists and create shelf
            if hasattr(fdma_shelf, 'build_shelf'):
                print("Creating FDMA 2530 shelf...")
                result = fdma_shelf.build_shelf(startup=False)
                
                if result:
                    print("Shelf created successfully!")
                    return True
                else:
                    return False
            else:
                return False
                
        except ImportError as e:
            return False
            
    except Exception as e:
        print("Failed to create shelf: {0}".format(e))
=======
# ---------------------------------------------------------------------------
# Shelf creation
# ---------------------------------------------------------------------------

def _import_and_build_shelf():
    """
    Import fdma_shelf (clearing any previous import) and build the shelf.
    Returns True/False for success.
    """
    for mod_name in [n for n in sys.modules if n.startswith("fdma_shelf")]:
        sys.modules.pop(mod_name)

    try:
        import fdma_shelf  # pylint: disable=import-error

        fdma_shelf.build_shelf(startup=False)
        LOG.info("Shelf built successfully")
        return True
    except Exception as exc:  # broad but user-facing
        LOG.error("Failed to build shelf: %s", exc, exc_info=True)
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
        return False

# ---------------------------------------------------------------------------
# High-level install / remove
# ---------------------------------------------------------------------------

def install_permanent():
    """Download, copy, write .mod, build shelf."""
    root = get_cmi_root()
    LOG.info("Installing into %s", root)
    if not os.path.exists(root):
        os.makedirs(root)

    if not download_and_extract_package(root):
        return False
    if not create_module_file():
        return False
    create_readme_file(root)

    # Ensure scripts folder is on sys.path for this session
    scripts_dir = os.path.join(root, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
<<<<<<< HEAD
        print("Added scripts directory to Python path: {0}".format(scripts_dir))
    
    # Use executeDeferred to ensure Maya UI is fully ready
    def deferred_shelf_creation():
        print("Executing deferred shelf creation...")
        success = create_shelf_safely()
        if success:
            print("Deferred shelf creation completed successfully")
        else:
            print("Deferred shelf creation failed")
        return success
    
    # Schedule shelf creation after Maya finishes current operations
    maya.utils.executeDeferred(deferred_shelf_creation)
    
    return True
=======

    return _import_and_build_shelf()
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af

def install_temporary():
    """Same as permanent but into a temp location (session only)."""
    temp_root = tempfile.mkdtemp(prefix="cmi_temp_")
    LOG.info("Installing temporarily into %s", temp_root)
    if not download_and_extract_package(temp_root):
        return False
<<<<<<< HEAD
    
    # Add temp scripts to Python path
    temp_scripts = os.path.join(temp_dir, "scripts")
    if temp_scripts not in sys.path:
        sys.path.insert(0, temp_scripts)
        print("Added temp scripts to Python path: {0}".format(temp_scripts))
    
    # Use executeDeferred for temporary installation too
    def deferred_temp_shelf():
        print("Executing deferred temporary shelf creation...")
        success = create_shelf_safely()
        if success:
            print("Deferred temporary shelf creation completed successfully")
        else:
            print("Deferred temporary shelf creation failed")
        return success
    
    maya.utils.executeDeferred(deferred_temp_shelf)
    
    return True

def uninstall():
    """Remove cmi-tools module system, MEL shelf, and prevent shelf recreation on Maya restart."""
    cmi_root = get_cmi_tools_root()
    modules_dir = get_modules_dir()
    mod_file = os.path.join(modules_dir, "cmi-tools.mod")
    
    # Remove shelf from Maya
=======

    scripts_dir = os.path.join(temp_root, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    return _import_and_build_shelf()

def uninstall():
    """Remove shelf, module file and entire cmi-tools folder."""
    shelf_removed = False
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
    try:
        if cmds.shelfLayout(SHELF_NAME, exists=True):
            cmds.deleteUI(SHELF_NAME, layout=True)
            shelf_removed = True
    except Exception:
        pass

    root = get_cmi_root()
    mod_file = os.path.join(get_modules_dir(), "cmi-tools.mod")

    if os.path.exists(root):
        shutil.rmtree(root, ignore_errors=True)
    if os.path.exists(mod_file):
<<<<<<< HEAD
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
                    print("Removed shelf MEL: {0}".format(shelf_path))
                except Exception as e:
                    print("Failed to remove shelf MEL: {0} ({1})".format(shelf_path, e))
    except Exception as e:
        print("Error searching for Maya shelf MEL files: {0}".format(e))
    
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
    """Try to get the installed fdma_shelf version, or return 'Not Installed' if not available."""
    try:
        # Check if the cmi-tools directory exists first
        cmi_root = get_cmi_tools_root()
        if not os.path.exists(cmi_root):
            return "Not Installed"
        
        # Check if the fdma_shelf package exists
        scripts_dir = os.path.join(cmi_root, "scripts")
        package_dir = os.path.join(scripts_dir, "fdma_shelf")
        if not os.path.exists(package_dir):
            return "Not Installed"
        
        # Try to add the scripts directory to path temporarily for import
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
            path_added = True
        else:
            path_added = False
        
        try:
            import fdma_shelf.utils.version_utils as vutils
            version = vutils.get_fdma2530_version()
            return version
        finally:
            # Clean up the path modification if we added it
            if path_added and scripts_dir in sys.path:
                sys.path.remove(scripts_dir)
    except Exception:
        return "Not Installed"

def show_install_dialog():
    """Show installation dialog with both installed and latest version."""
    installed_version = get_installed_package_version()
    latest_version = get_latest_release_version()
    
    # Create title based on installation status
    if installed_version == "Not Installed":
        title = "CMI Tools Installer (Latest: v{0})".format(latest_version)
    else:
        title = "CMI Tools Installer (Installed: v{0} | Latest: v{1})".format(installed_version, latest_version)
    
    choice = cmds.confirmDialog(
        title=title,
        message="CMI Tools Installation\n\nChoose installation type:\n\nInstall Tools: Permanent installation using Maya modules\nLoad Once: Temporary installation (session only)\nUninstall: Remove CMI Tools",
=======
        os.remove(mod_file)

    LOG.info(
        "Uninstalled cmi-tools%s",
        " and removed shelf" if shelf_removed else ""
    )
    return True

# ---------------------------------------------------------------------------
# Maya UI
# ---------------------------------------------------------------------------

def show_install_dialog():
    """Simple confirmDialog with permanent / temp / uninstall options."""
    # Get the actual version from repo before showing dialog
    actual_version = get_version_from_repo()
    
    choice = cmds.confirmDialog(
        title="CMI Tools Installer v{}".format(actual_version),
        message=(
            "Install FDMA 2530 Tools\n\n"
            "• Install – permanent (Maya modules)\n"
            "• Load Once – session only\n"
            "• Uninstall – remove everything"
        ),
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
        button=["Install", "Load Once", "Uninstall", "Cancel"],
        defaultButton="Install",
        cancelButton="Cancel",
    )

    if choice == "Install":
        if install_permanent():
            cmds.confirmDialog(
                title="Success",
                message=(
                    "FDMA 2530 shelf installed!\n\n"
                    "Version: {}\n"
                    "The shelf loads automatically at Maya startup."
                ).format(CURRENT_VERSION),
                button=["OK"],
            )
        else:
            cmds.confirmDialog(
                title="Error",
                message="Installation failed – check Script Editor.",
                button=["OK"],
            )
<<<<<<< HEAD
    elif choice == "Load Once":
        if install_temporary():
            cmds.confirmDialog(
                title="Success",
                message="CMI Tools - FDMA 2530 shelf loaded temporarily!\n\nShelf will be removed when Maya closes.\nFor permanent installation, run installer again.",
                button=["OK"]
=======

    elif choice == "Load Once":
        if install_temporary():
            cmds.confirmDialog(
                title="Loaded",
                message=(
                    "Shelf loaded for this session.\n"
                    "Version: {}\n"
                    "It will disappear when Maya closes."
                ).format(CURRENT_VERSION),
                button=["OK"],
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
            )
        else:
            cmds.confirmDialog(
                title="Error",
                message="Temporary load failed – check Script Editor.",
                button=["OK"],
            )
<<<<<<< HEAD
    elif choice == "Uninstall":
        # Check if anything is actually installed
        if installed_version == "Not Installed":
            cmds.confirmDialog(
                title="Nothing to Uninstall",
                message="CMI Tools is not currently installed.",
                button=["OK"]
            )
        else:
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
=======

    elif choice == "Uninstall":
        if cmds.confirmDialog(
            title="Confirm",
            message="Remove CMI Tools completely?",
            button=["Yes", "No"],
            defaultButton="No",
        ) == "Yes":
            uninstall()
            cmds.confirmDialog(
                title="Removed",
                message="CMI Tools uninstalled.",
                button=["OK"],
            )
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af

# Maya drag-and-drop entry point
def onMayaDroppedPythonFile(*_):
    show_install_dialog()

# When run standalone
if __name__ == "__main__":
    onMayaDroppedPythonFile()
