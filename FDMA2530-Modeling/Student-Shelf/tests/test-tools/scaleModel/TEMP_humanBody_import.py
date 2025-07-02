"""
Temporary Human Body Import Tool v0.1.0
=======================================

Temporary tool for importing the HumanBody.ma example file into the current Maya scene.

Created by: Alexander T. Santiago  
Contact: asanti89@nmsu.edu
"""

import maya.cmds as cmds
import sys
import os

__version__ = "0.1.0"

def main():
    """
    Locate the HumanBody.ma example asset under Maya's Examples folder
    and import it into the current scene.
    """
    # Determine Maya install directory and current version
    maya_version = cmds.about(version=True)
    maya_install = cmds.internalVar(mayaInstallDir=True)
    # Construct path: <MAYA_INSTALL>/Examples/Modeling/Sculpting_Base_Meshes/Bipeds/HumanBody.ma
    examples_dir = os.path.join(
        maya_install, "Examples", "Modeling",
        "Sculpting_Base_Meshes", "Bipeds"
    )
    file_path = os.path.join(examples_dir, "HumanBody.ma")

    # Verify the file exists
    if not os.path.isfile(file_path):
        cmds.warning(f"HumanBody.ma not found at {file_path}")
        return

    # Import the MA file
    try:
        cmds.file(file_path, i=True, force=False)
        print(f"Successfully imported: {file_path}")
    except Exception as e:
        cmds.warning(f"Failed to import file: {e}")

def run():
    """Alias entry point for shelf button commands."""
    main()

if __name__ == "__main__":
    main()
