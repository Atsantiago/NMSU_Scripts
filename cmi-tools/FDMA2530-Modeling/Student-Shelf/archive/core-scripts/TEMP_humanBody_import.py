import maya.cmds as cmds
import sys

# Determine Python version
python_version = sys.version_info[0]

# Base path for Maya content, adjust if your installation path differs
base_path = "C:/Program Files/Autodesk/"

# Determine Maya version and construct the file path
if python_version == 3:
    # This is for newer versions of Maya with Python 3
    maya_version = cmds.about(version=True)  # Automatically gets the Maya version
    file_path = f"{base_path}Maya{maya_version}/Examples/Modeling/Sculpting_Base_Meshes/Bipeds/HumanBody.ma"
else:
    # This is for older versions of Maya with Python 2
    maya_version = cmds.about(version=True)  # Automatically gets the Maya version
    file_path = "{base_path}Maya{}/Examples/Modeling/Sculpting_Base_Meshes/Bipeds/HumanBody.ma".format(maya_version)

# Import the "HumanBody.ma" file into the current scene
try:
    cmds.file(file_path, i=True, force=False)  # Use 'i=True' for import
    print("Successfully imported: " + file_path)
except Exception as e:
    print("Failed to import the file. Error: " + str(e))
