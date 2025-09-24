"""
CMI Tools - FDMA 2530 Shelf Installer
=====================================================

Drag-and-drop script that installs or loads the FDMA 2530 student
shelf.  Key features:

• Downloads the repository as a ZIP (fast, no git required).  
• Copies `fdma_shelf`, `shelf_config.json`, **and `releases.json`**  
  so version_utils can find the manifest.  
• Reads `current_version` from the manifest - no hard-coded numbers.  
• Creates a Maya `.mod` file so the shelf auto-loads.  
• Works on Windows / macOS / Linux, Maya 2016-2025, Py 2/3.  

Author:  Alexander T. Santiago   •   asanti89@nmsu.edu
"""

from __future__ import absolute_import, print_function

import json
import logging
import os
import shutil
import sys
import tempfile
import zipfile

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen

import maya.cmds as cmds

# ---------------------------------------------------------------------------
# Configuration / constants
# ---------------------------------------------------------------------------

REPO_ZIP_URL = (
    "https://github.com/Atsantiago/NMSU_Scripts/archive/refs/heads/master.zip"
)
MODULE_NAME = "cmi-tools"
SHELF_NAME = "FDMA_2530"
FALLBACK_VERSION = "2.0.1"

# CMI Tools directory structure (similar to prof-tools but separate)
CMI_TOOLS_DIR = "cmi-tools"  # Main directory name in Maya root

# Directory Structure:
# ~/maya/                    # Maya root directory (version-independent)
#   ├── modules/              # Maya modules directory  
#   │   └── cmi-tools.mod     # Module file that tells Maya about cmi-tools
#   └── cmi-tools/            # Main cmi-tools installation
#       └── scripts/          # Python scripts directory
#           ├── fdma_shelf/   # FDMA 2530 shelf package
#           ├── shelf_config.json
#           └── releases.json # Version manifest

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
    """cmi-tools installation root in Maya's main directory."""
    # Get Maya's main application directory (not version-specific)
    maya_app_dir = get_maya_app_dir()
    # Go up one level from version-specific to main Maya directory
    maya_root = os.path.dirname(maya_app_dir.rstrip("/\\"))
    return os.path.join(maya_root, CMI_TOOLS_DIR).replace("\\", "/")

def get_modules_dir():
    """Maya modules folder in root directory (version-independent); create it if missing."""
    # Get Maya's main application directory (not version-specific)
    maya_app_dir = get_maya_app_dir()
    # Go up one level from version-specific to main Maya directory
    maya_root = os.path.dirname(maya_app_dir.rstrip("/\\"))
    path = os.path.join(maya_root, "modules")
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
        if 'extract_dir' in locals() and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

