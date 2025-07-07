"""
FDMA2530 Shelf Updater v2.0.2

Checks for updates via GitHub manifest, compares versions,
and installs updates on demand. Persists installed version,
caches manifest on failure, and provides clear Maya UI feedback.
"""

from __future__ import absolute_import, print_function

import os
import sys
import json
import ssl
import tempfile
import zipfile
import shutil
import urllib.request
import traceback

import maya.cmds as cmds
import maya.utils as mu

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

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

<<<<<<< HEAD
def _download_and_extract(zip_url):
    """Download release ZIP and extract fdma_shelf, shelf_config.json, and releases.json."""
    cmi_root = _get_cmi_tools_root()
    scripts_dir = os.path.join(cmi_root, "scripts")
    
    # Download ZIP
=======
def _download_and_unpack(zip_url):
    """
    Download the release ZIP, extract Student-Shelf,
    and overwrite fdma_shelf package and shelf_config.json.
    """
    # Paths
    app_dir = cmds.internalVar(userAppDir=True)
    dest_dir = os.path.join(app_dir, "cmi-tools", "scripts")
>>>>>>> dev-grader
    ctx = ssl.create_default_context()

    # Download ZIP to temp file
    with urllib.request.urlopen(zip_url, timeout=30, context=ctx) as resp:
<<<<<<< HEAD
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp.write(resp.read())
        tmp.close()
    
    # Extract
    extract_dir = tempfile.mkdtemp(prefix="cmi_update_")
    with zipfile.ZipFile(tmp.name, "r") as zf:
        zf.extractall(extract_dir)
    
    # Locate extracted repository root
    repo_root = next(
        os.path.join(extract_dir, d)
        for d in os.listdir(extract_dir)
        if d.startswith("NMSU_Scripts-")
    )

    # Source paths - corrected for proper structure
    student_shelf_src = os.path.join(repo_root, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf")
    manifest_src = os.path.join(repo_root, "cmi-tools", "FDMA2530-Modeling", "releases.json")
    
    # Copy fdma_shelf package
    fdma_shelf_src = os.path.join(student_shelf_src, "fdma_shelf")
    fdma_shelf_dest = os.path.join(scripts_dir, "fdma_shelf")
    if os.path.exists(fdma_shelf_dest):
        shutil.rmtree(fdma_shelf_dest)
    shutil.copytree(fdma_shelf_src, fdma_shelf_dest)
    print("Copied fdma_shelf package")
    
    # Copy shelf_config.json
    config_src = os.path.join(student_shelf_src, "shelf_config.json")
    if os.path.exists(config_src):
        shutil.copy2(config_src, scripts_dir)
        print("Copied shelf_config.json")
    
    # Copy releases.json manifest
    if os.path.exists(manifest_src):
        manifest_dest = os.path.join(scripts_dir, "releases.json")
        shutil.copy2(manifest_src, manifest_dest)
        print("Copied releases.json manifest")
    else:
        print(f"Warning: releases.json not found at {manifest_src}")
    
    # Cleanup
    os.unlink(tmp.name)
    shutil.rmtree(extract_dir)


def _perform_release_update(body):
    """Reload package, rebuild shelf, and notify user."""
    # Clear cached modules
=======
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
>>>>>>> dev-grader
    for mod in [m for m in sys.modules if m.startswith("fdma_shelf")]:
        sys.modules.pop(mod, None)
    import fdma_shelf
    mu.executeDeferred(lambda: fdma_shelf.build_shelf(startup=False))
    _persist_local_version(new_version)
    _update_button_color("up_to_date")
<<<<<<< HEAD
    _show_viewport_message(f"CMI Tools updated to the latest version: {fdma_shelf.__version__}")
=======
    _show_message(f"You’re now on version {new_version}")
>>>>>>> dev-grader

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def startup_check():
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

def run_update():
    """
    Called by the Update button: compare, prompt, download, install.
    """
    _update_button_color("checking")
    try:
        local = _local_version()
        remote, zip_url = _get_latest_release()
        if _is_newer(remote, local):
            _update_button_color("updates_available")
            if cmds.confirmDialog(
                title="CMI Tools Update",
                message=f"New release {remote} available. Install now?",
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No"
            ) == "Yes":
                try:
                    _download_and_unpack(zip_url)
                    _finalize_update(remote)
                except Exception as err:
                    print(f"Update failed: {err}")
                    _update_button_color("update_failed")
                    _show_message("Update failed. See script editor.", "#FF5555")
        else:
            _update_button_color("up_to_date")
            _show_message(f"You are on the latest version: {local}")
    except Exception as e:
        print(f"Update process error: {e}")
        _update_button_color("update_failed")
        _show_message("Update check failed. See script editor.", "#FF5555")
