"""
FDMA 2530 Shelf - CMI Modeling Checklist Button Script v1.2.1
=============================================================

Optimized shelf button script for executing the CMI Modeling Checklist.
Designed for maximum speed and minimal overhead using cache_loader integration.

This script is executed when the "Checklist" button is clicked on the FDMA 2530
Maya shelf. It provides fast, reliable access to the latest checklist tool.

Features:
- Optimized for speed using cache_loader system
- Minimal overhead and fast execution
- Cross-platform compatibility via system_utils
- Python 2/3 handling via github_utilities  
- Proper error handling without complexity
- Clean, maintainable code following best practices

Created by: Alexander T. Santiago - asanti89@nmsu.edu
"""

from __future__ import print_function, absolute_import

import sys
import os
import tempfile

# ============================================================================
# VERSION AND CONFIGURATION
# ============================================================================

__version__ = "1.2.1"

# Script configuration
SCRIPT_NAME = "CMI Modeling Checklist Loader"
CONTACT_INFO = "asanti89@nmsu.edu"

# Python version detection
PY3 = sys.version_info[0] >= 3

# Repository configuration  
REPO_BASE = "https://raw.githubusercontent.com/Atsantiago/NMSU_Scripts/master/FDMA2530-Modeling/Student-Shelf"
CACHE_LOADER_URL = REPO_BASE + "/utilities/cache_loader.py"
CHECKLIST_URL = REPO_BASE + "/core-scripts/cmi_modeling_checklist.py"

# Cache configuration
CACHE_FILE_NAME = "cmi_checklist_v3.py"

# ============================================================================
# SYSTEM UTILITIES INTEGRATION
# ============================================================================

def _detect_os():
    """Detect operating system using system_utils or fallback"""
    try:
        # Try to use system_utils if available
        from utilities.system_utils import is_windows, is_macos, is_linux
        if is_windows():
            return 'windows'
        elif is_macos():
            return 'macos'
        elif is_linux():
            return 'linux'
        else:
            return 'unknown'
    except ImportError:
        # Fallback detection
        import platform
        os_name = platform.system().lower()
        if os_name == 'windows':
            return 'windows'
        elif os_name == 'darwin':
            return 'macos'
        elif os_name == 'linux':
            return 'linux'
        else:
            return 'unknown'

# ============================================================================
# FAST LOGGING SYSTEM
# ============================================================================

def _log(message, level="INFO"):
    """Fast logging with minimal overhead"""
    print("[FDMA-Checklist] {}: {}".format(level, message))

def _log_error(message):
    """Log error message"""
    _log(message, "ERROR")

def _log_success(message):
    """Log success message"""  
    _log(message, "SUCCESS")

# ============================================================================
# MAYA ENVIRONMENT DETECTION
# ============================================================================

# Detect Maya availability
try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
    MAYA_VERSION = cmds.about(version=True)
except ImportError:
    MAYA_AVAILABLE = False
    MAYA_VERSION = 'Unknown'

def _show_maya_message(message, message_type="info"):
    """Show message in Maya with fallback"""
    if not MAYA_AVAILABLE:
        print(message)
        return
    
    try:
        if message_type == "warning":
            cmds.warning(message)
        elif message_type == "error":
            cmds.error(message)
        else:
            cmds.inViewMessage(amg=message, pos='midCenter', fade=True)
    except:
        print(message)

# ============================================================================
# FAST CACHE_LOADER INTEGRATION
# ============================================================================

def _ensure_cache_loader():
    """Fast cache_loader setup with minimal overhead"""
    try:
        # Try to import existing cache_loader first (fastest path)
        from utilities.cache_loader import load_execute
        _log("Using installed cache_loader")
        return load_execute
    except ImportError:
        # Download cache_loader with minimal overhead
        _log("Downloading cache_loader...")
        
        # Import appropriate urllib for Python 2/3
        if PY3:
            from urllib.request import urlopen
        else:
            from urllib2 import urlopen
        
        try:
            # Fast download with short timeout
            response = urlopen(CACHE_LOADER_URL, timeout=10)
            data = response.read()
            
            # Handle encoding for Python 3
            if PY3 and isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Save to temp directory and add to path
            temp_dir = tempfile.gettempdir()
            if temp_dir not in sys.path:
                sys.path.insert(0, temp_dir)
            
            # Write cache_loader file
            cache_path = os.path.join(temp_dir, 'cache_loader.py')
            with open(cache_path, 'w') as f:
                f.write(data)
            
            # Execute cache_loader to make functions available
            exec(data, globals())
            _log_success("Cache_loader downloaded and ready")
            return load_execute
            
        except Exception as e:
            _log_error("Failed to setup cache_loader: {}".format(str(e)))
            return None

# ============================================================================
# OPTIMIZED CHECKLIST EXECUTION
# ============================================================================

