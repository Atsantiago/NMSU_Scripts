"""
FDMA 2530 Shelf Package
=======================

Root package for the FDMA 2530 student tool-set.

* Provides a one-click shelf for novice users.
* Uses semantic versioning (MAJOR.MINOR.PATCH).

Author:  Alexander T. Santiago
Version: 2.0.0  – first release under new package layout
"""

# ----------------------------------------------------------------------
# Public package metadata
# ----------------------------------------------------------------------
__version__: str = "2.0.0"           # MAJOR change: new folder structure
__author__:  str = "Alexander T. Santiago"
__all__ = ["build_shelf"]            # what `from fdma_shelf import *` exposes

# ----------------------------------------------------------------------
# Lazy shelf builder import
# ----------------------------------------------------------------------
def build_shelf(startup: bool = False) -> None:
    """
    Build (or rebuild) the FDMA 2530 shelf from the local JSON
    configuration.  Wrapped in a short stub so we do not import heavy
    modules until this function is called.

    Parameters
    ----------
    startup : bool, optional
        If True the function is being called during Maya startup;
        suppresses heavy pop-ups or view-port alerts.
    """
    # Local import keeps initial package import light-weight
    from .shelf.builder import build_shelf as _real_builder
    _real_builder(startup=startup)

# ----------------------------------------------------------------------
# Automatic shelf creation at Maya launch
# ----------------------------------------------------------------------
try:
    # Only runs when inside Maya
    import maya.utils as _mu
    _mu.executeDeferred(lambda: build_shelf(startup=True))
except ImportError:
    # Not running inside Maya – ignore
    pass
