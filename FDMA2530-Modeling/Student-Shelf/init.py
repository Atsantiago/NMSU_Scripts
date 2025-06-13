"""
FDMA 2530 Student Shelf System v1.2
===================================

Complete Maya shelf system for FDMA 2530 modeling students.
Provides automated tools sourced directly from GitHub with full
Python 2/3 compatibility across all Maya versions.

Features:
- CMI Modeling Checklist (v3.0) for comprehensive project validation
- Automatic update system with visual status indicators  
- Python 2/3 compatibility across all Maya versions (2016+)
- Robust error handling and user feedback
- Direct GitHub execution without temporary files
- Intelligent update detection and shelf reconstruction
- Backup and restore capabilities for safe updates

Directory Structure:
├── core-scripts/          Main educational tools (v3.0)
├── shelf-button-scripts/  Scripts executed by shelf buttons (v1.2)  
├── utilities/             GitHub operation utilities (v1.2)
├── media/                 Icons and resources
└── tests/                 Testing scripts

Installation:
Students receive only the shelf_FDMA_2530.mel file which automatically
sources all other components from GitHub for always up-to-date tools.

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
GitHub: github.com/atsantiago
Repository: https://github.com/Atsantiago/NMSU_Scripts
License: Educational use for FDMA 2530 students

Changelog:
v1.2 - Complete rewrite with:
     - Full Python 2/3 compatibility
     - Integration with GitHub utilities system
     - Visual update status indicators
     - Enhanced error handling and user feedback
     - Modular design following PEP 8 standards
     - Semantic versioning implementation
"""

__version__ = "1.2"

# Import version info from sub-packages for consistency checking
try:
    from .utilities import __version__ as utilities_version
    from .core_scripts import __version__ as core_version  
    from .shelf_button_scripts import __version__ as shelf_version
    
    def get_version_info():
        """
        Get comprehensive version information for the entire shelf system.
        
        Returns:
            dict: Version information for all components
        """
        return {
            'main_package': __version__,
            'utilities': utilities_version,
            'core_scripts': core_version,
            'shelf_button_scripts': shelf_version
        }
    
    def print_version_info():
        """Print formatted version information for all components."""
        print("FDMA 2530 Shelf System Component Versions:")
        print("• Main Package: v{0}".format(__version__))
        print("• Utilities: v{0}".format(utilities_version))
        print("• Core Scripts: v{0}".format(core_version))
        print("• Shelf Scripts: v{0}".format(shelf_version))
        
    # Check for version consistency (optional warning)
    expected_shelf_version = "1.2"
    if utilities_version != expected_shelf_version or shelf_version != expected_shelf_version:
        print("Notice: Sub-package versions may differ from main package (this is normal)")
        
    __all__ = ['__version__', 'get_version_info', 'print_version_info']
    
except ImportError:
    # Sub-packages not yet created or accessible
    def get_version_info():
        return {'main_package': __version__}
    
    def print_version_info():
        print("FDMA 2530 Shelf System v{0}".format(__version__))
        
    __all__ = ['__version__', 'get_version_info', 'print_version_info']
