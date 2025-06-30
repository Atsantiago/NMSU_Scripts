"""
FDMA 2530 Shelf Update System v1.2.1 - STREAMLINED VERSION
=========================================================

Optimized shelf update system for maximum speed and reliability.
Checks GitHub for shelf updates with visual status indicators.

Features:
- Fast update detection with minimal overhead
- Visual button status indicators (Gray/Green/Red/Yellow)
- Safe backup and rollback mechanisms
- Python 2/3 compatibility across Maya 2016-2025+
- Cross-platform support (Windows, macOS, Linux)
- Essential error handling without complexity

Created by: Alexander T. Santiago - asanti89@nmsu.edu
"""

import sys
import os
import hashlib

# Python 2/3 compatibility - minimal approach
try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, URLError

try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

__version__ = "1.2.1"

# Repository configuration
REPO_RAW = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/"
SHELF_MEL_PATH = "FDMA2530-Modeling/Student-Shelf/shelf_FDMA_2530.mel"
SHELF_NAME = "FDMA_2530"

# Visual status button colors (Maya RGB values)
BUTTON_COLORS = {
    'up_to_date': [0.5, 0.5, 0.5],        # Gray
    'updates_available': [0.2, 0.8, 0.2], # Green
    'update_failed': [0.8, 0.2, 0.2],     # Red
    'checking': [0.8, 0.8, 0.2]           # Yellow
}

# ============================================================================
# CORE UTILITIES
# ============================================================================

def safe_file_write(path, content):
    """Write file with Python 2/3 encoding compatibility"""
    try:
        if sys.version_info[0] >= 3:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            # Python 2 - use codecs for UTF-8
            import codecs
            with codecs.open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        return True
    except Exception as e:
        print("File write error: " + str(e))
        return False

