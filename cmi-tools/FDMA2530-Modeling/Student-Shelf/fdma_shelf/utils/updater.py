"""
FDMA2530 Shelf Updater v2.0.14

Checks for updates via GitHub manifest, compares versions,
and installs updates on demand. Provides clear Maya UI feedback.
"""

from __future__ import absolute_import, print_function

import os
import sys
import json
import ssl
import tempfile
import zipfile
import shutil

try:
    # Python 3
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    # Python 2
    from urllib2 import urlopen, URLError

import maya.cmds as cmds

from .version_utils import get_fdma2530_version


def run_update():
    """Main entry point for the Update button."""
    try:
        result = cmds.confirmDialog(
            title="FDMA 2530 Updater",
            message="Check for and install updates?",
            button=["Yes", "No"],
            defaultButton="Yes",
            cancelButton="No",
            dismissString="No"
        )
        
        if result == "Yes":
            _perform_update()
    except Exception as e:
        cmds.warning("Update check failed: {}".format(e))


def _perform_update():
    """Perform the actual update process."""
    try:
        # Check current version
        current_version = get_fdma2530_version()
        
        # Check for updates from GitHub
        manifest_url = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/cmi-tools/FDMA2530-Modeling/releases.json"
        
        # Disable SSL verification for GitHub
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        response = urlopen(manifest_url, context=ssl_context, timeout=30)
        manifest_data = json.loads(response.read().decode('utf-8'))
        
        latest_version = manifest_data.get("current_version", "Unknown")
        
        if latest_version == current_version:
            cmds.confirmDialog(
                title="Up to Date",
                message="You have the latest version: {}".format(current_version),
                button=["OK"]
            )
            return
        
        # Confirm update
        result = cmds.confirmDialog(
            title="Update Available",
            message="Update from {} to {}?".format(current_version, latest_version),
            button=["Update", "Cancel"],
            defaultButton="Update"
        )
        
        if result != "Update":
            return
        
        # Perform update by running the installer
        _run_installer_update()
        
    except Exception as e:
        cmds.confirmDialog(
            title="Update Failed",
            message="Could not check for updates: {}".format(str(e)),
            button=["OK"]
        )


def _run_installer_update():
    """Re-run the installer to update the shelf."""
    try:
        # Import the installer and run it
        from fdma_shelf.utils import system_utils
        
        # Get the Maya user directory
        maya_app_dir = cmds.internalVar(userAppDir=True)
        cmi_root = os.path.join(maya_app_dir, "cmi-tools")
        
        # Download and reinstall
        repo_url = "https://github.com/Atsantiago/NMSU_Scripts/archive/refs/heads/master.zip"
        
        if _download_and_install(repo_url, cmi_root):
            cmds.confirmDialog(
                title="Update Complete",
                message="FDMA 2530 shelf updated successfully!",
                button=["OK"]
            )
            
            # Rebuild shelf
            try:
                import fdma_shelf.shelf.builder as builder
                builder.build_shelf()
            except Exception as e:
                cmds.warning("Shelf rebuild failed: {}".format(e))
        else:
            cmds.confirmDialog(
                title="Update Failed",
                message="Could not download or install update.",
                button=["OK"]
            )
            
    except Exception as e:
        cmds.confirmDialog(
            title="Update Error",
            message="Update failed: {}".format(str(e)),
            button=["OK"]
        )


def _download_and_install(url, target_dir):
    """Download repository and install to target directory."""
    try:
        # Download ZIP
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        response = urlopen(url, context=ssl_context, timeout=60)
        zip_data = response.read()
        
        # Create temp file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.write(zip_data)
        temp_zip.close()
        
        # Extract
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find extracted repo
        repo_name = None
        for item in os.listdir(temp_dir):
            if item.startswith("NMSU_Scripts-"):
                repo_name = item
                break
        
        if not repo_name:
            return False
        
        # Source paths
        source_shelf = os.path.join(temp_dir, repo_name, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf", "fdma_shelf")
        source_config = os.path.join(temp_dir, repo_name, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf", "shelf_config.json")
        source_manifest = os.path.join(temp_dir, repo_name, "cmi-tools", "FDMA2530-Modeling", "releases.json")
        
        # Target paths
        scripts_dir = os.path.join(target_dir, "scripts")
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        
        target_shelf = os.path.join(scripts_dir, "fdma_shelf")
        target_config = os.path.join(scripts_dir, "shelf_config.json")
        target_manifest = os.path.join(target_shelf, "releases.json")
        
        # Copy files
        if os.path.exists(target_shelf):
            shutil.rmtree(target_shelf)
        shutil.copytree(source_shelf, target_shelf)
        
        if os.path.exists(source_config):
            shutil.copy2(source_config, target_config)
        
        if os.path.exists(source_manifest):
            shutil.copy2(source_manifest, target_manifest)
        
        # Cleanup
        os.unlink(temp_zip.name)
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print("Download/install failed: {}".format(e))
        return False


def startup_check():
    """Check for updates on Maya startup."""
    # Simple startup check - just log that we're available
    print("FDMA 2530 Updater: Ready for updates")
