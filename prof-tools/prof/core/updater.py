"""
Prof-Tools Updater Module

Handles checking for updates via releases.json manifest, version comparison,
and provides user feedback for the Prof-Tools Maya menu system.

This module handles checking for updates via releases.json manifest, version comparison,
and provides user feedback for the Prof-Tools Maya menu system using a 
manifest-based approach.

Author: Alexander T. Santiago
Version: Dynamic (Read from releases.json)
License: MIT
Repository: https://github.com/Atsantiago/NMSU_Scripts

Functions:
    check_for_updates() -> bool
        Check if a newer version exists in the manifest
    
    get_latest_version() -> str
        Fetch the latest version from releases.json
    
    compare_versions(local, remote) -> bool
        Compare semantic version strings
    
    launch_update_process() -> None
        Open GitHub repository for manual update
"""

# Ensure print/division behave the same in Python 2 and 3
from __future__ import absolute_import, division, print_function
import sys
import os
import webbrowser
import logging
import ssl
import json
import tempfile
import zipfile
import shutil
from datetime import datetime

try:
    # Python 3 built-in
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    # Python 2 fallback
    from urllib2 import urlopen, Request, URLError


def _merge_release_with_defaults(release, manifest):
    """
    Merge a release entry with default values from release_defaults.
    
    Args:
        release (dict): Individual release entry
        manifest (dict): Full manifest with release_defaults
        
    Returns:
        dict: Release with defaults applied, with dynamic URL substitution
    """
    defaults = manifest.get('release_defaults', {})
    merged = defaults.copy()
    merged.update(release)
    
    # Debug logging
    logger.debug("Merging release: %s", release.get('version', 'unknown'))
    logger.debug("Release data: %s", release)
    logger.debug("Defaults: %s", defaults)
    logger.debug("Merged before URL substitution: %s", merged)
    
    # Handle dynamic download URL substitution
    if 'download_url' in merged and '{commit_hash}' in merged['download_url']:
        commit_hash = merged.get('commit_hash', 'master')
        original_url = merged['download_url']
        merged['download_url'] = merged['download_url'].format(commit_hash=commit_hash)
        logger.debug("Download URL substitution: %s -> %s (commit_hash: %s)", 
                    original_url, merged['download_url'], commit_hash)
    
    # Handle dynamic manifest URL substitution in update_system if present
    if 'update_system' in manifest and 'manifest_url' in manifest['update_system']:
        manifest_url = manifest['update_system']['manifest_url']
        if '{commit_hash}' in manifest_url:
            commit_hash = merged.get('commit_hash', 'master')
            original_manifest_url = manifest_url
            substituted_manifest_url = manifest_url.format(commit_hash=commit_hash)
            logger.debug("Manifest URL substitution: %s -> %s (commit_hash: %s)", 
                        original_manifest_url, substituted_manifest_url, commit_hash)
    
    logger.debug("Final merged release: %s", merged)
    return merged

# Import version utilities for robust version handling
from .version_utils import get_prof_tools_version, parse_semantic_version, is_valid_semantic_version, get_manifest_data

# Configure logging for debug output
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Manifest URL - will be dynamically determined based on current branch
# Fallback order: dev-grader -> master for development workflow
MANIFEST_URL_TEMPLATE = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/{branch}/prof-tools/releases.json"
MANIFEST_BRANCHES = ["dev-grader", "master"]  # Try dev-grader first, then master

def _get_manifest_url():
    """
    Dynamically determine the manifest URL by trying different branches.
    Returns the first working manifest URL.
    """
    import sys
    
    if sys.version_info[0] >= 3:
        from urllib.request import urlopen, Request
        from urllib.error import URLError, HTTPError
    else:
        from urllib2 import urlopen, Request, URLError, HTTPError
    
    for branch in MANIFEST_BRANCHES:
        url = MANIFEST_URL_TEMPLATE.format(branch=branch)
        try:
            request = Request(url)
            request.add_header('User-Agent', 'Prof-Tools-Updater/1.0')
            response = urlopen(request, timeout=5)
            response.close()
            logger.debug("Found working manifest URL: %s", url)
            return url
        except (URLError, HTTPError) as e:
            logger.debug("Manifest URL %s failed: %s", url, e)
            continue
    
    # Fallback to master if nothing else works
    fallback_url = MANIFEST_URL_TEMPLATE.format(branch="master")
    logger.warning("All manifest URLs failed, using fallback: %s", fallback_url)
    return fallback_url

