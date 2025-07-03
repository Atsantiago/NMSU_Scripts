"""
Maya Menu Builder - Creates Prof-Tools menu in Maya
Builds the main Prof-Tools dropdown menu with grading tool sections.
Following GT-Tools patterns with MIT license compatibility.
"""

import maya.cmds as cmds
import maya.mel as mel
import logging
from prof import __version__

# Configure logging
logging.basicConfig()
logger = logging.getLogger("prof_menu_builder")

# Menu constants
MENU_NAME = "ProfTools"
MENU_LABEL = "Prof-Tools"

def build_menu():
    """
    Creates the main Prof-Tools menu in Maya's menu bar.
    Safely rebuilds the menu if it already exists.
    
    Returns:
        str: The menu path of the created menu, or empty string if failed
    """
    try:
        # Delete existing menu if it exists (singleton pattern)
        delete_menu()
        
        # Get Maya main window
        try:
            main_window = mel.eval('global string $gMainWindow; $tmp = $gMainWindow;')
        except Exception as e:
            logger.warning(f"Unable to find Maya main window: {e}")
            cmds.warning("Unable to find Maya Window. Menu creation was ignored.")
            return ""
        
        # Create main menu
        menu_path = cmds.menu(
            MENU_NAME,
            label=MENU_LABEL,
            parent=main_window,
            tearOff=True
        )
        
        # Add version information
        cmds.menuItem(
            divider=True,
            parent=menu_path
        )
        cmds.menuItem(
            label=f"Version: {__version__}",
            enable=False,
            parent=menu_path
        )
        cmds.menuItem(
            divider=True,
            parent=menu_path
        )
        
        # Create Grading Tools section
        _build_grading_section(menu_path)
        
        logger.info(f"Prof-Tools menu created successfully: {menu_path}")
        return menu_path
        
    except Exception as e:
        logger.error(f"Failed to create Prof-Tools menu: {e}")
        cmds.warning(f"Failed to create Prof-Tools menu: {e}")
        return ""

def _build_grading_section(parent_menu):
    """
    Builds the Grading Tools section of the menu.
    
    Args:
        parent_menu (str): Path to the parent menu
    """
    # Create Grading Tools submenu
    grading_menu = cmds.menuItem(
        label="Grading Tools",
        subMenu=True,
        tearOff=True,
        parent=parent_menu
    )
    
    # FDMA 1510 submenu
    fdma1510_menu = cmds.menuItem(
        label="FDMA 1510",
        subMenu=True,
        tearOff=True,
        parent=grading_menu
    )
    
    # Placeholder for FDMA 1510 tools (empty for now)
    cmds.menuItem(
        label="No tools available yet",
        enable=False,
        parent=fdma1510_menu
    )
    
    # FDMA 2530 submenu
    fdma2530_menu = cmds.menuItem(
        label="FDMA 2530",
        subMenu=True,
        tearOff=True,
        parent=grading_menu
    )
    
    # Placeholder for FDMA 2530 tools (empty for now)
    cmds.menuItem(
        label="No tools available yet",
        enable=False,
        parent=fdma2530_menu
    )
    
    # Close submenus properly
    cmds.setParent('..', menu=True)  # Close grading_menu
    cmds.setParent('..', menu=True)  # Close parent_menu

def delete_menu():
    """
    Deletes the Prof-Tools menu if it exists.
    Safe to call even if menu doesn't exist.
    """
    try:
        if cmds.menu(MENU_NAME, exists=True):
            cmds.menu(MENU_NAME, edit=True, deleteAllItems=True)
            cmds.deleteUI(MENU_NAME)
            logger.info("Existing Prof-Tools menu deleted")
    except Exception as e:
        logger.debug(f"Menu deletion failed (may not exist): {e}")

def menu_exists():
    """
    Checks if the Prof-Tools menu currently exists.
    
    Returns:
        bool: True if menu exists, False otherwise
    """
    try:
        return cmds.menu(MENU_NAME, exists=True)
    except Exception:
        return False

def refresh_menu():
    """
    Refreshes the Prof-Tools menu by rebuilding it.
    Useful for development and updates.
    
    Returns:
        str: The menu path of the refreshed menu
    """
    logger.info("Refreshing Prof-Tools menu...")
    return build_menu()

# Development and testing functions
def main():
    """
    Main function for testing the menu builder.
    Can be called directly for testing purposes.
    """
    print("Building Prof-Tools menu...")
    result = build_menu()
    if result:
        print(f"Menu created successfully: {result}")
    else:
        print("Menu creation failed")

if __name__ == "__main__":
    # Enable debug logging for development
    logger.setLevel(logging.DEBUG)
    main()
