"""
Prof-Tools for Maya - Instructor Grading and Utility Tools

A comprehensive suite of tools for grading and managing Maya assignments.

Defines core metadata, versioning, and compatibility checks for the Prof-Tools Maya instructor toolkit.

Created by: Alexander T. Santiago
Version: Dynamic (Read from releases.json)
License: MIT
Repository: https://github.com/Atsantiago/NMSU_Scripts
"""

# Python 2/3 compatibility imports
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
import logging

# Python version compatibility check
if sys.version_info.major < 3:
    user_version = "{}.{}.{}".format(
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro
    )
    error = (
        "Incompatible Python Version. Expected to find 3+. "
        "Found version: " + user_version + ".\n"
        "For Python 2, use an older version of Prof-Tools. "
        "(e.g. older Maya versions)\n"
    )
    raise ImportError(error)

# Simple fallback version for reliable import
__version_tuple__ = (0, 3, 8)   # MAJOR, MINOR, PATCH
__version__ = '.'.join(map(str, __version_tuple__))

# Try to get dynamic version from manifest, but don't fail import if it doesn't work
try:
    from .core.version_utils import get_prof_tools_version, get_version_tuple
    _dynamic_version = get_prof_tools_version()
    _dynamic_version_tuple = get_version_tuple()
    if _dynamic_version and _dynamic_version_tuple:
        __version__ = _dynamic_version
        __version_tuple__ = _dynamic_version_tuple
        # Log successful dynamic version loading
        import logging
        logger = logging.getLogger(__name__)
        logger.debug("Using dynamic version from manifest: {0}".format(__version__))
except (ImportError, Exception) as e:
    # Use fallback version if dynamic version loading fails
    # Log the fallback silently during import to avoid import issues
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Using fallback version due to: {0}".format(str(e)))

__version_suffix__ = ''         # e.g. '-alpha', '-beta', '-rc1'

__title__       = 'Prof-Tools'
__author__      = 'Alexander T. Santiago - https://github.com/Atsantiago'
__description__ = 'Maya instructor tools for grading and assignment management'
__license__     = 'MIT'
__url__         = 'https://github.com/Atsantiago/NMSU_Scripts'  # for updater

# Public API
__all__ = [
    '__version__',
    '__version_tuple__',
    '__title__',
    '__author__',
    '__description__',
    '__license__',
    '__url__',             # expose URL for updater
    'get_version',
    'get_version_info',
    'get_package_path',
    'is_maya_available',
    'get_maya_version',
    'get_python_version',
    'get_system_info'
]

# Configure package logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_version():
    """
    Returns the current version string.
    
    This function provides access to the dynamically loaded version
    from the manifest file, with fallback to the static version if
    the dynamic loading fails.
    
    Returns:
        str: Version string (e.g. "0.1.0") sourced from releases.json
             or fallback version if manifest unavailable
    
    Examples:
        >>> import prof
        >>> prof.get_version()
        '0.1.0'
    """
    return __version__

def get_version_info():
    """
    Returns detailed version and package information.
    
    Provides comprehensive metadata about the prof-tools package,
    including version information sourced from the manifest file
    and other package details.
    
    Returns:
        dict: Dictionary containing version metadata with keys:
            - version (str): Current version string
            - version_tuple (tuple): Version as tuple of integers
            - title (str): Package title
            - author (str): Package author
            - description (str): Package description
            - license (str): Package license
            - url (str): Package repository URL
    
    Examples:
        >>> import prof
        >>> info = prof.get_version_info()
        >>> print(f"{info['title']} v{info['version']}")
        Prof-Tools v0.1.0
    """
    return {
        'version': __version__,
        'version_tuple': __version_tuple__,
        'title': __title__,
        'author': __author__,
        'description': __description__,
        'license': __license__,
        'url': __url__
    }

def get_package_path():
    """
    Returns the absolute path to this package directory.
    
    Provides a reliable way to determine the installation location
    of the prof-tools package for file operations and debugging.
    
    Returns:
        str: Path to the prof package directory
    
    Examples:
        >>> import prof
        >>> prof.get_package_path()
        '/path/to/prof-tools/prof'
    """
    return os.path.dirname(os.path.abspath(__file__))