MANIFEST_URL = _get_manifest_url()
_HTTP_TIMEOUT = 10  # seconds


def get_latest_version(include_test=False):
    """
    Fetch the latest release version from the manifest.
    Returns the version string (e.g. "0.2.0") or None on error.
    
    This uses the version_utils manifest system for consistency with
    the rest of the prof-tools versioning infrastructure.
    
    Args:
        include_test (bool): Whether to include test versions in the search
    """
    try:
        manifest = get_manifest_data()
        if not manifest:
            logger.warning("Could not get manifest data for version check")
            return None

        if include_test:
            # Check for latest test version first
            latest_test_version = manifest.get('latest_test_version')
            if latest_test_version and is_valid_semantic_version(latest_test_version):
                return latest_test_version
        
        # Fall back to current_version (stable version)
        latest_version = manifest.get('current_version')
        if not latest_version:
            logger.error("No current_version field found in manifest")
            return None
            
        if not is_valid_semantic_version(latest_version):
            logger.error("Invalid semantic version in manifest: %s", latest_version)
            return None

        return latest_version
        
    except Exception as e:
        logger.error("Failed to parse latest version from manifest: %s", e)
        return None
        logger.error("Failed to parse latest version from manifest: %s", e)
        return None


def compare_versions(local, remote, include_test_versions=False):
    """
    Compare semantic version strings with support for test versions.
    Returns True if remote > local.
    
    This function now supports both:
    - Standard MAJOR.MINOR.PATCH format
    - Extended MAJOR.MINOR.PATCH.TEST format for testing
    
    Args:
        local (str): Local version string
        remote (str): Remote version string
        include_test_versions (bool): Whether to include test versions in comparison
        
    Returns:
        bool: True if remote version is newer than local
    """
    try:
        # Import here to avoid circular imports
        from prof.core.version_utils import compare_versions_extended
        
        return compare_versions_extended(local, remote, include_test_versions)
        
    except ImportError:
        # Fallback to basic comparison if enhanced version isn't available
        logger.warning("Enhanced version comparison not available, using basic comparison")
        return _basic_version_compare(local, remote)
    except Exception as e:
        logger.error("Version comparison error between %s and %s: %s", local, remote, e)
        return False


def _basic_version_compare(local, remote):
    """
    Basic version comparison fallback for MAJOR.MINOR.PATCH format only.
    """
    try:
        # Validate both versions first
        if not is_valid_semantic_version(local):
            logger.error("Invalid local version format: %s", local)
            return False
            
        if not is_valid_semantic_version(remote):
            logger.error("Invalid remote version format: %s", remote)
            return False
        
        # Parse both versions
        local_parsed = parse_semantic_version(local)
        remote_parsed = parse_semantic_version(remote)
        
        # Compare major.minor.patch only (ignore test versions in basic mode)
        local_tuple = (local_parsed['major'], local_parsed['minor'], local_parsed['patch'])
        remote_tuple = (remote_parsed['major'], remote_parsed['minor'], remote_parsed['patch'])
        
        is_newer = remote_tuple > local_tuple
        logger.debug("Basic version comparison: %s vs %s -> newer: %s", local, remote, is_newer)
        return is_newer
        
    except Exception as e:
        logger.error("Basic version comparison error between %s and %s: %s", local, remote, e)
        return False


def launch_update_process():
    """
    Open the GitHub repository releases page in the default web browser.
    This provides a manual update path for users.
    """
    try:
        # Use the repository URL from the prof module
        repo_url = "https://github.com/Atsantiago/NMSU_Scripts"
        releases_url = repo_url + "/releases"
        webbrowser.open(releases_url)
        logger.info("Opened releases page in browser: %s", releases_url)
    except Exception as e:
        logger.error("Failed to open releases page: %s", e)


