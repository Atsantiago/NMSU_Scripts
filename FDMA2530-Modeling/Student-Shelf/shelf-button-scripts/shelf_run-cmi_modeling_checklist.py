"""
FDMA 2530 Shelf - CMI Modeling Checklist Button Script - Version 1.0
====================================================================

This script is executed when the "Checklist" button is clicked on the FDMA 2530 
Maya shelf. It loads and runs the CMI Modeling Checklist tool directly from 
GitHub without requiring any local file downloads.

The script provides a seamless experience for students by:
- Automatically loading the latest version of the checklist from GitHub
- Working across all Maya versions (Python 2.7 through Python 3.x)
- Providing helpful error messages and troubleshooting information
- Falling back to direct download if utilities aren't available
- Offering clear feedback about the loading process

This script integrates with the FDMA 2530 GitHub repository structure and
uses the github_utilities.py module for robust GitHub operations.

Usage:
This script is called automatically when students click the "Checklist" button
on their FDMA 2530 shelf. Students don't need to run this manually.

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
GitHub: github.com/atsantiago
Repository: https://github.com/Atsantiago/NMSU_Scripts

Changelog:
v1.2 - Complete rewrite with:
     - Full Python 2/3 compatibility
     - Integration with github_utilities.py
     - Comprehensive error handling and user feedback
     - Direct execution without temporary files
     - Proper logging and status reporting
     - Fallback mechanisms for reliability
"""

# ============================================================================
# IMPORTS AND PYTHON 2/3 COMPATIBILITY
# ============================================================================
# Handle the differences between Python 2 and 3 to ensure this script works
# across all Maya versions from 2016 onwards.

import sys
import os
# Version information
__version__ = "1.2"
# User interface settings
SCRIPT_TITLE = "FDMA 2530 - CMI Modeling Checklist v{0}".format(__version__)
CONTACT_INFO = "Contact: asanti89@nmsu.edu"


# Python version detection for compatibility handling
PYTHON_VERSION = sys.version_info[0]
IS_PYTHON_2 = (PYTHON_VERSION == 2)
IS_PYTHON_3 = (PYTHON_VERSION >= 3)

# Import appropriate modules based on Python version
if IS_PYTHON_2:
    # Python 2 imports
    import urllib2 as urllib_request
    string_types = basestring
    
    def format_string(template, **kwargs):
        """Format strings for Python 2 compatibility."""
        return template.format(**kwargs)
        
    def exec_code(code, globals_dict):
        """Execute code with Python 2 compatibility."""
        exec(code, globals_dict)
        
else:
    # Python 3 imports
    import urllib.request as urllib_request
    string_types = str
    
    def format_string(template, **kwargs):
        """Format strings for Python 3."""
        return template.format(**kwargs)
        
    def exec_code(code, globals_dict):
        """Execute code with Python 3 compatibility."""
        exec(code, globals_dict)

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================
# Central configuration for the checklist loading system

# Repository configuration
REPOSITORY_URL = "https://github.com/Atsantiago/NMSU_Scripts"
REPOSITORY_BRANCH = "master"
BASE_PATH = "FDMA2530-Modeling/Student-Shelf"

# File paths within the repository structure
UTILITIES_PATH = "utilities/github_utilities.py"
CHECKLIST_PATH = "core-scripts/cmi_modeling_checklist.py"

# Network and timeout settings
DOWNLOAD_TIMEOUT = 20  # Seconds to wait for downloads
MAX_RETRY_ATTEMPTS = 2  # Number of times to retry failed operations

# User interface settings
SCRIPT_TITLE = "FDMA 2530 - CMI Modeling Checklist"
CONTACT_INFO = "Contact: asanti89@nmsu.edu"

# ============================================================================
# LOGGING AND USER FEEDBACK FUNCTIONS
# ============================================================================
# Centralized functions for providing consistent user feedback throughout
# the loading process, making it easy for students to understand what's happening.

def print_header():
    """Print a formatted header for the checklist loading process."""
    print("=" * 70)
    print(SCRIPT_TITLE)
    print("Loading latest version from GitHub...")
    print("=" * 70)


