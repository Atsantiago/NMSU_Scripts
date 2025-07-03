"""
Prof-Tools Menu Builder

Creates the Prof-Tools dropdown menu in Maya, with sections for grading
tools and a Help menu for version info and update checking.
"""

from __future__ import absolute_import, division, print_function

import logging
import maya.cmds as cmds
import maya.mel as mel

from prof import __version__
from prof.core.updater import check_for_updates

# Set up logging for this module
logging.basicConfig()
logger = logging.getLogger("prof_menu_builder")
logger.setLevel(logging.INFO)

# Menu labels
MENU_NAME     = "ProfTools"
MENU_LABEL    = "Prof-Tools"
GRADING_LABEL = "Grading Tools"
HELP_LABEL    = "Help"

def build_menu():
    """
    Create or rebuild the Prof-Tools menu in Maya's main window.
    """
    _delete_existing_menu()

    # Get Maya main window for parenting
    main_win = mel.eval('global string $gMainWindow; $tmp = $gMainWindow;')

    # Create the top-level Prof-Tools menu
    menu = cmds.menu(MENU_NAME, label=MENU_LABEL, parent=main_win, tearOff=True)

    _build_grading_section(menu)   # add grading tools section
    _build_help_section(menu)      # add help section

    logger.info("Prof-Tools menu created")

def _delete_existing_menu():
    """
    Remove any existing Prof-Tools menu before rebuilding.
    """
    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME)
        logger.debug("Removed existing Prof-Tools menu")

def _build_grading_section(parent_menu):
    """
    Add the 'Grading Tools' submenu with empty placeholders for each class.
    """
    # Open Grading Tools submenu
    grading = cmds.menuItem(
        label=GRADING_LABEL,
        subMenu=True,
        tearOff=True,
        parent=parent_menu
    )

    # FDMA 1510 placeholder
    fdma1510 = cmds.menuItem(
        label="FDMA 1510",
        subMenu=True,
        tearOff=True,
        parent=grading
    )
    cmds.menuItem(label="(no tools yet)", enable=False, parent=fdma1510)
    cmds.setParent('..', menu=True)  # close FDMA 1510 submenu

    # FDMA 2530 placeholder
    fdma2530 = cmds.menuItem(
        label="FDMA 2530",
        subMenu=True,
        tearOff=True,
        parent=grading
    )
    cmds.menuItem(label="(no tools yet)", enable=False, parent=fdma2530)
    cmds.setParent('..', menu=True)  # close FDMA 2530 submenu

    cmds.setParent('..', menu=True)    # close Grading Tools submenu

def _build_help_section(parent_menu):
    """
    Add the 'Help' submenu showing version and update option.
    """
    # Open Help submenu
    help_menu = cmds.menuItem(
        label=HELP_LABEL,
        subMenu=True,
        tearOff=True,
        parent=parent_menu
    )

    # Divider before version
    cmds.menuItem(divider=True, parent=help_menu)

    # Display current version
    cmds.menuItem(
        label="Version: {}".format(__version__),
        enable=False,
        parent=help_menu
    )

    # Divider before update option
    cmds.menuItem(divider=True, parent=help_menu)

    # Command to check for updates
    cmds.menuItem(
        label="Check for Updates…",
        parent=help_menu,
        command=lambda *args: check_for_updates()
    )

    cmds.setParent('..', menu=True)  # close Help submenu
    cmds.setParent('..', menu=True)  # close main Prof-Tools menu

if __name__ == "__main__":
    # When run directly in Maya script editor, build the menu
    logger.setLevel(logging.DEBUG)
    build_menu()
