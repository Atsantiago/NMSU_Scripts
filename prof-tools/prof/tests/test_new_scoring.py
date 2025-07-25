"""
Test examples for the updated FDMA 2530 U01_SS01 file name validation
Shows the new error-based scoring system: 1 error = 90%, 2 errors = 70%, 3+ errors = 50%
"""

test_cases = [
    # Perfect examples (100%)
    ("AB_U01_SS01_V01", "Perfect format"),
    ("ABC_U01_SS01_V01_01", "Perfect with iteration"),
    ("AB_U01_SS01_V02.0001", "Perfect with dot iteration"),
    
    # 1 error examples (90%)
    ("AB_U02_SS01_V01", "Wrong unit number only"),
    ("AB_U01_SS02_V01", "Wrong SoftSkill number only"),
    ("AB_U01_SS01_B01", "Missing V in version only"),
    ("AB_U01_SS01_V01_00", "Invalid iteration number only"),
    
    # 2 error examples (70%)
    ("AB_U02_SS02_V01", "Wrong unit AND SoftSkill"),
    ("AB_U02_SS01_B01", "Wrong unit AND missing V"),
    ("AB_U01_SS02_B01", "Wrong SoftSkill AND missing V"),
    
    # 3+ error examples (50%)
    ("AB_U02_SS02_B01", "Wrong unit, SoftSkill, AND missing V"),
    ("A_U02_SS02_B01", "Wrong initials, unit, SoftSkill, AND missing V"),
    
    # Structural errors (50%-90% based on error count)
    ("AB-U01-SS01-V01", "Missing underscores (structural)"),
    ("ABCD_U01_SS01_V01", "Wrong initials + good rest"),
    ("AB_U01_V01", "Missing SS01"),
    ("random_file", "Completely wrong format"),
]

print("FDMA 2530 U01_SS01 File Name Validation - New Error-Based Scoring")
print("=" * 80)
print("Scoring Rules:")
print("• 0 errors = 100% (Perfect)")
print("• 1 error = 90% (Good)")  
print("• 2 errors = 70% (Needs attention)")
print("• 3+ errors = 50% (Major issues)")
print("=" * 80)

for filename, description in test_cases:
    print(f"\nExample: '{filename}' ({description})")
    print("Expected behavior based on new logic:")
    
    # Manual analysis for demonstration
    if filename in ["AB_U01_SS01_V01", "ABC_U01_SS01_V01_01", "AB_U01_SS01_V02.0001"]:
        print("  Score: 100% - Perfect file naming!")
    elif filename in ["AB_U02_SS01_V01", "AB_U01_SS02_V01", "AB_U01_SS01_B01", "AB_U01_SS01_V01_00"]:
        print("  Score: 90% - Good file naming with 1 error")
    elif filename in ["AB_U02_SS02_V01", "AB_U02_SS01_B01", "AB_U01_SS02_B01"]:
        print("  Score: 70% - File naming has 2 errors")
    else:
        print("  Score: 50% - File naming has major issues (3+ errors or structural problems)")

print("\n" + "=" * 80)
print("The validation function now provides specific error details for each issue found!")
