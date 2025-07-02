"""
Utility modules for FDMA 2530 shelf system.

Provides helper functions for downloading, caching, system operations,
and other common tasks used throughout the shelf ecosystem.

Modules
-------
cache : Configuration caching and hash management
downloader : HTTP download utilities for GitHub integration  
system_utils : System and Maya environment helpers
updater : Shelf update checking and installation
"""

from __future__ import absolute_import

# Re-export commonly used functions for convenience
from .cache import (
    read_local_config,
    write_local_config, 
    get_config_hash,
    cache_exists,
    clear_cache
)

from .downloader import download_raw

__all__ = [
    "read_local_config",
    "write_local_config", 
    "get_config_hash",
    "cache_exists",
    "clear_cache",
    "download_raw"
]
