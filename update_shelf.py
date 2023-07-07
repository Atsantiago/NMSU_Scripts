"""
This script should update the shelf FDMA_2530
"""
import os
import shutil
import urllib.request
import maya.cmds as cmds
import platform

# Update the following variables with your GitHub information:
repository_url = "https://github.com/Atsantiago/NMSU_Scripts"
script_path = "shelf_FDMA_2530.mel"

# Download the updated shelf script from GitHub
script_url = f"{repository_url}/raw/master/{script_path}"

# Determine the active version of Maya
maya_version = cmds.about(version=True)

# Determine the location of the default Downloads folder based on the operating system
system = platform.system()
if system == "Windows":
    default_downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
elif system == "Darwin":  # macOS
    default_downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
else:  # Linux
    default_downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

temp_script_file = os.path.join(default_downloads_folder, "temp_script.mel")

urllib.request.urlretrieve(script_url, temp_script_file)

# Determine the location of the existing shelf script in Maya based on the active version
if system == "Windows":
    mel_folder = os.path.join(os.environ["USERPROFILE"], "Documents", "maya", maya_version, "prefs", "shelves")
elif system == "Darwin":  # macOS
    mel_folder = os.path.join(os.path.expanduser("~"), "Library", "Preferences", "Autodesk", "maya", maya_version, "prefs", "shelves")
else:  # Linux
    mel_folder = os.path.join(os.path.expanduser("~"), "maya", maya_version, "prefs", "shelves")

existing_script_path = os.path.join(mel_folder, "shelf_FDMA_2530.mel")

# Check if the existing shelf script file exists
if not os.path.exists(existing_script_path):
    # Create an empty file
    with open(existing_script_path, "w") as file:
        pass

# Print the existing script path
print(existing_script_path)

# Compare the existing and updated script versions
is_updated = False

with open(temp_script_file, "r") as updated_file, open(existing_script_path, "r") as existing_file:
    updated_contents = updated_file.read()
    existing_contents = existing_file.read()

if updated_contents != existing_contents:
    is_updated = True
    # Replace the existing shelf script with the updated one
    shutil.move(temp_script_file, existing_script_path)
    # Modify the permissions of the new shelf script file
    os.chmod(existing_script_path, 0o755)
else:
    # Remove the temporary file
    os.remove(temp_script_file)

# Display a pop-up dialogue indicating if the shelf is up to date
if is_updated:
    cmds.confirmDialog(title="Shelf Update", message="Shelf has been updated.", button=["OK"], defaultButton="OK")
else:
    cmds.confirmDialog(title="Shelf Update", message="Shelf is up to date.", button=["OK"], defaultButton="OK")
