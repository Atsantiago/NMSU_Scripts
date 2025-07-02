"""
FDMA 2530 GitHub Utilities - Version 1.0
========================================

A comprehensive utility module for handling GitHub operations in Maya shelf systems.
Provides Python 2/3 compatible functions for downloading, executing, and managing
scripts directly from GitHub repositories.

Features:
- Full Python 2/3 compatibility for all Maya versions
- Direct script execution without temporary files
- Intelligent update detection and version management
- Robust error handling with detailed feedback
- Network connectivity testing and timeout protection
- Centralized configuration for easy maintenance

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
GitHub: github.com/atsantiago
Repository: https://github.com/Atsantiago/NMSU_Scripts
Version: 1.2 - Enhanced Python 2/3 compatibility with new directory structure
"""

# ============================================================================
# IMPORTS AND PYTHON 2/3 COMPATIBILITY LAYER
# ============================================================================
# Handle all the differences between Python 2 and 3 to ensure this utility
# works across all Maya versions from 2016 (Python 2.7) to latest (Python 3.x)

import sys
import os
# Version information
__version__ = "1.2"


# Python version detection for compatibility branching
PYTHON_VERSION = sys.version_info[0]
IS_PYTHON_2 = (PYTHON_VERSION == 2)
IS_PYTHON_3 = (PYTHON_VERSION >= 3)

if IS_PYTHON_2:
    # ========================================================================
    # PYTHON 2 COMPATIBILITY IMPORTS
    # ========================================================================

    import urllib2 as urllib_request
    from urlparse import urljoin
    string_types = basestring  # Python 2 has basestring type
    
    def exec_code(code, globals_dict):
        """Execute code with Python 2 syntax."""
        exec(code, globals_dict)
        
    def format_string(template, **kwargs):
        """Format strings without f-string syntax for Python 2."""
        return template.format(**kwargs)
        
    def encode_url_params(params):
        """Handle URL encoding for Python 2."""
        import urllib
        return urllib.urlencode(params)
        
else:
    # ========================================================================
    # PYTHON 3 COMPATIBILITY IMPORTS  
    # ========================================================================
    
    import urllib.request as urllib_request
    from urllib.parse import urljoin, urlencode
    string_types = str  # Python 3 only has str type
    
    def exec_code(code, globals_dict):
        """Execute code with Python 3 syntax."""
        exec(code, globals_dict)
        
    def format_string(template, **kwargs):
        """Format strings for Python 3 (could use f-strings but keeping compatible)."""
        return template.format(**kwargs)
        
    def encode_url_params(params):
        """Handle URL encoding for Python 3."""
        return urlencode(params)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================
# Central configuration for all GitHub operations. Modify these values to
# change repository settings or adjust behavior across the entire system.

# Repository information
REPOSITORY_URL = "https://github.com/Atsantiago/NMSU_Scripts"
REPOSITORY_BRANCH = "master"
BASE_DIRECTORY_PATH = "FDMA2530-Modeling/Student-Shelf"

# Network and performance settings
DEFAULT_TIMEOUT = 15  # Seconds to wait for GitHub responses
MAX_RETRIES = 3       # Number of retry attempts for failed downloads
CHUNK_SIZE = 8192     # Bytes to read at a time for large files

# Debugging and logging configuration
VERBOSE_LOGGING = True  # Set to False to reduce console output
LOG_PREFIX = "[FDMA2530-GitHub]"  # Prefix for all log messages

# Subdirectory mappings for easy access
SUBDIRECTORIES = {
    'core': 'core-scripts',
    'buttons': 'shelf-button-scripts', 
    'utilities': 'utilities',
    'media': 'media'
}


# ============================================================================
# LOGGING AND DEBUG UTILITIES
# ============================================================================
# Centralized logging system for consistent message formatting and optional
# verbosity control across the entire utility system.

def log_info(message):
    """
    Log an informational message with consistent formatting.
    
    Args:
        message (str): The message to log
    """
    if VERBOSE_LOGGING:
        print("{0} INFO: {1}".format(LOG_PREFIX, message))


