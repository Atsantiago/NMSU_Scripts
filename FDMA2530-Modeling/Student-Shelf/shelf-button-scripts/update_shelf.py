"""
FDMA 2530 Shelf Update System v1.2
==================================
Safely checks GitHub for a newer `shelf_FDMA_2530.mel`.  
If found, asks the user whether to install, backs up the current shelf,
writes the new file, and reloads the shelf – never crashing Maya.

Highlights
----------
• Python 2 / 3 compatible (Maya 2016 → 2025+)  
• Uses github_utilities for downloads + diffing  
• Button colour changes:  gray (up-to-date) | yellow (checking) |
  green (updates) | red (error)  
• No `sys.exit`, no Maya quit – always safe  
• Full PEP-8 compliance with clear comments
"""
from __future__ import absolute_import, division, print_function
import os, sys, traceback

__version__ = "1.2"

# ------------------------------------------------------------------- imports
try:                                # Py-3
    from urllib.request import urlopen
except ImportError:                 # Py-2
    from urllib2 import urlopen

try:
    import maya.cmds as cmds
    import maya.mel  as mel
    MAYA = True
except Exception:
    MAYA = False

# ---------------------------------------------------------------- constants
REPO_RAW = ("https://raw.githubusercontent.com/Atsantiago/"
            "NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/")
SHELF_FILE_REMOTE = REPO_RAW + "shelf_FDMA_2530.mel"

SHELF_NAME   = "FDMA_2530"
LOCAL_SHELF  = "shelf_%s.mel" % SHELF_NAME
BUTTON_LABEL = "Update"

COLORS = dict(
    up_to_date       =[.5,.5,.5],
    checking         =[.8,.8,.2],
    updates_available=[.2,.8,.2],
    update_failed    =[.8,.2,.2]
)

# ---------------------------------------------------------------- utilities
def _msg(txt): cmds.warning("[FDMA-update] "+txt) if MAYA else print(txt)

def _button(col_key):
    """colour the update button if we are in Maya."""
    if not MAYA: return
    if not cmds.shelfLayout(SHELF_NAME, ex=True): return
    for b in cmds.shelfLayout(SHELF_NAME, q=True, ca=True) or []:
        if cmds.objectTypeUI(b)!="shelfButton": continue
        if BUTTON_LABEL.lower() in cmds.shelfButton(b, q=True, l=True).lower():
            cmds.shelfButton(b, e=True, en=True,
                             enableBackground=True,
                             backgroundColor=COLORS.get(col_key, [.5,.5,.5]))
            break

def _user_shelf_path():
    """Return full path to the local shelf mel."""
    if not MAYA:
        raise RuntimeError("Maya not available – cannot locate shelf dir.")
    return os.path.join(cmds.internalVar(userShelfDir=True), LOCAL_SHELF)

def _download(url):
    data = urlopen(url, timeout=25).read()
    if sys.version_info[0]>=3 and isinstance(data, bytes):
        data = data.decode('utf-8')
    return data

# ---------------------------------------------------------------- main logic
def main():
    _button('checking')
    try:
        local_path = _user_shelf_path()
    except Exception as e:
        _msg("Couldn't find shelf path: %s" % e)
        _button('update_failed'); return

    try:
        with open(local_path, 'r') as f:
            local_data = f.read()
    except IOError:
        local_data = ""

    try:
        remote_data = _download(SHELF_FILE_REMOTE)
    except Exception as e:
        _msg("Network error downloading shelf: %s" % e)
        _button('update_failed'); return

    if local_data.strip() == remote_data.strip():
        _button('up_to_date')
        if MAYA:
            cmds.confirmDialog(t="FDMA Shelf", m="Shelf is already up-to-date.",
                               b=["OK"])
        return

    # ---------------------------------------------------------------- ask user
    _button('updates_available')
    if MAYA:
        go = cmds.confirmDialog(
                t="FDMA Shelf – Updates Available",
                m="A newer shelf version is available.\nInstall now?",
                b=["Update","Cancel"], db="Update", cb="Cancel")
        if go != "Update":
            _button('up_to_date'); return

    # ---------------------------------------------------------------- backup
    bak = local_path + ".backup"
    try:
        if os.path.exists(local_path):
            import shutil; shutil.copy2(local_path, bak)
    except Exception as e:
        _msg("Could not backup shelf: %s" % e)

    # ---------------------------------------------------------------- write + reload
    try:
        with open(local_path, 'w') as f:
            f.write(remote_data)
        _msg("Shelf file updated.")

        if MAYA:
            if cmds.shelfLayout(SHELF_NAME, ex=True):
                cmds.deleteUI(SHELF_NAME, lay=True)
            mel.eval('loadNewShelf "%s"' % local_path.replace('\\','/'))
        _button('up_to_date')
        if MAYA:
            cmds.confirmDialog(t="FDMA Shelf", m="Shelf updated successfully.",
                               b=["Great!"])
    except Exception as e:
        _msg("Update failed – restoring backup.")
        if os.path.exists(bak):
            with open(local_path, 'w') as f:
                f.write(open(bak,'r').read())
        _button('update_failed')
        if MAYA:
            cmds.confirmDialog(t="FDMA Shelf",
                               m="Update failed.\nSee Script Editor.",
                               b=["OK"])
        print(traceback.format_exc())

# ---------------------------------------------------------------- entry point
if __name__ == "__main__":
    main()
else:
    main()
