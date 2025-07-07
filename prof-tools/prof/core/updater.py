"""
Prof-Tools Updater Module
Checks GitHub for newer releases and performs update on demand.
"""

# Ensure print/division behave the same in Python 2 and 3
from __future__ import absolute_import, division, print_function
import sys
import webbrowser
import logging

try:
    # Python 3 built-in
    from urllib.request import urlopen, Request
except ImportError:
    # Python 2 fallback
    from urllib2 import urlopen, Request

import json
from prof import __version__, __url__

# Configure logging for debug output
logger = logging.getLogger(__name__)
logging.basicConfig()

# GitHub API endpoint for latest release info
MANIFEST_URL = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/prof-tools/releases.json"

def _get_releases_manifest():
    """
    Fetch the releases manifest from GitHub.
    Returns the manifest data or None on error.
    """
    try:
        req = Request(MANIFEST_URL, headers={'User-Agent': 'Prof-Tools-Updater'})
        resp = urlopen(req, timeout=5)
        data = json.loads(resp.read().decode('utf-8'))
        return data
    except Exception as e:
        logger.error("Failed to fetch releases manifest: %s", e)
        return None

def get_latest_version():
    """
    Fetch the latest release version from the manifest.
    Returns the version string (e.g. "0.2.0") or None on error.
    """
    try:
        manifest = _get_releases_manifest()
        if not manifest:
            return None
        return manifest.get('current_version')
    except Exception as e:
        logger.error("Failed to parse latest version: %s", e)
        return None

def compare_versions(local, remote):
    """
    Compare semantic version strings "MAJOR.MINOR.PATCH".
    Returns True if remote > local.
    """
    try:
        # Convert "v0.2.0" to [0, 2, 0]
        lv = list(map(int, local.strip('v').split('.')))
        rv = list(map(int, remote.strip('v').split('.')))
        return rv > lv  # compare version lists
    except Exception as e:
        logger.error("Version comparison error: %s", e)
        return False


def launch_update_process():
    """
    Open the GitHub releases page in the default web browser.
    """
    webbrowser.open(__url__ + "/releases")


def check_for_updates():
    """
    Main function to check for updates and prompt the user.
    """
    try:
        import maya.cmds as cmds  # Maya commands for dialog boxes
    except ImportError:
        cmds = None  # if not in Maya, fallback to console output

    latest = get_latest_version()  # fetch remote version
    if not latest:
        _show_dialog("Update Check Failed",
                     "Could not determine latest version. Please try again later.",
                     cmds)
        return

    if compare_versions(__version__, latest):
        # construct message if an update is available
        msg = (
            "A new version of Prof-Tools is available.\n\n"
            "Current: {local}\nLatest: {remote}\n\n"
            "Open the releases page to download?"
        ).format(local=__version__, remote=latest)

        if cmds:
            # show Maya dialog with Yes/No
            res = cmds.confirmDialog(
                title="Prof-Tools Update",
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
                     "You are running the latest version ({ver}).".format(ver=__version__),
                     cmds)


def _show_dialog(title, message, cmds):
    """
    Show a simple OK dialog in Maya or print to console.
    """
    if cmds:
        cmds.confirmDialog(title=title, message=message, button=["OK"], defaultButton="OK")
    else:
        # console fallback
        print("{0}: {1}".format(title, message))
