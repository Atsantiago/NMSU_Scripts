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

# Import prof-tools modules - centralized versioning from prof/__init__.py
try:
    from prof.core import (
        PACKAGE_NAME, PACKAGE_MAIN_MODULE, PACKAGE_ENTRY_LINE,
        INSTALL_DIRECTORY_NAME, INSTALL_PACKAGE_NAME,
        DOCUMENTS_FOLDER_NAME, MAYA_FOLDER_NAME, PREFS_FOLDER_NAME,
        SCRIPTS_FOLDER_NAME, USERSETUP_FILE_NAME,
        log_info, log_warning, log_error
    )
    # Import version from single source of truth
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
    # Fallback version
    __version__ = "0.1.0"
    
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    
    def log_info(msg): logger.info(msg)
    def log_warning(msg): logger.warning(msg)
    def log_error(msg): logger.error(msg)
    
    log_warning("Using fallback constants due to import error: {}".format(str(e)))

class ProfToolsSetup(object):
    """
    Main setup class for prof-tools installation and management.
    """
    
    def __init__(self):
        self.package_name = PACKAGE_NAME
        self.main_module = PACKAGE_MAIN_MODULE
        self.entry_line = PACKAGE_ENTRY_LINE
        self.install_dir = INSTALL_DIRECTORY_NAME
        self.install_package_name = INSTALL_PACKAGE_NAME  # Renamed to avoid conflict with install_package method
        # Use centralized version from prof/__init__.py
        self.version = __version__
        
        self.platform = sys.platform
        self.is_windows = self.platform.startswith('win')
        self.is_mac = self.platform.startswith('darwin')
        self.is_linux = self.platform.startswith('linux')
        
        log_info("ProfToolsSetup initialized for platform: {}".format(self.platform))
    
    def get_maya_documents_path(self):
        if self.is_windows or self.is_mac:
            return os.path.join(os.path.expanduser("~"), DOCUMENTS_FOLDER_NAME, MAYA_FOLDER_NAME)
        else:
            return os.path.join(os.path.expanduser("~"), MAYA_FOLDER_NAME)
    
    def get_installation_path(self):
        return os.path.join(self.get_maya_documents_path(), self.install_dir)
    
    def get_usersetup_path(self):
        maya_docs = self.get_maya_documents_path()
        return os.path.join(maya_docs, PREFS_FOLDER_NAME, SCRIPTS_FOLDER_NAME, USERSETUP_FILE_NAME)
    
    def install_package(self):
        try:
            log_info("Starting prof-tools installation...")
            source_path = self._get_source_path()
            install_path = self.get_installation_path()
            
            log_info("Source path: {}".format(source_path))
            log_info("Install path: {}".format(install_path))
            
            # Create installation directory (compatible with older Python versions)
            if not os.path.exists(install_path):
                os.makedirs(install_path)
            
            self._copy_package_files(source_path, install_path)
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
            error_msg = "Installation failed: {}".format(e)
            log_error(error_msg)
            if MAYA_AVAILABLE:
                cmds.confirmDialog(title="Installation Error", message=error_msg, button=["OK"])
            return False
    
    def uninstall_package(self):
        try:
            log_info("Starting prof-tools uninstallation...")
            
            # Remove installation directory
            install_path = self.get_installation_path()
            if os.path.exists(install_path):
                shutil.rmtree(install_path)
                log_info("Removed installation directory: {}".format(install_path))
            
            # Clean userSetup.mel
            self._clean_usersetup_mel()
            
            # Remove Prof-Tools menu from Maya UI
            try:
                if MAYA_AVAILABLE:
                    top = mel.eval('global string $gMainWindow; $tmp = $gMainWindow;')
                    if cmds.menu("ProfTools", exists=True):
                        cmds.deleteUI("ProfTools")
                        log_info("Deleted Prof-Tools menu from Maya UI")
            except Exception:
                pass
            
            log_info("Prof-tools uninstallation completed successfully")
            if MAYA_AVAILABLE:
                cmds.confirmDialog(
                    title="Uninstallation Complete",
                    message="Prof-tools has been uninstalled successfully!\n\nPlease restart Maya to complete the removal.",
                    button=["OK"]
                )
            return True
            
        except Exception as e:
            error_msg = "Uninstallation failed: {}".format(e)
            log_error(error_msg)
            if MAYA_AVAILABLE:
                cmds.confirmDialog(title="Uninstallation Error", message=error_msg, button=["OK"])
            return False
    
    def run_only(self):
        """
        Run prof-tools without installation (temporary mode)
        """
        try:
            log_info("Running prof-tools in temporary mode...")
            source_path = self._get_source_path()
            if source_path not in sys.path:
                sys.path.insert(0, source_path)
            from prof.ui import builder
            result = builder.build_menu()  # now returns True
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
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    def _copy_package_files(self, source_path, install_path):
        prof_source = os.path.join(source_path, self.install_package_name)
        prof_dest = os.path.join(install_path, self.install_package_name)
        if os.path.exists(prof_dest):
            shutil.rmtree(prof_dest)
        shutil.copytree(prof_source, prof_dest)
        log_info("Copied package files from {} to {}".format(prof_source, prof_dest))
    
    def _update_usersetup_mel(self):
        usersetup_path = self.get_usersetup_path()
        scripts_dir = os.path.dirname(usersetup_path)
        
        # Create scripts directory if it doesn't exist (compatible with older Python)
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        
        existing = ""
        if os.path.exists(usersetup_path):
            with open(usersetup_path, 'r') as f:
                existing = f.read()
        
        if self.entry_line not in existing:
            with open(usersetup_path, 'a') as f:
                if existing and not existing.endswith('\n'):
                    f.write('\n')
                f.write('// Prof-Tools Auto-Generated Entry\n')
                f.write(self.entry_line + '\n')
            log_info("Updated userSetup.mel with prof-tools entry")
    
    def _clean_usersetup_mel(self):
        usersetup_path = self.get_usersetup_path()
        if not os.path.exists(usersetup_path):
            return
        with open(usersetup_path, 'r') as f:
            lines = f.readlines()
        cleaned = []
        skip = False
        for line in lines:
            if skip:
                skip = False
                continue
            if "Prof-Tools Auto-Generated Entry" in line:
                skip = True
                continue
            if self.entry_line.strip() in line.strip():
                continue
            cleaned.append(line)
        with open(usersetup_path, 'w') as f:
            f.writelines(cleaned)
        log_info("Cleaned userSetup.mel of prof-tools entries")

