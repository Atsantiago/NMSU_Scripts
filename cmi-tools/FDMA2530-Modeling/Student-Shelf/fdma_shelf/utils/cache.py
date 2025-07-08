from __future__ import absolute_import, print_function
"""
Cache management utilities for FDMA 2530 shelf system.

Handles reading and writing shelf configuration cache files,
hash comparison for update detection, and local file management.

Functions
---------
read_local_config() -> dict or None
    Read the cached shelf configuration from user scripts directory.

write_local_config(config_data) -> bool
    Write shelf configuration to cache file.

get_config_hash(config_text) -> str
    Generate MD5 hash of configuration text for change detection.

cache_exists() -> bool
    Check if local cache file exists.

clear_cache() -> bool
    Delete the local cache file.
"""

import os
import json
import hashlib

import maya.cmds as cmds


# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

_CACHE_FILENAME = "shelf_config_cache.json"


# ------------------------------------------------------------------
# Path helpers
# ------------------------------------------------------------------

def _get_cache_path():
    """Return full path to the cache file in user scripts directory."""
    scripts_dir = cmds.internalVar(userScriptDir=True)
    return os.path.join(scripts_dir, _CACHE_FILENAME)


# ------------------------------------------------------------------
# Public cache operations
# ------------------------------------------------------------------

def cache_exists():
    """Check if the cache file exists on disk."""
    return os.path.exists(_get_cache_path())


def read_local_config():
    """
    Read cached shelf configuration from disk.
    
    Returns
    -------
    dict or None
        Configuration dictionary if successful, None if file missing or invalid.
    """
    cache_path = _get_cache_path()
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, "r") as fh:
            return json.load(fh)
    except (IOError, ValueError, TypeError) as e:
        print("Failed to read cache file: {0}".format(e))
        return None


def write_local_config(config_data):
    """
    Write shelf configuration to cache file.
    
    Parameters
    ----------
    config_data : dict or str
        Configuration data as dictionary or JSON string.
        
    Returns
    -------
    bool
        True if write successful, False otherwise.
    """
    cache_path = _get_cache_path()
    
    try:
        # Ensure parent directory exists
        cache_dir = os.path.dirname(cache_path)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Convert to string if dict provided
        if isinstance(config_data, dict):
            config_text = json.dumps(config_data, indent=2, sort_keys=True)
        else:
            config_text = str(config_data)
        
        # Write to file
        with open(cache_path, "w") as fh:
            fh.write(config_text)
        
        return True
        
    except (IOError, TypeError) as e:
        print("Failed to write cache file: {0}".format(e))
        return False


def read_local_config_text():
    """
    Read cached configuration as raw text string.
    
    Returns
    -------
    str
        Raw JSON text from cache file, empty string if not found.
    """
    cache_path = _get_cache_path()
    
    if not os.path.exists(cache_path):
        return ""
    
    try:
        with open(cache_path, "r") as fh:
            return fh.read()
    except IOError as e:
        print("Failed to read cache text: {0}".format(e))
        return ""


def get_config_hash(config_text):
    """
    Generate MD5 hash of configuration text for change detection.
    
    Parameters
    ----------
    config_text : str
        Configuration text to hash.
        
    Returns
    -------
    str
        MD5 hash as hexadecimal string.
    """
    if not isinstance(config_text, str):
        config_text = str(config_text)
    
    return hashlib.md5(config_text.encode("utf-8")).hexdigest()


def clear_cache():
    """
    Delete the local cache file.
    
    Returns
    -------
    bool
        True if deletion successful or file did not exist, False on error.
    """
    cache_path = _get_cache_path()
    
    if not os.path.exists(cache_path):
        return True
    
    try:
        os.remove(cache_path)
        return True
    except OSError as e:
        print("Failed to delete cache file: {0}".format(e))
        return False


def get_cache_info():
    """
    Get information about the current cache state.
    
    Returns
    -------
    dict
        Dictionary with cache file path, existence status, and size.
    """
    cache_path = _get_cache_path()
    exists = os.path.exists(cache_path)
    
    size = 0
    if exists:
        try:
            size = os.path.getsize(cache_path)
        except OSError:
            size = -1
    
    return {
        "path": cache_path,
        "exists": exists,
        "size_bytes": size
    }