def print_status(message, is_success=False, is_error=False, is_warning=False):
    """
    Print a status message with consistent formatting.
    
    Args:
        message (str): The status message to display
        is_success (bool): Whether this is a success message
        is_error (bool): Whether this is an error message  
        is_warning (bool): Whether this is a warning message
    """
    if is_success:
        print("✓ SUCCESS: {0}".format(message))
    elif is_error:
        print("✗ ERROR: {0}".format(message))
    elif is_warning:
        print("⚠ WARNING: {0}".format(message))
    else:
        print("• INFO: {0}".format(message))


def print_footer(success=True):
    """
    Print a formatted footer with final status and contact information.
    
    Args:
        success (bool): Whether the overall operation was successful
    """
    print("=" * 70)
    if success:
        print("✓ CMI Modeling Checklist loaded successfully!")
        print("The checklist window should now be open.")
    else:
        print("✗ Failed to load the CMI Modeling Checklist")
        print("Please check your internet connection and try again.")
        print("")
        print("If problems persist:")
        print("• Verify GitHub access: https://github.com/Atsantiago/NMSU_Scripts")
        print("• Check Maya's Python console for detailed error messages")
        print("• {0}".format(CONTACT_INFO))
    print("=" * 70)


# ============================================================================
# GITHUB UTILITIES LOADING SYSTEM
# ============================================================================
# Functions for loading the GitHub utilities module, which provides all the
# core functionality for downloading and executing scripts from GitHub.

def load_github_utilities():
    """
    Load the GitHub utilities module dynamically from the repository.
    
    This function downloads and executes the utilities module directly from
    GitHub, ensuring we always have access to the latest utility functions.
    
    Returns:
        bool: True if utilities loaded successfully, False otherwise
    """
    try:
        print_status("Loading GitHub utilities from repository...")
        
        # ====================================================================
        # BUILD UTILITIES DOWNLOAD URL
        # ====================================================================
        # Construct the complete URL for the utilities file
        utilities_url = format_string(
            "{repo}/raw/{branch}/{base}/{path}",
            repo=REPOSITORY_URL.rstrip('/'),
            branch=REPOSITORY_BRANCH,
            base=BASE_PATH,
            path=UTILITIES_PATH
        )
        
        print_status("Downloading from: {0}".format(utilities_url))
        
        # ====================================================================
        # DOWNLOAD UTILITIES CONTENT
        # ====================================================================
        # Download the utilities file with timeout protection
        response = urllib_request.urlopen(utilities_url, timeout=DOWNLOAD_TIMEOUT)
        utilities_content = response.read()
        
        # Handle encoding for Python 3
        if IS_PYTHON_3 and isinstance(utilities_content, bytes):
            utilities_content = utilities_content.decode('utf-8')
        
        # ====================================================================
        # VALIDATE DOWNLOADED CONTENT
        # ====================================================================
        # Basic validation to ensure we got actual code
        if not utilities_content or len(utilities_content.strip()) < 100:
            print_status("Downloaded utilities content appears invalid", is_error=True)
            return False
        
        # Check for expected content markers
        if 'github_utilities' not in utilities_content.lower():
            print_status("Downloaded content doesn't appear to be utilities", is_warning=True)
        
        # ====================================================================
        # EXECUTE UTILITIES IN CURRENT NAMESPACE
        # ====================================================================
        # Execute the utilities code to make functions available
        exec_code(utilities_content, globals())
        
        print_status("GitHub utilities loaded successfully", is_success=True)
        return True
        
    except Exception as e:
        print_status("Failed to load GitHub utilities: {0}".format(str(e)), is_error=True)
        return False


def verify_utilities_available():
    """
    Verify that required utility functions are available.
    
    This function checks that the essential functions from github_utilities.py
    are available in the current namespace after loading.
    
    Returns:
        bool: True if all required functions are available, False otherwise
    """
    required_functions = [
        'download_file_content',
        'execute_script_from_github', 
        'test_github_connectivity',
        'build_github_raw_url'
    ]
    
    missing_functions = []
    
    for func_name in required_functions:
        if func_name not in globals():
            missing_functions.append(func_name)
    
    if missing_functions:
        print_status("Missing utility functions: {0}".format(
            ', '.join(missing_functions)), is_error=True)
        return False
    
    print_status("All required utility functions available", is_success=True)
    return True


# ============================================================================
# CHECKLIST EXECUTION SYSTEM
# ============================================================================
# Functions for loading and executing the CMI Modeling Checklist using the
# GitHub utilities or fallback methods.

