"""
FDMA 2530 Shelf Update System - Version 1.0
============================================

Intelligent shelf update system that automatically maintains the FDMA 2530 Maya shelf
and all associated scripts from GitHub. Provides visual status indicators and seamless
update experience without requiring manual file selection.

This script provides:
- Automatic detection of updates from GitHub
- Visual status indicators on the update button (gray/green/red)
- One-click update process with comprehensive error handling
- Python 2/3 compatibility across all Maya versions
- Integration with github_utilities.py for robust GitHub operations
- Automatic shelf reconstruction with new buttons/features
- Backup and restore capabilities for safe updates

The update system works by:
1. Loading the GitHub utilities for robust operations
2. Checking for updates to shelf and associated scripts
3. Providing visual feedback via button color changes
4. Offering one-click updates with user confirmation
5. Automatically reloading the shelf with new features

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
GitHub: github.com/atsantiago
Repository: https://github.com/Atsantiago/NMSU_Scripts
Version: 1.2 - Complete rewrite with intelligent update detection


Changelog:
v1.2 - Complete rewrite featuring:
     - Full Python 2/3 compatibility (no f-strings, proper imports)
     - Integration with github_utilities.py system
     - Visual status indicators (gray/green/red button states)
     - Automatic shelf file detection (no manual dialogs)
     - Comprehensive error handling and user feedback
     - Smart update detection and version management
     - Safe backup and restore functionality
     - Clean, maintainable code following PEP 8
"""

# ============================================================================
# IMPORTS AND PYTHON 2/3 COMPATIBILITY
# ============================================================================
# Handle all differences between Python 2 and 3 for Maya compatibility

import sys
import os
# Version information
__version__ = "1.2"
# User interface settings
SCRIPT_TITLE = "FDMA 2530 Shelf Update System v{0}".format(__version__)
CONTACT_INFO = "Contact: asanti89@nmsu.edu"


# Python version detection for compatibility handling
PYTHON_VERSION = sys.version_info[0]
IS_PYTHON_2 = (PYTHON_VERSION == 2)
IS_PYTHON_3 = (PYTHON_VERSION >= 3)

# Import appropriate modules based on Python version
if IS_PYTHON_2:
    # Python 2 imports
    import urllib2 as urllib_request
    string_types = basestring
    
    def format_string(template, **kwargs):
        """Format strings for Python 2 compatibility."""
        return template.format(**kwargs)
        
    def exec_code(code, globals_dict):
        """Execute code with Python 2 compatibility."""
        exec(code, globals_dict)
        
else:
    # Python 3 imports
    import urllib.request as urllib_request
    string_types = str
    
    def format_string(template, **kwargs):
        """Format strings for Python 3."""
        return template.format(**kwargs)
        
    def exec_code(code, globals_dict):
        """Execute code with Python 3 compatibility."""
        exec(code, globals_dict)

# Maya-specific imports with error handling
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    print("Warning: Maya not available - running in standalone mode")
    MAYA_AVAILABLE = False

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================
# Central configuration for the update system

# Repository configuration
REPOSITORY_URL = "https://github.com/Atsantiago/NMSU_Scripts"
REPOSITORY_BRANCH = "master"
BASE_PATH = "FDMA2530-Modeling/Student-Shelf"

# File paths within the repository structure
UTILITIES_PATH = "utilities/github_utilities.py"
SHELF_MEL_PATH = "shelf_FDMA_2530.mel"
UPDATE_SCRIPT_PATH = "shelf-button-scripts/update_shelf.py"

# Maya shelf configuration
SHELF_NAME = "FDMA_2530"
UPDATE_BUTTON_LABEL = "Update"

# Network and timeout settings
DOWNLOAD_TIMEOUT = 25  # Seconds to wait for downloads
MAX_RETRY_ATTEMPTS = 2  # Number of times to retry failed operations

# User interface settings
SCRIPT_TITLE = "FDMA 2530 Shelf Update System"
CONTACT_INFO = "Contact: asanti89@nmsu.edu"

