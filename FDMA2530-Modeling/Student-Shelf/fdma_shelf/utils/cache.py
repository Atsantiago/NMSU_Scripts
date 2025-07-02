"""
FDMA 2530 GitHub Cache Loader v1.2.1 - STREAMLINED VERSION
==========================================================

Minimal, fast cache loader optimized for Maya shelf performance.
Downloads GitHub scripts once, caches locally, executes instantly on subsequent runs.

Features:
- Lightning-fast execution with minimal overhead
- Python 2/3 compatibility across Maya 2016-2025+
- Simple MD5 manifest for update detection
- No external dependencies
- Optimized for speed over features

Author: Alexander T. Santiago - asanti89@nmsu.edu
"""

from __future__ import absolute_import, division, print_function

import os
import sys
import json
import hashlib

# Python 2/3 compatibility - minimal approach
try:
    from urllib.request import urlopen  # Python 3
except ImportError:
    from urllib2 import urlopen  # Python 2

# ============================================================================
# CONFIGURATION - MINIMAL AND FAST
# ============================================================================

__version__ = "1.2.1"
MANIFEST_FILE = "fdma_cache_manifest.json"

# ============================================================================
# OPTIMIZED DIRECTORY DETECTION
# ============================================================================

def _get_cache_dir():
    """Get cache directory with minimal overhead"""
    try:
        # Fast Maya detection
        import maya.cmds as cmds
        maya_scripts = cmds.internalVar(userScriptDir=True)
        if maya_scripts:
            return os.path.join(maya_scripts, "fdma_cache")
    except:
        pass
    
    # Fast fallback
    return os.path.join(os.path.expanduser('~'), '.fdma_cache')

# Global cache directory (computed once for speed)
CACHE_DIR = _get_cache_dir()
MANIFEST_PATH = os.path.join(CACHE_DIR, MANIFEST_FILE)

# ============================================================================
# FAST UTILITY FUNCTIONS
# ============================================================================

def _md5(data):
    """Fast MD5 calculation with minimal type checking"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.md5()
    h.update(data)
    return h.hexdigest()

def _read_manifest():
    """Read manifest with minimal error handling"""
    try:
        with open(MANIFEST_PATH, 'r') as fh:
            return json.load(fh)
    except:
        return {}

def _write_manifest(manifest):
    """Write manifest with atomic operation - optimized for speed"""
    try:
        # Ensure directory exists
        if not os.path.isdir(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        
        # Fast atomic write
        temp_path = MANIFEST_PATH + '.tmp'
        with open(temp_path, 'w') as fh:
            json.dump(manifest, fh, separators=(',', ':'))  # Compact JSON
        
        # Atomic rename (cross-platform safe)
        if os.path.exists(MANIFEST_PATH) and sys.platform.startswith('win'):
            os.remove(MANIFEST_PATH)  # Windows requirement
        os.rename(temp_path, MANIFEST_PATH)
    except:
        # Silent failure - don't break execution for manifest issues
        pass

# ============================================================================
# MAIN API FUNCTION - OPTIMIZED FOR SPEED
# ============================================================================

def load_execute(raw_url, local_name, namespace=None):
    """
    Download and cache script from GitHub, execute instantly on subsequent runs.
    
    Optimized for maximum speed:
    - Minimal error handling for performance
    - Fast cache checks with simple hash comparison
    - Direct execution without complex validation
    - Silent failures that don't break workflow
    """
    
    if namespace is None:
        namespace = globals()

    # Fast cache setup
    if not os.path.isdir(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
        except:
            pass  # Continue even if cache dir creation fails

    manifest = _read_manifest()
    local_path = os.path.join(CACHE_DIR, local_name)
    
    need_download = True
    data = b""

    # Fast cache check
    if os.path.exists(local_path):
        try:
            with open(local_path, 'rb') as fh:
                data = fh.read()
            
            # Quick hash comparison
            if manifest.get(local_name) == _md5(data):
                need_download = False
                print("[FDMA-cache] Using cached: {}".format(local_name))
        except:
            data = b""  # Force download on any error

    # Fast download with minimal retries
    if need_download:
        try:
            print("[FDMA-cache] Downloading: {}".format(raw_url))
            response = urlopen(raw_url, timeout=15)
            data = response.read()
            
            # Fast cache write
            try:
                with open(local_path, 'wb') as fh:
                    fh.write(data)
                
                # Update manifest
                manifest[local_name] = _md5(data)
                _write_manifest(manifest)
                
                print("[FDMA-cache] Cached: {}".format(local_path))
            except:
                pass  # Continue even if caching fails
                
        except Exception as e:
            print("[FDMA-cache] Download failed: {}".format(e))
            if not data:
                raise  # Only raise if we have no fallback data

    # Fast execution
    if sys.version_info[0] >= 3 and isinstance(data, bytes):
        data = data.decode('utf-8')
    
    exec(data, namespace)

# ============================================================================
# MINIMAL UTILITY FUNCTIONS
# ============================================================================

def clear_cache():
    """Clear cache with minimal error handling"""
    try:
        import shutil
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)
            print("[FDMA-cache] Cache cleared")
    except:
        pass

def get_cache_info():
    """Get basic cache info for diagnostics"""
    try:
        manifest = _read_manifest()
        cache_size = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) 
                        for f in os.listdir(CACHE_DIR) 
                        if os.path.isfile(os.path.join(CACHE_DIR, f)))
        return {
            'cache_dir': CACHE_DIR,
            'cached_files': len(manifest),
            'cache_size_mb': round(cache_size / (1024 * 1024), 2)
        }
    except:
        return {'error': 'Cache info unavailable'}

# ============================================================================
# MODULE INFO
# ============================================================================

if __name__ == "__main__":
    print("FDMA 2530 GitHub Cache Loader v{} - Streamlined".format(__version__))
    info = get_cache_info()
    if 'error' not in info:
        print("Cache: {} files, {:.1f}MB".format(info['cached_files'], info['cache_size_mb']))