def is_maya_available():
    """
    Checks if Maya Python modules are available in the current environment.
    
    This function tests whether the Maya Python API can be imported,
    which indicates if the code is running within Maya or if Maya's
    Python environment is properly configured.
    
    Returns:
        bool: True if Maya is available, False otherwise
    
    Examples:
        >>> import prof
        >>> if prof.is_maya_available():
        ...     print("Running in Maya environment")
        ... else:
        ...     print("Maya not available - limited functionality")
    """
    try:
        import maya.cmds
        return True
    except ImportError:
        return False

def get_maya_version():
    """
    Gets the current Maya version if available.
    
    Attempts to query Maya for its version information. This is useful
    for compatibility checks and debugging issues related to specific
    Maya versions.
    
    Returns:
        str: Maya version string, or empty string if not available
    
    Examples:
        >>> import prof
        >>> maya_ver = prof.get_maya_version()
        >>> if maya_ver:
        ...     print(f"Maya version: {maya_ver}")
        ... else:
        ...     print("Maya not available")
    """
    if not is_maya_available():
        return ""
    try:
        import maya.cmds as cmds
        return cmds.about(version=True)
    except Exception:
        return ""

def get_python_version():
    """
    Gets the current Python version information.
    
    Provides detailed information about the Python interpreter being
    used, which is essential for compatibility and debugging purposes.
    
    Returns:
        dict: Dictionary containing Python version info with keys:
            - version (str): Full version string
            - version_info (tuple): Version info tuple
            - major (int): Major version number
            - minor (int): Minor version number
            - micro (int): Micro version number
    
    Examples:
        >>> import prof
        >>> py_info = prof.get_python_version()
        >>> print(f"Python {py_info['major']}.{py_info['minor']}")
        Python 3.9
    """
    return {
        'version': sys.version,
        'version_info': sys.version_info,
        'major': sys.version_info.major,
        'minor': sys.version_info.minor,
        'micro': sys.version_info.micro
    }

def get_system_info():
    """
    Returns system and environment information for debugging.
    
    Compiles comprehensive information about the runtime environment,
    including Python version, Maya availability, package location,
    and prof-tools version. This is particularly useful for
    troubleshooting and support purposes.
    
    Returns:
        dict: Dictionary containing system information with keys:
            - platform (str): System platform identifier
            - python_version (dict): Python version information
            - maya_version (str): Maya version if available
            - maya_available (bool): Whether Maya is available
            - package_path (str): Path to prof package
            - prof_tools_version (str): Current prof-tools version
    
    Examples:
        >>> import prof
        >>> system_info = prof.get_system_info()
        >>> for key, value in system_info.items():
        ...     print(f"{key}: {value}")
    """
    return {
        'platform': sys.platform,
        'python_version': get_python_version(),
        'maya_version': get_maya_version(),
        'maya_available': is_maya_available(),
        'package_path': get_package_path(),
        'prof_tools_version': get_version()
    }

def _initialize_package():
    """
    Initialize the prof-tools package with compatibility checks.
    
    Performs startup checks and initialization tasks when the package
    is imported. This includes Python version verification and Maya
    availability detection with appropriate warnings.
    
    Called automatically on import - not intended for direct use.
    
    Raises:
        ImportError: If Python version is incompatible (already checked above)
        Exception: If critical initialization fails
    """
    try:
        # Verify Python version (already checked above, but log it)
        logger.info("Prof-Tools version %s initialization", __version__)
        logger.debug("Python version: %s", sys.version)
        
        # Log Maya availability status
        if is_maya_available():
            maya_version = get_maya_version()
            logger.info("Maya %s detected", maya_version if maya_version else "version unknown")
            
            # Check for and handle temporary installations
            try:
                from .core.tools.dev_prefs import get_prefs
                prefs = get_prefs()
                if prefs.check_and_revert_temp_install():
                    logger.info("Temporary installation detected and reverted on startup")
            except Exception as e:
                logger.debug("Temporary installation check failed: %s", e)
                # Don't fail the entire initialization for this
            
            # Initialize silent update checking if in Maya environment
            try:
                from .core.tools.silent_updater import initialize_silent_updates
                initialize_silent_updates()
                logger.debug("Silent update system initialized")
            except Exception as e:
                logger.debug("Silent update initialization failed: %s", e)
                # Don't fail the entire initialization for this
                
        else:
            logger.warning("Maya modules not found; UI features will be limited.")
            
        # Log package location for debugging
        logger.debug("Prof-Tools package location: %s", get_package_path())
        
    except Exception as e:
        logger.error("Failed to initialize prof-tools package: %s", e)
        raise

# Automatic initialization when package is imported
_initialize_package()
