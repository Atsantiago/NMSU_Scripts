"""
FDMA 2530 Student Shelf System v1.2.1
=====================================

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
- Startup update check with visual feedback

Directory Structure:
├── core-scripts/          Main educational tools (v3.0)
├── shelf-button-scripts/  Scripts executed by shelf buttons (v1.2)  
├── utilities/             GitHub operation utilities (v1.2)
├── media/                 Icons and resources
└── tests/                 Testing scripts

Installation:
Students receive only the installer.py file which automatically
sources all other components from GitHub for always up-to-date tools.

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
GitHub: github.com/atsantiago
Repository: https://github.com/Atsantiago/NMSU_Scripts
License: Educational use for FDMA 2530 students

Changelog:
v1.2.1 - Enhanced startup system with:
       - Automatic update checking on Maya startup
       - Visual status indicators for available updates
       - Non-intrusive update notifications
       - Improved error handling and fallback mechanisms
v1.2 - Complete rewrite with:
     - Full Python 2/3 compatibility
     - Integration with GitHub utilities system
     - Visual update status indicators
     - Enhanced error handling and user feedback
     - Modular design following PEP 8 standards
     - Semantic versioning implementation
"""

__version__ = "1.2.1"

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
    expected_shelf_version = "1.2.1"
    if utilities_version != expected_shelf_version or shelf_version != expected_shelf_version:
        print("Notice: Sub-package versions may differ from main package (this is normal)")
        
    __all__ = ['__version__', 'get_version_info', 'print_version_info', 'check_startup_updates']
    
except ImportError:
    # Sub-packages not yet created or accessible
    def get_version_info():
        return {'main_package': __version__}
    
    def print_version_info():
        print("FDMA 2530 Shelf System v{0}".format(__version__))
        
    __all__ = ['__version__', 'get_version_info', 'print_version_info', 'check_startup_updates']

# ============================================================================
# STARTUP UPDATE CHECK SYSTEM
# ============================================================================

def check_startup_updates():
    """
    Check for shelf updates on Maya startup and provide visual feedback.
    
    This function is designed to be called during Maya's startup sequence
    using evalDeferred to ensure proper UI timing. It will:
    1. Check if the FDMA_2530 shelf exists (permanent installation)
    2. Compare cached JSON configuration with GitHub version
    3. Update button visual status and show viewport message if updates available
    4. Remain silent if no updates are available
    """
    try:
        # Import Maya modules (may not be available during package import)
        import maya.cmds as cmds
        import maya.mel as mel
        import maya.utils
        import os
        import sys
        import json
        import hashlib
        
        # Python 2/3 compatibility for urllib
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen
        
        # Configuration
        SHELF_NAME = "FDMA_2530"
        CONFIG_URL = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf/shelf_config.json"
        
        # Visual status button colors (Maya RGB values)
        BUTTON_COLORS = {
            'up_to_date': [0.5, 0.5, 0.5],        # Gray
            'updates_available': [0.2, 0.8, 0.2], # Green
            'update_failed': [0.8, 0.2, 0.2],     # Red
            'checking': [0.8, 0.8, 0.2]           # Yellow
        }
        
        def safe_download(url):
            """Download content from URL with error handling"""
            try:
                response = urlopen(url, timeout=10)
                content = response.read()
                if sys.version_info[0] >= 3 and isinstance(content, bytes):
                    content = content.decode("utf-8")
                return content
            except Exception as e:
                print("FDMA 2530: Download failed during startup check: " + str(e))
                return None
        
        def update_button_visual_status(status):
            """Set backgroundColor on the Update button"""
            try:
                if not cmds.shelfLayout(SHELF_NAME, exists=True):
                    return False
                
                buttons = cmds.shelfLayout(SHELF_NAME, query=True, childArray=True) or []
                for btn in buttons:
                    try:
                        if cmds.objectTypeUI(btn) == 'shelfButton':
                            label = cmds.shelfButton(btn, query=True, label=True)
                            if label == "Update":
                                color = BUTTON_COLORS.get(status, BUTTON_COLORS['up_to_date'])
                                cmds.shelfButton(btn, edit=True, backgroundColor=color)
                                return True
                    except Exception:
                        continue
                return False
            except Exception:
                return False
        
        def show_update_notification():
            """Show non-intrusive yellow viewport message about available updates"""
            try:
                cmds.inViewMessage(
                    amg='<span style="color:#FFCC00">Updates to FDMA 2530 shelf available!</span>',
                    pos='botLeft',
                    fade=True,
                    alpha=0.9,
                    dragKill=False,
                    fadeStayTime=4000
                )
            except Exception:
                pass
        
        # Main startup check logic
        def perform_startup_check():
            """Perform the actual startup update check"""
            try:
                # Check if shelf exists (indicates permanent installation)
                if not cmds.shelfLayout(SHELF_NAME, exists=True):
                    print("FDMA 2530: Shelf not found, skipping startup update check")
                    return
                
                print("FDMA 2530: Checking for updates...")
                
                # Download latest configuration
                latest_config = safe_download(CONFIG_URL)
                if not latest_config:
                    print("FDMA 2530: Unable to check for updates during startup")
                    return
                
                # Get cached configuration path
                cache_path = os.path.join(cmds.internalVar(userScriptDir=True), "shelf_config_cache.json")
                
                # Read cached configuration if it exists
                cached_config = ""
                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, 'r') as f:
                            cached_config = f.read()
                    except Exception:
                        pass
                
                # Compare configurations using hash
                latest_hash = hashlib.md5(latest_config.encode('utf-8')).hexdigest()
                cached_hash = hashlib.md5(cached_config.encode('utf-8')).hexdigest()
                
                if latest_hash != cached_hash:
                    # Updates available
                    print("FDMA 2530: Updates available!")
                    update_button_visual_status('updates_available')
                    show_update_notification()
                else:
                    # Up to date - silent operation
                    print("FDMA 2530: Shelf is up to date")
                    update_button_visual_status('up_to_date')
                
            except Exception as e:
                print("FDMA 2530: Startup update check failed: " + str(e))
                # Don't show error status during startup to avoid confusion
        
        # Use evalDeferred to ensure Maya UI is ready
        maya.utils.executeDeferred(perform_startup_check)
        
    except ImportError:
        # Maya not available (probably importing package outside of Maya)
        pass
    except Exception as e:
        print("FDMA 2530: Startup check initialization failed: " + str(e))

# ============================================================================
# AUTOMATIC STARTUP INITIALIZATION
# ============================================================================

# Automatically run startup check when this package is imported in Maya
try:
    import maya.cmds
    # We're in Maya, schedule the startup check
    check_startup_updates()
except ImportError:
    # Not in Maya, skip startup check
    pass