def execute_checklist_via_utilities():
    """
    Execute the checklist using the GitHub utilities system.
    
    This is the preferred method as it uses the robust utilities framework
    with proper error handling and retry logic.
    
    Returns:
        bool: True if checklist executed successfully, False otherwise
    """
    try:
        print_status("Executing checklist via utilities system...")
        
        # Use the utility function to execute the checklist
        success = execute_script_from_github(CHECKLIST_PATH, globals())
        
        if success:
            print_status("Checklist executed successfully via utilities", is_success=True)
            return True
        else:
            print_status("Utilities execution failed", is_error=True)
            return False
            
    except NameError as e:
        print_status("Utilities function not available: {0}".format(str(e)), is_error=True)
        return False
    except Exception as e:
        print_status("Error during utilities execution: {0}".format(str(e)), is_error=True)
        return False


def execute_checklist_direct_fallback():
    """
    Execute the checklist using direct download as a fallback method.
    
    This method is used when the utilities system isn't available or fails.
    It provides a basic but reliable way to load the checklist.
    
    Returns:
        bool: True if checklist executed successfully, False otherwise
    """
    try:
        print_status("Attempting direct download fallback...")
        
        # ====================================================================
        # BUILD CHECKLIST DOWNLOAD URL
        # ====================================================================
        checklist_url = format_string(
            "{repo}/raw/{branch}/{base}/{path}",
            repo=REPOSITORY_URL.rstrip('/'),
            branch=REPOSITORY_BRANCH,
            base=BASE_PATH,
            path=CHECKLIST_PATH
        )
        
        print_status("Downloading checklist from: {0}".format(checklist_url))
        
        # ====================================================================
        # DOWNLOAD CHECKLIST CONTENT
        # ====================================================================
        response = urllib_request.urlopen(checklist_url, timeout=DOWNLOAD_TIMEOUT)
        checklist_content = response.read()
        
        # Handle encoding for Python 3
        if IS_PYTHON_3 and isinstance(checklist_content, bytes):
            checklist_content = checklist_content.decode('utf-8')
        
        # ====================================================================
        # VALIDATE AND EXECUTE CHECKLIST
        # ====================================================================
        if not checklist_content or len(checklist_content.strip()) < 500:
            print_status("Downloaded checklist content appears invalid", is_error=True)
            return False
        
        # Execute the checklist code
        exec_code(checklist_content, globals())
        
        print_status("Checklist executed successfully via fallback", is_success=True)
        return True
        
    except Exception as e:
        print_status("Fallback execution failed: {0}".format(str(e)), is_error=True)
        return False


# ============================================================================
# CONNECTIVITY AND PREREQUISITES TESTING
# ============================================================================
# Functions for testing system prerequisites before attempting to load
# the checklist, providing early feedback about potential issues.

def test_network_connectivity():
    """
    Test basic network connectivity to GitHub.
    
    This function performs a lightweight test to verify that GitHub is
    accessible before attempting larger downloads.
    
    Returns:
        bool: True if GitHub is accessible, False otherwise
    """
    try:
        print_status("Testing GitHub connectivity...")
        
        # Test with a simple HEAD request to the repository
        test_url = format_string(
            "{repo}/raw/{branch}/{base}/{path}",
            repo=REPOSITORY_URL.rstrip('/'),
            branch=REPOSITORY_BRANCH,
            base=BASE_PATH,
            path=UTILITIES_PATH
        )
        
        # Attempt to open the URL with a short timeout
        response = urllib_request.urlopen(test_url, timeout=5)
        
        # Check response
        if hasattr(response, 'getcode') and response.getcode() == 200:
            print_status("GitHub connectivity confirmed", is_success=True)
            return True
        else:
            print_status("GitHub responded but with unexpected status", is_warning=True)
            return True  # Might still work, so return True
            
    except Exception as e:
        print_status("GitHub connectivity test failed: {0}".format(str(e)), is_error=True)
        return False