def check_for_updates():
    """
    Main function to check for updates and show the professional update dialog.
    
    This function uses the new update dialog for a better user experience
    designed for advanced Maya users and instructors.
    """
    try:
        # Try to use the new update dialog
        from ..ui.update_dialog import check_for_updates_with_dialog
        check_for_updates_with_dialog()
        return
        
    except ImportError as e:
        logger.warning("Could not load update dialog, falling back to simple dialog: %s", e)
        
    # Fallback to simple dialog if update_dialog is not available
    try:
        import maya.cmds as cmds  # Maya commands for dialog boxes
    except ImportError:
        cmds = None  # if not in Maya, fallback to console output

    # Get current version using version_utils
    current_version = get_prof_tools_version()
    if not current_version:
        _show_dialog("Version Error",
                     "Could not determine current Prof-Tools version.",
                     cmds)
        return

    # Get latest version from manifest
    latest = get_latest_version()  # fetch remote version
    if not latest:
        _show_dialog("Update Check Failed",
                     "Could not determine latest version. Please check your internet connection and try again later.",
                     cmds)
        return

    # Compare versions
    if compare_versions(current_version, latest):
        # construct message if an update is available
        msg = (
            "A new version of Prof-Tools is available.\n\n"
            "Current: {local}\nLatest: {remote}\n\n"
            "Open the releases page to download?"
        ).format(local=current_version, remote=latest)

        if cmds:
            # show Maya dialog with Yes/No
            res = cmds.confirmDialog(
                title="Prof-Tools Update Available",
                message=msg,
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No",
                dismissString="No"
            )
            if res == "Yes":
                launch_update_process()
        else:
            # fallback: print to console and open browser
            print(msg)
            launch_update_process()
    else:
        # message if already up to date
        _show_dialog("Up to Date",
                     "You are running the latest version ({ver}).".format(ver=current_version),
                     cmds)


def _show_dialog(title, message, cmds):
    """
    Show a simple OK dialog in Maya or print to console.
    
    Args:
        title (str): Dialog title
        message (str): Dialog message
        cmds: Maya cmds module or None for console fallback
    """
    if cmds:
        cmds.confirmDialog(title=title, message=message, button=["OK"], defaultButton="OK")
    else:
        # console fallback
        print("{0}: {1}".format(title, message))


def check_for_test_updates():
    """
    Check for test versions (MAJOR.MINOR.PATCH.TEST format) available for testing.
    This is separate from the main update check to allow testing new features.
    """
    try:
        # Try to use the enhanced update dialog
        from ..ui.update_dialog import check_for_updates_with_dialog
        check_for_updates_with_dialog(include_test_versions=True)
        return
        
    except ImportError as e:
        logger.warning("Could not load update dialog, falling back to simple dialog: %s", e)
        
    # Fallback to simple test update check
    _simple_test_update_check()


def _simple_test_update_check():
    """
    Simple test update check fallback when UI dialog is not available.
    """
    try:
        import maya.cmds as cmds
    except ImportError:
        cmds = None

    # Get current version
    current_version = get_prof_tools_version()
    if not current_version:
        _show_dialog("Version Error",
                     "Could not determine current Prof-Tools version.",
                     cmds)
        return

    # Get latest version including test versions
    latest = get_latest_version(include_test=True)
    if not latest:
        _show_dialog("Update Check Failed",
                     "Could not determine latest version. Please check your internet connection.",
                     cmds)
        return

    # Compare versions including test versions
    if compare_versions(current_version, latest, include_test_versions=True):
        from prof.core.version_utils import is_test_version
        
        version_type = "test version" if is_test_version(latest) else "stable version"
        
        msg = (
            "A new {version_type} of Prof-Tools is available for testing.\n\n"
            "Current: {local}\nLatest: {remote}\n\n"
            "⚠️ Test versions are for development and testing only.\n"
            "Open the releases page to download?"
        ).format(local=current_version, remote=latest, version_type=version_type)

        if cmds:
            res = cmds.confirmDialog(
                title="Test Update Available",
                message=msg,
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No",
                dismissString="No"
            )
            if res == "Yes":
                launch_update_process()
        else:
            print(msg)
            launch_update_process()
    else:
        _show_dialog("Up to Date",
                     "You are running the latest version ({ver}) including test versions.".format(ver=current_version),
                     cmds)