def log_warning(message):
    """
    Log a warning message that's always displayed.
    
    Args:
        message (str): The warning message to log
    """
    print("{0} WARNING: {1}".format(LOG_PREFIX, message))


def log_error(message):
    """
    Log an error message that's always displayed.
    
    Args:
        message (str): The error message to log
    """
    print("{0} ERROR: {1}".format(LOG_PREFIX, message))


def log_success(message):
    """
    Log a success message with visual indicator.
    
    Args:
        message (str): The success message to log
    """
    if VERBOSE_LOGGING:
        print("{0} SUCCESS: ✓ {1}".format(LOG_PREFIX, message))


# ============================================================================
# URL CONSTRUCTION AND PATH UTILITIES
# ============================================================================
# Functions for building proper GitHub URLs and handling file paths within
# the repository structure. These ensure consistent URL formatting across
# all operations.

def build_github_raw_url(file_path):
    """
    Construct a complete GitHub raw content URL for a file.
    
    This function builds the proper URL format for accessing raw file content
    from GitHub, which allows direct download and execution of scripts.
    
    Args:
        file_path (str): Path to file relative to the Student-Shelf directory
                        Example: "core-scripts/checklist.py" or "utilities/github_utilities.py"
    
    Returns:
        str: Complete GitHub raw URL for the file
        
    Example:
        >>> build_github_raw_url("core-scripts/checklist.py")
        "https://github.com/Atsantiago/NMSU_Scripts/raw/master/FDMA2530-Modeling/Student-Shelf/core-scripts/checklist.py"
    """
    # Clean up input parameters to prevent double slashes or other URL issues
    repo_url = REPOSITORY_URL.rstrip('/')  # Remove trailing slash if present
    file_path = file_path.lstrip('/')      # Remove leading slash if present
    
    # Build the complete URL using GitHub's raw content format
    complete_url = format_string(
        "{repo}/raw/{branch}/{base_path}/{file_path}",
        repo=repo_url,
        branch=REPOSITORY_BRANCH,
        base_path=BASE_DIRECTORY_PATH,
        file_path=file_path
    )
    
    log_info("Built GitHub URL: {0}".format(complete_url))
    return complete_url


def build_subdirectory_path(subdirectory_key, filename):
    """
    Build a file path using predefined subdirectory mappings.
    
    This convenience function helps build proper paths for files in specific
    subdirectories without remembering the exact folder names.
    
    Args:
        subdirectory_key (str): Key from SUBDIRECTORIES mapping
                               ('core', 'buttons', 'utilities', 'media')
        filename (str): Name of the file in that subdirectory
    
    Returns:
        str: Complete path relative to Student-Shelf directory
        
    Example:
        >>> build_subdirectory_path('core', 'checklist.py')
        "core-scripts/checklist.py"
    """
    if subdirectory_key not in SUBDIRECTORIES:
        available_keys = ', '.join(SUBDIRECTORIES.keys())
        log_error("Invalid subdirectory key '{0}'. Available keys: {1}".format(
            subdirectory_key, available_keys))
        return None
    
    subdirectory_name = SUBDIRECTORIES[subdirectory_key]
    file_path = "{0}/{1}".format(subdirectory_name, filename)
    
    log_info("Built subdirectory path: {0}".format(file_path))
    return file_path


# ============================================================================
# NETWORK OPERATIONS AND DOWNLOAD FUNCTIONS
# ============================================================================
# Core functions for downloading content from GitHub with comprehensive error
# handling, retry logic, and progress feedback.

