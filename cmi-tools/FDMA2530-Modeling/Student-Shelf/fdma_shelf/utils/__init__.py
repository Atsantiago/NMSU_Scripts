from __future__ import absolute_import
"""
Utility modules for FDMA 2530 shelf system.

Provides helper functions for:
- caching (cache.py)
- downloading (downloader.py)  
- system utilities (system_utils.py)
- updating (updater.py)
- version utilities (version_utils.py)
"""

# Make submodules directly accessible for testing
try:
    from . import updater
except ImportError:
    updater = None

try:
    from . import version_utils
except ImportError:
    version_utils = None

try:
    from . import cache
except ImportError:
    cache = None

try:
    from . import downloader
except ImportError:
    downloader = None

try:
    from . import system_utils
except ImportError:
    system_utils = None

# Re-export core functions with error handling
try:
    from .cache import (
        read_local_config,
        write_local_config,
        get_config_hash,
        cache_exists,
        clear_cache,
    )
except ImportError:
    pass

try:
    from .downloader import download_raw
except ImportError:
    pass

try:
    from .system_utils import is_windows, is_macos, is_linux, get_os_name, get_platform_info
except ImportError:
    pass

try:
    from .updater import run_update, startup_check, check_for_updates
except ImportError:
    pass

try:
    from .version_utils import get_fdma2530_version, is_valid_semantic_version
except ImportError:
    pass

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
    "get_fdma2530_version",
    "is_valid_semantic_version"
]
