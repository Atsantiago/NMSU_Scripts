# Cross-Platform Path Detection Enhancement

## Overview
Enhanced the CMI Tools Maya installer (`setup_drag_drop_fdma2530.py`) with comprehensive cross-platform path detection to ensure correct installation locations on Windows, macOS, and Linux systems.

## Key Changes

### 1. Platform Detection
- Added `get_platform()` function to detect Windows, macOS, Linux
- Returns standardized platform names: "windows", "macos", "linux"

### 2. Platform-Specific Maya Directories
- **Windows**: `~/Documents/maya/`
- **macOS**: `~/Library/Preferences/Autodesk/maya/`
- **Linux**: `~/maya/`

### 3. Enhanced Path Detection (`get_maya_root()`)
The function now:
1. Extracts Maya root from Maya's `userAppDir` when possible
2. Falls back to platform-specific Maya directory conventions
3. Verifies path relationships make sense
4. Uses intelligent directory tree traversal as final fallback

### 4. Consistent Path Handling
- Replaced manual path separator handling (`str.replace("\\", "/")`) 
- Uses `os.path.normpath()` and `os.path.join()` throughout
- Ensures proper path separators for each platform

### 5. Enhanced Logging
- Shows detected platform and path resolution process
- Verifies correct path separators are used
- Displays path relationships for debugging

## Installation Locations

### Windows
```
~/Documents/maya/
├── modules/
│   └── cmi-tools.mod
└── cmi-tools/
    └── scripts/
        ├── fdma_shelf/
        ├── shelf_config.json
        └── releases.json
```

### macOS
```
~/Library/Preferences/Autodesk/maya/
├── modules/
│   └── cmi-tools.mod
└── cmi-tools/
    └── scripts/
        ├── fdma_shelf/
        ├── shelf_config.json
        └── releases.json
```

### Linux
```
~/maya/
├── modules/
│   └── cmi-tools.mod
└── cmi-tools/
    └── scripts/
        ├── fdma_shelf/
        ├── shelf_config.json
        └── releases.json
```

## Testing
- Created `test_cross_platform_paths.py` for standalone testing
- Verified path generation on Windows (current platform)
- Simulated path generation for macOS and Linux
- Confirmed proper path separators and directory structure

## Benefits
1. **Reliability**: Works consistently across all major platforms
2. **Maya Compatibility**: Respects Maya's platform-specific directory conventions
3. **Flexibility**: Handles both standard and non-standard Maya configurations
4. **Debugging**: Enhanced logging for troubleshooting installation issues
5. **Maintainability**: Clean, platform-aware code structure

## Backward Compatibility
- All existing functionality preserved
- Enhanced path detection improves reliability on edge cases
- No breaking changes to installation process

## Files Modified
- `setup_drag_drop_fdma2530.py` - Main installer with cross-platform enhancements
- `test_cross_platform_paths.py` - Standalone testing utility (new)

This enhancement ensures that CMI Tools will install to the correct Maya directories regardless of the operating system or Maya configuration, providing a robust cross-platform installation experience.