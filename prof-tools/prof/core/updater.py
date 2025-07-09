"""
Prof-Tools Updater Module

Handles checking for updates via releases.json manifest, version comparison,
and provides user feedback for the Prof-Tools Maya menu system.

This module follows the manifest-based update pattern established in FDMA2530
tools, ensuring all update checks use the local releases.json file as the 
source of truth rather than GitHub releases.

Author: Alexander T. Santiago
Version: Dynamic (Read from releases.json)
License: MIT
Repository: https://github.com/Atsantiago/NMSU_Scripts

Functions:
    check_for_updates() -> bool
        Check if a newer version exists in the manifest
    
    get_latest_version() -> str
        Fetch the latest version from releases.json
    
    compare_versions(local, remote) -> bool
        Compare semantic version strings
    
    launch_update_process() -> None
        Open GitHub repository for manual update
"""

# Ensure print/division behave the same in Python 2 and 3
from __future__ import absolute_import, division, print_function
import sys
import webbrowser
import logging
import ssl
import json

try:
    # Python 3 built-in
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    # Python 2 fallback
    from urllib2 import urlopen, Request, URLError

# Import version utilities for robust version handling
from .version_utils import get_prof_tools_version, parse_semantic_version, is_valid_semantic_version

# Configure logging for debug output
logger = logging.getLogger(__name__)
logging.basicConfig()

# Manifest URL - pointing to our releases.json file
MANIFEST_URL = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/prof-tools/releases.json"
_HTTP_TIMEOUT = 10  # seconds


def _get_releases_manifest():
    """
    Fetch the releases manifest from GitHub.
    Returns the manifest data or None on error.
    
    This function uses robust error handling and follows the pattern
    established in FDMA2530 tools for consistent manifest fetching.
    """
    try:
        req = Request(MANIFEST_URL, headers={'User-Agent': 'Prof-Tools-Updater'})
        resp = urlopen(req, timeout=_HTTP_TIMEOUT)
        data = json.loads(resp.read().decode('utf-8'))
        logger.debug("Successfully fetched releases manifest")
        return data
    except URLError as e:
        logger.error("Network error fetching releases manifest: %s", e)
        return None
    except json.JSONDecodeError as e:
        logger.error("JSON decode error in releases manifest: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected error fetching releases manifest: %s", e)
        return None


def get_latest_version():
    """
    Fetch the latest release version from the manifest.
    Returns the version string (e.g. "0.2.0") or None on error.
    
    This uses the manifest-based approach rather than GitHub releases API,
    ensuring consistency with the local releases.json file.
    """
    try:
        manifest = _get_releases_manifest()
        if not manifest:
            logger.warning("Could not fetch manifest for version check")
            return None
        
        latest_version = manifest.get('current_version')
        if not latest_version:
            logger.error("No current_version field found in manifest")
            return None
            
        if not is_valid_semantic_version(latest_version):
            logger.error("Invalid semantic version in manifest: %s", latest_version)
            return None
            
        logger.debug("Latest version from manifest: %s", latest_version)
        return latest_version
        
    except Exception as e:
        logger.error("Failed to parse latest version from manifest: %s", e)
        return None


def compare_versions(local, remote):
    """
    Compare semantic version strings "MAJOR.MINOR.PATCH".
    Returns True if remote > local.
    
    Uses robust semantic version parsing to handle edge cases
    and provide reliable version comparison.
    """
    try:
        # Validate both versions first
        if not is_valid_semantic_version(local):
            logger.error("Invalid local version format: %s", local)
            return False
            
        if not is_valid_semantic_version(remote):
            logger.error("Invalid remote version format: %s", remote)
            return False
        
        # Parse both versions
        local_parsed = parse_semantic_version(local)
        remote_parsed = parse_semantic_version(remote)
        
        # Compare major.minor.patch
        local_tuple = (local_parsed['major'], local_parsed['minor'], local_parsed['patch'])
        remote_tuple = (remote_parsed['major'], remote_parsed['minor'], remote_parsed['patch'])
        
        is_newer = remote_tuple > local_tuple
        logger.debug("Version comparison: %s vs %s -> newer: %s", local, remote, is_newer)
        return is_newer
        
    except Exception as e:
        logger.error("Version comparison error between %s and %s: %s", local, remote, e)
        return False


def launch_update_process():
    """
    Open the GitHub repository releases page in the default web browser.
    This provides a manual update path for users.
    """
    try:
        # Use the repository URL from the prof module
        repo_url = "https://github.com/Atsantiago/NMSU_Scripts"
        releases_url = repo_url + "/releases"
        webbrowser.open(releases_url)
        logger.info("Opened releases page in browser: %s", releases_url)
    except Exception as e:
        logger.error("Failed to open releases page: %s", e)


def check_for_updates():
    """
    Main function to check for updates and prompt the user.
    
    This function provides Maya-integrated dialogs when available,
    with console fallback for non-Maya environments.
    """
    try:
        import maya.cmds as cmds  # Maya commands for dialog boxes
    except ImportError:
        cmds = None  # if not in Maya, fallback to console output

    # Get current version using version_utils
    current_version = get_prof_tools_version()
    if not current_version:
        _show_dialog("Version Error",
                     "Could not determine current Prof-Tools version.",
                     cmds)
        return

    # Get latest version from manifest
    latest = get_latest_version()  # fetch remote version
    if not latest:
        _show_dialog("Update Check Failed",
                     "Could not determine latest version. Please check your internet connection and try again later.",
                     cmds)
        return

    # Compare versions
    if compare_versions(current_version, latest):
        # construct message if an update is available
        msg = (
            "A new version of Prof-Tools is available.\n\n"
            "Current: {local}\nLatest: {remote}\n\n"
            "Open the releases page to download?"
        ).format(local=current_version, remote=latest)

        if cmds:
            # show Maya dialog with Yes/No
            res = cmds.confirmDialog(
                title="Prof-Tools Update Available",
                message=msg,
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No",
                dismissString="No"
            )
            if res == "Yes":
                launch_update_process()
        else:
            # fallback: print to console and open browser
            print(msg)
            launch_update_process()
    else:
        # message if already up to date
        _show_dialog("Up to Date",
                     "You are running the latest version ({ver}).".format(ver=current_version),
                     cmds)


def _show_dialog(title, message, cmds):
    """
    Show a simple OK dialog in Maya or print to console.
    
    Args:
        title (str): Dialog title
        message (str): Dialog message
        cmds: Maya cmds module or None for console fallback
    """
    if cmds:
        cmds.confirmDialog(title=title, message=message, button=["OK"], defaultButton="OK")
    else:
        # console fallback
        print("{0}: {1}".format(title, message))