def launcher_entry_point():
    """
    Entry point for the drag-and-drop installer launcher.
    """
    try:
        # Add debug logging to identify where the error occurs
        log_info("Creating ProfToolsSetup instance...")
        setup_instance = ProfToolsSetup()
        log_info("ProfToolsSetup instance created successfully")
        
        # Verify that required methods exist and are callable
        required_methods = ['install_package', 'uninstall_package', 'run_only']
        for method_name in required_methods:
            if not hasattr(setup_instance, method_name):
                raise AttributeError("Required method '{}' not found on ProfToolsSetup instance".format(method_name))
            method = getattr(setup_instance, method_name)
            if not callable(method):
                raise AttributeError("Method '{}' exists but is not callable. Type: {}".format(method_name, type(method)))
        
        log_info("All required methods verified as callable")
        
        if MAYA_AVAILABLE:
            log_info("Maya available, showing dialog...")
            result = cmds.confirmDialog(
                title="Prof-Tools Setup",
                message="Choose installation option:",
                button=["Install", "Uninstall", "Run Only", "Cancel"],
                defaultButton="Install",
                cancelButton="Cancel",
                dismissString="Cancel"
            )
            log_info("Dialog result: {}".format(result))
            
            if result == "Install":
                log_info("Calling install_package method...")
                setup_instance.install_package()
            elif result == "Uninstall":
                log_info("Calling uninstall_package method...")
                setup_instance.uninstall_package()
            elif result == "Run Only":
                log_info("Calling run_only method...")
                setup_instance.run_only()
        else:
            print("Maya not available. Setup operations require Maya environment.")
    except Exception as e:
        error_msg = "Setup launcher failed: {}".format(e)
        log_error(error_msg)
        import traceback
        log_error("Full traceback: {}".format(traceback.format_exc()))
        if MAYA_AVAILABLE:
            try:
                cmds.confirmDialog(title="Setup Error", message=error_msg, button=["OK"])
            except Exception:
                print("Error: {}".format(error_msg))

if __name__ == "__main__":
    setup = ProfToolsSetup()
    print("Prof-Tools Setup initialized")
    print("Platform: {}".format(setup.platform))
    print("Maya docs path: {}".format(setup.get_maya_documents_path()))
    print("Install path: {}".format(setup.get_installation_path()))
