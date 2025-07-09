"""
Prof-Tools Drag-and-Drop Installer
Follows a proven installer pattern: no downloads, runs local code shipped alongside this file.

Place this file alongside your `prof/` package folder. Drag-and-drop onto Maya to Install, Uninstall, or Run Only.
"""

from __future__ import absolute_import, division, print_function
import sys
import os
import logging

# Try Maya imports
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# Configure logging
logging.basicConfig()
logger = logging.getLogger("prof_tools_installer")
logger.setLevel(logging.INFO)

def _remove_loaded_prof_modules():
    """
    Unload any previously loaded prof modules to force fresh import.
    """
    to_remove = [name for name in sys.modules if name.startswith("prof")]
    for name in to_remove:
        sys.modules.pop(name, None)
    logger.debug("Unloaded existing prof modules: %s", to_remove)

def onMayaDroppedPythonFile(*args):
    """
    Entry point for Maya drag-and-drop.
    Prepends local paths and launches installer UI.
    """
    try:
        logger.info("Launching Prof-Tools installer interface…")
        
        # Determine installer directory and prof package path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prof_dir = os.path.join(script_dir, "prof")
        
        if not os.path.isdir(prof_dir):
            raise RuntimeError("Cannot find 'prof' folder next to this installer")
        
        # Unload any cached prof modules
        _remove_loaded_prof_modules()
        
        # Prepend installer paths so Python uses local code
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        if prof_dir not in sys.path:
            sys.path.insert(0, prof_dir)
        logger.debug("Prepended to sys.path: %s, %s", script_dir, prof_dir)
        
        # Import and launch installer logic
        try:
            from prof.core.setup import launcher_entry_point
            if not callable(launcher_entry_point):
                raise TypeError("launcher_entry_point is not callable. Type: {}".format(type(launcher_entry_point)))
            launcher_entry_point()
        except ImportError as import_err:
            raise RuntimeError("Failed to import launcher: {}".format(import_err))
        except TypeError as type_err:
            raise RuntimeError("Launcher import issue: {}".format(type_err))
        except Exception as launcher_err:
            raise RuntimeError("Launcher execution failed: {}".format(launcher_err))
        
    except Exception as e:
        msg = "Prof-Tools installer failed: {}".format(e)
        logger.error(msg)
        # show Maya dialog if possible
        if MAYA_AVAILABLE:
            try:
                cmds.confirmDialog(title="Prof-Tools Installer Error",
                                   message=msg,
                                   button=["OK"])
            except Exception:
                print(msg)
        else:
            print(msg)

# Allow testing outside Maya
if __name__ == "__main__":
    onMayaDroppedPythonFile()