def download_and_extract_package(target_dir):
    """
    Download the repository ZIP and copy everything we need into
    *target_dir*/scripts | icons | shelves.
    """
    global CURRENT_VERSION

    zip_bytes = safe_download(REPO_ZIP_URL)
    if not zip_bytes:
        return False

    # Write the ZIP to a temp file
    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    tmp_zip.write(zip_bytes)
    tmp_zip.close()

    try:
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
        
        fdma_shelf_src = os.path.join(shelf_dir, "fdma_shelf")
        config_src = os.path.join(shelf_dir, "shelf_config.json")
        manifest_src = os.path.join(
            repo_root, "cmi-tools", "FDMA2530-Modeling", "releases.json"
        )

        # Target locations
        scripts_dir = os.path.join(target_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        fdma_shelf_dst = os.path.join(scripts_dir, "fdma_shelf")
        config_dst = os.path.join(scripts_dir, "shelf_config.json")
        manifest_dst = os.path.join(scripts_dir, "releases.json")  # Fixed: Copy to scripts dir, not inside fdma_shelf

        # Copy fdma_shelf package
        if os.path.exists(fdma_shelf_src):
            if os.path.exists(fdma_shelf_dst):
                shutil.rmtree(fdma_shelf_dst)
            shutil.copytree(fdma_shelf_src, fdma_shelf_dst)
            LOG.info("Copied fdma_shelf to scripts/")
        else:
            LOG.error("fdma_shelf not found in repository")
            return False

        # Copy shelf_config.json
        if os.path.exists(config_src):
            shutil.copy2(config_src, config_dst)
            LOG.info("Copied shelf_config.json")

        # Copy releases.json to scripts directory (so version_utils can find it)
        if os.path.exists(manifest_src):
            shutil.copy2(manifest_src, manifest_dst)
            CURRENT_VERSION = _read_manifest_version(manifest_src)
            LOG.info("Copied releases.json to scripts/ (version: %s)", CURRENT_VERSION)

        return True

    except Exception as exc:
        LOG.error("Package extraction failed: %s", exc)
        return False
    finally:
        if os.path.exists(tmp_zip.name):
            os.unlink(tmp_zip.name)
        if 'extract_dir' in locals() and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

# ---------------------------------------------------------------------------
# Maya module file creation
# ---------------------------------------------------------------------------

def create_module_file():
    """Create the .mod file so Maya auto-loads our package."""
    try:
        modules_dir = get_modules_dir()
        mod_file = os.path.join(modules_dir, MODULE_NAME + ".mod")
        cmi_root = get_cmi_root()

        mod_content = "+ {name} {version} {root}\nscripts: scripts\n".format(
            name=MODULE_NAME, version=CURRENT_VERSION, root=cmi_root
        )

        with open(mod_file, "w") as f:
            f.write(mod_content)
        
        LOG.info("Created module file: %s", mod_file)
        return True

    except Exception as exc:
        LOG.error("Failed to create module file: %s", exc)
        return False

# ---------------------------------------------------------------------------
# Installation / shelf creation
# ---------------------------------------------------------------------------

def install_permanent():
    """Download and install CMI Tools to Maya's modules system."""
    cmi_root = get_cmi_root()
    
    # Create target directory
    if os.path.exists(cmi_root):
        shutil.rmtree(cmi_root)
    os.makedirs(cmi_root)

    # Download and extract
    if not download_and_extract_package(cmi_root):
        LOG.error("Package download/extraction failed")
        return False

    # Create module file
    if not create_module_file():
        LOG.error("Module file creation failed")
        return False

    # Create/update shelf
    if not create_shelf():
        LOG.error("Shelf creation failed")
        return False

    LOG.info("Installation complete")
    return True

def install_temporary():
    """Load the shelf for this session only (no permanent installation)."""
    # Add to Python path temporarily
    temp_dir = tempfile.mkdtemp(prefix="cmi_temp_")
    LOG.info("Created temporary directory: %s", temp_dir)
    
    if not download_and_extract_package(temp_dir):
        LOG.error("Temporary package download failed")
        return False

    scripts_dir = os.path.join(temp_dir, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        LOG.info("Added to Python path: %s", scripts_dir)

    # Verify files exist before creating shelf
    shelf_config_path = os.path.join(scripts_dir, "shelf_config.json")
    manifest_path = os.path.join(scripts_dir, "releases.json")
    fdma_shelf_path = os.path.join(scripts_dir, "fdma_shelf")
    
    LOG.info("Checking file locations:")
    LOG.info("  shelf_config.json: %s (exists: %s)", shelf_config_path, os.path.exists(shelf_config_path))
    LOG.info("  releases.json: %s (exists: %s)", manifest_path, os.path.exists(manifest_path))
    LOG.info("  fdma_shelf/: %s (exists: %s)", fdma_shelf_path, os.path.exists(fdma_shelf_path))

    # Create shelf for this session
    return create_shelf()

def create_shelf():
    """Create the FDMA 2530 shelf using shelf_config.json."""
    try:
        # Try to import the shelf builder
        try:
            import fdma_shelf.shelf.builder as shelf_builder
            LOG.info("Successfully imported shelf builder")
        except ImportError as exc:
            LOG.error("Cannot import shelf builder: %s", exc)
            return False

        # Build the shelf
        LOG.info("Attempting to build shelf...")
        shelf_builder.build_shelf()
        LOG.info("Shelf created successfully")
        
        # Verify shelf was actually created
        import maya.cmds as cmds
        if cmds.shelfLayout("FDMA_2530", query=True, exists=True):
            LOG.info("Shelf 'FDMA_2530' verified to exist in Maya")
            return True
        else:
            LOG.warning("Shelf build completed but 'FDMA_2530' shelf not found")
            return False

    except Exception as exc:
        LOG.error("Shelf creation failed: %s", exc)
        import traceback
        LOG.error("Full traceback: %s", traceback.format_exc())
        return False

# ---------------------------------------------------------------------------
# Uninstallation
# ---------------------------------------------------------------------------

def uninstall():
    """Remove CMI Tools completely."""
    try:
        # Remove shelf if it exists
        if cmds.shelfLayout(SHELF_NAME, exists=True):
            cmds.deleteUI(SHELF_NAME, layout=True)
            LOG.info("Removed shelf: %s", SHELF_NAME)

        # Remove installation directory
        cmi_root = get_cmi_root()
        if os.path.exists(cmi_root):
            shutil.rmtree(cmi_root)
            LOG.info("Removed directory: %s", cmi_root)

        # Remove module file
        mod_file = os.path.join(get_modules_dir(), MODULE_NAME + ".mod")
        if os.path.exists(mod_file):
            os.unlink(mod_file)
            LOG.info("Removed module file: %s", mod_file)

        return True

    except Exception as exc:
        LOG.error("Uninstall failed: %s", exc)
        return False

# ---------------------------------------------------------------------------
# Status checking
# ---------------------------------------------------------------------------

def get_installed_version():
    """Return the installed version, or 'Not Installed'."""
    try:
        cmi_root = get_cmi_root()
        manifest_path = os.path.join(
            cmi_root, "scripts", "releases.json"
        )
        
        if os.path.exists(manifest_path):
            return _read_manifest_version(manifest_path)
        
        return "Not Installed"

    except Exception:
        return "Not Installed"

# ---------------------------------------------------------------------------
# UI Dialog
# ---------------------------------------------------------------------------

def show_install_dialog():
    """Show the main installation dialog."""
    # Get version info
    current_version = get_version_from_repo()
    installed_version = get_installed_version()
    
    # Determine dialog message
    if installed_version == "Not Installed":
        status_msg = "Status: Not installed"
        default_choice = "Install"
    elif installed_version == current_version:
        status_msg = "Status: Up to date (v{})".format(installed_version)
        default_choice = "Load Once"
    else:
        status_msg = "Status: Outdated (v{} → v{})".format(
            installed_version, current_version
        )
        default_choice = "Update"

    # Show dialog
    choice = cmds.confirmDialog(
        title="CMI Tools - FDMA 2530 Installer v{}".format(current_version),
        message=(
            "Maya shelf system for FDMA 2530 students.\n\n"
            "{}\n"
            "Latest version: v{}\n\n"
            "Choose an option:"
        ).format(status_msg, current_version),
        button=["Install", "Load Once", "Uninstall", "Cancel"],
        defaultButton=default_choice,
        cancelButton="Cancel",
        dismissString="Cancel"
    )

    # Handle user choice
    if choice == "Install":
        if install_permanent():
            cmds.confirmDialog(
                title="Installed",
                message=(
                    "CMI Tools installed successfully!\n"
                    "Version: {}\n"
                    "Shelf will load automatically in future Maya sessions."
                ).format(CURRENT_VERSION),
                button=["OK"],
            )
        else:
            cmds.confirmDialog(
                title="Error",
                message="Installation failed - check Script Editor for details.",
                button=["OK"],
            )

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
            )
        else:
            cmds.confirmDialog(
                title="Error",
                message="Temporary load failed - check Script Editor.",
                button=["OK"],
            )

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

# Maya drag-and-drop entry point
def onMayaDroppedPythonFile(*_):
    show_install_dialog()

# When run standalone
if __name__ == "__main__":
    onMayaDroppedPythonFile()
