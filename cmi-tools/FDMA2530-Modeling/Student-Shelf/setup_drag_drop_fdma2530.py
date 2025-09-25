"""
CMI Tools - FDMA 2530 Shelf Installer
=====================================================

Drag-and-drop script that installs or loads the FDMA 2530 student
shelf.  Key features:

• Downloads the repository as a ZIP (fast, no git required).  
• Copies `fdma_shelf`, `shelf_config.json`, **and `releases.json`**  
  so version_utils can find the manifest.  
• Reads `current_version` from the manifest - no hard-coded numbers.  
• Creates a Maya `.mod` file so the shelf auto-loads.  
• Works on Windows / macOS / Linux, Maya 2016-2025, Py 2/3.  

Author:  Alexander T. Santiago   •   asanti89@nmsu.edu
"""

from __future__ import absolute_import, print_function

import json
import logging
import os
import shutil
import sys
import tempfile
import zipfile

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen

import maya.cmds as cmds
import maya.mel as mel

# ---------------------------------------------------------------------------
# Configuration / constants
# ---------------------------------------------------------------------------

REPO_ZIP_URL = (
    "https://github.com/Atsantiago/NMSU_Scripts/archive/refs/heads/master.zip"
)
MODULE_NAME = "cmi-tools"
SHELF_NAME = "FDMA_2530"
FALLBACK_VERSION = "2.0.1"

# CMI Tools directory structure (similar to prof-tools but separate)
CMI_TOOLS_DIR = "cmi-tools"  # Main directory name in Maya root

# Directory Structure:
# ~/maya/                    # Maya root directory (version-independent)
#   ├── modules/              # Maya modules directory  
#   │   └── cmi-tools.mod     # Module file that tells Maya about cmi-tools
#   └── cmi-tools/            # Main cmi-tools installation
#       └── scripts/          # Python scripts directory
#           ├── fdma_shelf/   # FDMA 2530 shelf package
#           ├── shelf_config.json
#           └── releases.json # Version manifest

# Will be filled after the manifest is read
CURRENT_VERSION = FALLBACK_VERSION

# Logging
logging.basicConfig()
LOG = logging.getLogger("fdma2530_installer")
LOG.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Helper paths
# ---------------------------------------------------------------------------

def get_platform():
    """Detect the current operating system platform."""
    import platform
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def get_platform_maya_root():
    """Get platform-specific Maya root directory where user data is stored."""
    import os.path
    platform_name = get_platform()
    home_dir = os.path.expanduser("~")
    
    if platform_name == "windows":
        # Windows: ~/Documents/maya/
        return os.path.normpath(os.path.join(home_dir, "Documents", "maya"))
    elif platform_name == "macos":
        # macOS: ~/Library/Preferences/Autodesk/maya/
        return os.path.normpath(os.path.join(home_dir, "Library", "Preferences", "Autodesk", "maya"))
    elif platform_name == "linux":
        # Linux: ~/maya/
        return os.path.normpath(os.path.join(home_dir, "maya"))
    else:
        # Unknown platform, default to Linux-style
        LOG.warning("Unknown platform '%s', using Linux-style paths", platform_name)
        return os.path.normpath(os.path.join(home_dir, "maya"))

def get_maya_app_dir():
    """Return Maya's *user* application directory (~/maya/20xx/)."""  
    return cmds.internalVar(userAppDir=True)

def get_maya_root():
    """Find Maya's main directory with comprehensive cross-platform support."""
    import os.path
    
    platform_name = get_platform()
    maya_app_dir = get_maya_app_dir()
    LOG.info("Platform: %s", platform_name.upper())
    LOG.info("Maya userAppDir detected: %s", maya_app_dir)
    
    # Try to extract Maya root from the current Maya app directory
    maya_app_norm = os.path.normpath(maya_app_dir)
    path_parts = maya_app_norm.split(os.sep)
    
    # Look for 'maya' directory in the path
    maya_index = -1
    for i, part in enumerate(path_parts):
        if part.lower() == "maya":
            maya_index = i
            break
    
    if maya_index >= 0:
        # Found 'maya' in path - reconstruct path up to and including 'maya'
        maya_root_parts = path_parts[:maya_index + 1]
        maya_root = os.path.normpath(os.sep.join(maya_root_parts))
        LOG.info("Extracted Maya root from userAppDir: %s", maya_root)
        return maya_root
    
    # Maya directory not found in path - use platform-specific detection
    platform_maya_root = get_platform_maya_root()
    LOG.info("Using platform-specific Maya root: %s", platform_maya_root)
    
    # Verify this makes sense by checking if it's a reasonable parent of maya_app_dir
    try:
        # Check if maya_app_dir is a subdirectory of our platform root
        common_path = os.path.commonpath([platform_maya_root, maya_app_norm])
        if os.path.normpath(common_path) == os.path.normpath(platform_maya_root):
            LOG.info("Platform Maya root verified against userAppDir")
            return platform_maya_root
    except (ValueError, TypeError):
        # Paths are on different drives or incompatible
        pass
    
    # Final fallback - try to infer from maya_app_dir structure
    # Go up directories until we find a reasonable Maya root
    current_dir = os.path.dirname(maya_app_norm)
    max_levels = 3  # Don't go too far up the directory tree
    
    for level in range(max_levels):
        if not current_dir or current_dir == os.path.dirname(current_dir):
            break  # Reached filesystem root
        
        # Check if this directory name suggests it's a Maya root
        dir_name = os.path.basename(current_dir).lower()
        if dir_name in ("maya", "autodesk", "preferences"):
            maya_root = current_dir
            if dir_name != "maya":
                # If we're in Autodesk or Preferences, add maya subdirectory
                maya_root = os.path.join(current_dir, "maya")
            LOG.info("Inferred Maya root from directory structure: %s", maya_root)
            return os.path.normpath(maya_root)
        
        current_dir = os.path.dirname(current_dir)
    
    # Last resort - use platform default
    LOG.warning("Could not infer Maya root, using platform default: %s", platform_maya_root)
    return platform_maya_root