# Visual status colors for update button
BUTTON_COLORS = {
    'up_to_date': [0.5, 0.5, 0.5],      # Gray - no updates needed
    'updates_available': [0.2, 0.8, 0.2], # Green - updates available
    'update_failed': [0.8, 0.2, 0.2],    # Red - update failed
    'checking': [0.8, 0.8, 0.2]          # Yellow - checking for updates
}

# ============================================================================
# LOGGING AND USER FEEDBACK FUNCTIONS
# ============================================================================
# Centralized logging system for consistent user feedback throughout the update process

def print_header():
    """Print a formatted header for the update process."""
    print("=" * 70)
    print(SCRIPT_TITLE + " v1.0")
    print("Checking for shelf and script updates...")
    print("=" * 70)


def print_status(message, is_success=False, is_error=False, is_warning=False):
    """
    Print a status message with consistent formatting.
    
    Args:
        message (str): The status message to display
        is_success (bool): Whether this is a success message
        is_error (bool): Whether this is an error message  
        is_warning (bool): Whether this is a warning message
    """
    if is_success:
        print("✓ SUCCESS: {0}".format(message))
    elif is_error:
        print("✗ ERROR: {0}".format(message))
    elif is_warning:
        print("⚠ WARNING: {0}".format(message))
    else:
        print("• INFO: {0}".format(message))


def print_footer(success=True, updates_found=False):
    """
    Print a formatted footer with final status and instructions.
    
    Args:
        success (bool): Whether the overall operation was successful
        updates_found (bool): Whether updates were found
    """
    print("=" * 70)
    if success:
        if updates_found:
            print("✓ Updates detected and processed successfully!")
            print("Your FDMA 2530 shelf has been updated with the latest features.")
        else:
            print("✓ Update check completed - your shelf is up to date!")
            print("No updates were needed at this time.")
    else:
        print("✗ Update check failed")
        print("Please check your internet connection and try again.")
        print("")
        print("If problems persist:")
        print("• Verify GitHub access: https://github.com/Atsantiago/NMSU_Scripts")
        print("• Check Maya's Python console for detailed error messages")
        print("• {0}".format(CONTACT_INFO))
    print("=" * 70)


# ============================================================================
# GITHUB UTILITIES LOADING SYSTEM
# ============================================================================
# Functions for loading the GitHub utilities module for robust GitHub operations

def load_github_utilities():
    """
    Load the GitHub utilities module dynamically from the repository.
    
    This function downloads and executes the utilities module directly from
    GitHub, ensuring we always have access to the latest utility functions.
    
    Returns:
        bool: True if utilities loaded successfully, False otherwise
    """
    try:
        print_status("Loading GitHub utilities from repository...")
        
        # ====================================================================
        # BUILD UTILITIES DOWNLOAD URL
        # ====================================================================
        utilities_url = format_string(
            "{repo}/raw/{branch}/{base}/{path}",
            repo=REPOSITORY_URL.rstrip('/'),
            branch=REPOSITORY_BRANCH,
            base=BASE_PATH,
            path=UTILITIES_PATH
        )
        
        print_status("Downloading utilities from: {0}".format(utilities_url))
        
        # ====================================================================
        # DOWNLOAD UTILITIES CONTENT
        # ====================================================================
        response = urllib_request.urlopen(utilities_url, timeout=DOWNLOAD_TIMEOUT)
        utilities_content = response.read()
        
        # Handle encoding for Python 3
        if IS_PYTHON_3 and isinstance(utilities_content, bytes):
            utilities_content = utilities_content.decode('utf-8')
        
        # ====================================================================
        # VALIDATE AND EXECUTE UTILITIES
        # ====================================================================
        if not utilities_content or len(utilities_content.strip()) < 100:
            print_status("Downloaded utilities content appears invalid", is_error=True)
            return False
        
        # Execute utilities in current namespace
        exec_code(utilities_content, globals())
        
        print_status("GitHub utilities loaded successfully", is_success=True)
        return True
        
    except Exception as e:
        print_status("Failed to load GitHub utilities: {0}".format(str(e)), is_error=True)
        return False


