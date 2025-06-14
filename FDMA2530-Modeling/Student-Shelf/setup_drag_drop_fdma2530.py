"""
setup_drag_drop_fdma2530.py  •  v1.2.0
=======================================

Drag-and-drop this file into Maya’s viewport to install or
temporarily load the FDMA 2530 Student Shelf.

Options presented to the user
-----------------------------
•  Install Shelf   – copies required files to the user profile
•  Load Once       – loads the shelf for this session only
•  Cancel          – abort

Installed files
---------------
•  <maya>/scripts/utilities/cache_loader.py
•  <maya>/prefs/shelves/shelf_FDMA_2530.mel

Author: Alexander T. Santiago  •  asanti89@nmsu.edu
Repo  : https://github.com/Atsantiago/NMSU_Scripts
"""

from __future__ import absolute_import, division, print_function
import os, sys, tempfile, traceback, shutil

__version__ = "1.2.0"

# ---------------------------------------------------------  Py2 / Py3 urllib
try:                                # Py-3
    from urllib.request import urlopen
except ImportError:                 # Py-2
    from urllib2 import urlopen

# ---------------------------------------------------------  Maya imports
try:
    import maya.cmds as cmds
    import maya.mel  as mel
except Exception:
    raise RuntimeError("Must be executed inside Maya.")

# ---------------------------------------------------------  GitHub RAW URLs
BASE_RAW = ("https://raw.githubusercontent.com/Atsantiago/"
            "NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/")
URL_SHELF  = BASE_RAW + "shelf_FDMA_2530.mel"
URL_LOADER = BASE_RAW + "utilities/cache_loader.py"

# ---------------------------------------------------------  Local paths
SCRIPTS_DIR = cmds.internalVar(userScriptDir=True)
UTIL_DIR    = os.path.join(SCRIPTS_DIR, "utilities")
LOADER_DST  = os.path.join(UTIL_DIR, "cache_loader.py")

SHELF_DIR   = cmds.internalVar(userShelfDir=True)
SHELF_DST   = os.path.join(SHELF_DIR, "shelf_FDMA_2530.mel")

TEMP_DIR    = tempfile.gettempdir()

# ---------------------------------------------------------  Small helpers
def _download(url):
    """Return ASCII/UTF-8 text from *url* (raise on error)."""
    data = urlopen(url, timeout=25).read()
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    return data

def _safe_write(path, data):
    """Write *data* (str) to *path*, creating folders as needed."""
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with open(path, 'w') as fh:
        fh.write(data)

def _info(msg):
    cmds.warning("[FDMA 2530] " + msg)

def _load_shelf_from(path):
    """Instruct Maya to load a shelf file from *path*."""
    try:
        mel.eval('loadNewShelf "%s"' % path.replace("\\", "/"))
        _info("Shelf loaded from: " + path)
    except Exception as e:
        _info("Failed to load shelf: %s" % e)
        cmds.confirmDialog(t="FDMA 2530 Shelf",
                           m="Could not load shelf.\nSee Script-Editor.",
                           b=["OK"])
        print(traceback.format_exc())

# ---------------------------------------------------------  Main entry
def onMayaDroppedPythonFile(*_):
    """Entry-point Maya calls when the script is dropped into the viewport."""
    # --------------------------------------- ask user what to do
    choice = cmds.confirmDialog(
        t="FDMA 2530 Shelf Installer",
        m=("Choose an action for the FDMA 2530 shelf:\n\n"
           "•  Install Shelf  – installs files to your user profile\n"
           "•  Load Once      – loads shelf for this session only\n"
           "•  Cancel         – do nothing"),
        b=["Install Shelf", "Load Once", "Cancel"],
        db="Install Shelf", cb="Cancel", ds="Cancel")

    if choice == "Cancel":
        _info("Operation cancelled by user.")
        return

    try:
        # ----------------------------------- always ensure loader exists
        loader_data = _download(URL_LOADER)
        if choice == "Install Shelf":
            _safe_write(LOADER_DST, loader_data)
            _info("cache_loader.py installed to " + LOADER_DST)
        else:
            # load-once path: write to temp
            tmp_loader = os.path.join(TEMP_DIR, "cache_loader.py")
            _safe_write(tmp_loader, loader_data)
            sys.path.insert(0, TEMP_DIR)          # make importable

        # ----------------------------------- download shelf file
        shelf_data = _download(URL_SHELF)
        if choice == "Install Shelf":
            _safe_write(SHELF_DST, shelf_data)
            _load_shelf_from(SHELF_DST)
            cmds.confirmDialog(t="FDMA 2530 Shelf",
                               m="Shelf installed successfully!",
                               b=["Great!"])
        else:  # Load Once
            temp_shelf = os.path.join(TEMP_DIR, "shelf_FDMA_2530.mel")
            _safe_write(temp_shelf, shelf_data)
            _load_shelf_from(temp_shelf)

    except Exception as e:
        _info("Installer error: %s" % e)
        cmds.confirmDialog(t="FDMA 2530 Shelf",
                           m="Installer failed.\nSee Script-Editor.",
                           b=["OK"])
        print(traceback.format_exc())

# ---------------------------------------------------------  CLI support
if __name__ == "__main__":
    onMayaDroppedPythonFile()
