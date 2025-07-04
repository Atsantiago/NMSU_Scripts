"""
FDMA 2530 Shelf Update System v2.0.1
=====================================

Handles checking for updates via GitHub Releases, version comparison,
and update installation for the FDMA 2530 shelf system.
Provides both startup checking and on-demand update functionality.

Functions
---------
check_for_updates() -> bool
    Check if a newer GitHub Release exists.

run_update() -> None  
    Main entry point called by Update button.

startup_check() -> None
    Perform startup update check with visual feedback.

get_update_status() -> str
    Get current update status for button coloring.
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

import maya.cmds as cmds
import maya.utils as mu

from .cache import (
    read_local_config_text,
    write_local_config,
    get_config_hash,
    cache_exists
)
from .downloader import download_raw

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

_REPO_OWNER     = "Atsantiago"
_REPO_NAME      = "NMSU_Scripts"
_RELEASE_API    = f"https://api.github.com/repos/{_REPO_OWNER}/{_REPO_NAME}/releases/latest"
_HTTP_TIMEOUT   = 10  # seconds

# Visual status colors for update button
_BUTTON_COLORS = {
    "up_to_date":        [0.5, 0.5, 0.5],  # Gray
    "updates_available": [0.2, 0.8, 0.2],  # Green
    "update_failed":     [0.8, 0.2, 0.2],  # Red
    "checking":          [0.8, 0.8, 0.2],  # Yellow
}

_SHELF_NAME = "FDMA_2530"

# ------------------------------------------------------------------
# Button visual feedback
# ------------------------------------------------------------------

def _update_button_color(status):
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
    try:
        cmds.inViewMessage(
            amg='<span style="color:{0}">{1}</span>'.format(color, message),
            pos="botLeft", fade=True, alpha=0.9,
            dragKill=False, fadeStayTime=3000
        )
    except Exception:
        pass

# ------------------------------------------------------------------
# GitHub Releases logic
# ------------------------------------------------------------------

def _get_latest_release_info():
    """Return (tag_name, zipball_url, body) from the latest GitHub release."""
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(_RELEASE_API, timeout=_HTTP_TIMEOUT, context=ctx) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["tag_name"], data["zipball_url"], data.get("body", "")

def _is_newer(tag):
    """Compare semantic tag vX.Y.Z against local __version__."""
    from fdma_shelf import __version__ as local_version
    def to_tuple(v):
        return tuple(int(p) for p in v.lstrip("v").split("."))
    try:
        return to_tuple(tag) > to_tuple(local_version)
    except Exception:
        return False

def _get_cmi_tools_root():
    """Return the cmi-tools root directory path."""
    maya_app = cmds.internalVar(userAppDir=True)
    return os.path.join(maya_app, "cmi-tools").replace("\\", "/")

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
    src = os.path.join(repo_root, "FDMA2530-Modeling", "Student-Shelf")
    # Overwrite package
    for name in ("fdma_shelf", "shelf_config.json"):
        source = os.path.join(src, name)
        dest = os.path.join(scripts_dir, name)
        if os.path.isdir(source):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
        elif os.path.isfile(source):
            shutil.copy2(source, dest)
    # Cleanup
    os.unlink(tmp.name)
    shutil.rmtree(extract_dir)

def _perform_release_update(body):
    """Reload package, rebuild shelf, and notify user."""
    # Clear cached modules
    for mod in [m for m in sys.modules if m.startswith("fdma_shelf")]:
        sys.modules.pop(mod)
    import fdma_shelf
    # Rebuild shelf
    mu.executeDeferred(lambda: fdma_shelf.build_shelf(startup=False))
    _update_button_color("up_to_date")
    _show_viewport_message("CMI Tools updated!\n" + body[:200])

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def startup_check():
    """Perform startup update check with visual feedback."""
    try:
        # Check only if previously installed
        if not cache_exists():
            return
        tag, _, _ = _get_latest_release_info()
        if _is_newer(tag):
            _update_button_color("updates_available")
            _show_viewport_message("New CMI Tools release available!")
        else:
            _update_button_color("up_to_date")
    except Exception as e:
        print("Startup update check failed: {0}".format(e))

def run_update():
    """Main entry point for Update button."""
    try:
        _update_button_color("checking")
        tag, zip_url, body = _get_latest_release_info()
        if _is_newer(tag):
            _update_button_color("updates_available")
            if cmds.confirmDialog(
                title="New Release Available",
                message=f"Release {tag} available. Install now?",
                button=["Yes", "No"],
                defaultButton="Yes", cancelButton="No"
            ) == "Yes":
                try:
                    _download_and_extract(zip_url)
                    _perform_release_update(body)
                except Exception as ue:
                    print("Release update failed: {0}".format(ue))
                    _update_button_color("update_failed")
                    _show_viewport_message("Update failed. See console.", "#FF5555")
        else:
            _update_button_color("up_to_date")
            _show_viewport_message("You are on the latest CMI Tools version.")
    except Exception as e:
        print("Update process failed: {0}".format(e))
        _update_button_color("update_failed")
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
        if _is_newer(tag):
            return "updates_available"
        return "up_to_date"
    except Exception:
        return "unknown"
