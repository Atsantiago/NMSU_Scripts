"""
Prof-Tools Drag-and-Drop Installer

Single-file installer that downloads the latest Prof-Tools release from GitHub,
unzips it, and runs the setup logic.
"""

from __future__ import absolute_import, division, print_function
import sys
import os
import logging
import zipfile
import shutil

# Python 2/3 URL fetch
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

# Configure logger
logging.basicConfig()
logger = logging.getLogger("prof_tools_installer")
logger.setLevel(logging.INFO)

# GitHub ZIP URL for the default branch
GITHUB_REPO_ZIP = (
    "https://github.com/Atsantiago/NMSU_Scripts"
    "/archive/refs/heads/main.zip"
)

def onMayaDroppedPythonFile(*args):
    """
    Entry point for Maya drag-and-drop.
    Downloads Prof-Tools, extracts it, and launches the installer.
    """
    try:
        logger.info("Starting Prof-Tools installer…")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(script_dir, "prof_tools_tmp")

        # Clean up any previous temp folder
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # Download the ZIP from GitHub
        logger.info("Downloading Prof-Tools package…")
        resp = urlopen(GITHUB_REPO_ZIP, timeout=30)
        zip_path = os.path.join(temp_dir, "prof_tools.zip")
        with open(zip_path, "wb") as f:
            f.write(resp.read())

        # Extract ZIP into temp_dir
        logger.info("Extracting package…")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(temp_dir)

        # Identify the extracted root folder
        extracted_root = None
        for name in os.listdir(temp_dir):
            path = os.path.join(temp_dir, name)
            # Match either "-main" or "-master"
            if os.path.isdir(path) and (name.endswith("-main") or name.endswith("-master")):
                extracted_root = path
                break

        # Fallback: find any folder containing a 'prof' subfolder
        if not extracted_root:
            for name in os.listdir(temp_dir):
                path = os.path.join(temp_dir, name)
                if os.path.isdir(path):
                    if os.path.isdir(os.path.join(path, "prof")):
                        extracted_root = path
                        break

        # Fail if still not found
        if not extracted_root:
            raise RuntimeError("Could not find extracted Prof-Tools folder")

        # Locate the 'prof' package inside the extracted folder
        prof_path = os.path.join(extracted_root, "prof-tools", "prof")
        if not os.path.isdir(prof_path):
            prof_path = os.path.join(extracted_root, "prof")
        if not os.path.isdir(prof_path):
            raise RuntimeError("Cannot locate 'prof' package in download")

        # Add the path to sys.path so Python can import it
        if prof_path not in sys.path:
            sys.path.insert(0, prof_path)
        logger.info("Added prof package to sys.path: %s", prof_path)

        # Launch the installer logic from the downloaded package
        from prof.core.setup import launcher_entry_point
        launcher_entry_point()

    except Exception as e:
        msg = "Installer failed: {}".format(e)
        logger.error(msg)
        # Try to show a Maya dialog; fall back to console print
        try:
            import maya.cmds as cmds
            cmds.confirmDialog(
                title="Prof-Tools Installer Error",
                message=msg,
                button=["OK"]
            )
        except ImportError:
            print(msg)

if __name__ == "__main__":
    # Allow testing outside Maya
    onMayaDroppedPythonFile()
