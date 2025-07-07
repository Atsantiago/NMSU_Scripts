"""
Utility modules for FDMA 2530 shelf system.

Provides helper functions for:
- caching (cache.py)
- downloading (downloader.py)
- system utilities (system_utils.py)
- updating (updater.py)
"""

from __future__ import absolute_import

# Re-export core cache functions
from .cache import (
    read_local_config,
    write_local_config,
    get_config_hash,
    cache_exists,
    clear_cache,
)

# Re-export downloader function
from .downloader import download_raw

# Re-export system utility functions
from .system_utils import (
    is_windows,
    is_macos,
    is_linux,
    get_os_name,
    get_platform_info,
)

# Expose updater API
from .updater import (
    run_update,
    startup_check,
)

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
]