def get_cmi_root():
    """cmi-tools installation root in Maya's main directory."""
    maya_root = get_maya_root()
    cmi_root = os.path.normpath(os.path.join(maya_root, CMI_TOOLS_DIR))
    LOG.info("CMI Tools will be installed to: %s", cmi_root)
    return cmi_root

def get_modules_dir():
    """Maya modules folder in root directory (version-independent); create it if missing."""
    maya_root = get_maya_root()
    
    # Ensure Maya root directory exists first
    if not os.path.exists(maya_root):
        os.makedirs(maya_root)
        LOG.info("Created Maya root directory: %s", maya_root)
    
    # Create modules directory
    modules_path = os.path.normpath(os.path.join(maya_root, "modules"))
    if not os.path.exists(modules_path):
        os.makedirs(modules_path)
        LOG.info("Created modules directory: %s", modules_path)
    else:
        LOG.info("Using existing modules directory: %s", modules_path)
    
    return modules_path

# ---------------------------------------------------------------------------
# Progress feedback system
# ---------------------------------------------------------------------------

class SimpleProgressWindow(object):
    """Simple progress feedback window for installations."""
    
    def __init__(self, title="CMI Tools Progress"):
        self.window_name = "cmiToolsProgress"
        self.title = title
        self.current_step = 0
        self.total_steps = 5
        self.window = None
        self.progress_text = None
        
    def show(self):
        """Create and show the progress window."""
        try:
            # Delete existing window if it exists
            if cmds.window(self.window_name, exists=True):
                cmds.deleteUI(self.window_name, window=True)
            
            # Create window
            self.window = cmds.window(
                self.window_name,
                title=self.title,
                sizeable=False,
                resizeToFitChildren=True,
                widthHeight=(400, 120)
            )
            
            # Main layout
            main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
            
            # Progress text
            self.progress_text = cmds.text(
                label="Initializing...",
                align="left",
                font="boldLabelFont"
            )
            
            # Progress bar
            self.progress_bar = cmds.progressBar(
                maxValue=self.total_steps,
                value=0,
                width=380,
                height=20
            )
            
            # Status text
            self.status_text = cmds.text(
                label="Please wait...",
                align="left",
                font="smallPlainLabelFont"
            )
            
            # Show window
            cmds.showWindow(self.window)
            cmds.refresh()  # Force immediate display
            
        except Exception as exc:
            LOG.warning("Could not create progress window: %s", exc)
    
    def update(self, message, detail=""):
        """Update progress window with new message."""
        try:
            if self.progress_text and cmds.text(self.progress_text, exists=True):
                cmds.text(self.progress_text, edit=True, label=message)
            
            if detail and self.status_text and cmds.text(self.status_text, exists=True):
                cmds.text(self.status_text, edit=True, label=detail)
            
            self.current_step += 1
            if self.progress_bar and cmds.progressBar(self.progress_bar, exists=True):
                cmds.progressBar(self.progress_bar, edit=True, value=self.current_step)
            
            cmds.refresh()  # Force immediate update
            
        except Exception as exc:
            LOG.warning("Could not update progress window: %s", exc)
    
    def close(self):
        """Close the progress window."""
        try:
            if self.window and cmds.window(self.window_name, exists=True):
                cmds.deleteUI(self.window_name, window=True)
        except Exception as exc:
            LOG.warning("Could not close progress window: %s", exc)

# ---------------------------------------------------------------------------
# Module cleanup system
# ---------------------------------------------------------------------------

def cleanup_loaded_modules():
    """Remove any loaded CMI Tools modules to ensure clean installation."""
    modules_to_remove = []
    
    # Find modules that start with our package names
    for module_name in sys.modules.keys():
        if module_name.startswith(('fdma_shelf', 'cmi_tools')):
            modules_to_remove.append(module_name)
    
    # Remove found modules
    for module_name in modules_to_remove:
        try:
            del sys.modules[module_name]
            LOG.info("Removed cached module: %s", module_name)
        except Exception as exc:
            LOG.warning("Could not remove module %s: %s", module_name, exc)
    
    return len(modules_to_remove)

