"""
Version Utilities for Prof-Tools Maya Menu System

This module provides version management utilities for dynamically reading version information
from the releases.json manifest file. Follows the FDMA2530 pattern for consistency across
NMSU Scripts while allowing individual tools to maintain their own versions.

Author: Alexander T. Santiago
Version: Dynamic (Read from releases.json)
License: MIT
Repository: https://github.com/Atsantiago/NMSU_Scripts

Dependencies:
    - json (standard library)
    - urllib.request/urllib2 (standard library)
    - ssl (standard library)
    - logging (standard library)
    - os (standard library)
    - re (standard library)

Example Usage:
    >>> from prof.core.version_utils import get_prof_tools_version
    >>> version = get_prof_tools_version()
    >>> print("Prof-Tools Version: {0}".format(version))
    Prof-Tools Version: 0.2.0
"""

import json
try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    # Python 2 fallback
    from urllib2 import urlopen
    from urllib2 import URLError
import ssl
import logging
import os
import re
from functools import wraps

# Logging Configuration
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Constants - Following GT Tools naming conventions
MANIFEST_FILENAME = "releases.json"
DEFAULT_FALLBACK_VERSION = "0.1.0"
HTTP_TIMEOUT_SECONDS = 5
SEMANTIC_VERSION_PATTERN = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$"

# Cache for version information to avoid repeated file reads
_VERSION_CACHE = {}


