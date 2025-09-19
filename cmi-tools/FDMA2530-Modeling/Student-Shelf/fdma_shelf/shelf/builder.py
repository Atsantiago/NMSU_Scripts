"""
Builds or rebuilds the FDMA 2530 shelf from a local JSON config.

This module provides a clean, GT-Tools–inspired approach for
loading the shelf configuration regardless of Maya version.
Now includes dynamic version substitution from releases.json manifest.
"""
from __future__ import absolute_import, print_function
import json
import os
import hashlib
import maya.cmds as cmds
import maya.mel as mel
import maya.utils as mu
from fdma_shelf.utils.version_utils import get_fdma2530_version

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
_CONFIG_FILE = "shelf_config.json"
_SHELF_NAME = "FDMA_2530"
VERSION_TOKEN = "{version}"

# Directory containing this builder.py
_BUILDER_DIR = os.path.dirname(os.path.abspath(__file__))

# scripts/ directory where shelf_config.json resides
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(_BUILDER_DIR, os.pardir, os.pardir)
)

# Full path to JSON config
_CONFIG_PATH = os.path.join(_SCRIPTS_DIR, _CONFIG_FILE)
PACKAGE_VERSION = get_fdma2530_version()

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _read_json(path):
    """Read and return JSON object, or None on failure."""
    try:
        with open(path, "r") as fh:
            return json.load(fh)
    except Exception:
        cmds.warning("Failed to read shelf config at {}".format(path))
        return None

def _shelf_exists(name):
    """Return True if a shelf layout exists."""
    return cmds.shelfLayout(name, q=True, ex=True)

def _delete_shelf(name):
    """Delete the shelf layout if it exists."""
    if _shelf_exists(name):
        cmds.deleteUI(name, layout=True)

def _hash_text(text):
    """Return MD5 hash of text for change detection."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def _expand_version_tokens(obj):
    """
    Recursively expand all {version} tokens in the configuration data.
    Replaces any occurrence of {version} with the actual version number from releases.json.
    """
    if isinstance(obj, str):
        return obj.replace(VERSION_TOKEN, PACKAGE_VERSION)
    elif isinstance(obj, dict):
        return {key: _expand_version_tokens(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_expand_version_tokens(item) for item in obj]
    else:
        return obj

# ----------------------------------------------------------------------
# Main builder
# ----------------------------------------------------------------------
def _create_shelf(config, startup=False):
    """Create shelf UI according to config dict."""
    shelf_info = config.get("shelf_info", {})
    cell_w = int(shelf_info.get("cell_width", 35))
    cell_h = int(shelf_info.get("cell_height", 35))

    # Get Maya's shelf parent with validation
    g_top = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
    
    # Validate g_top and refresh if necessary
    if not g_top or g_top in ("None", "", "unknown"):
        cmds.refresh()
        g_top = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
        
        if not g_top or g_top in ("None", "", "unknown"):
            cmds.warning("Maya shelf system not ready - cannot create shelf")
            return False
    
    # Validate that the parent layout actually exists
    if not cmds.layout(g_top, query=True, exists=True):
        cmds.warning("Shelf parent layout does not exist")
        return False
    
    # Remove existing shelf
    _delete_shelf(_SHELF_NAME)
    
    # Create new shelf layout
    try:
        shelf = cmds.shelfLayout(
            _SHELF_NAME,
            parent=g_top,
            cellWidth=cell_w,
            cellHeight=cell_h,
        )
    except Exception as e:
        cmds.warning("Error creating shelf: {}".format(e))
        return False
    
    # Populate buttons and separators
    for item in config.get("buttons", []):
        if not item.get("enabled", True):
            continue
            
        if item.get("type") == "separator":
            cmds.separator(
                parent=shelf,
                style=item.get("style", "shelf"),
                hr=not item.get("horizontal", False),
                width=item.get("width", cell_w),
                height=item.get("height", cell_h),
            )
            continue
        
        if item.get("type") == "button":
            cmd_str = _build_button_command(item)
            cmds.shelfButton(
                parent=shelf,
                label=item.get("label", ""),
                image1=item.get("icon", "commandButton.png"),
                annotation=item.get("annotation", ""),
                command=cmd_str,
                width=int(item.get("width", cell_w)),
                height=int(item.get("height", cell_h)),
            )

    # Activate the new shelf tab
    if cmds.control(g_top, ex=True) and cmds.control(shelf, ex=True):
        cmds.tabLayout(g_top, edit=True, tabLabel=(shelf, _SHELF_NAME))

    if not startup:
        cmds.inViewMessage(
            amg="FDMA 2530 shelf rebuilt",
            pos="botLeft",
            fade=True
        )
    
    return True

def _build_button_command(item):
    """
    Return a Python command string for the shelf button.
    Priority:
    1. 'command' in JSON
    2. Update button fallback
    3. Legacy 'script_url' fallback
    """
    if "command" in item:
        return item["command"]
    
    label = item.get("label", "")
    if label.lower() == "update":
        return "import fdma_shelf.utils.updater as _u; _u.run_update()"
    
    url = item.get("script_url", "")
    if url:
        return (
            "import sys, urllib.request; "
            "from types import ModuleType; "
            "code = urllib.request.urlopen('{u}').read(); "
            "code = code.decode('utf-8') if isinstance(code, bytes) else code; "
            "mod = ModuleType('temp'); "
            "exec(code, mod.__dict__); "
            "fn = getattr(mod, 'main', None) or getattr(mod, 'run', None); "
            "fn() if callable(fn) else None"
        ).format(u=url)
    
    return "print('Button command not configured properly')"

def build_shelf(startup=False):
    """
    Public entry point. Reads config and schedules shelf creation.

    This function now includes dynamic version substitution, automatically
    replacing {version} tokens in the shelf configuration with the actual
    version number from the fdma_shelf package.

    Parameters
    ----------
    startup : bool
        If True, shelf is built at Maya startup (suppress messages).
    """
    # Check for and remove uninstall marker first
    marker = os.path.expanduser('~/.fdma2530_uninstalled')
    if os.path.exists(marker):
        os.remove(marker)
    
    cfg = _read_json(_CONFIG_PATH)
    if not cfg:
        cmds.warning("FDMA shelf config not found at {}".format(_CONFIG_PATH))
        return
    
    cfg = _expand_version_tokens(cfg)
    
    # For immediate installation, create shelf directly instead of deferred
    if not startup:
        _create_shelf(cfg, startup=startup)
    else:
        mu.executeDeferred(lambda: _create_shelf(cfg, startup=startup))
