"""
FDMA 2530 Shelf Update System v1.2
==================================
Safely checks GitHub for a newer `shelf_FDMA_2530.mel`.  
If found, asks the user whether to install, backs up the current shelf,
writes the new file, and reloads the shelf never crashing Maya.

"""
from __future__ import print_function
import sys
import os
import traceback

# Python 2/3 compatibility
try:
    from urllib.request import urlopen  # Python 3
except ImportError:
    from urllib2 import urlopen  # Python 2

try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# Configuration
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
SHELF_MEL_PATH = "FDMA2530-Modeling/Student-Shelf/shelf_FDMA_2530.mel"
SHELF_NAME = "FDMA_2530"

# ASCII-safe characters only
BUTTON_COLORS = {
    'up_to_date': [0.5, 0.5, 0.5],
    'updates_available': [0.2, 0.8, 0.2],
    'update_failed': [0.8, 0.2, 0.2],
    'checking': [0.8, 0.8, 0.2]
}

def _safe_write(path, data):
    """Write files with UTF-8 encoding"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

def update_button_visual_status(status):
    if not MAYA_AVAILABLE: return
    buttons = cmds.shelfLayout(SHELF_NAME, q=True, ca=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, q=True, l=True) == "Update":
            cmds.shelfButton(btn, e=True, backgroundColor=BUTTON_COLORS[status])

def check_for_updates():
    try:
        current_path = os.path.join(cmds.internalVar(userShelfDir=True), "shelf_FDMA_2530.mel")
        with open(current_path, 'r', encoding='utf-8') as f:
            local_content = f.read()
        
        remote_content = urlopen(REPO_RAW + SHELF_MEL_PATH).read().decode('utf-8')
        
        # Hash comparison for reliability
        import hashlib
        local_hash = hashlib.md5(local_content.encode('utf-8')).hexdigest()
        remote_hash = hashlib.md5(remote_content.encode('utf-8')).hexdigest()
        
        return local_hash != remote_hash
    except Exception as e:
        print("Update check error:", traceback.format_exc())
        return False

def perform_update():
    try:
        shelf_path = os.path.join(cmds.internalVar(userShelfDir=True), "shelf_FDMA_2530.mel")
        backup_path = shelf_path + ".bak"
        
        # Create backup
        if os.path.exists(shelf_path):
            import shutil
            shutil.copy2(shelf_path, backup_path)
        
        # Download new shelf
        new_content = urlopen(REPO_RAW + SHELF_MEL_PATH).read().decode('utf-8')
        _safe_write(shelf_path, new_content)
        
        # Reload shelf
        if cmds.shelfLayout(SHELF_NAME, ex=True):
            cmds.deleteUI(SHELF_NAME)
        mel.eval('loadNewShelf "{}"'.format(shelf_path.replace('\\', '/')))
        
        return True
    except Exception as e:
        print("Update failed:", traceback.format_exc())
        # Restore backup
        if os.path.exists(backup_path):
            shutil.move(backup_path, shelf_path)
        return False

def main():
    update_button_visual_status('checking')
    try:
        if check_for_updates():
            update_button_visual_status('updates_available')
            choice = cmds.confirmDialog(
                title='Updates Available',
                message='New shelf version found! Update now?',
                button=['Yes', 'No'],
                defaultButton='Yes'
            )
            if choice == 'Yes':
                if perform_update():
                    update_button_visual_status('up_to_date')
                    cmds.confirmDialog(title='Success', message='Shelf updated!', button=['OK'])
                else:
                    update_button_visual_status('update_failed')
        else:
            update_button_visual_status('up_to_date')
    except Exception as e:
        update_button_visual_status('update_failed')
        print("Critical error:", traceback.format_exc())

if __name__ == "__main__":
    main()
else:
    main()
