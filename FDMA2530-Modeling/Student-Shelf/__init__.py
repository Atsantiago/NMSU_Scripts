"""
FDMA 2530 Shelf Package v2.0.0
==============================

Root package for FDMA 2530 student shelf system.
Uses Maya module system for clean installation.

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
"""

__version__ = "2.0.0"
__author__ = "Alexander T. Santiago"

def build_shelf(startup=False):
    """Build the FDMA 2530 shelf from configuration"""
    from .shelf.builder import build_shelf as _real_builder
    _real_builder(startup=startup)

# Automatic shelf creation when module loads (only in Maya)
try:
    import maya.utils as _mu
    import maya.cmds as _cmds
    
    # Only auto-create on startup, not on manual imports
    def _startup_shelf():
        # Small delay to ensure Maya UI is ready
        _mu.executeDeferred(lambda: build_shelf(startup=True))
    
    # Schedule startup shelf creation
    _startup_shelf()
    
except ImportError:
    # Not in Maya - skip startup creation
    pass

__all__ = ["build_shelf"]
