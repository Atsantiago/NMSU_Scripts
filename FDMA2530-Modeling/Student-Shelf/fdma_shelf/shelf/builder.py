"""
Builds or rebuilds the FDMA 2530 shelf from a local JSON config.

Functions
---------
build_shelf(startup=False):
    Remove any existing FDMA_2530 shelf then create a new one
    based on the data stored in shelf_config.json.

The function is safe to call many times.  UI work happens
inside maya.utils.executeDeferred to avoid shelf-button
call-stack crashes.
"""

from __future__ import absolute_import, print_function

import json
import os
import hashlib

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as mu


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

_CONFIG_FILE = "shelf_config.json"
_SHELF_NAME = "FDMA_2530"


def _user_scripts_dir():
    """Return the user script directory path."""
    return cmds.internalVar(userScriptDir=True)


def _local_config_path():
    """Return full path to the local JSON config."""
    return os.path.join(_user_scripts_dir(), _CONFIG_FILE)


def _read_json(path):
    """Read and return JSON object or None on failure."""
    try:
        with open(path, "r") as fh:
            return json.load(fh)
    except Exception:
        return None


def _shelf_exists(name):
    """Check if a shelf layout exists."""
    return cmds.shelfLayout(name, q=True, ex=True)


def _delete_shelf(name):
    """Delete a shelf layout if it exists."""
    if _shelf_exists(name):
        cmds.deleteUI(name, layout=True)


def _hash_text(text):
    """Return MD5 hash of text for change detection."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------
# Main builder
# ------------------------------------------------------------------

def _create_shelf(config, startup=False):
    """Create shelf UI according to config dict."""
    shelf_info = config["shelf_info"]
    cell_w = int(shelf_info.get("cell_width", 35))
    cell_h = int(shelf_info.get("cell_height", 35))

    # Get gShelfTopLevel control
    g_top = mel.eval("global string $gShelfTopLevel; $tmp=$gShelfTopLevel;")
    if not g_top:
        cmds.warning("Shelf parent not found")
        return

    _delete_shelf(_SHELF_NAME)

    shelf = cmds.shelfLayout(
        _SHELF_NAME,
        parent=g_top,
        cellWidth=cell_w,
        cellHeight=cell_h,
    )

    for item in config["buttons"]:
        if not item.get("enabled", True):
            continue

        if item["type"] == "separator":
            cmds.separator(
                parent=shelf,
                style=item.get("style", "shelf"),
                hr=not item.get("horizontal", False),
            )
            continue

        if item["type"] == "button":
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

    # Activate shelf
    if cmds.control(g_top, ex=True) and cmds.control(shelf, ex=True):
        cmds.tabLayout(g_top, e=True, st=shelf)

    if not startup:
        cmds.inViewMessage(
            amg="<span style=\"color:#55FF55\">FDMA 2530 shelf rebuilt</span>",
            pos="botLeft", fade=True
        )


def _build_button_command(item):
    """Return a python string that will be executed when the button is pressed."""
    
    # Check if item has 'command' field (new JSON format)
    if 'command' in item:
        return item['command']
    
    # Fallback to old script_url format for backward compatibility
    if item.get("label") == "Update":
        # Update button points to updater inside main package
        return (
            "import fdma_shelf.utils.updater as _u; "
            "_u.run_update()"
        )

    # Regular tool button - try to use command first, fallback to script_url
    if 'script_url' in item:
        tool_import = item["script_url"]
        return (
            "import sys; "
            "try: from urllib.request import urlopen; "
            "except ImportError: from urllib2 import urlopen; "
            "import types; "
            "code = urlopen('{url}').read(); "
            "if sys.version_info[0] >= 3 and isinstance(code, bytes): code = code.decode('utf-8'); "
            "mod = types.ModuleType('temp_tool'); "
            "exec(code, mod.__dict__); "
            "func = getattr(mod, 'main', None) or getattr(mod, 'run', None); "
            "func() if callable(func) else print('No main/run function found')"
        ).format(url=tool_import)
    
    # Default fallback
    return "print('Button command not configured properly')"

def build_shelf(startup=False):
    """
    Public entry point.  Schedules the actual build with executeDeferred
    so that UI creation happens out of the caller stack.
    """
    cfg_path = _local_config_path()
    cfg = _read_json(cfg_path)
    if not cfg:
        cmds.warning("FDMA shelf config not found at {0}".format(cfg_path))
        return

    mu.executeDeferred(lambda: _create_shelf(cfg, startup=startup))