# ---------------------------------------------------------------------------
# Download / extract helpers
# ---------------------------------------------------------------------------

def safe_download(url, timeout=30):
    """Return raw bytes from *url* or None on failure."""
    try:
        LOG.info("Downloading %s …", url)
        return urlopen(url, timeout=timeout).read()
    except Exception as exc:
        LOG.error("Download failed - check internet connection and GitHub access: %s", exc)
        return None

def _find_repo_root(extract_dir):
    """Return the …/NMSU_Scripts-xxxx root inside *extract_dir*."""
    for name in os.listdir(extract_dir):
        if name.startswith("NMSU_Scripts-"):
            return os.path.join(extract_dir, name)
    return None

def _read_manifest_version(manifest_path):
    """Return *current_version* from a manifest JSON file."""
    try:
        with open(manifest_path, "r") as fin:
            data = json.load(fin)
        return data.get("current_version", FALLBACK_VERSION)
    except Exception as exc:
        LOG.warning("Could not read manifest version: %s", exc)
        return FALLBACK_VERSION

def get_version_from_repo():
    """
    Download repo and read version from manifest without installing.
    Used to show correct version in dialog title.
    """
    global CURRENT_VERSION
    
    zip_bytes = safe_download(REPO_ZIP_URL)
    if not zip_bytes:
        return FALLBACK_VERSION

    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    tmp_zip.write(zip_bytes)
    tmp_zip.close()

    try:
        with zipfile.ZipFile(tmp_zip.name, "r") as zf:
            extract_dir = tempfile.mkdtemp(prefix="cmi_version_check_")
            zf.extractall(extract_dir)

        repo_root = _find_repo_root(extract_dir)
        if not repo_root:
            return FALLBACK_VERSION

        manifest_path = os.path.normpath(os.path.join(
            repo_root, "cmi-tools", "FDMA2530-Modeling", "releases.json"
        ))
        
        if os.path.exists(manifest_path):
            version = _read_manifest_version(manifest_path)
            CURRENT_VERSION = version
            return version
        
        return FALLBACK_VERSION
        
    except Exception as exc:
        LOG.warning("Failed to read version from repo: %s", exc)
        return FALLBACK_VERSION
    finally:
        # Cleanup temp files
        if os.path.exists(tmp_zip.name):
            os.unlink(tmp_zip.name)
        if 'extract_dir' in locals() and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

