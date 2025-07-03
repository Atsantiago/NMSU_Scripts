"""
Builds or rebuilds the FDMA 2530 shelf from a local JSON config.

This module provides a clean, GT-Tools–inspired approach for
loading the shelf configuration regardless of Maya version.
"""

from __future__ import absolute_import, print_function

import json
import os
import hashlib

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as mu


# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------

_CONFIG_FILE = "shelf_config.json"
_SHELF_NAME = "FDMA_2530"

# Directory containing this builder.py
_BUILDER_DIR = os.path.dirname(os.path.abspath(__file__))
# scripts/ directory where shelf_config.json resides
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(_BUILDER_DIR, os.pardir, os.pardir)
)
# Full path to JSON config
_CONFIG_PATH = os.path.join(_SCRIPTS_DIR, _CONFIG_FILE)


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


# ----------------------------------------------------------------------
# Main builder
# ----------------------------------------------------------------------

def _create_shelf(config, startup=False):
    """Create shelf UI according to config dict."""
    shelf_info = config.get("shelf_info", {})
    cell_w = int(shelf_info.get("cell_width", 35))
    cell_h = int(shelf_info.get("cell_height", 35))

    # Get Maya's shelf parent
    g_top = mel.eval("global string $gShelfTopLevel; $tmp=$gShelfTopLevel;")
    if not g_top:
        cmds.warning("Shelf parent not found")
        return

    # Remove existing shelf
    _delete_shelf(_SHELF_NAME)

    # Create new shelf layout
    shelf = cmds.shelfLayout(
        _SHELF_NAME,
        parent=g_top,
        cellWidth=cell_w,
        cellHeight=cell_h,
    )

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
        cmds.tabLayout(g_top, edit=True, tabLabelIndex=(shelf, shelf))

    if not startup:
        cmds.inViewMessage(
            amg="FDMA 2530 shelf rebuilt",
            pos="botLeft",
            fade=True
        )


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

    Parameters
    ----------
    startup : bool
        If True, shelf is built at Maya startup (suppress messages).
    """
    cfg = _read_json(_CONFIG_PATH)
    if not cfg:
        cmds.warning("FDMA shelf config not found at {}".format(_CONFIG_PATH))
        return

    # Defer UI creation to avoid call-stack issues
    mu.executeDeferred(lambda: _create_shelf(cfg, startup=startup))