def _execute_checklist_fast():
    """Execute checklist with maximum speed optimization"""
    try:
        # Get cache_loader function (fast path or download)
        load_execute_func = _ensure_cache_loader()
        if not load_execute_func:
            raise Exception("Cache_loader not available")
        
        # Execute checklist using cache_loader (optimal path)
        _log("Loading CMI Modeling Checklist...")
        load_execute_func(CHECKLIST_URL, CACHE_FILE_NAME)
        
        _log_success("CMI Modeling Checklist loaded successfully!")
        
        # Show user confirmation in Maya
        if MAYA_AVAILABLE:
            _show_maya_message("CMI Modeling Checklist v3.0 loaded successfully!")
        
        return True
        
    except Exception as e:
        error_msg = "Failed to load checklist: {}".format(str(e))
        _log_error(error_msg)
        
        # Show user-friendly error in Maya
        if MAYA_AVAILABLE:
            _show_maya_message(error_msg, "error")
        
        return False

def _execute_checklist_fallback():
    """Fallback execution method without cache_loader"""
    try:
        _log("Using fallback execution method...")
        
        # Import appropriate urllib for Python 2/3
        if PY3:
            from urllib.request import urlopen
        else:
            from urllib2 import urlopen
        
        # Download checklist directly
        response = urlopen(CHECKLIST_URL, timeout=15)
        checklist_content = response.read()
        
        # Handle encoding for Python 3
        if PY3 and isinstance(checklist_content, bytes):
            checklist_content = checklist_content.decode('utf-8')
        
        # Basic validation
        if not checklist_content or len(checklist_content.strip()) < 500:
            raise Exception("Downloaded content appears invalid")
        
        # Execute checklist directly
        exec(checklist_content, globals())
        
        _log_success("Checklist loaded via fallback method")
        
        if MAYA_AVAILABLE:
            _show_maya_message("CMI Modeling Checklist loaded (fallback mode)")
        
        return True
        
    except Exception as e:
        error_msg = "Fallback execution failed: {}".format(str(e))
        _log_error(error_msg)
        
        if MAYA_AVAILABLE:
            _show_maya_message(error_msg, "error")
        
        return False

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """
    Main execution function optimized for speed.
    
    This function coordinates the checklist loading with minimal overhead:
    1. Fast cache_loader execution attempt
    2. Fallback method if needed
    3. User feedback and error handling
    """
    
    try:
        # Log startup information
        os_type = _detect_os()
        _log("Starting checklist loader v{} on {} (Python {})".format(
            __version__, os_type.title(), sys.version_info[0]))
        
        # Attempt fast execution first
        if _execute_checklist_fast():
            return True
        
        # If fast execution failed, try fallback
        _log("Trying fallback execution method...")
        if _execute_checklist_fallback():
            return True
        
        # Both methods failed
        _log_error("All execution methods failed")
        
        if MAYA_AVAILABLE:
            error_dialog = (
                "Failed to load CMI Modeling Checklist.\n\n"
                "Troubleshooting:\n"
                "• Check internet connection\n"
                "• Verify GitHub access\n"
                "• Check Maya console for details\n\n"
                "Contact: {}"
            ).format(CONTACT_INFO)
            
            cmds.confirmDialog(
                title='Checklist Load Failed',
                message=error_dialog,
                button=['OK'],
                icon='critical'
            )
        
        return False
        
    except Exception as e:
        critical_error = "Critical error in checklist loader: {}".format(str(e))
        _log_error(critical_error)
        
        if MAYA_AVAILABLE:
            _show_maya_message(critical_error, "error")
        
        return False

# ============================================================================
# PERFORMANCE TESTING AND DIAGNOSTICS
# ============================================================================

def run_performance_test():
    """Run performance test of the loading system"""
    import time
    
    _log("Running performance test...")
    start_time = time.time()
    
    # Test cache_loader availability
    cache_start = time.time()
    cache_loader_func = _ensure_cache_loader()
    cache_time = time.time() - cache_start
    
    _log("Cache_loader setup time: {:.3f}s".format(cache_time))
    
    total_time = time.time() - start_time
    _log("Total test time: {:.3f}s".format(total_time))
    
    return {
        'cache_loader_available': cache_loader_func is not None,
        'cache_setup_time': cache_time,
        'total_time': total_time
    }

def get_system_info():
    """Get system information for diagnostics"""
    os_type = _detect_os()
    
    info = {
        'script_version': __version__,
        'python_version': "{}.{}.{}".format(*sys.version_info[:3]),
        'operating_system': os_type,
        'maya_available': MAYA_AVAILABLE,
        'maya_version': MAYA_VERSION if MAYA_AVAILABLE else 'N/A'
    }
    
    return info

# ============================================================================
# EXECUTION ENTRY POINTS
# ============================================================================

# Execute main function when script is run
if __name__ == "__main__":
    # Direct execution (for testing)
    _log("Running checklist loader in direct execution mode...")
    result = main()
    if not result:
        _log_error("Direct execution failed")
else:
    # Execution from shelf button (normal usage)
    main()