def test_github_connectivity(timeout=None):
    """
    Test if GitHub is accessible and the repository can be reached.
    
    This function performs a lightweight test to verify network connectivity
    and repository accessibility before attempting larger operations.
    
    Args:
        timeout (int, optional): Timeout in seconds. Uses DEFAULT_TIMEOUT if None.
    
    Returns:
        bool: True if GitHub is accessible, False otherwise
    """
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
    try:
        log_info("Testing GitHub connectivity...")
        
        # Test with a lightweight file (this utilities file itself)
        test_url = build_github_raw_url("utilities/github_utilities.py")
        
        # Attempt to open the URL with timeout
        response = urllib_request.urlopen(test_url, timeout=timeout)
        
        # Check if we got a successful response
        if hasattr(response, 'getcode'):
            status_code = response.getcode()
            if status_code == 200:
                log_success("GitHub connectivity confirmed")
                return True
            else:
                log_warning("GitHub returned status code: {0}".format(status_code))
                return False
        else:
            # Older Python versions might not have getcode()
            log_success("GitHub connectivity confirmed (legacy response)")
            return True
            
    except Exception as e:
        log_error("GitHub connectivity test failed: {0}".format(str(e)))
        return False


def download_file_content(file_path, timeout=None, max_retries=None):
    """
    Download file content from GitHub with retry logic and error handling.
    
    This is the core download function that handles all the complexity of
    fetching content from GitHub, including retries, timeout handling,
    and proper encoding for both Python 2 and 3.
    
    Args:
        file_path (str): Path to file relative to Student-Shelf directory
        timeout (int, optional): Timeout in seconds. Uses DEFAULT_TIMEOUT if None.
        max_retries (int, optional): Max retry attempts. Uses MAX_RETRIES if None.
    
    Returns:
        str: File content as string, or None if download failed
    """
    # Use default values if not provided
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    if max_retries is None:
        max_retries = MAX_RETRIES
    
    # Build the download URL
    download_url = build_github_raw_url(file_path)
    if download_url is None:
        log_error("Could not build download URL for: {0}".format(file_path))
        return None
    
    # Attempt download with retry logic
    last_exception = None
    
    for attempt in range(max_retries + 1):  # +1 because range is exclusive
        try:
            if attempt > 0:
                log_info("Download attempt {0}/{1} for: {2}".format(
                    attempt + 1, max_retries + 1, file_path))
            else:
                log_info("Downloading: {0}".format(file_path))
            
            # ================================================================
            # PERFORM THE ACTUAL DOWNLOAD
            # ================================================================
            # Open the URL with timeout protection
            response = urllib_request.urlopen(download_url, timeout=timeout)
            
            # Read the content
            content = response.read()
            
            # ================================================================
            # HANDLE ENCODING FOR PYTHON 3
            # ================================================================
            # Python 3 returns bytes, but we need string for exec()
            if IS_PYTHON_3 and isinstance(content, bytes):
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError as e:
                    log_error("Encoding error decoding {0}: {1}".format(file_path, str(e)))
                    return None
            
            # ================================================================
            # VALIDATE DOWNLOADED CONTENT
            # ================================================================
            # Basic validation to ensure we got actual content
            if not content or len(content.strip()) == 0:
                log_warning("Downloaded content is empty for: {0}".format(file_path))
                return None
            
            # Log success with content size for debugging
            content_size = len(content)
            log_success("Downloaded {0} ({1} characters)".format(file_path, content_size))
            
            return content
            
        except Exception as e:
            last_exception = e
            log_warning("Download attempt {0} failed for {1}: {2}".format(
                attempt + 1, file_path, str(e)))
            
            # Don't retry on the last attempt
            if attempt < max_retries:
                log_info("Retrying download...")
            
    # If we get here, all attempts failed
    log_error("All download attempts failed for {0}. Last error: {1}".format(
        file_path, str(last_exception)))
    return None


# ============================================================================
# SCRIPT EXECUTION FUNCTIONS
# ============================================================================
# Functions for executing Python scripts directly from GitHub without saving
# to disk. Includes proper namespace handling and error reporting.