def perform_automatic_update(include_test_versions=False):
    """
    Perform an automatic update by downloading and installing the latest version.
    
    Args:
        include_test_versions (bool): Whether to include test versions in update selection
        
    Returns:
        True on success, False on failure.
    """
    try:
        import maya.cmds as cmds
        logger.info("Starting automatic update process (include_test=%s)...", include_test_versions)
        
        # Get the latest version info from manifest
        manifest = get_manifest_data()
        if not manifest:
            logger.error("Could not get manifest data for update")
            return False
        
        releases = manifest.get('releases', [])
        if not releases:
            logger.error("No releases found in manifest")
            return False
        
        # Find the appropriate release based on test version preference
        target_release = None
        if include_test_versions:
            # Get the latest test version from manifest
            latest_test_version = manifest.get('latest_test_version')
            if latest_test_version:
                for release in releases:
                    if release.get('version') == latest_test_version:
                        target_release = release
                        break
            
            # Fallback to highest version if latest_test_version not found
            if not target_release:
                latest_version = get_latest_version(include_test=True)
                for release in releases:
                    if release.get('version') == latest_version:
                        target_release = release
                        break
        else:
            # Get the latest stable version only (back to original logic)
            latest_stable_version = get_latest_version(include_test=False)
            for release in releases:
                if release.get('version') == latest_stable_version and not release.get('test_version', False):
                    target_release = release
                    break
        
        if not target_release:
            logger.error("Could not find appropriate release for update")
            return False
        
        logger.debug("Found target release before merge: %s", target_release)
        
        # Merge release with defaults
        target_release = _merge_release_with_defaults(target_release, manifest)
        
        logger.debug("Target release after merge: %s", target_release)
        
        download_url = target_release.get('download_url')
        directory_path = target_release.get('directory_path', 'prof-tools')
        version = target_release.get('version')
        
        logger.debug("Extracted values - URL: %s, Directory: %s, Version: %s", 
                    download_url, directory_path, version)
        
        if not download_url:
            logger.error("No download URL found in latest release")
            return False
        
        logger.info("Downloading update from: %s", download_url)
        
        # Create a temporary directory for the download
        temp_dir = tempfile.mkdtemp()
        try:
            # Download the ZIP file
            zip_path = os.path.join(temp_dir, "update.zip")
            _download_file(download_url, zip_path)
            
            # Extract the ZIP file
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the prof-tools directory in the extracted files
            prof_tools_source = None
            for root, dirs, files in os.walk(extract_dir):
                if directory_path in dirs:
                    prof_tools_source = os.path.join(root, directory_path)
                    break
            
            if not prof_tools_source:
                logger.error("Could not find prof-tools directory in download")
                return False
            
            # Use the setup module to perform the installation
            from prof.core.setup import ProfToolsSetup
            setup = ProfToolsSetup()
            
            # Get the installation path
            install_path = setup.get_installation_path()
            
            # Remove existing installation
            if os.path.exists(install_path):
                shutil.rmtree(install_path)
            
            # Copy new files
            prof_source = os.path.join(prof_tools_source, "prof")
            if os.path.exists(prof_source):
                shutil.copytree(prof_source, install_path)
                logger.info("Successfully copied updated files to: %s", install_path)
            else:
                logger.error("Could not find prof directory in download")
                return False
            
            # Rebuild the menu with updated code
            try:
                # Remove any cached modules to force reload
                import sys
                to_remove = [name for name in sys.modules if name.startswith("prof")]
                for name in to_remove:
                    sys.modules.pop(name, None)
                
                # Add install path to sys.path if not already there
                if install_path not in sys.path:
                    sys.path.insert(0, install_path)
                
                # Import and rebuild menu
                from prof.ui import builder
                builder.build_menu()
                logger.info("Successfully rebuilt menu with updated code (version: %s)", version)
                
                # Create installed version file to track the actual installed version
                # This is especially important for test versions that are permanently installed
                try:
                    parent_dir = os.path.dirname(install_path)
                    version_file = os.path.join(parent_dir, 'installed_version.txt')
                    with open(version_file, 'w') as f:
                        f.write(version)
                    logger.info("Created installed version file: %s", version)
                except Exception as e:
                    logger.warning("Failed to create installed version file: %s", e)
                
                # Clear version cache so new version is detected immediately
                try:
                    from prof.core.version_utils import clear_version_cache
                    clear_version_cache()
                    logger.debug("Cleared version cache after update")
                except Exception as e:
                    logger.debug("Could not clear version cache: %s", e)
                
                return True
                
            except Exception as e:
                logger.error("Failed to rebuild menu after update: %s", e)
                return False
                
        finally:
            # Clean up temporary files
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning("Failed to clean up temp directory: %s", e)
    
    except Exception as e:
        logger.error("Automatic update failed: %s", e)
        return False


