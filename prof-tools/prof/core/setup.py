"""
Prof-Tools Setup and Installation Module
Handles installation, uninstallation, and run-only operations for prof-tools.
"""

# Python 2/3 compatibility imports
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
import shutil
import logging

# Try to import Maya modules (may not be available during installation)
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# Import prof-tools modules
try:
    from prof.core import (
        PACKAGE_NAME, PACKAGE_MAIN_MODULE, PACKAGE_ENTRY_LINE,
        INSTALL_DIRECTORY_NAME, INSTALL_PACKAGE_NAME,
        DOCUMENTS_FOLDER_NAME, MAYA_FOLDER_NAME, PREFS_FOLDER_NAME,
        SCRIPTS_FOLDER_NAME, USERSETUP_FILE_NAME,
        log_info, log_warning, log_error
    )
    from prof import __version__
except ImportError as e:
    # Fallback constants if imports fail
    PACKAGE_NAME = "prof-tools"
    PACKAGE_MAIN_MODULE = "prof"
    PACKAGE_ENTRY_LINE = 'python("import prof.ui.builder as _p; _p.build_menu()");'
    INSTALL_DIRECTORY_NAME = "prof-tools"
    INSTALL_PACKAGE_NAME = "prof"
    DOCUMENTS_FOLDER_NAME = "Documents"
    MAYA_FOLDER_NAME = "maya"
    PREFS_FOLDER_NAME = "prefs"
    SCRIPTS_FOLDER_NAME = "scripts"
    USERSETUP_FILE_NAME = "userSetup.mel"
    __version__ = "0.1.0"
    
    # Basic logging setup
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    
    def log_info(msg): logger.info(msg)
    def log_warning(msg): logger.warning(msg)
    def log_error(msg): logger.error(msg)