def execute_script_from_github(file_path, globals_dict=None, locals_dict=None):
    """
    Download and execute a Python script directly from GitHub.
    
    This function combines downloading and execution in a safe way, with
    proper namespace handling and comprehensive error reporting.
    
    Args:
        file_path (str): Path to script relative to Student-Shelf directory
        globals_dict (dict, optional): Global namespace for script execution
        locals_dict (dict, optional): Local namespace for script execution
    
    Returns:
        bool: True if script executed successfully, False otherwise
    """
    log_info("Preparing to execute script: {0}".format(file_path))
    
    # ========================================================================
    # DOWNLOAD THE SCRIPT CONTENT
    # ========================================================================
    # First, get the script content from GitHub
    script_content = download_file_content(file_path)
    if script_content is None:
        log_error("Cannot execute script - download failed: {0}".format(file_path))
        return False
    
    # ========================================================================
    # PREPARE EXECUTION ENVIRONMENT
    # ========================================================================
    # Set up the namespace for script execution
    if globals_dict is None:
        globals_dict = globals()
    
    if locals_dict is None:
        locals_dict = globals_dict
    
    # ========================================================================
    # EXECUTE THE SCRIPT
    # ========================================================================
    # Use our compatibility function to execute the code
    try:
        log_info("Executing script: {0}".format(file_path))
        
        # Execute the script content in the provided namespace
        exec_code(script_content, globals_dict)
        
        log_success("Script executed successfully: {0}".format(file_path))
        return True
        
    except SyntaxError as e:
        log_error("Syntax error in script {0}: {1}".format(file_path, str(e)))
        return False
    except Exception as e:
        log_error("Runtime error executing {0}: {1}".format(file_path, str(e)))
        return False


# ============================================================================
# UPDATE DETECTION AND VERSION MANAGEMENT
# ============================================================================
# Functions for comparing local and remote content to detect when updates
# are available, plus utilities for extracting version information.

def check_for_file_updates(current_content, file_path):
    """
    Check if a file has updates available on GitHub.
    
    This function compares current content with the latest version on GitHub
    to determine if updates are available. Uses content comparison rather than
    timestamps for accuracy.
    
    Args:
        current_content (str): The current content to compare against
        file_path (str): Path to file relative to Student-Shelf directory
    
    Returns:
        dict: Update information with keys:
              - 'updates_available' (bool): Whether updates are available
              - 'current_size' (int): Size of current content
              - 'latest_size' (int): Size of latest content
              - 'error' (str): Error message if check failed
    """
    log_info("Checking for updates: {0}".format(file_path))
    
    try:
        # ====================================================================
        # DOWNLOAD LATEST VERSION FROM GITHUB
        # ====================================================================
        # Get the latest content to compare against
        latest_content = download_file_content(file_path)
        if latest_content is None:
            return {
                'updates_available': False,
                'error': 'Failed to download latest version for comparison',
                'current_size': len(current_content) if current_content else 0,
                'latest_size': 0
            }
        
        # ====================================================================
        # NORMALIZE CONTENT FOR COMPARISON
        # ====================================================================
        # Strip whitespace and normalize line endings to avoid false positives
        current_normalized = current_content.strip() if current_content else ""
        latest_normalized = latest_content.strip()
        
        # Replace different line ending styles for consistent comparison
        current_normalized = current_normalized.replace('\r\n', '\n').replace('\r', '\n')
        latest_normalized = latest_normalized.replace('\r\n', '\n').replace('\r', '\n')
        
        # ====================================================================
        # COMPARE CONTENT
        # ====================================================================
        # Determine if content differs
        updates_available = current_normalized != latest_normalized
        
        result = {
            'updates_available': updates_available,
            'current_size': len(current_content) if current_content else 0,
            'latest_size': len(latest_content),
            'error': None
        }
        
        if updates_available:
            log_info("Updates available for: {0}".format(file_path))
        else:
            log_info("No updates available for: {0}".format(file_path))
        
        return result
        
    except Exception as e:
        log_error("Error checking for updates: {0}".format(str(e)))
        return {
            'updates_available': False,
            'error': str(e),
            'current_size': len(current_content) if current_content else 0,
            'latest_size': 0
        }


