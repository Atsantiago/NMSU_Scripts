"""
Prof-Tools Drag-and-Drop Installer
Main entry point for prof-tools installation. Users drag this file onto Maya's viewport
to install, uninstall, or run prof-tools in temporary mode.

This installer provides three options:
- Install: Permanent installation with userSetup.mel integration
- Uninstall: Complete removal of prof-tools from Maya
- Run Only: Temporary mode without file copying

Cross-platform compatible for Windows, macOS, and Linux.
"""

# Python 2/3 compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import logging

# Configure logging
logging.basicConfig()
logger = logging.getLogger("prof_tools_installer")
logger.setLevel(logging.INFO)

def onMayaDroppedPythonFile(*args):
    """
    Main entry point called by Maya when this file is dropped onto the viewport.
    This function is automatically called by Maya's drag-and-drop system.
    
    Args:
        *args: Arguments passed by Maya (usually empty)
    """
    try:
        logger.info("Prof-Tools drag-and-drop installer started")
        
        # Python version compatibility check
        if not _check_python_compatibility():
            return
        
        # Maya environment check
        if not _check_maya_environment():
            return
        
        # Clean up any existing prof-tools modules from memory
        _cleanup_loaded_modules()
        
        # Add current directory to Python path for imports
        _setup_python_path()
        
        # Launch the main installer interface
        _launch_installer()
        
    except Exception as e:
        error_msg = "Prof-Tools installer failed to start: {}".format(str(e))
        logger.error(error_msg)
        _show_error_dialog("Installer Error", error_msg)

def _check_python_compatibility():
    """
    Checks if the current Python version is compatible with prof-tools.
    
    Returns:
        bool: True if compatible, False otherwise
    """
    try:
        if sys.version_info.major < 3:
            user_version = "{}.{}.{}".format(
                sys.version_info.major,
                sys.version_info.minor, 
                sys.version_info.micro
            )
            error_msg = "Python Version Incompatibility Detected\n\n"
            error_msg += "Prof-Tools requires Python 3.x\n"
            error_msg += "Current version: {}\n\n".format(user_version)
            error_msg += "Please use Maya 2020 or later for Python 3 support."
            
            logger.error(error_msg)
            _show_error_dialog("Python Version Error", error_msg)
            return False
        
        logger.info("Python version check passed: {}.{}.{}".format(
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro
        ))
        return True
        
    except Exception as e:
        logger.error("Python compatibility check failed: {}".format(str(e)))
        return False

def _check_maya_environment():
    """
    Checks if Maya is available and properly configured.
    
    Returns:
        bool: True if Maya is available, False otherwise
    """
    try:
        import maya.cmds as cmds
        import maya.mel as mel
        
        # Test Maya functionality
        maya_version = cmds.about(version=True)
        logger.info("Maya version detected: {}".format(maya_version))
        
        # Test if we can access Maya's main window
        try:
            main_window = mel.eval('global string $gMainWindow; $tmp = $gMainWindow;')
            if not main_window:
                raise Exception("Maya main window not available")
        except Exception as e:
            logger.warning("Maya UI may not be fully available: {}".format(str(e)))
        
        return True
        
    except ImportError as e:
        error_msg = "Maya Python modules not available\n\n"
        error_msg += "This installer must be run from within Maya.\n"
        error_msg += "Please drag this file onto Maya's viewport."
        
        logger.error(error_msg)
        print(error_msg)  # Print to console since Maya may not be available
        return False
        
    except Exception as e:
        error_msg = "Maya environment check failed: {}".format(str(e))
        logger.error(error_msg)
        _show_error_dialog("Maya Environment Error", error_msg)
        return False

