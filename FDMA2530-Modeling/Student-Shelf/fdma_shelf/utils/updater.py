"""
FDMA 2530 Shelf Update System v2.0.0
=====================================

Handles checking for updates, version comparison, and update installation
for the FDMA 2530 shelf system. Provides both startup checking and
on-demand update functionality.

Functions
---------
check_for_updates() -> bool
    Check if updates are available from GitHub.

run_update() -> None  
    Main entry point called by Update button.

startup_check() -> None
    Perform startup update check with visual feedback.

get_update_status() -> str
    Get current update status for button coloring.
"""

from __future__ import absolute_import, print_function

import os
import sys

import maya.cmds as cmds
import maya.utils as mu

# Import our utility modules
from .cache import (
    read_local_config_text, 
    write_local_config, 
    get_config_hash,
    cache_exists
)
from .downloader import download_raw


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

# GitHub URLs for updates
_GITHUB_CONFIG_URL = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/shelf_config.json"

# Visual status colors for update button
_BUTTON_COLORS = {
    "up_to_date": [0.5, 0.5, 0.5],        # Gray
    "updates_available": [0.2, 0.8, 0.2], # Green  
    "update_failed": [0.8, 0.2, 0.2],     # Red
    "checking": [0.8, 0.8, 0.2]           # Yellow
}

_SHELF_NAME = "FDMA_2530"


# ------------------------------------------------------------------
# Button visual feedback
# ------------------------------------------------------------------

def _update_button_color(status):
    """Update the visual color of the Update button."""
    try:
        if not cmds.shelfLayout(_SHELF_NAME, exists=True):
            return False
            
        # Find Update button
        buttons = cmds.shelfLayout(_SHELF_NAME, query=True, childArray=True) or []
        for btn in buttons:
            try:
                if cmds.objectTypeUI(btn) == "shelfButton":
                    label = cmds.shelfButton(btn, query=True, label=True)
                    if label == "Update":
                        color = _BUTTON_COLORS.get(status, _BUTTON_COLORS["up_to_date"])
                        cmds.shelfButton(btn, edit=True, backgroundColor=color)
                        return True
            except Exception:
                continue
        return False
        
    except Exception:
        return False


def _show_viewport_message(message, color="#FFCC00"):
    """Show a message in the Maya viewport."""
    try:
        cmds.inViewMessage(
            amg='<span style="color:{0}">{1}</span>'.format(color, message),
            pos="botLeft",
            fade=True,
            alpha=0.9,
            dragKill=False,
            fadeStayTime=3000
        )
    except Exception:
        pass


# ------------------------------------------------------------------
# Update checking logic
# ------------------------------------------------------------------

def check_for_updates():
    """
    Check if updates are available from GitHub.
    
    Returns
    -------
    bool
        True if updates are available, False otherwise.
    """
    try:
        # Download latest config from GitHub
        latest_config = download_raw(_GITHUB_CONFIG_URL, timeout=10)
        if not latest_config:
            return False
            
        # Get locally cached config
        local_config = read_local_config_text()
        
        # Compare hashes
        latest_hash = get_config_hash(latest_config)
        local_hash = get_config_hash(local_config)
        
        return latest_hash != local_hash
        
    except Exception as e:
        print("Update check failed: {0}".format(e))
        return False


def _confirm_update():
    """Show update confirmation dialog."""
    try:
        choice = cmds.confirmDialog(
            title="New Updates Available",
            message="New Updates Available. Would you like to update the shelf?",
            button=["Yes", "No"],
            defaultButton="Yes",
            cancelButton="No"
        )
        return choice == "Yes"
    except Exception:
        return False


def _perform_update():
    """Perform the actual update process."""
    try:
        # Download latest configuration
        latest_config = download_raw(_GITHUB_CONFIG_URL, timeout=15)
        if not latest_config:
            return False
            
        # Save new configuration to cache
        if not write_local_config(latest_config):
            return False
            
        # Rebuild shelf with new configuration
        def _deferred_rebuild():
            try:
                # Import and call shelf builder
                from ..shelf.builder import build_shelf
                build_shelf(startup=False)
                
                # Update button color
                _update_button_color("up_to_date")
                
                # Show success message
                _show_viewport_message("Shelf updated successfully!", "#55FF55")
                
            except Exception as e:
                print("Deferred shelf rebuild failed: {0}".format(e))
                _update_button_color("update_failed")
                
        # Use executeDeferred to avoid Maya crashes
        mu.executeDeferred(_deferred_rebuild)
        return True
        
    except Exception as e:
        print("Update process failed: {0}".format(e))
        return False


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def startup_check():
    """
    Perform startup update check with visual feedback.
    Called automatically when Maya starts if shelf is installed.
    """
    try:
        # Only check if cache exists (shelf was previously installed)
        if not cache_exists():
            return
            
        # Check for updates
        updates_available = check_for_updates()
        
        if updates_available:
            # Update button color and show notification
            _update_button_color("updates_available")
            _show_viewport_message("Updates to FDMA 2530 shelf available!")
        else:
            # Set button to up-to-date color
            _update_button_color("up_to_date")
            
    except Exception as e:
        print("Startup update check failed: {0}".format(e))


def run_update():
    """
    Main entry point for update button.
    Checks for updates and handles user interaction.
    """
    try:
        # Set checking status
        _update_button_color("checking")
        
        # Check for updates
        updates_available = check_for_updates()
        
        if updates_available:
            # Updates found - set button color and ask user
            _update_button_color("updates_available")
            
            if _confirm_update():
                # User wants to update
                if _perform_update():
                    print("Shelf update completed successfully")
                else:
                    _update_button_color("update_failed")
                    _show_viewport_message("Update failed. Check console for details.", "#FF5555")
            else:
                # User declined - keep button green as reminder
                print("User declined shelf update")
                
        else:
            # No updates available
            _update_button_color("up_to_date")
            _show_viewport_message("You are already on the latest version")
            
    except Exception as e:
        print("Update process failed: {0}".format(e))
        _update_button_color("update_failed")
        _show_viewport_message("Update check failed. Check console for details.", "#FF5555")


def get_update_status():
    """
    Get current update status for external use.
    
    Returns
    -------
    str
        Status string: 'up_to_date', 'updates_available', 'update_failed', or 'unknown'
    """
    try:
        if check_for_updates():
            return "updates_available"
        else:
            return "up_to_date"
    except Exception:
        return "unknown"
