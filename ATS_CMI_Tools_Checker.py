"""
This script sources the CMI Modeling Checklist from github. It will be used in the FDMA 2530 Shelf that I will give to students at CMI at NMSU. 
The students will receive the shelf "shelf_FDMA_2530.mel" and there will only be one button on it. In future updates I might add more tools. 
If there are any issues please contact:
 Alexander T. Santiago - github.com/atsantiago
 asanti89@nmsu.edu

 
 V1.0
 Only have CMI Modleing Checklist on shelf. (V2.0)
"""


import os
import sys
import urllib.request
import tempfile

# Update the following variables with your GitHub information:
repository_url = "https://github.com/Atsantiago/NMSU_Scripts"
script_path = "cmi_modeling_checklist.py"

# Check the Maya Python version
if sys.version_info.major == 2:
    # Python 2
    exec_function = execfile
else:
    # Python 3
    exec_function = exec

# Create a temporary directory to download the script
temp_dir = tempfile.mkdtemp()

# Download the script from GitHub
script_url = f"{repository_url}/raw/master/{script_path}"
script_file = os.path.join(temp_dir, os.path.basename(script_path))

urllib.request.urlretrieve(script_url, script_file)

# Source the script in Maya
maya_script_path = os.path.join(temp_dir, "cmi_modeling_checklist.py")

if os.path.isfile(maya_script_path):
    with open(maya_script_path, "r") as file:
        script_contents = file.read()
        exec_function(script_contents, globals())
else:
    print(f"Failed to locate the script: {maya_script_path}")