def safe_file_read(path):
    """Read file with Python 2/3 encoding compatibility"""
    try:
        if sys.version_info[0] >= 3:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Python 2 - use codecs for UTF-8
            import codecs
            with codecs.open(path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print("File read error: " + str(e))
        return None

def safe_download(url):
    """Download content with basic error handling"""
    try:
        response = urlopen(url, timeout=15)
        content = response.read()
        
        # Handle Python 3 encoding
        if sys.version_info[0] >= 3 and isinstance(content, bytes):
            content = content.decode('utf-8')
        
        return content
    except Exception as e:
        print("Download error: " + str(e))
        return None

# ============================================================================
# VISUAL STATUS MANAGEMENT
# ============================================================================

def update_button_visual_status(status):
    """Update the visual status of the update button"""
    if not MAYA_AVAILABLE:
        return
    
    try:
        # Check if shelf exists
        if not cmds.shelfLayout(SHELF_NAME, exists=True):
            return
        
        # Find and update the update button
        buttons = cmds.shelfLayout(SHELF_NAME, query=True, childArray=True) or []
        
        for btn in buttons:
            try:
                if cmds.objectTypeUI(btn) == 'shelfButton':
                    label = cmds.shelfButton(btn, query=True, label=True)
                    if label == "Update":
                        color = BUTTON_COLORS.get(status, BUTTON_COLORS['up_to_date'])
                        cmds.shelfButton(btn, edit=True, backgroundColor=color)
                        break
            except Exception:
                continue
                
    except Exception as e:
        print("Button status update failed: " + str(e))

# ============================================================================
# UPDATE DETECTION
# ============================================================================

def check_for_updates():
    """Check if shelf updates are available using hash comparison"""
    try:
        # Get current shelf path
        shelf_dir = cmds.internalVar(userShelfDir=True)
        current_path = os.path.join(shelf_dir, "shelf_FDMA_2530.mel")
        
        # Read current shelf content
        current_content = safe_file_read(current_path)
        if current_content is None:
            return False
        
        # Download latest shelf content
        latest_content = safe_download(REPO_RAW + SHELF_MEL_PATH)
        if latest_content is None:
            return False
        
        # Compare content using hash for reliability
        current_hash = hashlib.md5(current_content.encode('utf-8')).hexdigest()
        latest_hash = hashlib.md5(latest_content.encode('utf-8')).hexdigest()
        
        return current_hash != latest_hash
        
    except Exception as e:
        print("Update check error: " + str(e))
        return False

# ============================================================================
# UPDATE EXECUTION
# ============================================================================

def create_backup(shelf_path):
    """Create backup of current shelf file"""
    try:
        backup_path = shelf_path + ".backup"
        
        # Copy current shelf to backup
        current_content = safe_file_read(shelf_path)
        if current_content and safe_file_write(backup_path, current_content):
            print("Backup created: " + backup_path)
            return backup_path
        return None
    except Exception as e:
        print("Backup creation failed: " + str(e))
        return None

def restore_backup(shelf_path, backup_path):
    """Restore shelf from backup"""
    try:
        if backup_path and os.path.exists(backup_path):
            backup_content = safe_file_read(backup_path)
            if backup_content and safe_file_write(shelf_path, backup_content):
                print("Backup restored successfully")
                return True
        return False
    except Exception as e:
        print("Backup restore failed: " + str(e))
        return False

def perform_update():
    """Perform shelf update with backup and rollback"""
    try:
        # Get shelf path
        shelf_dir = cmds.internalVar(userShelfDir=True)
        shelf_path = os.path.join(shelf_dir, "shelf_FDMA_2530.mel")
        
        # Create backup
        backup_path = create_backup(shelf_path)
        if not backup_path:
            print("Cannot proceed without backup")
            return False
        
        # Download new shelf content
        new_content = safe_download(REPO_RAW + SHELF_MEL_PATH)
        if not new_content:
            print("Failed to download new shelf")
            return False
        
        # Validate new content
        if 'shelf_FDMA_2530' not in new_content:
            print("Downloaded content appears invalid")
            return False
        
        # Write new shelf file
        if not safe_file_write(shelf_path, new_content):
            print("Failed to write new shelf")
            restore_backup(shelf_path, backup_path)
            return False
        
        # Reload shelf in Maya
        try:
            # Remove existing shelf
            if cmds.shelfLayout(SHELF_NAME, exists=True):
                cmds.deleteUI(SHELF_NAME)
            
            # Load new shelf
            shelf_path_mel = shelf_path.replace('\\', '/')  # MEL needs forward slashes
            mel.eval('loadNewShelf "{}"'.format(shelf_path_mel))
            
            print("Shelf updated and reloaded successfully")
            return True
            
        except Exception as e:
            print("Shelf reload failed: " + str(e))
            restore_backup(shelf_path, backup_path)
            return False
            
    except Exception as e:
        print("Update failed: " + str(e))
        return False

# ============================================================================
# USER INTERFACE
# ============================================================================

def show_update_dialog():
    """Show update confirmation dialog"""
    if not MAYA_AVAILABLE:
        return False
    
    try:
        choice = cmds.confirmDialog(
            title='FDMA 2530 Shelf Updates Available',
            message=(
                'A new version of the FDMA 2530 shelf is available!\n\n'
                'The update includes:\n'
                '• Bug fixes and improvements\n'
                '• Enhanced compatibility\n'
                '• Performance optimizations\n\n'
                'Your current shelf will be backed up automatically.\n'
                'Update now?'
            ),
            button=['Yes, Update Now', 'Not Now'],
            defaultButton='Yes, Update Now',
            cancelButton='Not Now',
            icon='question'
        )
        
        return choice == 'Yes, Update Now'
        
    except Exception as e:
        print("Dialog error: " + str(e))
        return False

def show_success_dialog():
    """Show update success dialog"""
    if not MAYA_AVAILABLE:
        return
    
    try:
        cmds.confirmDialog(
            title='Update Successful',
            message=(
                'FDMA 2530 shelf updated successfully!\n\n'
                'New features and improvements are now available.\n'
                'Your previous shelf was automatically backed up.'
            ),
            button=['Great!'],
            icon='information'
        )
    except Exception:
        pass

def show_error_dialog():
    """Show update error dialog"""
    if not MAYA_AVAILABLE:
        return
    
    try:
        cmds.confirmDialog(
            title='Update Failed',
            message=(
                'The shelf update encountered an error.\n\n'
                'Troubleshooting:\n'
                '• Check internet connection\n'
                '• Verify GitHub access\n'
                '• Check Maya console for details\n'
                '• Contact: asanti89@nmsu.edu'
            ),
            button=['OK'],
            icon='critical'
        )
    except Exception:
        pass

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """Main update function with streamlined workflow"""
    try:
        print("FDMA 2530 Shelf Updater v{} starting...".format(__version__))
        
        # Set checking status
        update_button_visual_status('checking')
        
        # Check for updates
        if check_for_updates():
            print("Updates available")
            update_button_visual_status('updates_available')
            
            # Show update dialog
            if show_update_dialog():
                print("User chose to update")
                
                # Perform update
                if perform_update():
                    print("Update completed successfully")
                    update_button_visual_status('up_to_date')
                    show_success_dialog()
                    return True
                else:
                    print("Update failed")
                    update_button_visual_status('update_failed')
                    show_error_dialog()
                    return False
            else:
                print("User declined update")
                return False
        else:
            print("No updates available")
            update_button_visual_status('up_to_date')
            
            if MAYA_AVAILABLE:
                cmds.inViewMessage(
                    amg="FDMA 2530 shelf is up to date!",
                    pos='botLeft',
                    fade=True
                )
            return True
            
    except Exception as e:
        print("Critical error: " + str(e))
        update_button_visual_status('update_failed')
        show_error_dialog()
        return False

# ============================================================================
# EXECUTION ENTRY POINTS
# ============================================================================

# Execute when script is run
if __name__ == "__main__":
    main()
else:
    main()
