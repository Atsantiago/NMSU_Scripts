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

# Maya optionVar for installed version
_OPTION_VAR = "fdma2530_installed_version"

# ------------------------------------------------------------------
# UI Feedback Helpers
# ------------------------------------------------------------------

def _update_button_color(status):
    """Set the Update button’s shelf color."""
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
    On failure, load from local cache; update cache on success.
    """
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(_MANIFEST_URL, timeout=_HTTP_TIMEOUT, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        # Write cache
        cache_dir = os.path.dirname(_CACHE_FILE)
        os.makedirs(cache_dir, exist_ok=True)
        with open(_CACHE_FILE, "w") as f:
            json.dump(data, f)
        return data
    except Exception:
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
    """
    data = _fetch_manifest()
    curr = data.get("current_version")
    releases = data.get("releases", [])
    # 1. Match current_version entry
    for entry in releases:
        if entry.get("version") == curr:
            return entry["version"], entry["download_url"]
    # 2. Fallback: sort by semantic version
    def _ver_tuple(v): return tuple(int(p) for p in v.split("."))
    sorted_releases = sorted(releases, key=lambda e: _ver_tuple(e["version"]), reverse=True)
    if not sorted_releases:
        raise RuntimeError("No releases in manifest")
    latest = sorted_releases[0]
    return latest["version"], latest["download_url"]

def _local_version():
    """
    Return the installed version (optionVar → manifest → __version__).
    """
    try:
        if cmds.optionVar(exists=_OPTION_VAR):
            return cmds.optionVar(query=_OPTION_VAR)
    except Exception:
        pass
    try:
        data = _fetch_manifest()
        if data.get("current_version"):
            return data["current_version"]
    except Exception:
        pass
    from fdma_shelf import __version__
    return __version__

def _persist_local_version(new_version):
    """Store the installed version."""
    try:
        cmds.optionVar(stringValue=(_OPTION_VAR, new_version))
    except Exception:
        pass

def _is_newer(remote, local):
    """Return True if semantic remote > local."""
    try:
        rv = tuple(int(p) for p in remote.split("."))
        lv = tuple(int(p) for p in local.split("."))
        return rv > lv
    except Exception:
        return False

# ------------------------------------------------------------------
# Download & Install (with tools folder)
# ------------------------------------------------------------------

def _download_and_unpack(zip_url):
    """
    Download the release ZIP, extract Student-Shelf,
    and overwrite fdma_shelf package, tools folder, and shelf_config.json.
    """
    # Paths
    app_dir  = cmds.internalVar(userAppDir=True)
    scripts  = os.path.join(app_dir, "cmi-tools", "scripts")
    ctx      = ssl.create_default_context()

    # Download ZIP
    with urllib.request.urlopen(zip_url, timeout=30, context=ctx) as resp:
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp_zip.write(resp.read())
        tmp_zip.close()

    # Extract
    tmp_folder = tempfile.mkdtemp(prefix="cmi_update_")
    with zipfile.ZipFile(tmp_zip.name, "r") as zf:
        zf.extractall(tmp_folder)

    # Locate repo root folder
    root = next(d for d in os.listdir(tmp_folder) if d.startswith("NMSU_Scripts-"))
    src_base = os.path.join(
        tmp_folder, root,
        "cmi-tools", "FDMA2530-Modeling", "Student-Shelf"
    )

    # Overwrite fdma_shelf package
    src_pkg = os.path.join(src_base, "fdma_shelf")
    dst_pkg = os.path.join(scripts, "fdma_shelf")
    shutil.rmtree(dst_pkg, ignore_errors=True)
    shutil.copytree(src_pkg, dst_pkg)

    # Overwrite tools folder
    src_tools = os.path.join(src_base, "fdma_shelf", "tools")
    dst_tools = os.path.join(scripts, "fdma_shelf", "tools")
    shutil.rmtree(dst_tools, ignore_errors=True)
    shutil.copytree(src_tools, dst_tools)

    # Overwrite shelf_config.json
    for filename in ("shelf_config.json",):
        src_f = os.path.join(src_base, filename)
        dst_f = os.path.join(scripts, filename)
        if os.path.isfile(src_f):
            shutil.copy2(src_f, dst_f)

    # Cleanup
    os.unlink(tmp_zip.name)
    shutil.rmtree(tmp_folder)

def _finalize_update(new_version):
    """
    Clear cached modules, rebuild shelf, persist version, and notify.
    """
    # Remove old modules
    for mod in [m for m in sys.modules if m.startswith("fdma_shelf")]:
        sys.modules.pop(mod, None)
    _persist_local_version(new_version)
    import fdma_shelf
    mu.executeDeferred(lambda: fdma_shelf.build_shelf(startup=False))
    _update_button_color("up_to_date")
    _show_message(f"You’re now on version {new_version}")

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def startup_check():
    """On Maya startup, mark the button if updates exist."""
    try:
        local = _local_version()
        remote, _ = _get_latest_release()
        status = "updates_available" if _is_newer(remote, local) else "up_to_date"
        _update_button_color(status)
    except Exception:
        _update_button_color("up_to_date")

def run_update():
    """
    On-demand update: check → notify if none → prompt if available → install.
    """
    _update_button_color("checking")
    try:
        local = _local_version()
        remote, zip_url = _get_latest_release()

        if not _is_newer(remote, local):
            _update_button_color("up_to_date")
            _show_message(f"You are on the current version of CMI Tools: {local}")
            return

        _update_button_color("updates_available")
        ans = cmds.confirmDialog(
            title="CMI Tools Update Available",
            message=(
                f"A new version of CMI Tools is available.\n\n"
                f"Current Version: {local}\n"
                f"New Version: {remote}\n\n"
                "Would you like to update the shelf now?"
            ),
            button=["Yes", "No"],
            defaultButton="Yes",
            cancelButton="No",
            dismissString="No"
        )
        if ans != "Yes":
            return

        _update_button_color("checking")
        _download_and_unpack(zip_url)
        _finalize_update(remote)
        cmds.confirmDialog(
            title="Update Complete",
            message=f"CMI Tools successfully updated to version {remote}.",
            button=["OK"],
            defaultButton="OK"
        )
    except Exception as e:
        print(f"Update process error: {e}")
        _update_button_color("update_failed")
        _show_message("Update check failed. See script editor.", "#FF5555")
