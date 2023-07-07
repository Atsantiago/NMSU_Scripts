"""
Created by Alexander T. Santiago - github.com/atsantiago
This script should update the shelf FDMA_2530.
"""
import os
import sys
import urllib.request
import tempfile
import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets
import shutil

# Update the following variables with your GitHub information:
repository_url = "https://github.com/Atsantiago/NMSU_Scripts"
updated_script_path = "shelf_FDMA_2530.mel"

# Check the Maya Python version
if sys.version_info.major == 2:
    # Python 2
    exec_function = execfile
else:
    # Python 3
    exec_function = exec

# Create a temporary directory to download the script
temp_dir = tempfile.mkdtemp()

# Download the updated shelf script from GitHub
updated_script_url = f"{repository_url}/raw/master/{updated_script_path}"
updated_script_file = os.path.join(temp_dir, os.path.basename(updated_script_path))

urllib.request.urlretrieve(updated_script_url, updated_script_file)

# Prompt the user to locate the current shelf MEL file or cancel the update
msg_box = QtWidgets.QMessageBox()
msg_box.setWindowTitle("Shelf Update")
msg_box.setText("To update the shelf script, please locate the current shelf script file or cancel the update.")
msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
msg_box.setDefaultButton(QtWidgets.QMessageBox.Ok)
msg_box.setEscapeButton(QtWidgets.QMessageBox.Cancel)
ret = msg_box.exec_()

if ret == QtWidgets.QMessageBox.Ok:
    while True:
        # Prompt the user to locate the current shelf MEL file
        dialog = QtWidgets.QFileDialog()
        dialog.setWindowTitle("Select Current Shelf MEL File")
        dialog.setDirectory(cmds.internalVar(userShelfDir=True))
        dialog.setNameFilter("Shelf MEL Files (*.mel)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_():
            selected_files = dialog.selectedFiles()
            if selected_files:
                current_script_file = selected_files[0]
                selected_shelf_name = os.path.splitext(os.path.basename(current_script_file))[0]
                if selected_shelf_name == "shelf_FDMA_2530":
                    break
                else:
                    confirm_msg_box = QtWidgets.QMessageBox()
                    confirm_msg_box.setWindowTitle("Shelf Verification")
                    confirm_msg_box.setText("The selected shelf script does not match the expected shelf script name (shelf_FDMA_2530).\n\nPlease verify the selection or cancel the update.")
                    confirm_msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                    confirm_msg_box.setDefaultButton(QtWidgets.QMessageBox.Ok)
                    confirm_msg_box.setEscapeButton(QtWidgets.QMessageBox.Cancel)
                    confirm_ret = confirm_msg_box.exec_()
                    if confirm_ret == QtWidgets.QMessageBox.Cancel:
                        print("Shelf update operation cancelled.")
                        sys.exit(0)  # Exit the script if operation is cancelled
            else:
                print("Shelf update operation cancelled.")
                sys.exit(0)  # Exit the script if operation is cancelled
        else:
            print("Shelf update operation cancelled.")
            sys.exit(0)  # Exit the script if operation is cancelled
else:
    print("Shelf update operation cancelled.")
    sys.exit(0)  # Exit the script if operation is cancelled

# Compare the downloaded script with the current shelf MEL file
with open(updated_script_file, "r") as updated_file, open(current_script_file, "r") as current_file:
    updated_contents = updated_file.read()
    current_contents = current_file.read()

if updated_contents != current_contents:
    # Create a backup of the existing shelf
    backup_file = current_script_file + ".bak"
    shutil.copy(current_script_file, backup_file)

    # Overwrite the current shelf MEL file with the downloaded script
    shutil.copy(updated_script_file, current_script_file)
    print("Shelf updated successfully!")
    QtWidgets.QMessageBox.information(None, "Shelf Update", "Shelf updated successfully!")
else:
    print("Shelf is up to date.")
    QtWidgets.QMessageBox.information(None, "Shelf Update", "Shelf is up to date.")

# Reload the shelf
shelf_name = "FDMA_2530"  # Specify the name of the shelf to update

# Check if the shelf exists
if cmds.shelfLayout(shelf_name, exists=True):
    cmds.deleteUI(shelf_name, layout=True)

# Load the updated shelf into Maya
updated_shelf_path = current_script_file.replace("\\", "/")
mel.eval(f'loadNewShelf "{updated_shelf_path}"')

# Check if the shelf was successfully reloaded
if cmds.shelfLayout(shelf_name, exists=True):
    print("Shelf reloaded successfully!")
else:
    if os.path.isfile(backup_file):
        # Restore the backup
        backup_file_without_extension = backup_file[:-4]
        shutil.copy(backup_file, current_script_file)
        print("An error occurred during the update. Shelf restored from backup.")
        # Load the original shelf from the backup
        mel.eval(f'source "{backup_file_without_extension}"')
        if cmds.shelfLayout(shelf_name, exists=True):
            print("Original shelf restored successfully!")
        else:
            print("Failed to restore the original shelf.")
    else:
        print("An error occurred during the update. Unable to restore the shelf.")

# Remove the backup file
if os.path.isfile(backup_file):
    os.remove(backup_file)

# Remove the temporary directory
shutil.rmtree(temp_dir)
