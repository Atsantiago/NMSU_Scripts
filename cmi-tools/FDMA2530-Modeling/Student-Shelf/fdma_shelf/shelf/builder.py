# builder.py
"""
FDMA 2530 Shelf Builder Module

Defines the core function to construct the Maya shelf for FDMA 2530 tools.
"""

from maya import cmds
import maya.utils as mu
import json
import os

# Path to your shelf configuration JSON
_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    "config",
    "fdma_shelf_config.json"
)


def _read_json(path):
    """
    Read and return JSON data from the given file path.
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        cmds.warning(f"Failed to read shelf config at {path}: {e}")
        return None


def _expand_version_tokens(cfg):
    """
    Replace version tokens in button labels or icons if needed.
    """
    version = cfg.get("version", "")
    for btn in cfg.get("buttons", []):
        if "{version}" in btn.get("annotation", ""):
            btn["annotation"] = btn["annotation"].replace("{version}", version)
    return cfg


def _create_shelf(cfg, startup=False):
    """
    Create Maya shelf and buttons based on the provided configuration.
    """
    shelf_name = cfg.get("shelfName", "FDMA_2530")
    # Delete existing shelf if it exists
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name, layout=True)

    # Create new shelf
    cmds.shelfLayout(shelf_name, parent="ShelfLayout")

    for btn in cfg.get("buttons", []):
        cmds.shelfButton(
            label=btn.get("label", ""),
            annotation=btn.get("annotation", ""),
            command=btn.get("command", ""),
            image=btn.get("icon", ""),
            style="iconAndTextVertical"
        )

    if startup:
        cmds.inViewMessage(
            amg=f"<hl>FDMA 2530 shelf built (v{cfg.get('version','unknown')})</hl>",
            pos="topCenter",
            fade=True
        )


def build_shelf(startup=False):
    """
    Public entry point. Reads config and defers shelf creation.
    """
    cfg = _read_json(_CONFIG_PATH)
    if not cfg:
        return

    cfg = _expand_version_tokens(cfg)
    # Defer actual UI creation until Maya is ready
    mu.executeDeferred(lambda: _create_shelf(cfg, startup=startup))