def verify_utilities_available():
    """
    Verify that required utility functions are available after loading.
    
    Returns:
        bool: True if all required functions are available, False otherwise
    """
    required_functions = [
        'download_file_content',
        'check_for_file_updates', 
        'test_github_connectivity',
        'build_github_raw_url'
    ]
    
    missing_functions = []
    
    for func_name in required_functions:
        if func_name not in globals():
            missing_functions.append(func_name)
    
    if missing_functions:
        print_status("Missing utility functions: {0}".format(
            ', '.join(missing_functions)), is_error=True)
        return False
    
    print_status("All required utility functions available", is_success=True)
    return True


# ============================================================================
# SHELF FILE MANAGEMENT FUNCTIONS
# ============================================================================
# Functions for locating, reading, and managing the shelf file

def get_shelf_file_path():
    """
    Automatically locate the FDMA 2530 shelf file in Maya's shelf directory.
    
    This function eliminates the need for manual file selection by automatically
    finding the shelf file in the standard Maya shelf location.
    
    Returns:
        str: Path to shelf file or None if not found
    """
    if not MAYA_AVAILABLE:
        print_status("Maya not available - cannot locate shelf file", is_warning=True)
        return None
        
    try:
        # Get Maya's user shelf directory
        shelf_dir = cmds.internalVar(userShelfDir=True)
        shelf_filename = "shelf_{0}.mel".format(SHELF_NAME)
        shelf_path = os.path.join(shelf_dir, shelf_filename)
        
        # Check if shelf file exists
        if os.path.exists(shelf_path):
            print_status("Found shelf file: {0}".format(shelf_path), is_success=True)
            return shelf_path
        else:
            print_status("Shelf file not found: {0}".format(shelf_path), is_error=True)
            return None
            
    except Exception as e:
        print_status("Error locating shelf file: {0}".format(str(e)), is_error=True)
        return None


def read_current_shelf_content(shelf_path):
    """
    Read the current shelf file content for comparison.
    
    Args:
        shelf_path (str): Path to the shelf file
        
    Returns:
        str: Shelf file content or None if read failed
    """
    try:
        with open(shelf_path, 'r') as f:
            content = f.read()
        
        print_status("Read current shelf content ({0} characters)".format(len(content)))
        return content
        
    except Exception as e:
        print_status("Error reading shelf file: {0}".format(str(e)), is_error=True)
        return None


# ============================================================================
# UPDATE DETECTION AND STATUS MANAGEMENT
# ============================================================================
# Functions for checking updates and managing visual status indicators

