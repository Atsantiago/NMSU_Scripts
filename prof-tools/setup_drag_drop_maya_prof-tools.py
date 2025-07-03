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

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2 fallback
    from urllib2 import urlopen

# Configure logger
logging.basicConfig()
logger = logging.getLogger("prof_tools_installer")
logger.setLevel(logging.INFO)

# GitHub repo and API URLs
GITHUB_REPO_ZIP = "https://github.com/Atsantiago/NMSU_Scripts/archive/refs/heads/main.zip"

def onMayaDroppedPythonFile(*args):
    """
    Entry point for Maya drag-and-drop.
    Downloads Prof-Tools, extracts, and launches installer.
    """
    try:
        logger.info("Starting Prof-Tools installer…")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(script_dir, "prof_tools_tmp")
        
        # Clean up any previous temp
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # Download the ZIP
        logger.info("Downloading Prof-Tools package…")
        resp = urlopen(GITHUB_REPO_ZIP, timeout=30)
        zip_path = os.path.join(temp_dir, "prof_tools.zip")
        with open(zip_path, "wb") as f:
            f.write(resp.read())

        # Extract ZIP
        logger.info("Extracting package…")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(temp_dir)

        # The repo root folder ends with "-main"
        extracted_root = None
        for name in os.listdir(temp_dir):
            path = os.path.join(temp_dir, name)
            if os.path.isdir(path) and name.endswith("-main"):
                extracted_root = path
                break
        if not extracted_root:
            raise RuntimeError("Could not find extracted Prof-Tools folder")
        
        # Add the extracted 'prof' package to sys.path
        prof_path = os.path.join(extracted_root, "prof-tools", "prof")
        if not os.path.isdir(prof_path):
            # Some repos name the folder differently
            prof_path = os.path.join(extracted_root, "prof")
        if not os.path.isdir(prof_path):
            raise RuntimeError("Cannot locate 'prof' package in download")
        if prof_path not in sys.path:
            sys.path.insert(0, prof_path)
        logger.info("prof package path added to sys.path: %s", prof_path)

        # Launch the packaged installer logic
        from prof.core.setup import launcher_entry_point
        launcher_entry_point()

    except Exception as e:
        msg = "Installer failed: {}".format(str(e))
        logger.error(msg)
        try:
            import maya.cmds as cmds
            cmds.confirmDialog(title="Prof-Tools Installer Error",
                               message=msg,
                               button=["OK"])
        except ImportError:
            print(msg)

# Allow for direct testing outside of Maya
if __name__ == "__main__":
    onMayaDroppedPythonFile()