def download_and_extract_package(target_dir):
    """
    Download the repository ZIP and copy everything we need into
    *target_dir*/scripts | icons | shelves.
    """
    global CURRENT_VERSION

    zip_bytes = safe_download(REPO_ZIP_URL)
    if not zip_bytes:
        return False

    # Write the ZIP to a temp file
    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    tmp_zip.write(zip_bytes)
    tmp_zip.close()

    try:
        with zipfile.ZipFile(tmp_zip.name, "r") as zf:
            extract_dir = tempfile.mkdtemp(prefix="cmi_extract_")
            zf.extractall(extract_dir)

        repo_root = _find_repo_root(extract_dir)
        if not repo_root:
            LOG.error("Downloaded file appears to be corrupted - repository structure not found")
            return False

        # Source locations inside the repo
        shelf_dir = os.path.join(
            repo_root, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf"
        )
        
        fdma_shelf_src = os.path.join(shelf_dir, "fdma_shelf")
        config_src = os.path.join(shelf_dir, "shelf_config.json")
        manifest_src = os.path.join(
            repo_root, "cmi-tools", "FDMA2530-Modeling", "releases.json"
        )

        # Target locations
        scripts_dir = os.path.join(target_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        fdma_shelf_dst = os.path.join(scripts_dir, "fdma_shelf")
        config_dst = os.path.join(scripts_dir, "shelf_config.json")
        manifest_dst = os.path.join(scripts_dir, "releases.json")  # Fixed: Copy to scripts dir, not inside fdma_shelf

        # Copy fdma_shelf package
        if os.path.exists(fdma_shelf_src):
            if os.path.exists(fdma_shelf_dst):
                shutil.rmtree(fdma_shelf_dst)
            shutil.copytree(fdma_shelf_src, fdma_shelf_dst)
            LOG.info("Copied fdma_shelf to scripts/")
        else:
            LOG.error("Required shelf files missing from download - repository may be corrupted")
            return False

        # Copy shelf_config.json
        if os.path.exists(config_src):
            shutil.copy2(config_src, config_dst)
            LOG.info("Copied shelf_config.json")

        # Copy releases.json to scripts directory (so version_utils can find it)
        if os.path.exists(manifest_src):
            shutil.copy2(manifest_src, manifest_dst)
            CURRENT_VERSION = _read_manifest_version(manifest_src)
            LOG.info("Copied releases.json to scripts/ (version: %s)", CURRENT_VERSION)

        return True

    except Exception as exc:
        LOG.error("Package extraction failed: %s", exc)
        return False
    finally:
        if os.path.exists(tmp_zip.name):
            os.unlink(tmp_zip.name)
        if 'extract_dir' in locals() and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

# ---------------------------------------------------------------------------
# Maya module file creation
# ---------------------------------------------------------------------------

def create_module_file():
    """Create the .mod file so Maya auto-loads our package."""
    try:
        modules_dir = get_modules_dir()
        mod_file = os.path.normpath(os.path.join(modules_dir, MODULE_NAME + ".mod"))
        cmi_root = get_cmi_root()

        mod_content = "+ {name} {version} {root}\nscripts: scripts\n".format(
            name=MODULE_NAME, version=CURRENT_VERSION, root=cmi_root
        )

        with open(mod_file, "w") as f:
            f.write(mod_content)
        
        LOG.info("Created module file: %s", mod_file)
        return True

    except Exception as exc:
        LOG.error("Failed to create module file: %s", exc)
        return False

# ---------------------------------------------------------------------------
# Installation / shelf creation
# ---------------------------------------------------------------------------

def install_permanent():
    """Download and install CMI Tools to Maya's modules system."""
    progress = SimpleProgressWindow("Installing FDMA 2530 Shelf")
    progress.show()
    
    try:
        # Step 1: Module cleanup
        progress.update("Preparing installation...", "Cleaning up existing modules")
        removed_count = cleanup_loaded_modules()
        if removed_count > 0:
            LOG.info("Cleaned up %d existing modules", removed_count)
        
        # Debug cross-platform path detection
        LOG.info("=== CMI Tools Cross-Platform Installation ===")
        platform_name = get_platform()
        maya_app_dir = get_maya_app_dir()
        platform_maya_root = get_platform_maya_root()
        maya_root = get_maya_root()
        cmi_root = get_cmi_root()
        modules_dir = get_modules_dir()
        
        LOG.info("Detected Platform: %s", platform_name.upper())
        LOG.info("Maya userAppDir: %s", maya_app_dir)
        LOG.info("Platform-specific Maya root: %s", platform_maya_root)
        LOG.info("Selected Maya root: %s", maya_root)
        LOG.info("CMI Tools target: %s", cmi_root)
        LOG.info("Modules directory: %s", modules_dir)
        
        # Verify path relationships make sense
        try:
            import os
            # Check if paths exist or can be created
            if os.path.exists(maya_root):
                LOG.info("✓ Maya root directory exists")
            else:
                LOG.info("⚠ Maya root directory will be created: %s", maya_root)
                
            # Verify paths are using correct separators for platform
            expected_sep = os.sep
            LOG.info("Platform path separator: '%s'", expected_sep)
            if expected_sep in maya_root and expected_sep in cmi_root:
                LOG.info("✓ Paths using correct platform separators")
            else:
                LOG.info("⚠ Path separator verification: maya_root=%s, cmi_root=%s", 
                        repr(maya_root), repr(cmi_root))
                
        except Exception as e:
            LOG.warning("Path verification error: %s", e)
        
        LOG.info("==============================================")
        
        # Step 2: Prepare directories
        progress.update("Setting up directories...", "Creating installation folder")
        if os.path.exists(cmi_root):
            LOG.info("Removing existing installation: %s", cmi_root)
            shutil.rmtree(cmi_root)
        
        LOG.info("Creating installation directory: %s", cmi_root)
        os.makedirs(cmi_root)

        # Step 3: Download and extract
        progress.update("Downloading shelf files...", "This may take a moment")
        if not download_and_extract_package(cmi_root):
            LOG.error("Package download/extraction failed")
            return False

        # Step 4: Create module file
        progress.update("Configuring Maya integration...", "Creating module file")
        if not create_module_file():
            LOG.error("Module file creation failed")
            return False

        # Add scripts directory to Python path for immediate access
        scripts_dir = os.path.normpath(os.path.join(cmi_root, "scripts"))
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
            LOG.info("Added to Python path: %s", scripts_dir)
        else:
            LOG.info("Scripts directory already in Python path: %s", scripts_dir)
        
        # Verify fdma_shelf directory exists before trying to import
        fdma_shelf_dir = os.path.normpath(os.path.join(scripts_dir, "fdma_shelf"))
        LOG.info("Checking fdma_shelf directory: %s (exists: %s)", fdma_shelf_dir, os.path.exists(fdma_shelf_dir))
        if os.path.exists(fdma_shelf_dir):
            init_file = os.path.normpath(os.path.join(fdma_shelf_dir, "__init__.py"))
            LOG.info("Checking __init__.py: %s (exists: %s)", init_file, os.path.exists(init_file))
            
            # Test import immediately to verify Python path works
            try:
                import fdma_shelf
                LOG.info("SUCCESS: fdma_shelf package can be imported")
            except ImportError as e:
                LOG.error("FAILED: Cannot import fdma_shelf package: %s", e)
                LOG.error("This indicates a Python path issue")

        # Step 5: Create shelf
        progress.update("Creating shelf...", "Loading FDMA 2530 tools")
        if not create_shelf():
            LOG.error("Shelf creation failed")
            return False

        LOG.info("Installation complete")
        return True
        
    except Exception as exc:
        LOG.error("Installation failed: %s", exc)
        return False
    finally:
        progress.close()

def _setup_temporary_cleanup(temp_dir):
    """Set up cleanup callbacks for temporary installation."""
    import atexit
    
    def cleanup_temp_install():
        """Clean up temporary installation files and shelf."""
        try:
            # Remove shelf from current session
            if cmds.shelfLayout(SHELF_NAME, exists=True):
                cmds.deleteUI(SHELF_NAME, layout=True)
                LOG.info("Removed temporary shelf: %s", SHELF_NAME)
            
            # Clean up any shelf preferences that might have been saved
            try:
                # Remove shelf name preference if it exists
                if cmds.optionVar(exists="shelfName{}".format(SHELF_NAME)):
                    cmds.optionVar(remove="shelfName{}".format(SHELF_NAME))
                    LOG.info("Cleaned temporary shelf preference")
            except Exception:
                pass  # Not critical if this fails
            
            # CRITICAL: Remove the shelf file from prefs/shelves so it doesn't persist
            try:
                maya_app_dir = cmds.internalVar(userAppDir=True)
                prefs_dir = os.path.normpath(os.path.join(maya_app_dir, "prefs", "shelves"))
                shelf_file_path = os.path.join(prefs_dir, "shelf_{}.mel".format(SHELF_NAME))
                
                if os.path.exists(shelf_file_path):
                    deleted_shelf_path = shelf_file_path + ".deleted"
                    os.rename(shelf_file_path, deleted_shelf_path)
                    LOG.info("Renamed shelf file to .deleted for temporary cleanup: shelf_{}.mel.deleted".format(SHELF_NAME))
                else:
                    LOG.info("No shelf file found to clean up in: %s", prefs_dir)
            except Exception as e:
                LOG.warning("Could not clean up shelf file: %s", e)
                
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                LOG.info("Cleaned up temporary directory: %s", temp_dir)
            
            # Remove scripts directory from Python path
            scripts_dir = os.path.normpath(os.path.join(temp_dir, "scripts"))
            if scripts_dir in sys.path:
                sys.path.remove(scripts_dir)
                LOG.info("Removed temporary path from sys.path")
                
        except Exception as exc:
            LOG.warning("Temporary cleanup warning: %s", exc)
    
    # Register cleanup for when Python/Maya exits
    atexit.register(cleanup_temp_install)
    
    # Also register Maya-specific cleanup using scriptJob
    try:
        # Clean up when Maya file is closed, new file created, or Maya exits
        cmds.scriptJob(event=["NewSceneOpened", cleanup_temp_install], protected=False)
        cmds.scriptJob(event=["SceneOpened", cleanup_temp_install], protected=False)
        # This is the critical one - clean up when Maya exits
        cmds.scriptJob(event=["quitApplication", cleanup_temp_install], protected=False)
        LOG.info("Registered temporary cleanup callbacks (including Maya exit)")
    except Exception as exc:
        LOG.warning("Could not register Maya cleanup callbacks: %s", exc)

def install_temporary():
    """Load the shelf for this session only (no permanent installation)."""
    progress = SimpleProgressWindow("Loading FDMA 2530 Shelf")
    progress.show()
    
    try:
        # Step 1: Module cleanup
        progress.update("Preparing session...", "Cleaning up existing modules")
        removed_count = cleanup_loaded_modules()
        if removed_count > 0:
            LOG.info("Cleaned up %d existing modules", removed_count)
        
        # Step 2: Create temporary directory
        progress.update("Setting up temporary files...", "Creating session folder")
        temp_dir = tempfile.mkdtemp(prefix="cmi_temp_")
        LOG.info("Created temporary directory: %s", temp_dir)
        
        # Step 3: Download and extract
        progress.update("Downloading shelf files...", "This may take a moment")
        if not download_and_extract_package(temp_dir):
            LOG.error("Temporary package download failed")
            return False

        # Step 4: Setup Python path
        progress.update("Configuring session...", "Setting up Python paths")
        scripts_dir = os.path.normpath(os.path.join(temp_dir, "scripts"))
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
            LOG.info("Added to Python path: %s", scripts_dir)

        # Verify files exist before creating shelf
        shelf_config_path = os.path.join(scripts_dir, "shelf_config.json")
        manifest_path = os.path.join(scripts_dir, "releases.json")
        fdma_shelf_path = os.path.join(scripts_dir, "fdma_shelf")
        
        LOG.info("Checking file locations:")
        LOG.info("  shelf_config.json: %s (exists: %s)", shelf_config_path, os.path.exists(shelf_config_path))
        LOG.info("  releases.json: %s (exists: %s)", manifest_path, os.path.exists(manifest_path))
        LOG.info("  fdma_shelf/: %s (exists: %s)", fdma_shelf_path, os.path.exists(fdma_shelf_path))

        # Step 5: Create shelf
        progress.update("Creating shelf...", "Loading FDMA 2530 tools")
        if create_shelf():
            # Set up cleanup when Maya closes (temporary install only)
            _setup_temporary_cleanup(temp_dir)
            return True
        else:
            # Clean up temp directory if shelf creation failed
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
            return False
            
    except Exception as exc:
        LOG.error("Temporary installation failed: %s", exc)
        # Clean up temp directory on any error
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
        return False
    finally:
        progress.close()

def create_shelf():
    """Create the FDMA 2530 shelf using shelf_config.json."""
    try:
        # Debug Python path
        LOG.info("Current Python path:")
        for i, path in enumerate(sys.path[:5]):  # Show first 5 paths
            LOG.info("  [%d] %s", i, path)
        
        # Try to import the shelf builder
        try:
            # Clear any cached imports first
            if 'fdma_shelf.shelf.builder' in sys.modules:
                if sys.version_info.major >= 3:
                    import importlib
                    importlib.reload(sys.modules['fdma_shelf.shelf.builder'])
                else:
                    # Python 2 reload
                    exec("reload(sys.modules['fdma_shelf.shelf.builder'])")
                LOG.info("Reloaded existing fdma_shelf.shelf.builder module")
            
            import fdma_shelf.shelf.builder as shelf_builder
            LOG.info("Successfully imported shelf builder")
        except ImportError as exc:
            LOG.error("Cannot import shelf builder: %s", exc)
            LOG.error("Make sure fdma_shelf package is in Python path")
            return False

        # Build the shelf
        LOG.info("Attempting to build shelf...")
        shelf_builder.build_shelf(startup=False)
        LOG.info("Shelf created successfully")
        
        # Verify shelf was actually created
        import maya.cmds as cmds
        if cmds.shelfLayout("FDMA_2530", query=True, exists=True):
            LOG.info("Shelf 'FDMA_2530' verified to exist in Maya")
            return True
        else:
            LOG.error("Shelf creation failed - FDMA_2530 shelf not found after build")
            return False

    except ImportError as exc:
        LOG.error("Cannot import shelf builder - missing files: %s", exc)
        return False
    except Exception as exc:
        LOG.error("Shelf creation failed with unexpected error: %s", exc)
        import traceback
        LOG.error("Technical details: %s", traceback.format_exc())
        return False

# ---------------------------------------------------------------------------
# Uninstallation
# ---------------------------------------------------------------------------

def _remove_shelf_from_preferences():
    """Remove shelf from Maya's persistent preferences so it doesn't reappear."""
    try:
        # Remove shelf from shelf layout preferences
        if cmds.optionVar(exists="shelfName{}".format(SHELF_NAME)):
            cmds.optionVar(remove="shelfName{}".format(SHELF_NAME))
            LOG.info("Removed shelf name preference")
        
        # Remove shelf configuration files from Maya prefs
        maya_app_dir = get_maya_app_dir()
        # Maya stores shelves in prefs/shelves/ within the version-specific directory
        prefs_dir = os.path.normpath(os.path.join(maya_app_dir, "prefs", "shelves"))
        LOG.info("Maya app directory: %s", maya_app_dir)
        LOG.info("Looking for shelf files in: %s", prefs_dir)
        
        # Ensure shelves directory exists for debug purposes
        if not os.path.exists(prefs_dir):
            LOG.warning("Shelves directory does not exist: %s", prefs_dir)
            # Try alternative location - sometimes Maya uses different paths
            alt_prefs_dir = os.path.normpath(os.path.join(maya_app_dir, "prefs"))
            LOG.info("Checking alternative prefs location: %s", alt_prefs_dir)
            if os.path.exists(alt_prefs_dir):
                all_prefs_files = os.listdir(alt_prefs_dir)
                shelf_files_in_prefs = [f for f in all_prefs_files if f.startswith("shelf_") and f.endswith(".mel")]
                LOG.info("Shelf files found in prefs root: %s", shelf_files_in_prefs)
        else:
            LOG.info("Shelves directory exists, proceeding with shelf file removal")
        
        # 1. Rename our specific shelf file to .deleted (Maya's standard behavior)
        shelf_file_path = os.path.join(prefs_dir, "shelf_{}.mel".format(SHELF_NAME))
        deleted_shelf_path = shelf_file_path + ".deleted"
        LOG.info("Checking for shelf file at: %s", shelf_file_path)
        
        if os.path.exists(shelf_file_path):
            try:
                os.rename(shelf_file_path, deleted_shelf_path)
                LOG.info("Successfully renamed shelf file to .deleted: shelf_{}.mel.deleted".format(SHELF_NAME))
            except Exception as e:
                LOG.error("Failed to rename shelf file: %s", e)
        else:
            LOG.warning("Shelf file not found at expected location: shelf_{}.mel".format(SHELF_NAME))
            # Try to find shelf files in alternate locations
            search_locations = [
                prefs_dir,  # Standard shelves directory
                os.path.normpath(os.path.join(maya_app_dir, "prefs")),  # Prefs root
                maya_app_dir,  # Maya app directory root
            ]
            
            for search_dir in search_locations:
                if os.path.exists(search_dir):
                    try:
                        all_files = os.listdir(search_dir)
                        shelf_files = [f for f in all_files if f.startswith("shelf_") and f.endswith(".mel")]
                        if shelf_files:
                            LOG.info("Found shelf files in %s: %s", search_dir, shelf_files)
                            # Look for our specific shelf file in this location
                            our_shelf_file = "shelf_{}.mel".format(SHELF_NAME)
                            if our_shelf_file in shelf_files:
                                alt_shelf_path = os.path.join(search_dir, our_shelf_file)
                                alt_deleted_path = alt_shelf_path + ".deleted"
                                LOG.info("Found our shelf file at alternate location: %s", alt_shelf_path)
                                try:
                                    os.rename(alt_shelf_path, alt_deleted_path)
                                    LOG.info("Successfully renamed shelf file to .deleted at: %s", alt_deleted_path)
                                    break  # Found and renamed, stop searching
                                except Exception as e:
                                    LOG.error("Failed to rename shelf file from %s: %s", alt_shelf_path, e)
                        else:
                            LOG.info("No shelf files found in: %s", search_dir)
                    except Exception as e:
                        LOG.warning("Could not search directory %s: %s", search_dir, e)
        
        # 2. Surgically remove our shelf from windowPrefs.mel (fixes tab persistence)
        windowprefs_path = os.path.normpath(os.path.join(maya_app_dir, "prefs", "windowPrefs.mel"))
        if os.path.exists(windowprefs_path):
            try:
                with open(windowprefs_path, 'r') as f:
                    lines = f.readlines()
                
                # Only remove lines that reference our specific shelf name
                cleaned_lines = []
                for line in lines:
                    # Look for exact shelf name matches, not partial matches
                    if '"{}"'.format(SHELF_NAME) in line or "'{}'".format(SHELF_NAME) in line:
                        LOG.info("Removing windowPrefs line: %s", line.strip())
                    else:
                        cleaned_lines.append(line)
                
                # Only write back if we actually removed something
                if len(cleaned_lines) != len(lines):
                    with open(windowprefs_path, 'w') as f:
                        f.writelines(cleaned_lines)
                    LOG.info("Cleaned shelf references from windowPrefs.mel")
                    
            except Exception as e:
                LOG.warning("Could not clean windowPrefs.mel: %s", e)
        
        # 3. Clean any other shelf files that might reference our shelf (existing logic)
        if os.path.exists(prefs_dir):
            shelf_files = [f for f in os.listdir(prefs_dir) if f.startswith("shelf_") and f.endswith(".mel") and f != "shelf_{}.mel".format(SHELF_NAME)]
            
            for shelf_file in shelf_files:
                shelf_path = os.path.join(prefs_dir, shelf_file)
                try:
                    with open(shelf_path, 'r') as f:
                        content = f.read()
                    
                    if SHELF_NAME in content:
                        # Remove references to our shelf from other shelf files
                        lines = content.split('\n')
                        cleaned_lines = [line for line in lines if SHELF_NAME not in line]
                        
                        if len(cleaned_lines) != len(lines):
                            with open(shelf_path, 'w') as f:
                                f.write('\n'.join(cleaned_lines))
                            LOG.info("Cleaned shelf references from: %s", shelf_file)
                        
                except Exception as e:
                    LOG.warning("Could not clean shelf file %s: %s", shelf_file, e)
    
    except Exception as exc:
        LOG.warning("Could not fully clean shelf preferences: %s", exc)

def uninstall():
    """Remove CMI Tools completely."""
    try:
        # Remove shelf if it exists in current session
        if cmds.shelfLayout(SHELF_NAME, exists=True):
            cmds.deleteUI(SHELF_NAME, layout=True)
            LOG.info("Removed shelf from current session: %s", SHELF_NAME)

        # Remove shelf from Maya's persistent shelf preferences
        _remove_shelf_from_preferences()

        # Remove installation directory
        cmi_root = get_cmi_root()
        if os.path.exists(cmi_root):
            shutil.rmtree(cmi_root)
            LOG.info("Removed directory: %s", cmi_root)

        # Remove module file
        mod_file = os.path.normpath(os.path.join(get_modules_dir(), MODULE_NAME + ".mod"))
        if os.path.exists(mod_file):
            os.unlink(mod_file)
            LOG.info("Removed module file: %s", mod_file)

        return True

    except Exception as exc:
        LOG.error("Uninstall encountered an error: %s", exc)
        LOG.warning("Some files may not have been completely removed")
        return False

# ---------------------------------------------------------------------------
# Cross-platform testing
# ---------------------------------------------------------------------------

def test_cross_platform_paths():
    """Test and display cross-platform path generation for verification."""
    import os
    import platform as platform_module
    
    print("\\n=== Cross-Platform Path Testing ===")
    print("Current system: {}".format(platform_module.system()))
    print("Detected platform: {}".format(get_platform().upper()))
    
    # Show platform-specific Maya roots
    home = os.path.expanduser("~")
    print("\\nPlatform-specific Maya root directories:")
    print("  Windows: {}".format(os.path.normpath(os.path.join(home, "Documents", "maya"))))
    print("  macOS:   {}".format(os.path.normpath(os.path.join(home, "Library", "Preferences", "Autodesk", "maya"))))
    print("  Linux:   {}".format(os.path.normpath(os.path.join(home, "maya"))))
    
    # Show selected paths
    print("\\nSelected paths for current platform:")
    try:
        platform_maya_root = get_platform_maya_root()
        print("  Platform Maya root: {}".format(platform_maya_root))
        
        try:
            import maya.cmds
            maya_app_dir = get_maya_app_dir()
            maya_root = get_maya_root()
            cmi_root = get_cmi_root()
            modules_dir = get_modules_dir()
            
            print("  Maya userAppDir: {}".format(maya_app_dir))
            print("  Resolved Maya root: {}".format(maya_root))
            print("  CMI Tools target: {}".format(cmi_root))
            print("  Modules directory: {}".format(modules_dir))
        except ImportError:
            print("  (Maya not available - showing platform defaults only)")
            cmi_root = os.path.normpath(os.path.join(platform_maya_root, CMI_TOOLS_DIR))
            modules_dir = os.path.normpath(os.path.join(platform_maya_root, "modules"))
            print("  CMI Tools target: {}".format(cmi_root))
            print("  Modules directory: {}".format(modules_dir))
            
    except Exception as e:
        print("  Error during path resolution: {}".format(e))
    
    print("==============================\\n")

# ---------------------------------------------------------------------------
# Status checking
# ---------------------------------------------------------------------------

def get_installed_version():
    """Return the installed version, or 'Not Installed'."""
    try:
        cmi_root = get_cmi_root()
        manifest_path = os.path.normpath(os.path.join(
            cmi_root, "scripts", "releases.json"
        ))
        
        if os.path.exists(manifest_path):
            return _read_manifest_version(manifest_path)
        
        return "Not Installed"

    except Exception:
        return "Not Installed"

# ---------------------------------------------------------------------------
# UI Dialog
# ---------------------------------------------------------------------------

def show_install_dialog():
    """Show the main installation dialog."""
    # Get version info
    current_version = get_version_from_repo()
    installed_version = get_installed_version()
    
    # Determine dialog message
    if installed_version == "Not Installed":
        status_msg = "Status: Not installed"
        default_choice = "Install"
    elif installed_version == current_version:
        status_msg = "Status: Up to date (v{})".format(installed_version)
        default_choice = "Run Only"
    else:
        status_msg = "Status: Outdated (v{} → v{})".format(
            installed_version, current_version
        )
        default_choice = "Install"

    # Show dialog
    choice = cmds.confirmDialog(
        title="CMI Tools - FDMA 2530 Installer v{}".format(current_version),
        message=(
            "Maya shelf system for FDMA 2530 students.\n\n"
            "{}\n"
            "Latest version: v{}\n\n"
            "Choose an option:"
        ).format(status_msg, current_version),
        button=["Install", "Run Only", "Uninstall", "Cancel"],
        defaultButton=default_choice,
        cancelButton="Cancel",
        dismissString="Cancel"
    )

    # Handle user choice
    if choice == "Install":
        if install_permanent():
            cmds.confirmDialog(
                title="Installation Complete",
                message=(
                    "FDMA 2530 shelf installed successfully!\n"
                    "Version: {}\n\n"
                    "The shelf will automatically load in future Maya sessions."
                ).format(CURRENT_VERSION),
                button=["OK"],
            )
        else:
            cmds.confirmDialog(
                title="Installation Failed",
                message="Unable to complete installation.\nPlease check the Script Editor for technical details.",
                button=["OK"],
            )

    elif choice == "Run Only":
        if install_temporary():
            cmds.confirmDialog(
                title="Loaded for Session",
                message=(
                    "FDMA 2530 shelf loaded successfully!\n"
                    "Version: {}\n\n"
                    "This session-only installation will be removed when Maya closes."
                ).format(CURRENT_VERSION),
                button=["OK"],
            )
        else:
            cmds.confirmDialog(
                title="Load Failed",
                message="Unable to load shelf for this session.\nPlease check the Script Editor for technical details.",
                button=["OK"],
            )

    elif choice == "Uninstall":
        if cmds.confirmDialog(
            title="Confirm Uninstall",
            message="Remove FDMA 2530 shelf completely?\n\nThis will delete all installed files and preferences.",
            button=["Yes", "No"],
            defaultButton="No",
        ) == "Yes":
            if uninstall():
                cmds.confirmDialog(
                    title="Uninstall Complete",
                    message="FDMA 2530 shelf has been completely removed from Maya.",
                    button=["OK"],
                )
            else:
                cmds.confirmDialog(
                    title="Uninstall Failed",
                    message="Unable to complete uninstall.\nPlease check the Script Editor for technical details.",
                    button=["OK"],
                )

# Maya drag-and-drop entry point
def onMayaDroppedPythonFile(*_):
    show_install_dialog()

# When run standalone
if __name__ == "__main__":
    onMayaDroppedPythonFile()
