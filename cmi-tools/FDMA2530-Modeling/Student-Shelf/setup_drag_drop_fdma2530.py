"""
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
        src_pkg = os.path.join(shelf_dir, "fdma_shelf")
        src_cfg = os.path.join(shelf_dir, "shelf_config.json")
        src_manifest = os.path.join(
            repo_root, "cmi-tools", "FDMA2530-Modeling", "releases.json"
        )

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
    """Write a cmi-tools.mod file for Maya’s module system."""
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

    return _import_and_build_shelf()


def install_temporary():
    """Same as permanent but into a temp location (session only)."""
    temp_root = tempfile.mkdtemp(prefix="cmi_temp_")
    LOG.info("Installing temporarily into %s", temp_root)
    if not download_and_extract_package(temp_root):
        return False

    scripts_dir = os.path.join(temp_root, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    return _import_and_build_shelf()


def uninstall():
    """Remove shelf, module file and entire cmi-tools folder."""
    shelf_removed = False
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
    choice = cmds.confirmDialog(
        title="CMI Tools Installer v{}".format(CURRENT_VERSION),
        message=(
            "Install FDMA 2530 Tools\n\n"
            "• Install – permanent (Maya modules)\n"
            "• Load Once – session only\n"
            "• Uninstall – remove everything"
        ),
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
                message="Temporary load failed – check Script Editor.",
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
