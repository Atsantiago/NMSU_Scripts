"""
FDMA 2530 Shelf Package v2.0.1
==============================

Root package for the FDMA 2530 student shelf system.
Provides a single entry point to build or rebuild the shelf
and automatically creates the shelf at Maya startup.

Created by: Alexander T. Santiago
"""

__version__ = "2.0.1"
__author__ = "Alexander T. Santiago"
__all__ = ["build_shelf"]

def build_shelf(startup: bool = False) -> None:
    """
    Build or rebuild the FDMA 2530 shelf from the local JSON config.

    Parameters
    ----------
    startup : bool, optional
        If True, the shelf is being built on Maya startup; suppresses
        interactive messages.
    """
    from .shelf.builder import build_shelf as _real_builder
    _real_builder(startup=startup)

# Automatically build the shelf at Maya startup
try:
    import maya.utils as _mu
    _mu.executeDeferred(lambda: build_shelf(startup=True))
except ImportError:
    # Not running inside Maya; do nothing
    pass
