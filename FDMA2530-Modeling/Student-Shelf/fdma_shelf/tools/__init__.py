"""
FDMA 2530 Student Tools Package v2.0.1
======================================

Collection of educational tools for FDMA 2530 modeling students.
Each tool module provides specific functionality accessible through
the shelf interface.

Version
-------
2.0.1
"""

from __future__ import absolute_import

# ----------------------------------------------------------------------
# Package metadata
# ----------------------------------------------------------------------

__version__ = "2.0.1"         # Update this when making a new package release
__author__ = "Alexander T. Santiago"

# ----------------------------------------------------------------------
# Import tool modules here
# To add a new tool:
#  1. Place its .py file in this folder (fdma_shelf/tools).
#  2. Add an import block below.
#  3. Add its name to __all__ if you want it available via wildcard import.
# To remove a tool:
#  1. Remove its .py file from this folder.
#  2. Remove or comment out its import block below.
#  3. Remove its name from __all__.
# ----------------------------------------------------------------------

__all__ = []  # Tools exported when using `from fdma_shelf.tools import *`

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
# ----------------------------------------------------------------------
# Helper functions for tool discovery (optional)
# ----------------------------------------------------------------------

def get_available_tools():
    """
    Return a list of tool module names currently available.
    Use this to dynamically build menus or validate tool presence.
    """
    return list(__all__)


def get_tool_info():
    """
    Return detailed info for each tool, helpful for debugging
    or building a Tools menu with annotations.
    Each entry contains:
      - name: human-friendly name
      - version: tool version string if defined, else 'unknown'
      - description: docstring first line if present, else empty
    """
    info = {}
    for tool_name in __all__:
        try:
            mod = globals()[tool_name]
            version = getattr(mod, "__version__", "unknown")
            doc = (mod.__doc__ or "").strip().splitlines()[0]
            info[tool_name] = {
                "version": version,
                "description": doc
            }
        except Exception:
            info[tool_name] = {
                "version": "error",
                "description": ""
            }
    return info


# ----------------------------------------------------------------------
# If this file is run directly, print package and tool info
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("FDMA 2530 Tools Package v{}".format(__version__))
    tools = get_available_tools()
    if tools:
        print("Available tools:", ", ".join(tools))
        for name, data in get_tool_info().items():
            print(" - {0}: v{1} — {2}".format(name, data["version"], data["description"]))
    else:
        print("No tools are currently available.")
