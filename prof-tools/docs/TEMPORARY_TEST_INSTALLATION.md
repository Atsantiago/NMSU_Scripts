# Temporary Test Installation System

The Prof-Tools framework includes a sophisticated temporary test installation system that allows developers to quickly test new versions without affecting their stable installation.

## Overview

The temporary test installation system provides:

- **Safe Testing**: Install test versions without overwriting stable installations
- **Automatic Reversion**: Test versions automatically revert to stable on Maya restart
- **Developer-Only Access**: Only visible when Developer Mode is enabled
- **Visual Status Indicators**: Clear indication when a temporary installation is active
- **Easy Management**: Simple install and revert operations

## How It Works

### Installation Process

1. **Enable Developer Mode**: Access `Prof-Tools > Developer Tools > Enable Developer Mode`
2. **Install Test Version**: Select `Developer Tools > Install Test Version Temporarily…`
3. **Version Selection**: The system automatically selects the latest available test version
4. **Installation**: The test version is installed over the current stable version
5. **Tracking**: The system tracks both the installed test version and original stable version

### Automatic Reversion

- **On Maya Restart**: The system automatically detects temporary installations on startup
- **Version Restoration**: Reverts to the stable version that was running before test installation
- **File Cleanup**: Removes temporary installation tracking files
- **Logging**: All reversion activity is logged for debugging

### Manual Reversion

- **Immediate Revert**: Use `Developer Tools > Revert to Stable Version`
- **Confirmation Dialog**: Shows which versions are involved
- **Restart Required**: Manual reversion requires Maya restart to complete

## User Interface Features

### Developer Tools Menu

When Developer Mode is enabled, the Developer Tools menu shows:

- **Status Indicator**: Menu title shows "(Test X.X.X active)" when test version is running
- **Installation Status**: Disabled menu items show current test version and stable version
- **Conditional Options**: Menu items change based on whether a temporary installation is active

### Status Display Examples

```
Developer Tools (Test 0.2.13.1 active)
├── Status: Test 0.2.13.1 Temporarily Installed     [disabled]
├── Will revert to 0.2.13 on restart                [disabled]
├── ─────────────────────────────────────────────────
├── Check for Test Updates…
├── ─────────────────────────────────────────────────
├── Configure Auto-Updates…
├── Test Silent Update Check
├── ─────────────────────────────────────────────────
├── Install Different Test Version…
└── Revert to Stable Version                        [enabled]
```

## Technical Implementation

### File Structure

```
Maya Preferences/
└── prof_tools/
    ├── prof_tools_prefs.json    # Main preferences including temp install tracking
    └── temp_install.json        # Startup detection file
```

### Preference Tracking

The system uses `prof.core.tools.dev_prefs` to track:

```json
{
  "temp_install": {
    "enabled": true,
    "version": "0.2.13.1",
    "stable_version": "0.2.13",
    "install_date": "2024-01-15 14:30:25"
  }
}
```

### Startup Detection

- **Initialization Hook**: `prof.__init__._initialize_package()`
- **Detection Logic**: Checks for `temp_install.json` on startup
- **Reversion Process**: Automatically reverts if temporary installation detected
- **Cleanup**: Removes tracking files after successful reversion

## Developer API

### Core Functions

```python
from prof.core.tools.dev_prefs import get_prefs

prefs = get_prefs()

# Check status
is_active = prefs.is_temp_install_active()
info = prefs.get_temp_install_info()

# Set up temporary installation
prefs.set_temp_install("0.2.13.1", "0.2.13")

# Clear temporary installation
prefs.clear_temp_install()

# Check and revert on startup
reverted = prefs.check_and_revert_temp_install()
```

### Installation Function

```python
from prof.core.updater import _install_specific_version

# Install specific version temporarily
success = _install_specific_version("0.2.13.1", temporary=True)
```

## Best Practices

### For Developers

1. **Enable Developer Mode**: Always enable before accessing test features
2. **Check Status**: Use menu indicators to know current installation state
3. **Test Thoroughly**: Test versions may contain experimental features
4. **Revert When Done**: Manually revert or restart Maya when testing is complete

### For System Administrators

1. **Monitor Logs**: Check Maya logs for temporary installation activity
2. **Backup Awareness**: Temporary installations don't create permanent backups
3. **User Training**: Ensure developers understand the temporary nature
4. **Version Control**: Track which test versions are being used

## Troubleshooting

### Common Issues

1. **Installation Fails**
   - Check internet connection for download
   - Verify test versions are available in releases.json
   - Check Maya console for detailed error messages

2. **Reversion Doesn't Work**
   - Try manual reversion via Developer Tools menu
   - Check preferences files aren't corrupted
   - Restart Maya to trigger automatic reversion

3. **Menu Not Showing**
   - Ensure Developer Mode is enabled
   - Check that dev_prefs module is working correctly
   - Verify prof-tools is properly installed

### Log Messages

```
INFO: Temporarily installed test version 0.2.13.1
INFO: Temporary installation detected and reverted on startup
INFO: Reverted to stable version
```

## Version Compatibility

- **Minimum Version**: Prof-Tools 0.2.13+
- **Maya Versions**: All supported Maya versions
- **Python**: Compatible with Maya's Python environment
- **Test Version Format**: MAJOR.MINOR.PATCH.TEST (e.g., 0.2.13.1)

## Security Considerations

- **Developer-Only**: Only available when Developer Mode is explicitly enabled
- **Download Verification**: Uses same secure download system as regular updates
- **File Permissions**: Respects Maya's file system permissions
- **Logging**: All actions are logged for audit purposes