class ProfToolsSetup(object):
    """
    Main setup class for prof-tools installation and management.
    Follows GT-Tools patterns for cross-platform compatibility.
    """
    
    def __init__(self):
        """Initialize the setup class with default values"""
        self.package_name = PACKAGE_NAME
        self.main_module = PACKAGE_MAIN_MODULE
        self.entry_line = PACKAGE_ENTRY_LINE
        self.install_dir = INSTALL_DIRECTORY_NAME
        self.install_package = INSTALL_PACKAGE_NAME
        self.version = __version__
        
        # Platform detection
        self.platform = sys.platform
        self.is_windows = self.platform.startswith('win')
        self.is_mac = self.platform.startswith('darwin')
        self.is_linux = self.platform.startswith('linux')
        
        log_info("ProfToolsSetup initialized for platform: {}".format(self.platform))
    
    def get_maya_documents_path(self):
        """
        Get the Maya documents path for the current platform
        
        Returns:
            str: Path to Maya documents directory
        """
        if self.is_windows:
            documents_path = os.path.join(
                os.path.expanduser("~"), 
                DOCUMENTS_FOLDER_NAME, 
                MAYA_FOLDER_NAME
            )
        elif self.is_mac:
            documents_path = os.path.join(
                os.path.expanduser("~"), 
                DOCUMENTS_FOLDER_NAME, 
                MAYA_FOLDER_NAME
            )
        else:  # Linux
            documents_path = os.path.join(
                os.path.expanduser("~"), 
                MAYA_FOLDER_NAME
            )
        
        return documents_path
    
    def get_installation_path(self):
        """
        Get the full installation path for prof-tools
        
        Returns:
            str: Full installation path
        """
        maya_docs = self.get_maya_documents_path()
        return os.path.join(maya_docs, self.install_dir)
    
    def get_usersetup_path(self):
        """
        Get the path to the userSetup.mel file
        
        Returns:
            str: Path to userSetup.mel file
        """
        maya_docs = self.get_maya_documents_path()
        prefs_path = os.path.join(maya_docs, PREFS_FOLDER_NAME)
        scripts_path = os.path.join(prefs_path, SCRIPTS_FOLDER_NAME)
        return os.path.join(scripts_path, USERSETUP_FILE_NAME)
    
    def install_package(self):
        """
        Install prof-tools package to Maya environment
        
        Returns:
            bool: True if installation successful, False otherwise
        """
        try:
            log_info("Starting prof-tools installation...")
            
            # Get source and destination paths
            source_path = self._get_source_path()
            install_path = self.get_installation_path()
            
            log_info("Source path: {}".format(source_path))
            log_info("Install path: {}".format(install_path))
            
            # Create installation directory if it doesn't exist
            os.makedirs(install_path, exist_ok=True)
            
            # Copy package files
            self._copy_package_files(source_path, install_path)
            
            # Update userSetup.mel
            self._update_usersetup_mel()
            
            log_info("Prof-tools installation completed successfully")
            
            if MAYA_AVAILABLE:
                cmds.confirmDialog(
                    title="Installation Complete",
                    message="Prof-tools has been installed successfully!\n\nPlease restart Maya to see the tools in the menu.",
                    button=["OK"]
                )
            
            return True
            
        except Exception as e:
            error_msg = "Installation failed: {}".format(str(e))
            log_error(error_msg)
            
            if MAYA_AVAILABLE:
                cmds.confirmDialog(
                    title="Installation Error", 
                    message=error_msg,
                    button=["OK"]
                )
            
            return False
    
    def uninstall_package(self):
        """
        Uninstall prof-tools package from Maya environment
        
        Returns:
            bool: True if uninstallation successful, False otherwise
        """
        try:
            log_info("Starting prof-tools uninstallation...")
            
            # Remove installation directory
            install_path = self.get_installation_path()
            if os.path.exists(install_path):
                shutil.rmtree(install_path)
                log_info("Removed installation directory: {}".format(install_path))
            
            # Clean userSetup.mel
            self._clean_usersetup_mel()
            
            log_info("Prof-tools uninstallation completed successfully")
            
            if MAYA_AVAILABLE:
                cmds.confirmDialog(
                    title="Uninstallation Complete",
                    message="Prof-tools has been uninstalled successfully!\n\nPlease restart Maya to complete the removal.",
                    button=["OK"]
                )
            
            return True
            
        except Exception as e:
            error_msg = "Uninstallation failed: {}".format(str(e))
            log_error(error_msg)
            
            if MAYA_AVAILABLE:
                cmds.confirmDialog(
                    title="Uninstallation Error",
                    message=error_msg,
                    button=["OK"]
                )
            
            return False
    
    def run_only(self):
        """
        Run prof-tools without installation (temporary mode)
        
        Returns:
            bool: True if run successful, False otherwise
        """
        try:
            log_info("Running prof-tools in temporary mode...")
            
            # Add current directory to Python path
            source_path = self._get_source_path()
            if source_path not in sys.path:
                sys.path.insert(0, source_path)
            
            # Import and run the menu builder
            from prof.ui import builder
            result = builder.build_menu()
            
            if result:
                log_info("Prof-tools menu created successfully in temporary mode")
                if MAYA_AVAILABLE:
                    cmds.confirmDialog(
                        title="Run Only Mode",
                        message="Prof-tools is now running in temporary mode!\n\nThe tools will be available until Maya is closed.",
                        button=["OK"]
                    )
                return True
            else:
                raise Exception("Failed to create menu")
                
        except Exception as e:
            error_msg = "Run Only mode failed: {}".format(str(e))
            log_error(error_msg)
            
            if MAYA_AVAILABLE:
                cmds.confirmDialog(
                    title="Run Only Error",
                    message=error_msg,
                    button=["OK"]
                )
            
            return False
    
    def _get_source_path(self):
        """
        Get the source path of the prof-tools package
        
        Returns:
            str: Path to the source prof-tools directory
        """
        # Get the directory containing this file
        current_file = os.path.abspath(__file__)
        # Go up two levels: prof/core/setup.py -> prof-tools/
        return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    
    def _copy_package_files(self, source_path, install_path):
        """
        Copy package files from source to installation directory
        
        Args:
            source_path (str): Source directory path
            install_path (str): Installation directory path
        """
        prof_source = os.path.join(source_path, self.install_package)
        prof_dest = os.path.join(install_path, self.install_package)
        
        if os.path.exists(prof_dest):
            shutil.rmtree(prof_dest)
        
        shutil.copytree(prof_source, prof_dest)
        log_info("Copied package files from {} to {}".format(prof_source, prof_dest))
    
    def _update_usersetup_mel(self):
        """
        Update userSetup.mel file with prof-tools entry line
        """
        usersetup_path = self.get_usersetup_path()
        
        # Create scripts directory if it doesn't exist
        scripts_dir = os.path.dirname(usersetup_path)
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Read existing content
        existing_content = ""
        if os.path.exists(usersetup_path):
            with open(usersetup_path, 'r') as f:
                existing_content = f.read()
        
        # Add entry line if not already present
        if self.entry_line not in existing_content:
            with open(usersetup_path, 'a') as f:
                if existing_content and not existing_content.endswith('\n'):
                    f.write('\n')
                f.write('// Prof-Tools Auto-Generated Entry\n')
                f.write(self.entry_line + '\n')
            
            log_info("Updated userSetup.mel with prof-tools entry")
    
    def _clean_usersetup_mel(self):
        """
        Remove prof-tools entry from userSetup.mel file
        """
        usersetup_path = self.get_usersetup_path()
        
        if not os.path.exists(usersetup_path):
            return
        
        # Read existing content
        with open(usersetup_path, 'r') as f:
            lines = f.readlines()
        
        # Remove prof-tools related lines
        cleaned_lines = []
        skip_next = False
        
        for line in lines:
            if skip_next:
                skip_next = False
                continue
            
            if "Prof-Tools Auto-Generated Entry" in line:
                skip_next = True
                continue
            
            if self.entry_line.strip() in line.strip():
                continue
            
            cleaned_lines.append(line)
        
        # Write cleaned content
        with open(usersetup_path, 'w') as f:
            f.writelines(cleaned_lines)
        
        log_info("Cleaned userSetup.mel of prof-tools entries")

def launcher_entry_point():
    """
    Entry point for the drag-and-drop installer launcher
    This function will be called from setup_drag_drop_maya.py
    """
    try:
        # Create setup GUI (will be implemented in future)
        setup_instance = ProfToolsSetup()
        
        # For now, show a simple dialog to select operation
        if MAYA_AVAILABLE:
            result = cmds.confirmDialog(
                title="Prof-Tools Setup",
                message="Choose installation option:",
                button=["Install", "Uninstall", "Run Only", "Cancel"],
                defaultButton="Install",
                cancelButton="Cancel",
                dismissString="Cancel"
            )
            
            if result == "Install":
                setup_instance.install_package()
            elif result == "Uninstall":
                setup_instance.uninstall_package()
            elif result == "Run Only":
                setup_instance.run_only()
        else:
            print("Maya not available. Setup operations require Maya environment.")
            
    except Exception as e:
        error_msg = "Setup launcher failed: {}".format(str(e))
        log_error(error_msg)
        if MAYA_AVAILABLE:
            cmds.confirmDialog(
                title="Setup Error",
                message=error_msg,
                button=["OK"]
            )

# For testing purposes
if __name__ == "__main__":
    setup = ProfToolsSetup()
    print("Prof-Tools Setup initialized")
    print("Platform: {}".format(setup.platform))
    print("Maya docs path: {}".format(setup.get_maya_documents_path()))
    print("Install path: {}".format(setup.get_installation_path()))
