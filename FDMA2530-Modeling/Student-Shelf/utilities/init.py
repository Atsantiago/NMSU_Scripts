"""
FDMA 2530 GitHub Utilities Package v1.2
=======================================

Core utilities for GitHub operations in Maya shelf systems.
Provides Python 2/3 compatible functions for downloading and executing scripts.

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
GitHub: github.com/atsantiago
Repository: https://github.com/Atsantiago/NMSU_Scripts
License: Educational use for FDMA 2530 students
"""

__version__ = "1.2"

# Import main utility functions for easy access
try:
    from .github_utilities import (
        download_file_content,
        execute_script_from_github,
        test_github_connectivity,
        build_github_raw_url,
        check_for_file_updates,
        extract_version_info,
        run_system_diagnostics
    )
    
    __all__ = [
        'download_file_content',
        'execute_script_from_github', 
        'test_github_connectivity',
        'build_github_raw_url',
        'check_for_file_updates',
        'extract_version_info',
        'run_system_diagnostics',
        '__version__'
    ]
except ImportError:
    # Handle case where github_utilities.py doesn't exist yet
    __all__ = ['__version__']