def _download_file(url, destination):
    """
    Download a file from URL to destination with SSL context.
    """
    import sys
    
    # Create SSL context for secure downloads
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    if sys.version_info[0] >= 3:
        # Python 3
        from urllib.request import urlopen, Request
        from urllib.error import URLError, HTTPError
    else:
        # Python 2
        from urllib2 import urlopen, Request, URLError, HTTPError
    
    try:
        request = Request(url)
        request.add_header('User-Agent', 'Prof-Tools-Updater/1.0')
        
        if sys.version_info[0] >= 3:
            response = urlopen(request, timeout=30, context=ssl_context)
        else:
            response = urlopen(request, timeout=30)
        
        with open(destination, 'wb') as f:
            shutil.copyfileobj(response, f)
        
        logger.info("Successfully downloaded file to: %s", destination)
        
    except (URLError, HTTPError) as e:
        logger.error("Failed to download file: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error during download: %s", e)
        raise


def _install_specific_version(version, temporary=False):
    """
    Install a specific version of prof-tools.
    
    Args:
        version (str): The specific version to install (e.g., "0.2.13.1")
        temporary (bool): Whether this is a temporary installation
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    try:
        from prof.core.version_utils import get_manifest_data
        
        logger.info("Installing specific version %s (temporary=%s)", version, temporary)
        
        # Get the manifest data
        manifest = get_manifest_data()
        if not manifest:
            logger.error("Could not get manifest data for specific version installation")
            return False
        
        releases = manifest.get('releases', [])
        if not releases:
            logger.error("No releases found in manifest")
            return False
        
        # Find the specific release
        target_release = None
        for release in releases:
            if release.get('version') == version:
                target_release = release
                break
        
        if not target_release:
            logger.error("Could not find release for version %s", version)
            return False
        
        logger.debug("Found target release for version %s before merge: %s", version, target_release)
        
        # Merge release with defaults
        target_release = _merge_release_with_defaults(target_release, manifest)
        
        logger.debug("Target release for version %s after merge: %s", version, target_release)
        
        download_url = target_release.get('download_url')
        directory_path = target_release.get('directory_path', 'prof-tools')
        
        logger.debug("Extracted values for version %s - URL: %s, Directory: %s", 
                    version, download_url, directory_path)
        
        if not download_url:
            logger.error("No download URL found for version %s", version)
            return False
        
        logger.info("Downloading version %s from: %s", version, download_url)
        
        # Create a temporary directory for the download
        temp_dir = tempfile.mkdtemp()
        try:
            # Download the ZIP file
            zip_path = os.path.join(temp_dir, "update.zip")
            _download_file(download_url, zip_path)
            
            # Extract and install (reuse logic from perform_automatic_update)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get current script directory (where prof-tools is installed)
                current_script_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                parent_dir = os.path.dirname(current_script_dir)
                
                # Create backup if not temporary
                backup_path = None
                if not temporary:
                    backup_path = os.path.join(parent_dir, "prof-tools-backup-{0}".format(
                        datetime.now().strftime("%Y%m%d_%H%M%S")
                    ))
                    if os.path.exists(current_script_dir):
                        shutil.copytree(current_script_dir, backup_path)
                        logger.info("Created backup at: %s", backup_path)
                
                # Extract new version
                extract_path = os.path.join(temp_dir, "extracted")
                zip_ref.extractall(extract_path)
                
                # Find the prof-tools directory in the extracted content
                extracted_prof_tools = None
                for root, dirs, files in os.walk(extract_path):
                    if os.path.basename(root) == directory_path:
                        extracted_prof_tools = root
                        break
                
                if not extracted_prof_tools:
                    logger.error("Could not find prof-tools directory in extracted content")
                    return False
                
                # Install the new version
                if os.path.exists(current_script_dir):
                    shutil.rmtree(current_script_dir)
                
                shutil.copytree(extracted_prof_tools, current_script_dir)
                logger.info("Successfully installed version %s", version)
                
                # Create installed version file to track the actual installed version
                # This is especially important for test versions
                if not temporary:  # Only create for permanent installations
                    try:
                        parent_dir = os.path.dirname(current_script_dir)
                        version_file = os.path.join(parent_dir, 'installed_version.txt')
                        with open(version_file, 'w') as f:
                            f.write(version)
                        logger.info("Created installed version file for version: %s", version)
                        
                        # Clear version cache so new version is detected immediately
                        from prof.core.version_utils import clear_version_cache
                        clear_version_cache()
                        logger.debug("Cleared version cache after installation")
                    except Exception as e:
                        logger.warning("Failed to create installed version file: %s", e)
                
                return True
                
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        logger.error("Failed to install specific version %s: %s", version, e)
        return False
