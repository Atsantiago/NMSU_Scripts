"""
FDMA2530 Shelf Updater v2.0.2

Checks for updates via GitHub manifest, compares versions,
and installs updates on demand.
"""

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

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

_REPO_OWNER        = "Atsantiago"
_REPO_NAME         = "NMSU_Scripts"
_MANIFEST_URL      = (
    f"https://raw.githubusercontent.com/"
    f"{_REPO_OWNER}/{_REPO_NAME}/master/"
    "cmi-tools/FDMA2530-Modeling/releases.json"
)
_HTTP_TIMEOUT      = 10  # seconds
_SHELF_NAME        = "FDMA_2530"

# Button colors keyed by status
_BUTTON_COLORS = {
    "up_to_date":        [0.5, 0.5, 0.5],
    "updates_available": [0.2, 0.8, 0.2],
    "update_failed":     [0.8, 0.2, 0.2],
    "checking":          [0.8, 0.8, 0.2],
}

# ------------------------------------------------------------------
# Helpers: UI feedback
# ------------------------------------------------------------------

def _update_button_color(status):
    """Set the Update button’s shelf color by status."""
    try:
        if not cmds.shelfLayout(_SHELF_NAME, exists=True):
            return
        for btn in (cmds.shelfLayout(_SHELF_NAME, q=True, childArray=True) or []):
            if cmds.objectTypeUI(btn) == "shelfButton" and cmds.shelfButton(btn, q=True, label=True) == "Update":
                cmds.shelfButton(btn, e=True, backgroundColor=_BUTTON_COLORS[status])
                return
    except Exception:
        pass

def _show_message(text, color="#FFCC00"):
    """Show a brief in-viewport message."""
    try:
        cmds.inViewMessage(
            amg=f'<span style="color:{color}">{text}</span>',
            pos="botLeft", fade=True,
            fadeStayTime=3000, fadeOutTime=500
        )
    except Exception:
        pass

# ------------------------------------------------------------------
# Version logic
# ------------------------------------------------------------------

def _fetch_manifest():
    """Download and decode the releases.json manifest."""
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(_MANIFEST_URL, timeout=_HTTP_TIMEOUT, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _get_latest_release():
    """
    Return (latest_version, zip_url).
    Assumes the first entry in "releases" is the most recent.
    """
    data = _fetch_manifest()
    if not data.get("releases"):
        raise RuntimeError("No releases in manifest")
    latest = data["releases"][0]
    return latest["version"], latest["download_url"]

def _local_version():
    """Get the local shelf version from manifest field or fallback."""
    try:
        return _fetch_manifest().get("current_version")
    except Exception:
        from fdma_shelf import __version__  # fallback
        return __version__

def _is_newer(remote, local):
    """Return True if remote > local (semantic)."""
    try:
        rv = tuple(map(int, remote.lstrip("v").split(".")))
        lv = tuple(map(int, local.lstrip("v").split(".")))
        return rv > lv
    except Exception:
        return False

# ------------------------------------------------------------------
# Update operations
# ------------------------------------------------------------------

def _download_and_unpack(zip_url):
    """Download ZIP, unpack Student-Shelf, overwrite existing files."""
    # Build paths
    app_dir    = cmds.internalVar(userAppDir=True)
    cmi_dir    = os.path.join(app_dir, "cmi-tools", "scripts")
    ctx        = ssl.create_default_context()

    # Download to temp file
    with urllib.request.urlopen(zip_url, timeout=30, context=ctx) as resp:
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp_zip.write(resp.read())
        tmp_zip.close()

    # Extract to temp folder
    tmp_folder = tempfile.mkdtemp(prefix="cmi_update_")
    with zipfile.ZipFile(tmp_zip.name, "r") as zf:
        zf.extractall(tmp_folder)

    # Find extracted repo root
    root = next(d for d in os.listdir(tmp_folder) if d.startswith("NMSU_Scripts-"))
    src = os.path.join(tmp_folder, root, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf")

    # Overwrite fdma_shelf package + config
    for item in ("fdma_shelf", "shelf_config.json"):
        s = os.path.join(src, item)
        d = os.path.join(cmi_dir, item)
        if os.path.isdir(s):
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(s, d)
        elif os.path.isfile(s):
            shutil.copy2(s, d)

    # Clean up
    os.unlink(tmp_zip.name)
    shutil.rmtree(tmp_folder)

def _finalize_update():
    """Reload shelf and notify user."""
    # Clear old modules
    for m in [m for m in sys.modules if m.startswith("fdma_shelf")]:
        sys.modules.pop(m)
    import fdma_shelf
    mu.executeDeferred(lambda: fdma_shelf.build_shelf(startup=False))
    _update_button_color("up_to_date")
    _show_message(f"You’re on the latest: {fdma_shelf.__version__}")

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def startup_check():
    """Call at Maya startup to mark button if updates exist."""
    try:
        local = _local_version()
        remote, _ = _get_latest_release()
        _update_button_color("updates_available" if _is_newer(remote, local) else "up_to_date")
    except Exception:
        _update_button_color("up_to_date")

def run_update():
    """On-demand update: compare, prompt, download, install."""
    _update_button_color("checking")
    try:
        local = _local_version()
        remote, zip_url = _get_latest_release()

        if _is_newer(remote, local):
            _update_button_color("updates_available")
            if cmds.confirmDialog(
                title="CMI Tools Update",
                message=f"New release {remote} available. Install now?",
                button=["Yes","No"],
                defaultButton="Yes", cancelButton="No"
            ) == "Yes":
                try:
                    _download_and_unpack(zip_url)
                    _finalize_update()
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