def _cleanup_loaded_modules():
    """
    Removes any existing prof-tools modules from sys.modules to ensure fresh imports.
    This prevents caching issues when updating prof-tools.
    """
    try:
        modules_to_remove = []
        
        # Find all prof-tools related modules
        for module_name in sys.modules.keys():
            if module_name.startswith('prof'):
                modules_to_remove.append(module_name)
        
        # Remove the modules
        for module_name in modules_to_remove:
            try:
                del sys.modules[module_name]
                logger.debug("Removed cached module: {}".format(module_name))
            except Exception as e:
                logger.warning("Failed to remove cached module '{}': {}".format(module_name, str(e)))
        
        if modules_to_remove:
            logger.info("Cleaned up {} cached prof-tools modules".format(len(modules_to_remove)))
        
    except Exception as e:
        logger.warning("Module cleanup failed: {}".format(str(e)))

def _setup_python_path():
    """
    Adds the current directory and prof package to Python path for imports.
    """
    try:
        # Get the directory containing this installer file
        installer_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Add installer directory to Python path
        if installer_dir not in sys.path:
            sys.path.insert(0, installer_dir)
            logger.debug("Added installer directory to Python path: {}".format(installer_dir))
        
        # Add prof package directory to Python path
        prof_dir = os.path.join(installer_dir, 'prof')
        if os.path.exists(prof_dir) and prof_dir not in sys.path:
            sys.path.insert(0, prof_dir)
            logger.debug("Added prof package directory to Python path: {}".format(prof_dir))
        
    except Exception as e:
        logger.error("Failed to setup Python path: {}".format(str(e)))
        raise

def _launch_installer():
    """
    Launches the main installer interface by importing and calling the setup module.
    """
    try:
        # Import the setup module
        from prof.core.setup import launcher_entry_point
        
        # Launch the installer interface
        launcher_entry_point()
        
        logger.info("Prof-Tools installer interface launched successfully")
        
    except ImportError as e:
        error_msg = "Failed to import prof-tools setup module\n\n"
        error_msg += "Please ensure the prof-tools package is complete.\n"
        error_msg += "Error: {}".format(str(e))
        
        logger.error(error_msg)
        _show_error_dialog("Import Error", error_msg)
        
    except Exception as e:
        error_msg = "Failed to launch installer interface: {}".format(str(e))
        logger.error(error_msg)
        _show_error_dialog("Installer Launch Error", error_msg)

def _show_error_dialog(title, message):
    """
    Shows an error dialog to the user if Maya is available.
    
    Args:
        title (str): Dialog title
        message (str): Error message to display
    """
    try:
        import maya.cmds as cmds
        cmds.confirmDialog(
            title=title,
            message=message,
            button=["OK"],
            defaultButton="OK"
        )
    except Exception:
        # If Maya dialog fails, print to console
        print("ERROR - {}: {}".format(title, message))

def _show_info_dialog(title, message):
    """
    Shows an info dialog to the user if Maya is available.
    
    Args:
        title (str): Dialog title
        message (str): Info message to display
    """
    try:
        import maya.cmds as cmds
        cmds.confirmDialog(
            title=title,
            message=message,
            button=["OK"],
            defaultButton="OK"
        )
    except Exception:
        # If Maya dialog fails, print to console
        print("INFO - {}: {}".format(title, message))

def get_installer_info():
    """
    Returns information about this installer for debugging purposes.
    
    Returns:
        dict: Dictionary containing installer information
    """
    return {
        'installer_file': __file__,
        'installer_dir': os.path.dirname(os.path.abspath(__file__)),
        'python_version': sys.version,
        'platform': sys.platform
    }

# For testing and debugging
def main():
    """
    Main function for testing the installer outside of Maya's drag-and-drop system.
    This function can be called directly for debugging purposes.
    """
    print("Prof-Tools Installer Test")
    print("=" * 40)
    
    # Display installer information
    info = get_installer_info()
    for key, value in info.items():
        print("{}: {}".format(key, value))
    
    print("\nNote: This installer is designed to be dragged onto Maya's viewport.")
    print("To test the full functionality, please use Maya's drag-and-drop system.")

if __name__ == "__main__":
    main()