def extract_version_info(file_path):
    """
    Extract version information from a script's header comments.
    
    This function downloads a script and parses its header to extract
    version information, author details, and other metadata.
    
    Args:
        file_path (str): Path to script relative to Student-Shelf directory
    
    Returns:
        dict: Version information with keys:
              - 'version' (str): Version string if found
              - 'author' (str): Author information if found  
              - 'contact' (str): Contact information if found
              - 'description' (str): Brief description if found
              - 'file_path' (str): The original file path
              - 'error' (str): Error message if extraction failed
    """
    log_info("Extracting version info from: {0}".format(file_path))
    
    try:
        # ====================================================================
        # DOWNLOAD FILE CONTENT
        # ====================================================================
        content = download_file_content(file_path)
        if content is None:
            return {
                'version': 'Unknown',
                'author': 'Unknown', 
                'contact': 'Unknown',
                'description': 'Unknown',
                'file_path': file_path,
                'error': 'Failed to download file'
            }
        
        # ====================================================================
        # PARSE HEADER FOR VERSION INFORMATION
        # ====================================================================
        # Look for version info in the first 30 lines (header area)
        lines = content.split('\n')[:30]
        
        version_info = {
            'version': 'Unknown',
            'author': 'Unknown',
            'contact': 'Unknown', 
            'description': 'Unknown',
            'file_path': file_path,
            'error': None
        }
        
        # Search patterns for different types of information
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Look for version patterns
            if any(pattern in line_lower for pattern in ['version:', 'version ', 'v1.', 'v2.', 'v3.']):
                if version_info['version'] == 'Unknown':
                    version_info['version'] = line_stripped
            
            # Look for author information
            elif any(pattern in line_lower for pattern in ['created by', 'author:', 'by:']):
                if version_info['author'] == 'Unknown':
                    version_info['author'] = line_stripped
            
            # Look for contact information
            elif any(pattern in line_lower for pattern in ['contact:', 'email:', '@']):
                if version_info['contact'] == 'Unknown':
                    version_info['contact'] = line_stripped
            
            # Look for description (first substantial comment line)
            elif (line_stripped.startswith('#') or line_stripped.startswith('"""')) and len(line_stripped) > 10:
                if version_info['description'] == 'Unknown':
                    # Clean up the description
                    desc = line_stripped.lstrip('#').lstrip('"').strip()
                    if desc and not any(word in desc.lower() for word in ['import', 'copyright', 'license']):
                        version_info['description'] = desc
        
        log_success("Version info extracted from: {0}".format(file_path))
        return version_info
        
    except Exception as e:
        log_error("Error extracting version info: {0}".format(str(e)))
        return {
            'version': 'Unknown',
            'author': 'Unknown',
            'contact': 'Unknown',
            'description': 'Unknown',
            'file_path': file_path,
            'error': str(e)
        }


# ============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON OPERATIONS
# ============================================================================
# High-level convenience functions for common operations that combine
# multiple utility functions to provide simple interfaces for typical tasks.

def execute_core_script(script_name):
    """
    Execute a script from the core-scripts directory.
    
    Args:
        script_name (str): Name of the script file (e.g., "checklist.py")
    
    Returns:
        bool: True if successful, False otherwise
    """
    file_path = build_subdirectory_path('core', script_name)
    if file_path is None:
        return False
    
    return execute_script_from_github(file_path)


def execute_button_script(script_name):
    """
    Execute a script from the shelf-button-scripts directory.
    
    Args:
        script_name (str): Name of the script file
    
    Returns:
        bool: True if successful, False otherwise
    """
    file_path = build_subdirectory_path('buttons', script_name)
    if file_path is None:
        return False
    
    return execute_script_from_github(file_path)


def get_all_available_scripts():
    """
    Get information about all available scripts in the repository.
    
    Note: This function would require GitHub API access to enumerate files.
    For now, it returns known script information.
    
    Returns:
        dict: Dictionary of available scripts by category
    """
    # This is a simplified implementation
    # In a full implementation, this could use GitHub API to enumerate files
    return {
        'core-scripts': [
            'cmi_modeling_checklist.py'
        ],
        'shelf-button-scripts': [
            'FDMA2530_shelf_runChecklist.py',
            'update_shelf.py'
        ],
        'utilities': [
            'github_utilities.py'
        ]
    }


# ============================================================================
# SYSTEM DIAGNOSTICS AND TESTING
# ============================================================================
# Functions for testing the utility system and diagnosing issues.

