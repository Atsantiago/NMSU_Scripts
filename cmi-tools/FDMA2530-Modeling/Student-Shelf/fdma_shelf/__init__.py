"""
FDMA 2530 Shelf Package v2.0.1+
===============================

Root package for the FDMA 2530 student shelf system.
Provides a single entry point to build or rebuild the shelf
and automatically creates the shelf at Maya startup.

Created by: Alexander T. Santiago
Version: Dynamic (Read from releases.json or persisted install)
License: MIT
Repository: https://github.com/Atsantiago/NMSU_Scripts
"""

# Try to get version from persisted install, then manifest via version_utils, then fallback
from maya.utils import executeDeferred as _defer
import maya.cmds as _cmds

__author__ = "Alexander T. Santiago"

# Expose build_shelf and updater APIs
__all__ = ["build_shelf", "startup_check", "run_update"]

# Version resolution
try:
    # Prefer persisted installed version, else manifest
    from .utils.updater import _local_version as get_installed_version
    __version__ = get_installed_version()
except Exception:
    try:
        from .utils.version_utils import get_fdma2530_version
        __version__ = get_fdma2530_version()
    except Exception:
        __version__ = "2.0.1"

# Build functions
def build_shelf(startup: bool = False) -> None:
    """
    Build or rebuild the FDMA 2530 shelf from the local JSON config.

    Parameters
    ----------
    startup : bool, optional
        If True, suppresses interactive messages and error dialogs.
    """
    from .shelf.builder import build_shelf as _real_builder
    _real_builder(startup=startup)

# Import updater API functions
from .utils.updater import startup_check, run_update  # noqa: F401

# Automatically build the shelf at Maya startup and check for updates
try:
    _defer(lambda: build_shelf(startup=True))
    _defer(startup_check)
except Exception:
    # Not running inside Maya; ignore
    pass
