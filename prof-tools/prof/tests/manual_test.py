"""
Manual test of some file name validation examples
"""

# Test file names manually
test_names = [
    "AB_U01_SS01_V01",      # Perfect
    "ABC_U01_SS01_V01_01",  # Perfect with iteration
    "AB_U01_SS01_V01.0001", # Perfect with dot iteration
    "AB_U02_SS01_V01",      # Wrong unit
    "AB_U01_SS02_V01",      # Wrong softskill
    "AB_U01_SS01_B01",      # Missing V
    "AB-U01-SS01-V01",      # Wrong separators
    ""                      # Empty
]

print("File Name Validation Examples:")
print("=" * 50)

for name in test_names:
    print(f"'{name}'")
    
    # Manual validation logic
    if not name:
        print("  -> FAIL: Empty filename")
        continue
        
    parts = name.split('_')
    if len(parts) < 4:
        print("  -> FAIL: Not enough underscore-separated parts")
        continue
        
    initials, unit, softskill, version_part = parts[:4]
    
    # Check initials (2-3 letters)
    if not (2 <= len(initials) <= 3 and initials.isalpha()):
        print(f"  -> FAIL: Initials '{initials}' should be 2-3 letters")
        continue
        
    # Check unit
    if unit != "U01":
        print(f"  -> FAIL: Unit '{unit}' should be 'U01'")
        continue
        
    # Check softskill  
    if softskill != "SS01":
        print(f"  -> FAIL: SoftSkill '{softskill}' should be 'SS01'")
        continue
        
    # Check version
    if not version_part.startswith('V'):
        print(f"  -> FAIL: Version '{version_part}' should start with 'V'")
        continue
        
    print("  -> PASS: Basic format correct")

print("\nThe validation function should handle these cases appropriately.")
