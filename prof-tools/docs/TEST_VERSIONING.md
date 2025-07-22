# Test Versioning System for Prof-Tools

Prof-Tools now supports an enhanced versioning system that allows for test versions using the format `MAJOR.MINOR.PATCH.TEST`.

## Version Format

### Standard Releases
- Format: `MAJOR.MINOR.PATCH` (e.g., `0.2.7`)
- These are stable, production-ready releases
- Recommended for all regular use

### Test Versions
- Format: `MAJOR.MINOR.PATCH.TEST` (e.g., `0.2.7.1`, `0.2.7.2`)
- These are development/testing versions for new features
- **⚠️ Use only for testing and development purposes**

## Version Precedence

The system follows this precedence order (highest to lowest):

1. `1.0.1` (stable release)
2. `1.0.0.5` (test version 5 of 1.0.0)
3. `1.0.0.4` (test version 4 of 1.0.0)
4. `1.0.0.1` (test version 1 of 1.0.0)
5. `1.0.0` (stable release)

## How to Use Test Versions

### For Developers

1. **Creating Test Versions:**
   ```json
   {
     "version": "0.2.8.1",
     "test_version": true,
     "testing_notes": "⚠️ This is a test version for development purposes."
   }
   ```

2. **Updating releases.json:**
   - Add test version entries to the `releases` array
   - Set `test_version: true` flag
   - Use a different `commit_hash` (e.g., "test-branch")
   - Include detailed `testing_notes`

### For Users

1. **Checking for Stable Updates:**
   - Use `Prof-Tools → Help → Check for Updates...`
   - This only shows stable releases

2. **Checking for Test Updates:**
   - Use `Prof-Tools → Help → Check for Test Updates...`
   - This includes both stable and test versions
   - **Warning dialogs will indicate test versions**

## Example Test Version Entry

```json
{
  "version": "0.2.8.1",
  "date": "2025-07-21",
  "commit_hash": "test-branch",
  "description": "TEST VERSION: Enhanced versioning system",
  "features": [
    "Added support for MAJOR.MINOR.PATCH.TEST versioning",
    "Enhanced version comparison for test versions",
    "Added test update checking functionality"
  ],
  "test_version": true,
  "testing_notes": "⚠️ This is a test version for development purposes. Use at your own risk.",
  "breaking_changes": false
}
```

## Version Comparison Logic

The enhanced version comparison system:

1. **Validates semantic versioning** for both standard and test formats
2. **Prioritizes stable versions** over test versions of the same base
3. **Orders test versions** numerically by test number
4. **Provides fallback** to basic comparison if enhanced features aren't available

## API Reference

### Version Utilities

```python
from prof.core.version_utils import (
    is_test_version,
    compare_versions_extended,
    get_stable_version_string,
    parse_semantic_version
)

# Check if a version is a test version
is_test = is_test_version("0.2.8.1")  # Returns True

# Compare versions with test support
is_newer = compare_versions_extended("0.2.7", "0.2.8.1", include_test_versions=True)

# Get stable version from test version
stable = get_stable_version_string("0.2.8.1")  # Returns "0.2.8"

# Parse version components
parsed = parse_semantic_version("0.2.8.1")
# Returns: {'major': 0, 'minor': 2, 'patch': 8, 'test': 1, 'is_test_version': True}
```

### Update Checking

```python
from prof.core.updater import check_for_test_updates, get_latest_version

# Check for test updates with UI dialog
check_for_test_updates()

# Get latest version including test versions
latest = get_latest_version(include_test=True)
```

## Best Practices

### For Developers

1. **Increment test numbers** sequentially for the same base version
2. **Use descriptive commit hashes** for test branches
3. **Include clear testing notes** about what's being tested
4. **Set test_version flag** to true in releases.json
5. **Test thoroughly** before promoting to stable release

### For Users

1. **Use stable versions** for production work
2. **Only use test versions** when specifically testing new features
3. **Report issues** found in test versions to developers
4. **Backup your work** before installing test versions
5. **Check testing notes** before installing

## Migration from Old System

The new system is **fully backward compatible** with the existing MAJOR.MINOR.PATCH format:

- Existing version strings continue to work unchanged
- Old releases.json entries are automatically supported
- Legacy version comparison functions still work
- No migration is required for existing installations

## Error Handling

The system includes robust error handling:

- **Invalid version formats** are caught and logged
- **Fallback mechanisms** ensure continued operation
- **Clear error messages** help with debugging
- **Graceful degradation** if test features aren't available
