from __future__ import absolute_import, print_function
"""
FDMA2530 Shelf Updater v2.0.2

<<<<<<< HEAD
Handles checking for updates via GitHub Releases, version comparison,
and update installation for the FDMA 2530 shelf system.
Provides both startup checking and on-demand update functionality.

Update Button Highlighting
-------------------------
The Update button on the shelf is automatically colored based on update status:
- Green: Updates are available
- Gray: Up-to-date (default)
- Yellow: Checking for updates
- Red: Update check or installation failed

This happens automatically on Maya startup and when the Update button is clicked.

Functions
---------
check_for_updates() -> bool
    Check if a newer GitHub Release exists.

run_update() -> None  
    Main entry point called by Update button.

startup_check() -> None
    Perform startup update check with visual feedback.
    Called automatically when Maya starts, even on first startup.

get_update_status() -> str
    Get current update status for button coloring.
"""
=======
Checks for updates via GitHub manifest, compares versions,
and installs updates on demand. Persists installed version,
caches manifest on failure, and provides clear Maya UI feedback.
"""

from __future__ import absolute_import, print_function

>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
import os
import sys
import json
import ssl
import tempfile
import zipfile
import shutil
import urllib.request
import traceback

try:
    import maya.cmds as cmds
    import maya.utils as mu
except ImportError:
    cmds = None
    mu = None

<<<<<<< HEAD
from .cache import (
    read_local_config_text,
    get_config_hash,
    cache_exists
)
from .downloader import download_raw
from fdma_shelf.utils.version_utils import get_fdma2530_version

=======
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

<<<<<<< HEAD
_REPO_OWNER     = "Atsantiago"
_REPO_NAME      = "NMSU_Scripts"
_RELEASES_MANIFEST_URL = "https://raw.githubusercontent.com/{0}/{1}/master/cmi-tools/FDMA2530-Modeling/releases.json".format(_REPO_OWNER, _REPO_NAME)
_HTTP_TIMEOUT = 10  # seconds
=======
_REPO_OWNER   = "Atsantiago"
_REPO_NAME    = "NMSU_Scripts"
_MANIFEST_URL = (
    f"https://raw.githubusercontent.com/"
    f"{_REPO_OWNER}/{_REPO_NAME}/master/"
    "cmi-tools/FDMA2530-Modeling/releases.json"
)
_CACHE_FILE   = os.path.join(
    cmds.internalVar(userAppDir=True),
    "cmi-tools",
    "releases_cache.json"
)
_HTTP_TIMEOUT = 10  # seconds
_SHELF_NAME   = "FDMA_2530"
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af

# Button colors keyed by status
_BUTTON_COLORS = {
    "up_to_date":        [0.5, 0.5, 0.5],
    "updates_available": [0.2, 0.8, 0.2],
    "update_failed":     [0.8, 0.2, 0.2],
    "checking":          [0.8, 0.8, 0.2],
}

# Maya optionVar name to persist installed version
_OPTION_VAR = "fdma2530_installed_version"

# ------------------------------------------------------------------
<<<<<<< HEAD
# Helper Functions for GitHub Release Handling
# ------------------------------------------------------------------

def _is_newer(remote_version, local_version):
    """Compare semantic versions vX.Y.Z."""
    try:
        def to_tuple(v):
            # Remove 'v' prefix if present and split on '.'
            clean_v = v.lstrip("v")
            return tuple(int(p) for p in clean_v.split("."))
        return to_tuple(remote_version) > to_tuple(local_version)
    except Exception as e:
        print("Version comparison failed: {0}".format(e))
        return False

def _get_cmi_tools_root():
    """Return the cmi-tools root directory path."""
    if cmds is not None:
        maya_app = cmds.internalVar(userAppDir=True)
        return os.path.join(maya_app, "cmi-tools").replace("\\", "/")
    else:
        return os.path.join(os.path.expanduser("~"), "maya", "cmi-tools").replace("\\", "/")

def _download_and_extract(zip_url):
    """Download release ZIP and extract fdma_shelf and shelf_config.json."""
    cmi_root = _get_cmi_tools_root()
    scripts_dir = os.path.join(cmi_root, "scripts")
    # Download ZIP
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(zip_url, timeout=30, context=ctx) as resp:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp.write(resp.read())
        tmp.close()
    # Extract
    extract_dir = tempfile.mkdtemp(prefix="cmi_update_")
    with zipfile.ZipFile(tmp.name, "r") as zf:
        zf.extractall(extract_dir)
    # Locate extracted Student-Shelf folder
    repo_root = next(
        os.path.join(extract_dir, d)
        for d in os.listdir(extract_dir)
        if d.startswith("NMSU_Scripts-")
    )
    src = os.path.join(repo_root, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf")
    # Overwrite package and config
    for name in ("fdma_shelf", "shelf_config.json"):
        source = os.path.join(src, name)
        dest = os.path.join(scripts_dir, name)
        if os.path.isdir(source):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
        elif os.path.isfile(source):
            shutil.copy2(source, dest)
    # Copy releases.json to fdma_shelf package for version detection
    releases_source = os.path.join(repo_root, "cmi-tools", "FDMA2530-Modeling", "releases.json")
    releases_dest = os.path.join(scripts_dir, "fdma_shelf", "releases.json")
    if os.path.exists(releases_source):
        shutil.copy2(releases_source, releases_dest)
        print("Updated releases.json in fdma_shelf package")
    # Cleanup
    os.unlink(tmp.name)
    shutil.rmtree(extract_dir)

def _perform_release_update(new_version):
    """Reload package, clear version cache, rebuild shelf, and notify user."""
    # Clear cached modules
    for mod in [m for m in sys.modules if m.startswith("fdma_shelf")]:
        sys.modules.pop(mod)
    # Clear version cache so get_fdma2530_version() reads the new manifest
    try:
        import fdma_shelf.utils.version_utils as vutils
        vutils.clear_version_cache()
    except Exception as e:
        print("Warning: Could not clear version cache after update: {}".format(e))
    import fdma_shelf
    # Rebuild shelf
    if mu is not None:
        mu.executeDeferred(lambda: fdma_shelf.build_shelf(startup=False))
    _update_button_color("up_to_date")
    _show_viewport_message("CMI Tools updated to the latest version: {0}".format(new_version))
=======
# UI Feedback Helpers
# ------------------------------------------------------------------

def _update_button_color(status):
    """Set the Update button’s shelf color by status."""
    try:
        if not cmds.shelfLayout(_SHELF_NAME, exists=True):
            return
        for btn in (cmds.shelfLayout(_SHELF_NAME, q=True, childArray=True) or []):
            if (cmds.objectTypeUI(btn) == "shelfButton" and
                    cmds.shelfButton(btn, q=True, label=True) == "Update"):
                cmds.shelfButton(btn, e=True, backgroundColor=_BUTTON_COLORS[status])
                return
    except Exception:
        pass

def _show_message(text, color="#FFCC00"):
    """Show a brief in-viewport message."""
    try:
        cmds.inViewMessage(
            amg=f'<span style="color:{color}">{text}</span>',
            pos="botLeft",
            fade=True,
            fadeStayTime=3000,
            fadeOutTime=500
        )
    except Exception:
        print(text)

# ------------------------------------------------------------------
# Manifest Fetching with Cache Fallback
# ------------------------------------------------------------------

def _fetch_manifest():
    """
    Download and decode the releases.json manifest.
    On failure, load from local cache.
    After successful download, overwrite cache.
    """
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(_MANIFEST_URL, timeout=_HTTP_TIMEOUT, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        # Ensure cache directory exists
        cache_dir = os.path.dirname(_CACHE_FILE)
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)
        # Write cache
        with open(_CACHE_FILE, "w") as f:
            json.dump(data, f)
        return data
    except Exception:
        # Fallback to cache
        try:
            with open(_CACHE_FILE, "r") as f:
                data = json.load(f)
            _show_message("Using cached update data", "#FFCC00")
            return data
        except Exception:
            traceback.print_exc()
            raise RuntimeError("Could not load manifest or cache")

# ------------------------------------------------------------------
# Version Logic
# ------------------------------------------------------------------

def _get_latest_release():
    """
    Return (latest_version, download_url).
    Finds matching current_version entry first; else picks highest version.
    """
    data = _fetch_manifest()
    curr = data.get("current_version")
    releases = data.get("releases", [])
    # 1. Try to find manifest entry matching current_version
    for entry in releases:
        if entry.get("version") == curr:
            return entry["version"], entry["download_url"]
    # 2. Fallback: sort all releases descending by semantic tuple
    def _ver_tuple(v):
        return tuple(int(p) for p in v.split("."))
    sorted_releases = sorted(
        releases,
        key=lambda e: _ver_tuple(e.get("version", "0.0.0")),
        reverse=True
    )
    if not sorted_releases:
        raise RuntimeError("No releases available in manifest")
    latest = sorted_releases[0]
    return latest["version"], latest["download_url"]

def _local_version():
    """
    Return the installed version:
      1. Maya optionVar if set
      2. manifest 'current_version'
      3. fallback to package __version__
    """
    try:
        if cmds.optionVar(exists=_OPTION_VAR):
            ver = cmds.optionVar(query=_OPTION_VAR)
            return ver
    except Exception:
        pass
    # manifest fallback
    try:
        data = _fetch_manifest()
        if data.get("current_version"):
            return data["current_version"]
    except Exception:
        pass
    # package fallback
    from fdma_shelf import __version__
    return __version__

def _persist_local_version(new_version):
    """Store the installed version in Maya optionVar."""
    try:
        cmds.optionVar(stringValue=(_OPTION_VAR, new_version))
    except Exception:
        pass

def _is_newer(remote, local):
    """Return True if semantic version remote > local."""
    try:
        rv = tuple(int(p) for p in remote.split("."))
        lv = tuple(int(p) for p in local.split("."))
        return rv > lv
    except Exception:
        return False

# ------------------------------------------------------------------
# Download & Install
# ------------------------------------------------------------------

def _download_and_unpack(zip_url):
    """
    Download the release ZIP, extract Student-Shelf,
    and overwrite fdma_shelf package and shelf_config.json.
    """
    # Paths
    app_dir = cmds.internalVar(userAppDir=True)
    dest_dir = os.path.join(app_dir, "cmi-tools", "scripts")
    ctx = ssl.create_default_context()

    # Download ZIP to temp file
    with urllib.request.urlopen(zip_url, timeout=30, context=ctx) as resp:
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp_zip.write(resp.read())
        tmp_zip.close()

    # Extract
    tmp_folder = tempfile.mkdtemp(prefix="cmi_update_")
    with zipfile.ZipFile(tmp_zip.name, "r") as zf:
        zf.extractall(tmp_folder)

    # Locate repo root
    root_name = next(
        d for d in os.listdir(tmp_folder) if d.startswith("NMSU_Scripts-")
    )
    src = os.path.join(
        tmp_folder,
        root_name,
        "cmi-tools",
        "FDMA2530-Modeling",
        "Student-Shelf"
    )

    # Overwrite package and config
    for name in ("fdma_shelf", "shelf_config.json"):
        src_path = os.path.join(src, name)
        dest_path = os.path.join(dest_dir, name)
        if os.path.isdir(src_path):
            shutil.rmtree(dest_path, ignore_errors=True)
            shutil.copytree(src_path, dest_path)
        elif os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)

    # Cleanup
    os.unlink(tmp_zip.name)
    shutil.rmtree(tmp_folder)

def _finalize_update(new_version):
    """
    Clear cached modules, rebuild shelf,
    persist version, update UI feedback.
    """
    # Remove old modules
    for mod in [m for m in sys.modules if m.startswith("fdma_shelf")]:
        sys.modules.pop(mod, None)
    import fdma_shelf
    mu.executeDeferred(lambda: fdma_shelf.build_shelf(startup=False))
    _persist_local_version(new_version)
    _update_button_color("up_to_date")
    _show_message(f"You’re now on version {new_version}")
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def startup_check():
<<<<<<< HEAD
    """Perform startup update check with visual feedback."""
    try:
        # Always check for updates on startup (removed cache_exists() check)
        # This ensures update button highlighting works on first Maya startup
        tag, _, _ = _get_latest_release_info()
        local_version = get_fdma2530_version()
        if _is_newer(tag, local_version):
            # Try to update button color, but don't fail if shelf isn't ready
            if _update_button_color("updates_available"):
                _show_viewport_message("New CMI Tools release available!")
        else:
            # Try to update button color, but don't fail if shelf isn't ready
            if _update_button_color("up_to_date"):
                _show_viewport_message(
                    "You are already the latest version of CMI Tools! {0}".format(local_version)
                )
    except Exception as e:
        print("Startup update check failed: {0}".format(e))
=======
    """
    On Maya startup, mark the button if updates exist;
    otherwise show ‘up_to_date’ color.
    """
    try:
        local = _local_version()
        remote, _ = _get_latest_release()
        status = "updates_available" if _is_newer(remote, local) else "up_to_date"
        _update_button_color(status)
    except Exception:
        _update_button_color("up_to_date")
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af

def run_update():
    """
    Called by the Update button: compare, prompt, download, install.
    """
    _update_button_color("checking")
    try:
<<<<<<< HEAD
        _update_button_color("checking")
        tag, zip_url, body = _get_latest_release_info()
        local_version = get_fdma2530_version()
        if _is_newer(tag, local_version):
            _update_button_color("updates_available")
            if cmds is not None and cmds.confirmDialog(
                title="New Release Available",
                message=(
                    "Installed version: {0}\n"
                    "Latest version: {1}\n\n"
                    "Install the latest version now?"
                ).format(local_version, tag),
=======
        local = _local_version()
        remote, zip_url = _get_latest_release()
        if _is_newer(remote, local):
            _update_button_color("updates_available")
            if cmds.confirmDialog(
                title="CMI Tools Update",
                message=f"New release {remote} available. Install now?",
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No"
            ) == "Yes":
                try:
<<<<<<< HEAD
                    _download_and_extract(zip_url)
                    _perform_release_update(tag)
                except Exception as ue:
                    print("Release update failed: {0}".format(ue))
=======
                    _download_and_unpack(zip_url)
                    _finalize_update(remote)
                except Exception as err:
                    print(f"Update failed: {err}")
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
                    _update_button_color("update_failed")
                    _show_message("Update failed. See script editor.", "#FF5555")
        else:
            _update_button_color("up_to_date")
<<<<<<< HEAD
            _show_viewport_message(
                "You are already the latest version of CMI Tools! {0}".format(local_version)
            )
=======
            _show_message(f"You are on the latest version: {local}")
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
    except Exception as e:
        print(f"Update process error: {e}")
        _update_button_color("update_failed")
<<<<<<< HEAD
        _show_viewport_message("Update check failed. See console.", "#FF5555")


def check_for_updates():
    """
    Legacy check for shelf_config.json changes.
    Returns True if JSON changed since last cache.
    """
    try:
        latest = download_raw(
            "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
            "FDMA2530-Modeling/Student-Shelf/shelf_config.json", timeout=10
        )
        if not latest:
            return False
        local = read_local_config_text()
        return get_config_hash(latest) != get_config_hash(local)
    except Exception:
        return False

def get_update_status():
    """
    Get current update status: 'up_to_date', 'updates_available',
    'update_failed', or 'unknown'
    """
    try:
        tag, _, _ = _get_latest_release_info()
        local_version = get_fdma2530_version()
        if _is_newer(tag, local_version):
            return "updates_available"
        return "up_to_date"
    except Exception:
        return "unknown"

# ------------------------------------------------------------------
# Button visual feedback
# ------------------------------------------------------------------

def _update_button_color(status):
    if cmds is None:
        return False
    try:
        if not cmds.shelfLayout(_SHELF_NAME, exists=True):
            return False
        buttons = cmds.shelfLayout(_SHELF_NAME, query=True, childArray=True) or []
        for btn in buttons:
            try:
                if cmds.objectTypeUI(btn) == "shelfButton":
                    label = cmds.shelfButton(btn, query=True, label=True)
                    if label == "Update":
                        color = _BUTTON_COLORS.get(status, _BUTTON_COLORS["up_to_date"])
                        cmds.shelfButton(btn, edit=True, backgroundColor=color)
                        return True
            except Exception:
                continue
        return False
    except Exception:
        return False

def _show_viewport_message(message, color="#FFCC00"):
    if cmds is None:
        return
    try:
        cmds.inViewMessage(
            amg='<span style="color:{0}">{1}</span>'.format(color, message),
            pos="botLeft", fade=True, alpha=0.9,
            dragKill=False, fadeStayTime=3000
        )
    except Exception:
        pass
def _get_releases_manifest():
    """Return manifest data from the releases.json file."""
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(_RELEASES_MANIFEST_URL, timeout=_HTTP_TIMEOUT, context=ctx) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data

def _get_latest_release_info():
    """Return (version, download_url, description) from the manifest."""
    manifest = _get_releases_manifest()
    current_version = manifest["current_version"]
    
    # Find the release data for the current version
    for release in manifest["releases"]:
        if release["version"] == current_version:
            return (
                release["version"],
                release["download_url"],
                release["description"]
            )
    
    # Fallback if current version not found in releases
    if manifest["releases"]:
        latest = manifest["releases"][0]
        return latest["version"], latest["download_url"], latest["description"]
    
    raise ValueError("No releases found in manifest")
=======
        _show_message("Update check failed. See script editor.", "#FF5555")
>>>>>>> bd60b003fa2b3ac6c11a49f980642cfa6d6f37af