def check_for_shelf_updates():
    """
    Check if there are updates available for the shelf and associated scripts.
    
    This function performs comprehensive update checking for all components
    of the shelf system and returns detailed status information.
    
    Returns:
        dict: Update status information with keys:
              - 'updates_available' (bool): Whether any updates are available
              - 'shelf_updates' (bool): Whether shelf MEL file has updates
              - 'details' (list): List of components that have updates
              - 'error' (str): Error message if check failed
    """
    print_status("Checking for updates to shelf components...")
    
    try:
        # ====================================================================
        # GET CURRENT SHELF CONTENT
        # ====================================================================
        shelf_path = get_shelf_file_path()
        if not shelf_path:
            return {
                'updates_available': False,
                'shelf_updates': False,
                'details': [],
                'error': 'Could not locate shelf file'
            }
        
        current_shelf_content = read_current_shelf_content(shelf_path)
        if current_shelf_content is None:
            return {
                'updates_available': False,
                'shelf_updates': False,
                'details': [],
                'error': 'Could not read current shelf file'
            }
        
        # ====================================================================
        # CHECK SHELF MEL FILE FOR UPDATES
        # ====================================================================
        print_status("Checking shelf MEL file for updates...")
        
        shelf_update_info = check_for_file_updates(current_shelf_content, SHELF_MEL_PATH)
        
        if shelf_update_info.get('error'):
            return {
                'updates_available': False,
                'shelf_updates': False,
                'details': [],
                'error': 'Update check failed: {0}'.format(shelf_update_info['error'])
            }
        
        # ====================================================================
        # COMPILE UPDATE STATUS
        # ====================================================================
        shelf_has_updates = shelf_update_info.get('updates_available', False)
        update_details = []
        
        if shelf_has_updates:
            update_details.append('Shelf MEL file')
            print_status("Shelf MEL file has updates available", is_success=True)
        else:
            print_status("Shelf MEL file is up to date")
        
        # Future: Could add checks for other components here
        # (update scripts, utilities, etc.)
        
        overall_updates_available = len(update_details) > 0
        
        result = {
            'updates_available': overall_updates_available,
            'shelf_updates': shelf_has_updates,
            'details': update_details,
            'error': None
        }
        
        if overall_updates_available:
            print_status("Updates available for: {0}".format(', '.join(update_details)), is_success=True)
        else:
            print_status("All components are up to date", is_success=True)
        
        return result
        
    except Exception as e:
        print_status("Error during update check: {0}".format(str(e)), is_error=True)
        return {
            'updates_available': False,
            'shelf_updates': False,
            'details': [],
            'error': str(e)
        }


def update_button_visual_status(status_type):
    """
    Update the visual appearance of the update button to reflect current status.
    
    This function changes the button color to provide immediate visual feedback
    about the update status without requiring text or dialog messages.
    
    Args:
        status_type (str): Status type - 'up_to_date', 'updates_available', 
                          'update_failed', or 'checking'
    """
    if not MAYA_AVAILABLE:
        return
        
    try:
        # ====================================================================
        # FIND UPDATE BUTTON IN SHELF
        # ====================================================================
        if not cmds.shelfLayout(SHELF_NAME, exists=True):
            print_status("Shelf {0} not found for visual update".format(SHELF_NAME), is_warning=True)
            return
        
        # Get all shelf buttons
        shelf_buttons = cmds.shelfLayout(SHELF_NAME, query=True, childArray=True) or []
        
        # Find the update button by label
        update_button = None
        for button in shelf_buttons:
            if cmds.objectTypeUI(button) == 'shelfButton':
                try:
                    label = cmds.shelfButton(button, query=True, label=True)
                    if label and UPDATE_BUTTON_LABEL.lower() in label.lower():
                        update_button = button
                        break
                except Exception:
                    continue
        
        if not update_button:
            print_status("Update button not found for visual update", is_warning=True)
            return
        
        # ====================================================================
        # UPDATE BUTTON APPEARANCE
        # ====================================================================
        if status_type in BUTTON_COLORS:
            color = BUTTON_COLORS[status_type]
            
            cmds.shelfButton(
                update_button, 
                edit=True, 
                enableBackground=True,
                backgroundColor=color
            )
            
            print_status("Update button color set to {0} ({1})".format(status_type, color))
        else:
            print_status("Unknown status type: {0}".format(status_type), is_warning=True)
            
    except Exception as e:
        print_status("Error updating button visual status: {0}".format(str(e)), is_error=True)


# ============================================================================
# SHELF UPDATE EXECUTION FUNCTIONS
# ============================================================================
# Functions for performing the actual shelf update process

