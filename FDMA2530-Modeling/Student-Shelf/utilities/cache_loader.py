"""
FDMA 2530 GitHub Cache Loader v1.2
==================================
Small helper that downloads a script from GitHub once, caches it in the
Maya scripts folder, and executes it instantly on subsequent runs.

Advantages
----------
- Huge speed-up: first call downloads, later calls run local copy  
- Works in Python 2 and 3 (Maya 2016 -> 2025+)  
- Keeps a simple MD5 manifest to know when the remote file changed  
- No external dependencies and safe to import multiple times

Author: Alexander T. Santiago - asanti89@nmsu.edu
"""

from __future__ import absolute_import, division, print_function
import os
import sys
import json
import hashlib
import traceback

try:                                # Py-3
    from urllib.request import urlopen
except ImportError:                 # Py-2
    from urllib2 import urlopen

# ------------------------------------------------------------------ constants
__version__ = "1.2"
MANIFEST_FILE = "fdma_cache_manifest.json"

# Locate user-specific Maya scripts directory
def _maya_scripts_dir():
    try:
        import maya.cmds as cmds
        return cmds.internalVar(userScriptDir=True)
    except Exception:
        # Stand-alone / test mode fallback
        return os.path.join(os.path.expanduser('~'), '.fdma_scripts')

CACHE_DIR = os.path.join(_maya_scripts_dir(), "fdma_cache")
MANIFEST_PATH = os.path.join(CACHE_DIR, MANIFEST_FILE)

# ----------------------------------------------------------------- utilities
def _md5(data):
    """Return hexdigest MD5 for *data* (bytes or str)."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.md5(); h.update(data)
    return h.hexdigest()

def _read_manifest():
    try:
        with open(MANIFEST_PATH, 'r') as fh:
            return json.load(fh)
    except Exception:
        return {}

def _write_manifest(manifest):
    try:
        with open(MANIFEST_PATH, 'w') as fh:
            json.dump(manifest, fh, indent=2)
    except Exception as e:
        print("[FDMA-cache] Could not save manifest:", e)

# ---------------------------------------------------------------- main api
def load_execute(raw_url, local_name, namespace=None):
    """
    Download *raw_url* (GitHub raw link) if needed, cache as *local_name*
    inside FDMA cache directory, exec() the code in *namespace*.
    """
    if namespace is None:
        namespace = globals()

    # ----------------------------------------------------------- ensure cache
    if not os.path.isdir(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
        except OSError:
            pass  # race condition safe

    manifest = _read_manifest()
    local_path = os.path.join(CACHE_DIR, local_name)
    need_download = True

    if os.path.exists(local_path):
        with open(local_path, 'rb') as fh:
            data = fh.read()
        if manifest.get(local_name) == _md5(data):
            need_download = False
    else:
        data = b""

    # ------------------------------------------------------------- download
    if need_download:
        try:
            print("[FDMA-cache] Downloading:", raw_url)
            data = urlopen(raw_url, timeout=20).read()
            with open(local_path, 'wb') as fh:
                fh.write(data)
            manifest[local_name] = _md5(data)
            _write_manifest(manifest)
            print("[FDMA-cache] Cached:", local_path)
        except Exception as e:
            print("[FDMA-cache] Download failed:", e)
            print(traceback.format_exc())
            if not data:
                raise  # nothing to exec - bubble up

    # ------------------------------------------------------ decode / execute
    if sys.version_info[0] >= 3 and isinstance(data, bytes):
        data = data.decode('utf-8')

    exec(data, namespace)  # run in supplied namespace
