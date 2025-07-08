"""
FDMA 2530 Shelf Package
==============================

Root package for FDMA 2530 student shelf system.
Uses Maya module system for clean installation.

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
"""

from fdma_shelf.utils.version_utils import get_fdma2530_version
__version__ = get_fdma2530_version()
__author__ = "Alexander T. Santiago"

import os

_UNINSTALL_MARKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".fdma2530_uninstalled")

def build_shelf(startup=False):
    """Build the FDMA 2530 shelf from configuration"""
    from .shelf.builder import build_shelf as _real_builder
    _real_builder(startup=startup)

# Automatic shelf creation when module loads (only in Maya)
try:
    import maya.utils as _mu
    import maya.cmds as _cmds

    def _startup_shelf():
        # Only create shelf if uninstall marker does not exist
        if not os.path.exists(_UNINSTALL_MARKER):
            _mu.executeDeferred(lambda: build_shelf(startup=True))
    _startup_shelf()
except ImportError:
    pass

__all__ = ["build_shelf"]