def handle_version_errors(fallback_version=DEFAULT_FALLBACK_VERSION):
    """
    Decorator to handle version-related errors gracefully with fallback support.
    
    This decorator provides consistent error handling across all version utility functions,
    ensuring that the instructor tools remain functional even when version detection fails.
    
    Args:
        fallback_version (str, optional): Version to return if the decorated function fails.
                                        Defaults to DEFAULT_FALLBACK_VERSION.
    
    Returns:
        function: Decorated function with error handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result and is_valid_semantic_version(result):
                    return result
                else:
                    logger.warning("Function {0} returned invalid version: {1}".format(func.__name__, result))
                    return fallback_version
            except Exception as e:
                logger.debug("Error in {0}: {1}".format(func.__name__, str(e)))
                logger.info("Using fallback version: {0}".format(fallback_version))
                return fallback_version
        return wrapper
    return decorator


def is_valid_semantic_version(version_string):
    """
    Validate if a version string follows semantic versioning (SemVer) conventions.
    
    Args:
        version_string (str): Version string to validate
    
    Returns:
        bool: True if version string is valid semantic version, False otherwise
    """
    if not isinstance(version_string, str):
        return False
    
    try:
        return bool(re.match(SEMANTIC_VERSION_PATTERN, version_string.strip()))
    except Exception as e:
        logger.debug("Error validating version string '{0}': {1}".format(version_string, e))
        return False


def parse_semantic_version(version_string):
    """
    Parse a semantic version string into its component parts.
    
    Args:
        version_string (str): Semantic version string to parse
    
    Returns:
        dict: Dictionary containing version components
    
    Raises:
        ValueError: If version string is not a valid semantic version
    """
    if not is_valid_semantic_version(version_string):
        raise ValueError("Invalid semantic version: '{0}'".format(version_string))
    
    match = re.match(SEMANTIC_VERSION_PATTERN, version_string.strip())
    if not match:
        raise ValueError("Failed to parse version string: '{0}'".format(version_string))
    
    major, minor, patch, prerelease, build = match.groups()
    
    return {
        'major': int(major),
        'minor': int(minor), 
        'patch': int(patch),
        'prerelease': prerelease,
        'build': build
    }


def get_current_file_directory():
    """
    Get the directory containing this version_utils.py file.
    
    Returns:
        str: Absolute path to the directory containing this file
    """
    return os.path.dirname(os.path.abspath(__file__))


def find_manifest_file():
    """
    Locate the releases.json manifest file by searching up the directory tree.
    
    Returns:
        str or None: Absolute path to releases.json file if found, None otherwise
    """
    current_dir = get_current_file_directory()
    
    # Search up the directory tree for releases.json
    max_levels = 10  # Prevent infinite loops
    for _ in range(max_levels):
        manifest_path = os.path.join(current_dir, MANIFEST_FILENAME)
        
        if os.path.isfile(manifest_path):
            logger.debug("Found manifest file at: {0}".format(manifest_path))
            return manifest_path
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached filesystem root
            break
        current_dir = parent_dir
    
    logger.warning("Manifest file '{0}' not found in directory tree".format(MANIFEST_FILENAME))
    return None


def read_manifest_from_file():
    """
    Read and parse the releases.json manifest file from the local filesystem.
    
    Returns:
        dict or None: Parsed manifest data if successful, None if file not found or invalid
    
    Raises:
        Exception: For file not found or invalid JSON
    """
    manifest_path = find_manifest_file()
    if not manifest_path:
        raise FileNotFoundError("Manifest file '{0}' not found".format(MANIFEST_FILENAME))
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as file:
            manifest_data = json.load(file)
            
        # Validate manifest structure
        required_fields = ['current_version', 'tool_name']
        for field in required_fields:
            if field not in manifest_data:
                raise ValueError("Invalid manifest: missing required field '{0}'".format(field))
        
        logger.debug("Successfully read manifest from: {0}".format(manifest_path))
        return manifest_data
        
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON in manifest file: {0}".format(e))
    except Exception as e:
        raise Exception("Failed to read manifest file: {0}".format(e))


def read_manifest_from_url(manifest_url=None):
    """
    Read and parse the releases.json manifest file from a remote URL.
    
    Args:
        manifest_url (str, optional): URL to the manifest file
    
    Returns:
        dict or None: Parsed manifest data if successful, None if URL not accessible
    
    Raises:
        Exception: For HTTP errors or invalid JSON
    """
    if manifest_url is None:
        # Default GitHub raw content URL for prof-tools
        manifest_url = ("https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/"
                       "master/prof-tools/releases.json")
    
    try:
        # Create SSL context for HTTPS requests
        ctx = ssl.create_default_context()
        
        with urlopen(manifest_url, timeout=HTTP_TIMEOUT_SECONDS, context=ctx) as response:
            if response.status != 200:
                raise Exception("HTTP {0}: {1}".format(response.status, response.reason))
            
            manifest_data = json.loads(response.read().decode('utf-8'))
        
        # Validate manifest structure
        required_fields = ['current_version', 'tool_name']
        for field in required_fields:
            if field not in manifest_data:
                raise ValueError("Invalid manifest: missing required field '{0}'".format(field))
        
        logger.debug("Successfully read manifest from URL: {0}".format(manifest_url))
        return manifest_data
        
    except URLError as e:
        raise Exception("Failed to access manifest URL: {0}".format(e))
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON in remote manifest: {0}".format(e))
    except Exception as e:
        raise Exception("Failed to read remote manifest: {0}".format(e))


def get_manifest_data():
    """
    Get manifest data using a cascade of fallback methods.
    
    Returns:
        dict or None: Manifest data from the first successful method, None if all fail
    """
    # Try local file first (most reliable)
    try:
        manifest_data = read_manifest_from_file()
        if manifest_data:
            _VERSION_CACHE['manifest'] = manifest_data  # Cache successful read
            return manifest_data
    except Exception as e:
        logger.debug("Local manifest read failed: {0}".format(e))
    
    # Try remote URL as fallback
    try:
        manifest_data = read_manifest_from_url()
        if manifest_data:
            _VERSION_CACHE['manifest'] = manifest_data  # Cache successful read
            return manifest_data
    except Exception as e:
        logger.debug("Remote manifest read failed: {0}".format(e))
    
    # Use cached data if available
    if 'manifest' in _VERSION_CACHE:
        logger.info("Using cached manifest data")
        return _VERSION_CACHE['manifest']
    
    logger.warning("All manifest read methods failed")
    return None


@handle_version_errors()
def get_prof_tools_version():
    """
    Get the current version of Prof-Tools Maya Menu System from the manifest.
    
    Returns:
        str: Current version string (e.g., "0.2.0") or fallback version if manifest unavailable
    """
    # Check cache first for performance
    cache_key = 'prof_tools_version'
    if cache_key in _VERSION_CACHE:
        cached_version = _VERSION_CACHE[cache_key]
        if is_valid_semantic_version(cached_version):
            return cached_version
    
    manifest_data = get_manifest_data()
    if not manifest_data:
        raise Exception("Unable to read manifest data from any source")
    
    current_version = manifest_data.get('current_version')
    if not current_version:
        raise ValueError("Manifest does not contain 'current_version' field")
    
    if not is_valid_semantic_version(current_version):
        raise ValueError("Invalid version format in manifest: '{0}'".format(current_version))
    
    # Cache the successful result
    _VERSION_CACHE[cache_key] = current_version
    
    logger.debug("Retrieved Prof-Tools version: {0}".format(current_version))
    return current_version


def get_version_tuple():
    """
    Get the current version as a tuple of integers for easy comparison.
    
    Returns:
        tuple: Version as (major, minor, patch) integers
    """
    try:
        version_string = get_prof_tools_version()
        parsed = parse_semantic_version(version_string)
        return (parsed['major'], parsed['minor'], parsed['patch'])
    except Exception as e:
        logger.debug("Error creating version tuple: {0}".format(e))
        # Parse fallback version
        parsed = parse_semantic_version(DEFAULT_FALLBACK_VERSION)
        return (parsed['major'], parsed['minor'], parsed['patch'])


def get_tool_info():
    """
    Get comprehensive tool information from the manifest.
    
    Returns:
        dict: Dictionary containing tool information
    """
    try:
        manifest_data = get_manifest_data()
        if not manifest_data:
            # Return fallback info
            return {
                'version': DEFAULT_FALLBACK_VERSION,
                'version_tuple': get_version_tuple(),
                'tool_name': 'prof-tools',
                'description': 'Maya instructor tools for grading and assignment management',
                'author': 'Alexander T. Santiago'
            }
        
        # Extract version information
        version = get_prof_tools_version()
        version_tuple = get_version_tuple()
        
        # Combine manifest data with version info
        tool_info = manifest_data.copy()
        tool_info['version'] = version
        tool_info['version_tuple'] = version_tuple
        
        return tool_info
        
    except Exception as e:
        logger.warning("Error getting tool info: {0}".format(e))
        # Return fallback info
        return {
            'version': DEFAULT_FALLBACK_VERSION,
            'version_tuple': (0, 1, 0),
            'tool_name': 'prof-tools',
            'description': 'Maya instructor tools for grading and assignment management',
            'author': 'Alexander T. Santiago'
        }


def get_individual_tool_version(tool_name, tool_module=None):
    """
    Get version for an individual tool within prof-tools.
    
    Some tools may want to maintain their own version numbers independent of the
    main prof-tools version. This function checks for individual tool versions
    following GT Tools patterns.
    
    Args:
        tool_name (str): Name of the tool
        tool_module (module, optional): Tool module to check for __version__
    
    Returns:
        str: Tool version if found, otherwise returns main prof-tools version
    """
    try:
        # If module is provided, check for __version__ attribute
        if tool_module and hasattr(tool_module, '__version__'):
            tool_version = getattr(tool_module, '__version__')
            if is_valid_semantic_version(tool_version):
                logger.debug("Found individual version for {0}: {1}".format(tool_name, tool_version))
                return tool_version
        
        # Fall back to main prof-tools version
        main_version = get_prof_tools_version()
        logger.debug("Using main prof-tools version for {0}: {1}".format(tool_name, main_version))
        return main_version
        
    except Exception as e:
        logger.warning("Error getting tool version for {0}: {1}".format(tool_name, e))
        return DEFAULT_FALLBACK_VERSION


def clear_version_cache():
    """
    Clear the internal version cache.
    
    Useful for testing or when you want to force fresh reads from the manifest.
    """
    global _VERSION_CACHE
    _VERSION_CACHE.clear()
    logger.debug("Version cache cleared")
