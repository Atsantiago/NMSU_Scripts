from __future__ import absolute_import, print_function
"""
Builds or rebuilds the FDMA 2530 shelf from a local JSON config.
This module provides a clean, GT-Tools–inspired approach for
loading the shelf configuration regardless of Maya version.
Now includes dynamic version substitution from releases.json manifest.
"""
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
    print("[FDMA SHELF DEBUG] Starting shelf creation with startup={}".format(startup))
    
    shelf_info = config.get("shelf_info", {})
    cell_w = int(shelf_info.get("cell_width", 35))
    cell_h = int(shelf_info.get("cell_height", 35))

    # Get Maya's shelf parent with improved validation
    g_top = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
    print("[FDMA SHELF DEBUG] Initial g_top value: '{}'".format(g_top))
    
    # Improved g_top validation - check for multiple failure states
    if not g_top or g_top in ("None", "", "unknown"):
        print("[FDMA SHELF DEBUG] g_top invalid, attempting refresh")
        # Force UI refresh and try again
        cmds.refresh()
        g_top = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
        print("[FDMA SHELF DEBUG] After refresh g_top: '{}'".format(g_top))
        
        if not g_top or g_top in ("None", "", "unknown"):
            cmds.warning("Maya shelf system not ready - cannot create shelf")
            return False
    
    # Validate that the parent layout actually exists
    if not cmds.layout(g_top, query=True, exists=True):
        print("[FDMA SHELF DEBUG] Parent layout {} does not exist".format(g_top))
        return False
    
    print("[FDMA SHELF DEBUG] Using validated shelf parent: {}".format(g_top))
    
    # Remove existing shelf
    _delete_shelf(_SHELF_NAME)
    
    # Create new shelf layout with explicit parent specification
    try:
        shelf = cmds.shelfLayout(
            _SHELF_NAME,
            parent=g_top,  # Explicit parent instead of relying on setParent
            cellWidth=cell_w,
            cellHeight=cell_h,
        )
        print("[FDMA SHELF DEBUG] Created shelf: {}".format(shelf))
    except Exception as e:
        print("[FDMA SHELF DEBUG] Error creating shelf: {}".format(e))
        return False
    
    # Populate buttons and separators
    for item in config.get("buttons", []):
        if not item.get("enabled", True):
            continue
            
        if item.get("type") == "separator":
            try:
                cmds.separator(
                    parent=shelf,
                    style=item.get("style", "shelf"),
                    hr=not item.get("horizontal", False),
                    width=item.get("width", cell_w),
                    height=item.get("height", cell_h),
                )
                print("[FDMA SHELF DEBUG] Added separator")
            except Exception as e:
                print("[FDMA SHELF DEBUG] Error adding separator: {}".format(e))
            continue
        
        if item.get("type") == "button":
            try:
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
                print("[FDMA SHELF DEBUG] Added button: {}".format(item.get("label", "Unknown")))
            except Exception as e:
                print("[FDMA SHELF DEBUG] Error adding button {}: {}".format(item.get("label", "Unknown"), e))
    
    # Activate the new shelf with improved error handling
    try:
        if cmds.control(g_top, query=True, exists=True) and cmds.control(shelf, query=True, exists=True):
            cmds.tabLayout(g_top, edit=True, selectTab=shelf)
            print("[FDMA SHELF DEBUG] FDMA_2530 shelf created and activated successfully")
        else:
            print("[FDMA SHELF DEBUG] FDMA_2530 shelf created successfully (activation skipped - UI timing issue)")
    except Exception as e:
        print("[FDMA SHELF DEBUG] Shelf activation error: {}".format(e))
        
        # Fallback: try to refresh and select again
        try:
            cmds.refresh()
            shelf_tabs = cmds.tabLayout(g_top, query=True, childArray=True)
            if shelf_tabs and _SHELF_NAME in shelf_tabs:
                idx = shelf_tabs.index(_SHELF_NAME)
                cmds.tabLayout(g_top, edit=True, selectTabIndex=idx+1)
                print("[FDMA SHELF DEBUG] Shelf activated via fallback method")
        except Exception as e2:
            print("[FDMA SHELF DEBUG] Fallback activation also failed: {}".format(e2))
    
    # Show success message for manual installations
    if not startup:
        cmds.inViewMessage(
            amg="FDMA 2530 shelf rebuilt",
            pos="botLeft",
            fade=True
        )
    
    print("[FDMA SHELF DEBUG] _create_shelf() completed successfully")
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
    ----------
    startup : bool
        If True, shelf is built at Maya startup (suppress messages).
    """
    # Check for and remove uninstall marker first
    marker = os.path.expanduser('~/.fdma2530_uninstalled')
    if os.path.exists(marker):
        os.remove(marker)
        print("[FDMA SHELF DEBUG] Removed uninstall marker")
    
    cfg = _read_json(_CONFIG_PATH)
    if not cfg:
        cmds.warning("FDMA shelf config not found at {}".format(_CONFIG_PATH))
        return
    
    cfg = _expand_version_tokens(cfg)
    
    # Use consistent deferred execution for both startup and manual installation
    if startup:
        print("[FDMA SHELF DEBUG] Using executeDeferred for startup")
        mu.executeDeferred(lambda: _create_shelf(cfg, startup=startup))
    else:
        print("[FDMA SHELF DEBUG] Creating shelf immediately for manual installation")
        success = _create_shelf(cfg, startup=startup)
        
        # Print shelf tabs after creation for debugging
        try:
            g_top = mel.eval("global string $gShelfTopLevel; $tmp=$gShelfTopLevel;")
            shelf_tabs = cmds.tabLayout(g_top, query=True, childArray=True)
            print("[FDMA SHELF DEBUG] Shelf tabs after creation: {}".format(shelf_tabs))
        except Exception as e:
            print("[FDMA SHELF DEBUG] Error listing shelf tabs: {}".format(e))
        
        return success
