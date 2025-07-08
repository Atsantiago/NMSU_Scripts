"""
Version Utilities for FDMA2530 Maya Shelf Tools

This module provides version management utilities for dynamically reading version information
from manifest files with robust fallback mechanisms. Inspired by GT Tools architecture and
following PEP 8 coding standards.

Author: Alexander T. Santiago
Version: Dynamic (Read from releases.json)
License: MIT
Repository: https://github.com/Atsantiago/NMSU_Scripts

Dependencies:
    - json (standard library)
    - urllib.request (standard library)
    - ssl (standard library)
    - logging (standard library)
    - os (standard library)
    - re (standard library)

Example Usage:
    >>> from fdma_shelf.utils.version_utils import get_fdma2530_version
    >>> version = get_fdma2530_version()
    >>> print(f"FDMA2530 Tools Version: {version}")
    FDMA2530 Tools Version: 2.0.1
"""

import json
import urllib.request
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
DEFAULT_FALLBACK_VERSION = "2.0.1"
HTTP_TIMEOUT_SECONDS = 5
SEMANTIC_VERSION_PATTERN = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$"

# Cache for version information to avoid repeated file reads
_VERSION_CACHE = {}


def handle_version_errors(fallback_version=DEFAULT_FALLBACK_VERSION):
    """
    Decorator to handle version-related errors gracefully with fallback support.
    
    This decorator provides consistent error handling across all version utility functions,
    ensuring that the system remains functional even when version detection fails.
    
    Args:
        fallback_version (str, optional): Version to return if the decorated function fails.
                                        Defaults to DEFAULT_FALLBACK_VERSION.
    
    Returns:
        function: Decorated function with error handling
    
    Example:
        @handle_version_errors("1.0.0")
        def get_version():
            # Function that might raise exceptions
            return read_version_from_file()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result and is_valid_semantic_version(result):
                    return result
                else:
                    logger.warning(f"Function {func.__name__} returned invalid version: {result}")
                    return fallback_version
            except Exception as e:
                logger.debug(f"Error in {func.__name__}: {str(e)}")
                logger.info(f"Using fallback version: {fallback_version}")
                return fallback_version
        return wrapper
    return decorator


def is_valid_semantic_version(version_string):
    """
    Validate if a version string follows semantic versioning (SemVer) conventions.
    
    Supports the standard MAJOR.MINOR.PATCH format with optional pre-release and build metadata.
    Based on SemVer 2.0.0 specification and GT Tools validation patterns.
    
    Args:
        version_string (str): Version string to validate
    
    Returns:
        bool: True if version string is valid semantic version, False otherwise
    
    Examples:
        >>> is_valid_semantic_version("1.2.3")
        True
        >>> is_valid_semantic_version("1.2.3-alpha.1")
        True
        >>> is_valid_semantic_version("1.2.3+build.1")
        True
        >>> is_valid_semantic_version("1.2")
        False
        >>> is_valid_semantic_version("invalid")
        False
    """
    if not isinstance(version_string, str):
        return False
    
    try:
        return bool(re.match(SEMANTIC_VERSION_PATTERN, version_string.strip()))
    except Exception as e:
        logger.debug(f"Error validating version string '{version_string}': {e}")
        return False


def parse_semantic_version(version_string):
    """
    Parse a semantic version string into its component parts.
    
    Following GT Tools patterns for version parsing with comprehensive error handling
    and validation. Returns a dictionary with major, minor, patch components and
    optional pre-release and build metadata.
    
    Args:
        version_string (str): Semantic version string to parse
    
    Returns:
        dict: Dictionary containing version components:
            - major (int): Major version number
            - minor (int): Minor version number  
            - patch (int): Patch version number
            - prerelease (str or None): Pre-release identifier
            - build (str or None): Build metadata
    
    Raises:
        ValueError: If version string is not a valid semantic version
    
    Examples:
        >>> parse_semantic_version("1.2.3")
        {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': None, 'build': None}
        >>> parse_semantic_version("1.2.3-alpha.1+build.2")
        {'major': 1, 'minor': 2, 'patch': 3, 'prerelease': 'alpha.1', 'build': 'build.2'}
    """
    if not is_valid_semantic_version(version_string):
        raise ValueError(f"Invalid semantic version: '{version_string}'. "
                        f"Expected format: MAJOR.MINOR.PATCH[-prerelease][+build]")
    
    match = re.match(SEMANTIC_VERSION_PATTERN, version_string.strip())
    if not match:
        raise ValueError(f"Failed to parse version string: '{version_string}'")
    
    major, minor, patch, prerelease, build = match.groups()
    
    return {
        'major': int(major),
        'minor': int(minor), 
        'patch': int(patch),
        'prerelease': prerelease,
        'build': build
    }


def compare_versions(version_a, version_b):
    """
    Compare two semantic version strings following SemVer precedence rules.
    
    Implements semantic version comparison logic as defined in SemVer 2.0.0 specification.
    Pre-release versions have lower precedence than normal versions. Build metadata
    is ignored during comparison.
    
    Args:
        version_a (str): First version string
        version_b (str): Second version string
    
    Returns:
        int: -1 if version_a < version_b
             0 if version_a == version_b  
             1 if version_a > version_b
    
    Examples:
        >>> compare_versions("1.0.0", "2.0.0")
        -1
        >>> compare_versions("2.0.0", "1.0.0")
        1
        >>> compare_versions("1.0.0", "1.0.0")
        0
        >>> compare_versions("1.0.0-alpha", "1.0.0")
        -1
    """
    try:
        parsed_a = parse_semantic_version(version_a)
        parsed_b = parse_semantic_version(version_b)
    except ValueError as e:
        logger.error(f"Version comparison failed: {e}")
        return 0
    
    # Compare major, minor, patch
    for component in ['major', 'minor', 'patch']:
        if parsed_a[component] < parsed_b[component]:
            return -1
        elif parsed_a[component] > parsed_b[component]:
            return 1
    
    # Handle pre-release comparison
    pre_a = parsed_a['prerelease']
    pre_b = parsed_b['prerelease']
    
    if pre_a is None and pre_b is None:
        return 0
    elif pre_a is None:
        return 1  # Normal version > pre-release
    elif pre_b is None:
        return -1  # Pre-release < normal version
    else:
        # Both have pre-release, compare lexically
        if pre_a < pre_b:
            return -1
        elif pre_a > pre_b:
            return 1
        else:
            return 0


def get_current_file_directory():
    """
    Get the directory where this version_utils.py file is located.
    
    Provides a reliable way to determine the base path for relative file operations,
    following GT Tools patterns for path resolution.
    
    Returns:
        str: Absolute path to the directory containing this file
    
    Example:
        >>> get_current_file_directory()
        '/path/to/FDMA2530-Modeling/Student-Shelf/fdma_shelf/utils'
    """
    return os.path.dirname(os.path.abspath(__file__))


def find_manifest_file():
    """
    Locate the releases.json manifest file by searching up the directory tree.
    
    Searches from the current file location up through parent directories until
    it finds the releases.json file. This provides flexibility for different
    deployment scenarios while maintaining reliability.
    
    Returns:
        str or None: Absolute path to releases.json file if found, None otherwise
    
    Example:
        >>> find_manifest_file()
        '/path/to/FDMA2530-Modeling/releases.json'
    """
    current_dir = get_current_file_directory()
    
    # Search up the directory tree for releases.json
    max_levels = 10  # Prevent infinite loops
    for _ in range(max_levels):
        manifest_path = os.path.join(current_dir, MANIFEST_FILENAME)
        
        if os.path.isfile(manifest_path):
            logger.debug(f"Found manifest file at: {manifest_path}")
            return manifest_path
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached filesystem root
            break
        current_dir = parent_dir
    
    logger.warning(f"Manifest file '{MANIFEST_FILENAME}' not found in directory tree")
    return None


@handle_version_errors()
def read_manifest_from_file():
    """
    Read and parse the releases.json manifest file from the local filesystem.
    
    Provides the primary method for reading version information from the local
    manifest file. Includes comprehensive error handling and validation.
    
    Returns:
        dict or None: Parsed manifest data if successful, None if file not found or invalid
    
    Raises:
        Exception: Re-raised by decorator as fallback version
    """
    manifest_path = find_manifest_file()
    if not manifest_path:
        raise FileNotFoundError(f"Manifest file '{MANIFEST_FILENAME}' not found")
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as file:
            manifest_data = json.load(file)
            
        # Validate manifest structure
        required_fields = ['current_version', 'tool_name']
        for field in required_fields:
            if field not in manifest_data:
                raise ValueError(f"Invalid manifest: missing required field '{field}'")
        
        logger.debug(f"Successfully read manifest from: {manifest_path}")
        return manifest_data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest file: {e}")
    except Exception as e:
        raise Exception(f"Failed to read manifest file: {e}")


@handle_version_errors()
def read_manifest_from_url(manifest_url=None):
    """
    Read and parse the releases.json manifest file from a remote URL.
    
    Provides a fallback method for reading version information when local file
    is not available. Useful for development scenarios or when tools are run
    from different locations.
    
    Args:
        manifest_url (str, optional): URL to the manifest file. If None, constructs
                                    default GitHub raw content URL.
    
    Returns:
        dict or None: Parsed manifest data if successful, None if URL not accessible
    
    Raises:
        Exception: Re-raised by decorator as fallback version
    """
    if manifest_url is None:
        # Default GitHub raw content URL for FDMA2530 tools
        manifest_url = ("https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/"
                       "master/cmi-tools/FDMA2530-Modeling/releases.json")
    
    try:
        # Create SSL context for HTTPS requests
        ctx = ssl.create_default_context()
        
        with urllib.request.urlopen(manifest_url, timeout=HTTP_TIMEOUT_SECONDS, context=ctx) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {response.reason}")
            
            manifest_data = json.loads(response.read().decode('utf-8'))
        
        # Validate manifest structure
        required_fields = ['current_version', 'tool_name']
        for field in required_fields:
            if field not in manifest_data:
                raise ValueError(f"Invalid manifest: missing required field '{field}'")
        
        logger.debug(f"Successfully read manifest from URL: {manifest_url}")
        return manifest_data
        
    except urllib.error.URLError as e:
        raise Exception(f"Failed to access manifest URL: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in remote manifest: {e}")
    except Exception as e:
        raise Exception(f"Failed to read remote manifest: {e}")


def get_manifest_data():
    """
    Get manifest data using a cascade of fallback methods.
    
    Attempts to read manifest data in order of preference:
    1. Local file (fastest, most reliable)
    2. Remote URL (fallback for development/distributed scenarios)
    3. Cache (if available from previous successful reads)
    
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
        logger.debug(f"Local manifest read failed: {e}")
    
    # Try remote URL as fallback
    try:
        manifest_data = read_manifest_from_url()
        if manifest_data:
            _VERSION_CACHE['manifest'] = manifest_data  # Cache successful read
            return manifest_data
    except Exception as e:
        logger.debug(f"Remote manifest read failed: {e}")
    
    # Use cached data if available
    if 'manifest' in _VERSION_CACHE:
        logger.info("Using cached manifest data")
        return _VERSION_CACHE['manifest']
    
    logger.warning("All manifest read methods failed")
    return None


def get_fdma2530_version():
    """
    Get the current version of FDMA2530 Maya Shelf Tools from the manifest.
    Returns the version string (e.g., "2.0.5") or fallback version if manifest unavailable or invalid.
    """
    cache_key = 'fdma2530_version'
    if cache_key in _VERSION_CACHE:
        cached_version = _VERSION_CACHE[cache_key]
        if is_valid_semantic_version(cached_version):
            return cached_version
    try:
        manifest_data = read_manifest_from_file()
        if not manifest_data:
            raise Exception("Unable to read manifest data from any source")
        current_version = manifest_data.get('current_version')
        if not current_version or not is_valid_semantic_version(current_version):
            raise ValueError(f"Invalid version format in manifest: '{current_version}'")
        _VERSION_CACHE[cache_key] = current_version
        logger.debug(f"Retrieved FDMA2530 version: {current_version}")
        return current_version
    except Exception as e:
        logger.warning(f"get_fdma2530_version failed: {e}")
        return DEFAULT_FALLBACK_VERSION


def get_tool_info():
    """
    Get comprehensive tool information from the manifest.
    
    Provides additional metadata about the FDMA2530 tools beyond just version
    information. Useful for about dialogs, debugging, and system information.
    
    Returns:
        dict: Dictionary containing tool information with keys:
            - version (str): Current version
            - tool_name (str): Name of the tool
            - description (str): Tool description
            - author (str): Tool author
            - Other fields as available in manifest
    
    Example:
        >>> info = get_tool_info()
        >>> print(f"{info['tool_name']} v{info['version']}")
        FDMA2530-Modeling v2.0.1
    """
    default_info = {
        'version': DEFAULT_FALLBACK_VERSION,
        'tool_name': 'FDMA2530-Modeling',
        'description': 'Maya shelf tools for FDMA 2530 - Introduction to 3D Modeling',
        'author': 'Alexander T. Santiago'
    }
    
    try:
        manifest_data = get_manifest_data()
        if not manifest_data:
            return default_info
        
        # Extract available information from manifest
        tool_info = default_info.copy()
        tool_info.update({
            'version': manifest_data.get('current_version', default_info['version']),
            'tool_name': manifest_data.get('tool_name', default_info['tool_name']),
            'description': manifest_data.get('description', default_info['description']),
            'author': manifest_data.get('author', default_info['author']),
            'repository': manifest_data.get('repository', ''),
            'license': manifest_data.get('license', 'MIT')
        })
        
        return tool_info
        
    except Exception as e:
        logger.debug(f"Error retrieving tool info: {e}")
        return default_info


def clear_version_cache():
    """
    Clear the internal version cache.
    
    Useful for testing, debugging, or when you need to force a fresh read
    of version information from manifest sources.
    
    Example:
        >>> clear_version_cache()
        >>> version = get_fdma2530_version()  # Will read fresh from manifest
    """
    global _VERSION_CACHE
    _VERSION_CACHE.clear()
    logger.debug("Version cache cleared")


# Module initialization and validation
if __name__ == "__main__":
    # Self-test when module is run directly
    logger.setLevel(logging.DEBUG)
    
    print("FDMA2530 Version Utils Self-Test")
    print("=" * 40)
    
    # Test version retrieval
    version = get_fdma2530_version()
    print(f"Current Version: {version}")
    
    # Test tool info
    info = get_tool_info()
    print(f"Tool Name: {info['tool_name']}")
    print(f"Description: {info['description']}")
    print(f"Author: {info['author']}")
    
    # Test version validation
    test_versions = ["1.2.3", "1.2.3-alpha", "1.2.3+build", "invalid"]
    print("\nVersion Validation Tests:")
    for test_ver in test_versions:
        is_valid = is_valid_semantic_version(test_ver)
        print(f"  {test_ver}: {'✓' if is_valid else '✗'}")
    
    # Test version comparison
    print("\nVersion Comparison Tests:")
    comparisons = [
        ("1.0.0", "2.0.0", -1),
        ("2.0.0", "1.0.0", 1),
        ("1.0.0", "1.0.0", 0),
        ("1.0.0-alpha", "1.0.0", -1)
    ]
    for v1, v2, expected in comparisons:
        result = compare_versions(v1, v2)
        status = "✓" if result == expected else "✗"
        print(f"  {v1} vs {v2}: {result} (expected {expected}) {status}")
    
    print("\nSelf-test completed!")
