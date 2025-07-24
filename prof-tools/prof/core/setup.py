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
    
    def get_available_maya_preferences_dirs(self):
        """
        Get all Maya version preference directories (e.g., 2024, 2025)
        Returns:
            dict: Dictionary with maya versions as keys and path as value
                 e.g. {"2024": "C:/Users/.../Documents/maya/2024"}
        """
        maya_preferences_dir = self.get_maya_documents_path()
        
        if not os.path.exists(maya_preferences_dir):
            log_warning("Maya preferences directory not found: {}".format(maya_preferences_dir))
            return {}
        
        maya_folders = os.listdir(maya_preferences_dir)
        existing_folders = {}
        
        for folder in maya_folders:
            # Look for 4-digit year folders (2020, 2021, etc.)
            if folder.isdigit() and len(folder) == 4:
                full_path = os.path.join(maya_preferences_dir, folder)
                if os.path.isdir(full_path):
                    existing_folders[folder] = full_path
        
        if existing_folders:
            log_info("Found Maya versions: {}".format(", ".join(existing_folders.keys())))
        else:
            log_warning("No Maya version folders found in: {}".format(maya_preferences_dir))
        
        return existing_folders
    
    def get_maya_documents_path(self):
        """Get Maya documents base path (without version-specific subfolder)"""
        if self.is_windows or self.is_mac:
            return os.path.join(os.path.expanduser("~"), DOCUMENTS_FOLDER_NAME, MAYA_FOLDER_NAME)
        else:
            return os.path.join(os.path.expanduser("~"), MAYA_FOLDER_NAME)
    
    def get_installation_path(self):
        return os.path.join(self.get_maya_documents_path(), self.install_dir)
    
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
            
            # Load the menu immediately after installation
            try:
                if install_path not in sys.path:
                    sys.path.insert(0, install_path)
                from prof.ui import builder
                menu_result = builder.build_menu()
                if menu_result:
                    log_info("Prof-tools menu loaded immediately after installation")
                    menu_success = True
                else:
                    log_warning("Failed to load menu immediately, but installation completed")
                    menu_success = False
            except Exception as e:
                log_warning("Failed to load menu immediately: {}".format(e))
                menu_success = False
            
            log_info("Prof-tools installation completed successfully")
            if MAYA_AVAILABLE:
                if menu_success:
                    cmds.confirmDialog(
                        title="Installation Complete",
                        message="Prof-tools has been installed successfully!\n\nThe tools are now available in the menu bar.",
                        button=["OK"]
                    )
                else:
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
            else:
                log_warning("No installation directory found to remove: {}".format(install_path))
            
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
        """Update userSetup.mel files for ALL Maya versions"""
        maya_versions = self.get_available_maya_preferences_dirs()
        
        if not maya_versions:
            log_warning("No Maya versions found. Cannot create userSetup.mel entries.")
            return
        
        success_count = 0
        for version, version_path in maya_versions.items():
            try:
                scripts_dir = os.path.join(version_path, SCRIPTS_FOLDER_NAME)
                usersetup_path = os.path.join(scripts_dir, USERSETUP_FILE_NAME)
                
                # Create scripts directory if it doesn't exist
                if not os.path.exists(scripts_dir):
                    os.makedirs(scripts_dir)
                
                existing = ""
                if os.path.exists(usersetup_path):
                    with open(usersetup_path, 'r') as f:
                        existing = f.read()
                
                # Check if prof-tools entry already exists (avoid duplicates)
                prof_tools_comment = "// Prof-Tools Auto-Generated Entry"
                if self.entry_line not in existing and prof_tools_comment not in existing:
                    with open(usersetup_path, 'a') as f:
                        # Ensure proper line ending before adding our content
                        if existing and not existing.endswith('\n'):
                            f.write('\n')
                        # Add a blank line for better separation if file has content
                        if existing.strip():
                            f.write('\n')
                        f.write('// Prof-Tools Auto-Generated Entry\n')
                        f.write(self.entry_line + '\n')
                    log_info("Added prof-tools entry to Maya {} userSetup.mel".format(version))
                    success_count += 1
                else:
                    log_info("Prof-tools entry already exists in Maya {} userSetup.mel".format(version))
                    success_count += 1
                    
            except Exception as e:
                log_warning("Failed to update userSetup.mel for Maya {}: {}".format(version, e))
        
        if success_count > 0:
            log_info("Successfully updated userSetup.mel for {} Maya version(s)".format(success_count))
        else:
            log_error("Failed to update any userSetup.mel files")
    
    def _clean_usersetup_mel(self):
        """Clean userSetup.mel files from ALL Maya versions"""
        maya_versions = self.get_available_maya_preferences_dirs()
        
        if not maya_versions:
            log_warning("No Maya versions found for cleaning userSetup.mel files.")
            return
        
        success_count = 0
        for version, version_path in maya_versions.items():
            try:
                scripts_dir = os.path.join(version_path, SCRIPTS_FOLDER_NAME)
                usersetup_path = os.path.join(scripts_dir, USERSETUP_FILE_NAME)
                
                if self._clean_usersetup_file(usersetup_path):
                    log_info("Cleaned prof-tools entries from Maya {} userSetup.mel".format(version))
                    success_count += 1
                else:
                    log_info("No prof-tools entries found in Maya {} userSetup.mel".format(version))
                    
            except Exception as e:
                log_warning("Failed to clean userSetup.mel for Maya {}: {}".format(version, e))
        
        if success_count > 0:
            log_info("Successfully cleaned userSetup.mel for {} Maya version(s)".format(success_count))
        else:
            log_info("No prof-tools entries found to clean in any Maya versions")
    
    def _clean_usersetup_file(self, usersetup_path):
        """
        Clean a specific userSetup.mel file by removing only prof-tools entries.
        Preserves all other user content.
        Returns:
            bool: True if prof-tools entries were found and removed, False otherwise
        """
        if not os.path.exists(usersetup_path):
            return False
            
        try:
            with open(usersetup_path, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            log_error("Could not read userSetup.mel at {}: {}".format(usersetup_path, e))
            return False
        
        cleaned = []
        skip_next = False
        prof_tools_removed = False
        
        for line in lines:
            # If we marked the previous line to skip, skip this one too
            if skip_next:
                skip_next = False
                prof_tools_removed = True
                continue
            
            # Check for prof-tools comment marker
            if "Prof-Tools Auto-Generated Entry" in line:
                skip_next = True  # Skip the next line (the actual entry)
                prof_tools_removed = True
                continue
            
            # Check for direct prof-tools entry line (in case comment is missing)
            if self.entry_line.strip() in line.strip():
                prof_tools_removed = True
                continue
                
            # Keep all other lines
            cleaned.append(line)
        
        # Only write back if we actually removed something
        if prof_tools_removed:
            try:
                with open(usersetup_path, 'w') as f:
                    f.writelines(cleaned)
                return True
            except Exception as e:
                log_error("Could not write cleaned userSetup.mel at {}: {}".format(usersetup_path, e))
                return False
        else:
            return False

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