def check_maya_environment():
    """
    Check that we're running in a proper Maya environment.
    
    This function verifies that Maya's Python environment is available
    and that we can access Maya commands.
    
    Returns:
        bool: True if Maya environment is available, False otherwise
    """
    try:
        # Try to import Maya commands
        import maya.cmds as cmds
        
        # Verify Maya is actually running (not just modules available)
        maya_version = cmds.about(version=True)
        
        print_status("Maya {0} environment confirmed".format(maya_version), is_success=True)
        return True
        
    except ImportError:
        print_status("Maya not available - running in standalone mode", is_warning=True)
        return False
    except Exception as e:
        print_status("Maya environment check failed: {0}".format(str(e)), is_warning=True)
        return False


# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================
# The main orchestration function that coordinates the entire checklist
# loading process, including error handling and user feedback.

def main():
    """
    Main execution function for loading the CMI Modeling Checklist.
    
    This function coordinates the entire process:
    1. Print welcome message and setup
    2. Test prerequisites (network, Maya environment)
    3. Load GitHub utilities
    4. Execute the checklist
    5. Provide final status and troubleshooting information
    
    Returns:
        bool: True if checklist loaded successfully, False otherwise
    """
    # ========================================================================
    # INITIALIZATION AND WELCOME MESSAGE
    # ========================================================================
    print_header()
    
    # Display Python version information for debugging
    print_status("Python {0}.{1}.{2} compatibility mode active".format(
        sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    
    # ========================================================================
    # PREREQUISITES TESTING
    # ========================================================================
    # Test basic system requirements before proceeding
    
    # Check Maya environment (non-critical)
    maya_available = check_maya_environment()
    
    # Test network connectivity (critical)
    if not test_network_connectivity():
        print_status("Network connectivity test failed", is_error=True)
        print_status("Please check your internet connection", is_error=True)
        print_footer(success=False)
        return False
    
    # ========================================================================
    # ATTEMPT TO LOAD GITHUB UTILITIES
    # ========================================================================
    # Try to load the utilities system for robust execution
    
    utilities_loaded = False
    
    for attempt in range(MAX_RETRY_ATTEMPTS):
        if attempt > 0:
            print_status("Retrying utilities load (attempt {0}/{1})...".format(
                attempt + 1, MAX_RETRY_ATTEMPTS))
        
        if load_github_utilities():
            if verify_utilities_available():
                utilities_loaded = True
                break
            else:
                print_status("Utilities loaded but verification failed", is_warning=True)
        
    # ========================================================================
    # EXECUTE CHECKLIST USING AVAILABLE METHOD
    # ========================================================================
    # Try utilities first, then fallback to direct download
    
    checklist_success = False
    
    if utilities_loaded:
        # Try execution via utilities system
        for attempt in range(MAX_RETRY_ATTEMPTS):
            if attempt > 0:
                print_status("Retrying checklist execution (attempt {0}/{1})...".format(
                    attempt + 1, MAX_RETRY_ATTEMPTS))
            
            if execute_checklist_via_utilities():
                checklist_success = True
                break
    
    # If utilities method failed, try direct fallback
    if not checklist_success:
        print_status("Trying direct download fallback method...", is_warning=True)
        
        for attempt in range(MAX_RETRY_ATTEMPTS):
            if attempt > 0:
                print_status("Retrying fallback execution (attempt {0}/{1})...".format(
                    attempt + 1, MAX_RETRY_ATTEMPTS))
            
            if execute_checklist_direct_fallback():
                checklist_success = True
                break
    
    # ========================================================================
    # FINAL STATUS AND USER FEEDBACK
    # ========================================================================
    # Provide clear feedback about the final result
    
    print_footer(success=checklist_success)
    
    # Additional debugging information if execution failed
    if not checklist_success:
        print("")
        print("TROUBLESHOOTING INFORMATION:")
        print("• Python Version: {0}.{1}.{2}".format(*sys.version_info[:3]))
        print("• Maya Available: {0}".format('Yes' if maya_available else 'No'))
        print("• Utilities Loaded: {0}".format('Yes' if utilities_loaded else 'No'))
        print("• Repository URL: {0}".format(REPOSITORY_URL))
        print("")
    
    return checklist_success


# ============================================================================
# SCRIPT EXECUTION ENTRY POINTS
# ============================================================================
# Handle execution whether the script is run directly or imported/executed
# from the Maya shelf button.

if __name__ == "__main__":
    # Direct execution (for testing)
    print("Running FDMA 2530 Checklist in direct execution mode...")
    main()
else:
    # Execution from shelf button (normal usage)
    main()