def run_system_diagnostics():
    """
    Run comprehensive diagnostics of the GitHub utilities system.
    
    This function tests all major components and provides a detailed report
    of system status, useful for troubleshooting issues.
    
    Returns:
        dict: Diagnostic results with detailed status information
    """
    log_info("Starting GitHub Utilities diagnostics...")
    
    diagnostics = {
        'python_version': "{0}.{1}.{2}".format(*sys.version_info[:3]),
        'python_compatibility': 'Python 2' if IS_PYTHON_2 else 'Python 3',
        'github_connectivity': False,
        'url_construction': False,
        'download_test': False,
        'execution_test': False,
        'errors': []
    }
    
    try:
        # ====================================================================
        # TEST 1: GITHUB CONNECTIVITY
        # ====================================================================
        log_info("Testing GitHub connectivity...")
        diagnostics['github_connectivity'] = test_github_connectivity(timeout=10)
        
        if not diagnostics['github_connectivity']:
            diagnostics['errors'].append('GitHub connectivity failed')
        
        # ====================================================================
        # TEST 2: URL CONSTRUCTION
        # ====================================================================
        log_info("Testing URL construction...")
        test_url = build_github_raw_url("utilities/github_utilities.py")
        if test_url and 'github.com' in test_url:
            diagnostics['url_construction'] = True
        else:
            diagnostics['errors'].append('URL construction failed')
        
        # ====================================================================
        # TEST 3: DOWNLOAD FUNCTIONALITY
        # ====================================================================
        log_info("Testing download functionality...")
        if diagnostics['github_connectivity']:
            test_content = download_file_content("utilities/github_utilities.py")
            if test_content and len(test_content) > 100:
                diagnostics['download_test'] = True
            else:
                diagnostics['errors'].append('Download test failed')
        
        # ====================================================================
        # TEST 4: EXECUTION CAPABILITY
        # ====================================================================
        log_info("Testing execution capability...")
        # Test with a simple Python expression
        try:
            exec_code("test_var = 42", {'test_var': None})
            diagnostics['execution_test'] = True
        except Exception as e:
            diagnostics['errors'].append('Execution test failed: {0}'.format(str(e)))
        
    except Exception as e:
        diagnostics['errors'].append('Diagnostic error: {0}'.format(str(e)))
    
    # ========================================================================
    # GENERATE DIAGNOSTIC REPORT
    # ========================================================================
    log_info("=" * 60)
    log_info("FDMA 2530 GitHub Utilities Diagnostic Report")
    log_info("=" * 60)
    log_info("Python Version: {0}".format(diagnostics['python_version']))
    log_info("Compatibility: {0}".format(diagnostics['python_compatibility']))
    log_info("GitHub Connectivity: {0}".format('✓' if diagnostics['github_connectivity'] else '✗'))
    log_info("URL Construction: {0}".format('✓' if diagnostics['url_construction'] else '✗'))
    log_info("Download Test: {0}".format('✓' if diagnostics['download_test'] else '✗'))
    log_info("Execution Test: {0}".format('✓' if diagnostics['execution_test'] else '✗'))
    
    if diagnostics['errors']:
        log_warning("Errors encountered:")
        for error in diagnostics['errors']:
            log_warning("  - {0}".format(error))
    else:
        log_success("All diagnostics passed!")
    
    log_info("=" * 60)
    
    return diagnostics


# ============================================================================
# MODULE INITIALIZATION AND SELF-TEST
# ============================================================================
# Code that runs when the module is imported or executed directly.

def _initialize_module():
    """
    Initialize the module and perform basic validation.
    
    This function runs when the module is first imported to ensure
    everything is working correctly.
    """
    log_info("Initializing FDMA 2530 GitHub Utilities v1.0")
    log_info("Python {0} compatibility mode active".format(
        '2' if IS_PYTHON_2 else '3'))
    

# Run initialization when module is imported
_initialize_module()


# Self-test when run directly
if __name__ == "__main__":
    log_info("Running GitHub Utilities in self-test mode...")
    run_system_diagnostics()
