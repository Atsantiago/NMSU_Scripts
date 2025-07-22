"""
Prof-Tools Developer Mode and Silent Update System

Inspired by GT Tools' approach to developer mode and silent updates.
Provides a clean separation between stable and development features.

Features:
- Developer mode toggle (persistent preference)
- Silent update checking with configurable intervals
- Auto-check preferences system
- Temporary test version installation
- Automatic revert on Maya restart

Author: Alexander T. Santiago
"""

from __future__ import absolute_import, division, print_function

import logging
import os
import json
import shutil
from datetime import datetime, timedelta

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

class ProfToolsPrefs(object):
    """
    Preference management system for prof-tools.
    Handles developer mode, auto-update settings, and temporary installations.
    """
    
    def __init__(self):
        self.prefs_dir = self._get_prefs_dir()
        self.prefs_file = os.path.join(self.prefs_dir, "prof_tools_prefs.json")
        self.temp_install_file = os.path.join(self.prefs_dir, "temp_install.json")
        self._ensure_prefs_dir()
        self.prefs = self._load_prefs()
    
    def _get_prefs_dir(self):
        """Get the preferences directory for prof-tools."""
        if MAYA_AVAILABLE:
            try:
                maya_prefs = cmds.internalVar(userPrefDir=True)
                return os.path.join(maya_prefs, "prof_tools")
            except:
                pass
        
        # Fallback to user directory
        import os.path
        return os.path.join(os.path.expanduser("~"), ".prof_tools")
    
    def _ensure_prefs_dir(self):
        """Ensure the preferences directory exists."""
        if not os.path.exists(self.prefs_dir):
            try:
                os.makedirs(self.prefs_dir)
            except OSError:
                logger.warning("Could not create preferences directory: %s", self.prefs_dir)
    
    def _load_prefs(self):
        """Load preferences from file."""
        defaults = {
            "dev_mode_enabled": False,
            "auto_check_enabled": False,
            "check_interval_days": 7,
            "last_check_date": None,
            "include_test_versions": False,
            "temp_install": {
                "enabled": False,
                "version": None,
                "stable_version": None,
                "install_date": None
            }
        }
        
        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file, 'r') as f:
                    loaded_prefs = json.load(f)
                    defaults.update(loaded_prefs)
            except (IOError, ValueError) as e:
                logger.warning("Could not load preferences: %s", e)
        
        return defaults
    
    def _save_prefs(self):
        """Save preferences to file."""
        try:
            with open(self.prefs_file, 'w') as f:
                json.dump(self.prefs, f, indent=2)
        except IOError as e:
            logger.warning("Could not save preferences: %s", e)
    
    # Developer Mode Methods
    def is_dev_mode_enabled(self):
        """Check if developer mode is enabled."""
        return self.prefs.get("dev_mode_enabled", False)
    
    def set_dev_mode_enabled(self, enabled):
        """Enable or disable developer mode."""
        self.prefs["dev_mode_enabled"] = bool(enabled)
        self._save_prefs()
    
    def toggle_dev_mode(self):
        """Toggle developer mode on/off."""
        new_state = not self.is_dev_mode_enabled()
        self.set_dev_mode_enabled(new_state)
        
        if MAYA_AVAILABLE:
            # Show feedback in Maya
            state_msg = "Enabled" if new_state else "Disabled"
            cmds.inViewMessage(
                amg=f'Developer Mode: <span style="color:#FF0000;text-decoration:underline;">{state_msg}</span>',
                pos='botLeft', fade=True, alpha=0.9
            )
        
        logger.info("Developer mode %s", "enabled" if new_state else "disabled")
        return new_state
    
    # Auto Update Methods
    def is_auto_check_enabled(self):
        """Check if automatic update checking is enabled."""
        return self.prefs.get("auto_check_enabled", False)
    
    def set_auto_check_enabled(self, enabled):
        """Enable or disable automatic update checking."""
        self.prefs["auto_check_enabled"] = bool(enabled)
        self._save_prefs()
    
    def get_check_interval_days(self):
        """Get the auto-check interval in days."""
        return self.prefs.get("check_interval_days", 7)
    
    def set_check_interval_days(self, days):
        """Set the auto-check interval in days."""
        self.prefs["check_interval_days"] = int(days)
        self._save_prefs()
    
    def get_last_check_date(self):
        """Get the last update check date."""
        date_str = self.prefs.get("last_check_date")
        if date_str:
            try:
                return datetime.fromisoformat(date_str)
            except (ValueError, AttributeError):
                # Handle Python 2.7 compatibility
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return None
        return None
    
    def set_last_check_date(self, date=None):
        """Set the last update check date."""
        if date is None:
            date = datetime.now()
        
        # Format for cross-Python compatibility
        self.prefs["last_check_date"] = date.strftime("%Y-%m-%d %H:%M:%S")
        self._save_prefs()
    
    def should_check_for_updates(self):
        """Check if it's time to check for updates."""
        if not self.is_auto_check_enabled():
            return False
        
        last_check = self.get_last_check_date()
        if last_check is None:
            return True
        
        interval = timedelta(days=self.get_check_interval_days())
        return datetime.now() - last_check >= interval
    
    def includes_test_versions(self):
        """Check if test versions should be included in updates."""
        return self.prefs.get("include_test_versions", False)
    
    def set_include_test_versions(self, include):
        """Set whether to include test versions in updates."""
        self.prefs["include_test_versions"] = bool(include)
        self._save_prefs()
    
    # Temporary Installation Methods
    def is_temp_install_active(self):
        """Check if a temporary installation is active."""
        temp_info = self.prefs.get("temp_install", {})
        return temp_info.get("enabled", False)
    
    def get_temp_install_info(self):
        """Get information about the current temporary installation."""
        return self.prefs.get("temp_install", {})
    
    def set_temp_install(self, version, stable_version):
        """Set up a temporary installation."""
        self.prefs["temp_install"] = {
            "enabled": True,
            "version": version,
            "stable_version": stable_version,
            "install_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_prefs()
        
        # Also save to separate temp file for startup detection
        try:
            with open(self.temp_install_file, 'w') as f:
                json.dump(self.prefs["temp_install"], f)
        except IOError:
            logger.warning("Could not save temp install file")
    
    def clear_temp_install(self):
        """Clear the temporary installation."""
        self.prefs["temp_install"] = {
            "enabled": False,
            "version": None,
            "stable_version": None,
            "install_date": None
        }
        self._save_prefs()
        
        # Remove temp file
        if os.path.exists(self.temp_install_file):
            try:
                os.remove(self.temp_install_file)
            except OSError:
                logger.warning("Could not remove temp install file")
    
    def check_and_revert_temp_install(self):
        """Check if we should revert from a temporary installation on startup."""
        if not os.path.exists(self.temp_install_file):
            return False
        
        try:
            with open(self.temp_install_file, 'r') as f:
                temp_info = json.load(f)
            
            if temp_info.get("enabled", False):
                # We have a temp install that should be reverted
                stable_version = temp_info.get("stable_version")
                if stable_version:
                    logger.info("Reverting temporary installation to stable version %s", stable_version)
                    self.clear_temp_install()
                    return True
        except (IOError, ValueError):
            logger.warning("Could not read temp install file")
        
        return False


def get_prefs():
    """Get the global preferences instance."""
    if not hasattr(get_prefs, '_instance'):
        get_prefs._instance = ProfToolsPrefs()
    return get_prefs._instance


def is_dev_mode_enabled():
    """Quick function to check if dev mode is enabled."""
    return get_prefs().is_dev_mode_enabled()


def toggle_dev_mode():
    """Quick function to toggle dev mode."""
    return get_prefs().toggle_dev_mode()


def should_show_dev_features():
    """Check if development features should be shown in the UI."""
    return is_dev_mode_enabled()


if __name__ == "__main__":
    # Test the preferences system
    prefs = ProfToolsPrefs()
    print("Dev mode enabled:", prefs.is_dev_mode_enabled())
    print("Auto check enabled:", prefs.is_auto_check_enabled())
    print("Should check for updates:", prefs.should_check_for_updates())
