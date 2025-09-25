# Maya Shelf Persistence Issue - Solution & Diagnosis

## The Problem You're Experiencing

After uninstalling the FDMA 2530 shelf:
- ✅ **Files are properly removed** (shelf functions don't work)
- ❌ **Shelf tab still appears** in new Maya sessions
- ❌ **Empty/broken shelf persists** in Maya UI

## Root Cause

Maya stores shelf tab information in **multiple preference files** that our original uninstall wasn't cleaning:

### Critical Files Maya Uses:
1. **`windowPrefs.mel`** - Stores UI layout including which shelf tabs exist
2. **`userPrefs.mel`** - User preferences including shelf settings  
3. **`shelves/shelf_FDMA_2530.mel`** - The actual shelf definition file
4. **Maya optionVars** - Runtime preferences stored in Maya's database

## Enhanced Solution Implemented

### **More Aggressive Preference Cleaning**

I've updated the `_remove_shelf_from_preferences()` function to:

#### 1. **Clean windowPrefs.mel** 
```python
windowprefs_path = os.path.join(maya_app_dir, "prefs", "windowPrefs.mel")
# Remove any lines containing SHELF_NAME
```

#### 2. **Clean userPrefs.mel**
```python
userprefs_path = os.path.join(maya_app_dir, "prefs", "userPrefs.mel") 
# Remove any lines containing SHELF_NAME
```

#### 3. **Force MEL Tab Removal**
```python
# Use MEL commands to forcibly remove shelf tab
mel.eval('deleteUI "{}";'.format(SHELF_NAME))
```

#### 4. **Save Both Preference Types**
```python
cmds.savePrefs(shelves=True)    # Save shelf preferences
cmds.savePrefs(general=True)    # Save general UI preferences
```

## Diagnostic Function Added

Run this in Maya to see exactly where shelf references are hiding:

```python
# Import and run the installer
exec(open(r"path/to/setup_drag_drop_fdma2530.py").read())

# Run diagnostic
diagnose_shelf_persistence()
```

This will show you:
- Which preference files contain shelf references
- What optionVars exist
- Current shelf tab layout status
- Installation file status

## Expected Results After Fix

### **Immediate (Same Session)**
- Shelf functionality disabled
- Files removed
- Preferences cleaned

### **After Maya Restart**
- ✅ Shelf tab should NOT appear
- ✅ No broken shelf remnants
- ✅ Clean Maya interface

## Testing Instructions

1. **Install** the shelf first (if not already installed)
2. **Run enhanced uninstaller** (with new preference cleaning)
3. **Restart Maya completely**
4. **Verify** shelf tab does not appear

## If Shelf Still Persists

Run the diagnostic function to see exactly where Maya is storing the shelf reference, then we can target those specific files.

The enhanced uninstaller now targets the most common locations where Maya stores persistent shelf information, which should resolve the issue completely.

## Key Improvement

**Before**: Only removed shelf files and basic optionVars
**After**: Comprehensive cleaning of all Maya preference locations + forced UI cleanup

This addresses the core issue where Maya's UI layout preferences were maintaining shelf tab references even after the actual shelf content was removed.