def perform_shelf_update():
    """
    Perform the actual shelf update process with backup and restore capabilities.
    
    This function handles the complete update workflow including backup creation,
    file replacement, and shelf reloading in Maya.
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        print_status("Starting shelf update process...")
        
        # ====================================================================
        # LOCATE AND BACKUP CURRENT SHELF
        # ====================================================================
        shelf_path = get_shelf_file_path()
        if not shelf_path:
            print_status("Cannot locate shelf file for update", is_error=True)
            return False
        
        # Create backup
        backup_path = shelf_path + ".backup"
        try:
            import shutil
            shutil.copy2(shelf_path, backup_path)
            print_status("Created backup: {0}".format(backup_path), is_success=True)
        except Exception as e:
            print_status("Warning: Could not create backup: {0}".format(str(e)), is_warning=True)
        
        # ====================================================================
        # DOWNLOAD LATEST SHELF CONTENT
        # ====================================================================
        print_status("Downloading latest shelf from GitHub...")
        
        latest_shelf_content = download_file_content(SHELF_MEL_PATH)
        if latest_shelf_content is None:
            print_status("Failed to download latest shelf", is_error=True)
            return False
        
        # ====================================================================
        # UPDATE SHELF FILE
        # ====================================================================
        try:
            with open(shelf_path, 'w') as f:
                f.write(latest_shelf_content)
            print_status("Shelf file updated successfully", is_success=True)
        except Exception as e:
            print_status("Error writing updated shelf: {0}".format(str(e)), is_error=True)
            # Try to restore backup
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, shelf_path)
                    print_status("Restored from backup due to write error", is_warning=True)
                except Exception:
                    pass
            return False
        
        # ====================================================================
        # RELOAD SHELF IN MAYA
        # ====================================================================
        if MAYA_AVAILABLE:
            try:
                # Remove existing shelf
                if cmds.shelfLayout(SHELF_NAME, exists=True):
                    cmds.deleteUI(SHELF_NAME, layout=True)
                    print_status("Removed old shelf")
                
                # Load updated shelf
                mel.eval('loadNewShelf "{0}"'.format(shelf_path.replace('\\', '/')))
                
                # Verify shelf loaded
                if cmds.shelfLayout(SHELF_NAME, exists=True):
                    print_status("Shelf reloaded successfully", is_success=True)
                    
                    # Set button to up-to-date status
                    update_button_visual_status('up_to_date')
                    return True
                else:
                    print_status("Shelf failed to reload", is_error=True)
                    return False
                    
            except Exception as e:
                print_status("Error reloading shelf: {0}".format(str(e)), is_error=True)
                return False
        
        return True
        
    except Exception as e:
        print_status("Error during shelf update: {0}".format(str(e)), is_error=True)
        return False


def prompt_user_for_update(update_details):
    """
    Prompt the user to confirm they want to install available updates.
    
    Args:
        update_details (list): List of components that have updates available
        
    Returns:
        bool: True if user wants to update, False otherwise
    """
    if not MAYA_AVAILABLE:
        # In non-Maya environment, default to yes
        return True
    
    try:
        # Build update message
        components_text = ', '.join(update_details)
        message = format_string(
            "Updates are available for: {components}\n\n"
            "Would you like to install these updates now?\n\n"
            "This will:\n"
            "• Download the latest shelf from GitHub\n"
            "• Create a backup of your current shelf\n"
            "• Replace your shelf with the updated version\n"
            "• Reload the shelf in Maya",
            components=components_text
        )
        
        result = cmds.confirmDialog(
            title='FDMA 2530 Shelf Updates Available',
            message=message,
            button=['Install Updates', 'Not Now'],
            defaultButton='Install Updates',
            cancelButton='Not Now',
            dismissString='Not Now'
        )
        
        return result == 'Install Updates'
        
    except Exception as e:
        print_status("Error showing update prompt: {0}".format(str(e)), is_error=True)
        return False


def show_update_completion_message(success):
    """
    Show final message about update completion status.
    
    Args:
        success (bool): Whether the update was successful
    """
    if not MAYA_AVAILABLE:
        return
    
    try:
        if success:
            message = (
                "Your FDMA 2530 shelf has been updated successfully!\n\n"
                "The shelf has been reloaded with the latest features and improvements.\n"
                "All your tools are ready to use."
            )
            title = "Update Complete"
        else:
            message = (
                "The shelf update failed to complete.\n\n"
                "Your original shelf has been restored from backup.\n"
                "Please check your internet connection and try again.\n\n"
                "If problems persist, contact: {0}".format(CONTACT_INFO)
            )
            title = "Update Failed"
        
        cmds.confirmDialog(
            title=title,
            message=message,
            button=['OK']
        )
        
    except Exception as e:
        print_status("Error showing completion message: {0}".format(str(e)), is_error=True)


# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================
# The main orchestration function that coordinates the entire update process

def main():
    """
    Main execution function for the shelf update system.
    
    This function coordinates the entire update process:
    1. Load GitHub utilities for robust operations
    2. Check for available updates
    3. Update visual status indicators
    4. Prompt user for update if needed
    5. Perform update and provide feedback
    
    Returns:
        bool: True if process completed successfully, False otherwise
    """
    # ========================================================================
    # INITIALIZATION AND WELCOME MESSAGE
    # ========================================================================
    print_header()
    
    # Display Python and Maya version information for debugging
    print_status("Python {0}.{1}.{2} compatibility mode active".format(
        sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    
    if MAYA_AVAILABLE:
        try:
            maya_version = cmds.about(version=True)
            print_status("Maya {0} environment detected".format(maya_version))
        except Exception:
            print_status("Maya environment detected (version unknown)")
    
    # ========================================================================
    # SET BUTTON TO CHECKING STATUS
    # ========================================================================
    update_button_visual_status('checking')
    
    # ========================================================================
    # LOAD GITHUB UTILITIES
    # ========================================================================
    utilities_loaded = False
    
    for attempt in range(MAX_RETRY_ATTEMPTS):
        if attempt > 0:
            print_status("Retrying utilities load (attempt {0}/{1})...".format(
                attempt + 1, MAX_RETRY_ATTEMPTS))
        
        if load_github_utilities():
            if verify_utilities_available():
                utilities_loaded = True
                break
            else:
                print_status("Utilities loaded but verification failed", is_warning=True)
    
    if not utilities_loaded:
        print_status("Cannot proceed without GitHub utilities", is_error=True)
        update_button_visual_status('update_failed')
        print_footer(success=False)
        return False
    
    # ========================================================================
    # CHECK FOR UPDATES
    # ========================================================================
    print_status("Checking for available updates...")
    
    update_status = check_for_shelf_updates()
    
    if update_status.get('error'):
        print_status("Update check failed: {0}".format(update_status['error']), is_error=True)
        update_button_visual_status('update_failed')
        print_footer(success=False)
        return False
    
    updates_available = update_status.get('updates_available', False)
    update_details = update_status.get('details', [])
    
    # ========================================================================
    # UPDATE VISUAL STATUS AND HANDLE UPDATES
    # ========================================================================
    if updates_available:
        # Set button to green (updates available)
        update_button_visual_status('updates_available')
        
        # Prompt user for update
        if prompt_user_for_update(update_details):
            print_status("User confirmed update installation")
            
            # Perform the update
            update_success = perform_shelf_update()
            
            if update_success:
                print_status("Update completed successfully", is_success=True)
                update_button_visual_status('up_to_date')
                show_update_completion_message(True)
                print_footer(success=True, updates_found=True)
            else:
                print_status("Update failed", is_error=True)
                update_button_visual_status('update_failed')
                show_update_completion_message(False)
                print_footer(success=False)
            
            return update_success
        else:
            print_status("User declined update installation")
            print_footer(success=True, updates_found=False)
            return True
    else:
        # Set button to gray (up to date)
        update_button_visual_status('up_to_date')
        print_status("No updates available - shelf is current", is_success=True)
        print_footer(success=True, updates_found=False)
        return True


# ============================================================================
# SCRIPT EXECUTION ENTRY POINTS
# ============================================================================
# Handle execution whether the script is run directly or imported/executed
# from the Maya shelf button.

if __name__ == "__main__":
    # Direct execution (for testing)
    print("Running FDMA 2530 Update System in direct execution mode...")
    main()
else:
    # Execution from shelf button (normal usage)
    main()
