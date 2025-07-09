"""
FDMA 2530 Shelf Package
===============================

Root package for the FDMA 2530 student shelf system.
Provides a single entry point to build or rebuild the shelf
and automatically creates the shelf at Maya startup.

Created by: Alexander T. Santiago
Version: Dynamic (Read from releases.json)
License: MIT
Repository: https://github.com/Atsantiago/NMSU_Scripts
"""

# Always get version from manifest via version_utils
try:
    from .utils.version_utils import get_fdma2530_version
    __version__ = get_fdma2530_version()
except (ImportError, Exception):
    __version__ = "unknown"

__author__ = "Alexander T. Santiago"
__all__ = ["build_shelf"]

import os

# Marker file to prevent shelf recreation after uninstall
_UNINSTALL_MARKER = os.path.expanduser('~/.fdma2530_uninstalled')

def build_shelf(startup: bool = False) -> None:
    """
    Build or rebuild the FDMA 2530 shelf from the local JSON config.

    This function serves as the main entry point for creating or rebuilding
    the Maya shelf interface for FDMA 2530 tools. It handles both startup
    initialization and manual rebuild scenarios.

    Parameters
    ----------
    startup : bool, optional
        If True, the shelf is being built on Maya startup; suppresses
        interactive messages and error dialogs to avoid disrupting the
        Maya startup process. Defaults to False.
        
    Notes
    -----
    The shelf builder will:
    - Read configuration from the local shelf_config.json file
    - Create shelf buttons for each configured tool
    - Set up proper icons, labels, and command callbacks
    - Handle Maya-specific shelf creation and management
    
    Examples
    --------
    Manual shelf rebuild:
    >>> import fdma_shelf
    >>> fdma_shelf.build_shelf()
    
    Startup shelf creation (suppresses messages):
    >>> fdma_shelf.build_shelf(startup=True)
    """
    # Prevent shelf recreation if uninstall marker exists
    if os.path.exists(_UNINSTALL_MARKER):
        return
    from .shelf.builder import build_shelf as _real_builder
    _real_builder(startup=startup)

# Automatically build the shelf at Maya startup
try:
    import maya.utils as _mu
    # Only build shelf if uninstall marker does not exist
    if not os.path.exists(_UNINSTALL_MARKER):
        def _startup_initialization():
            """Build shelf and check for updates at startup."""
            build_shelf(startup=True)
            # Delay update check to ensure shelf buttons exist
            try:
                from .utils.updater import startup_check
                startup_check()
            except Exception:
                pass  # Silently ignore update check failures at startup
        _mu.executeDeferred(_startup_initialization)
except ImportError:
    # Not running inside Maya; do nothing
    # This allows the package to be imported in other contexts
    # without Maya dependencies
    pass
