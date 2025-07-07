"""
FDMA 2530 Student Tools Package

Collection of educational tools for FDMA 2530 modeling students.
Each tool module provides specific functionality accessible through
the shelf interface.
"""

from __future__ import absolute_import

# ----------------------------------------------------------------------------
# Dynamic Package Version Metadata
# ----------------------------------------------------------------------------
from fdma_shelf.utils.updater import _fetch_manifest

def _get_cmi_tools_version():
    """
    Read the current CMI Tools version from releases.json manifest.
    """
    try:
        manifest = _fetch_manifest()
        return manifest.get("current_version", "unknown")
    except Exception:
        return "unknown"

__version__ = _get_cmi_tools_version()
__author__ = "Alexander T. Santiago"

# ----------------------------------------------------------------------------
# Import tool modules here

# To add a new tool:
# 1. Place its .py file in this folder (fdma_shelf/tools).
# 2. Add an import block below.
# 3. Add its name to __all__ if you want it available via wildcard import.
# To remove a tool:
# 1. Remove its .py file from this folder.
# 2. Remove or comment out its import block below.
# 3. Remove its name from __all__.
# ----------------------------------------------------------------------------

__all__ = []  # Start with empty list - tools will be added dynamically

# Import checklist tool
try:
    from . import checklist
    __all__.append("checklist")
except ImportError:
    # checklist.py missing or had import errors
    pass

"""
# Import temporary human body import tool
try:
    from . import TEMP_humanBody_import
    __all__.append("TEMP_humanBody_import")
except ImportError:
    # TEMP_humanBody_import.py missing or had import errors
    pass
"""
 
# ----------------------------------------------------------------------------
# Helper functions for tool discovery (optional)
# ----------------------------------------------------------------------------

def get_available_tools():
    """
    Return a list of tool entry names currently available.
    """
    return list(__all__)

def get_tool_info():
    """
    Return detailed info for each tool, helpful for debugging.
    Each entry contains:
    - name: entry point name
    - version: tool module __version__ or 'unknown'
    - description: module docstring first line or empty
    """
    info = {}
    for entry in __all__:
        fn = globals()[entry]
        mod = __import__(fn.__module__, fromlist=[fn.__name__])
        info[entry] = {
            "version": getattr(mod, "__version__", "unknown"),
            "description": (mod.__doc__ or "").strip().splitlines()[0]
        }
    return info


# ----------------------------------------------------------------------------
# If this file is run directly, print package and tool info
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"FDMA 2530 Tools Package v{__version__}")
    tools = get_available_tools()
    if tools:
        print("Available tools:", ", ".join(tools))
        for name, data in get_tool_info().items():
            print(f" - {name}: v{data['version']} — {data['description']}")
    else:
        print("No tools are currently available.")
