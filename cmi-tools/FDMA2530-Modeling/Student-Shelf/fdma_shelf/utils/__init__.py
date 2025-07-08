from __future__ import absolute_import
"""
Utility modules for FDMA 2530 shelf system.

Provides helper functions for:
- caching (cache.py)
- downloading (downloader.py)
- system utilities (system_utils.py)
- updating (updater.py)
"""

# Re-export core cache functions
try:
    from .cache import (
        read_local_config,
        write_local_config,
        get_config_hash,
        cache_exists,
        clear_cache,
    )
except ImportError:
    # Define stubs or raise a clear error if needed
    raise ImportError("Could not import from .cache. Please ensure cache.py exists and exports the required functions.")

try:
    from .downloader import download_raw
except ImportError:
    raise ImportError("Could not import download_raw from .downloader. Please ensure downloader.py exists.")

try:
    from .system_utils import is_windows, is_macos, is_linux, get_os_name, get_platform_info
except ImportError:
    raise ImportError("Could not import system utility functions from .system_utils. Please ensure system_utils.py exists.")

try:
    from .updater import run_update, startup_check, check_for_updates
except ImportError:
    raise ImportError("Could not import updater functions from .updater. Please ensure updater.py exists.")

__all__ = [
    "read_local_config",
    "write_local_config",
    "get_config_hash",
    "cache_exists",
    "clear_cache",
    "download_raw",
    "is_windows",
    "is_macos",
    "is_linux",
    "get_os_name",
    "get_platform_info",
    "run_update",
    "startup_check",
    "check_for_updates",
]
