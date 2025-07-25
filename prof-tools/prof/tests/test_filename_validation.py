#!/usr/bin/env python
"""
Test script for the FDMA 2530 U01_SS01 file name validation logic.
"""

import sys
import os
import re

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def validate_file_name(file_name):
    """
    Validate FDMA 2530 U01_SS01 file naming convention.
    
    Expected format: "XX_U01_SS01_V01_ZZ" OR "XX_U01_SS01_V01.ZZZZ"
    Where:
    - XX/XXX: Student initials (2-3 letters)
    - U01: Unit number (must be exactly "U01")
    - SS01: SoftSkill number (must be exactly "SS01") 
    - V##: Version number (must start with "V" + numbers)
    - ZZ/ZZZZ: Iteration number (optional, can be _## or .####)
    
    Args:
        file_name (str): The file name to validate
        
    Returns:
        tuple: (score_percentage, comments)
            score_percentage: 0-100 based on file name compliance
            comments: Detailed feedback about the file name
    """
    if not file_name or file_name.strip() == "":
        return (0, "No file name found.")
    
    # Remove common Maya file extensions for analysis
    clean_name = file_name
    for ext in ['.ma', '.mb', '.mayaAscii', '.mayaBinary']:
        if clean_name.lower().endswith(ext.lower()):
            clean_name = clean_name[:-len(ext)]
            break
    
    # Define the regex pattern for the expected format
    # Pattern breakdown:
    # ^([A-Za-z]{2,3})    - 2-3 initials at start
    # _                   - required underscore
    # (U\d+)              - Unit (should be U01)
    # _                   - required underscore  
    # (SS\d+)             - SoftSkill (should be SS01)
    # _                   - required underscore
    # (V\d+)              - Version (must start with V)
    # (?:_(\d+)|\.(\d+))? - optional iteration: either _## or .####
    # $                   - end of string
    pattern = r'^([A-Za-z]{2,3})_(U\d+)_(SS\d+)_(V\d+)(?:_(\d+)|\.(\d+))?$'
    
    match = re.match(pattern, clean_name)
    
    if not match:
        # Check for common issues and provide specific feedback
        if '_' not in clean_name:
            return (10, "File name missing required underscores between components.")
        elif not re.search(r'^[A-Za-z]{2,3}_', clean_name):
            return (30, "File name should start with 2-3 letter initials followed by underscore.")
        elif 'U01' not in clean_name:
            return (50, "File name missing required unit number 'U01'.")
        elif 'SS01' not in clean_name:
            return (50, "File name missing required SoftSkill number 'SS01'.")
        elif not re.search(r'_V\d+', clean_name):
            return (65, "File name missing required version number (format: _V##).")
        else:
            return (70, "File name format incorrect. Expected: XX_U01_SS01_V##[_##|.####]")
    
    # Extract components
    initials, unit, softskill, version, iter_underscore, iter_dot = match.groups()
    
    # Validate each component
    issues = []
    base_score = 100
    
    # Check unit number (most critical)
    if unit != 'U01':
        issues.append(f"Unit number should be 'U01', found '{unit}'")
        base_score -= 40  # Major deduction for wrong unit
    
    # Check SoftSkill number (most critical)  
    if softskill != 'SS01':
        issues.append(f"SoftSkill number should be 'SS01', found '{softskill}'")
        base_score -= 40  # Major deduction for wrong SoftSkill
    
    # Check version format (must start with V)
    if not version.startswith('V'):
        issues.append(f"Version should start with 'V', found '{version}'")
        base_score -= 20
    
    # Iteration number validation (if present)
    iteration_num = iter_underscore or iter_dot
    if iteration_num:
        try:
            iter_int = int(iteration_num)
            if iter_int < 1:
                issues.append("Iteration number should start from 01 (or 0001)")
                base_score -= 10
        except ValueError:
            issues.append("Iteration number should be numeric")
            base_score -= 10
    
    # Generate feedback
    if base_score == 100:
        if iteration_num:
            comments = f"Perfect file naming! Format: {initials}_{unit}_{softskill}_{version} with iteration {iteration_num}."
        else:
            comments = f"Perfect file naming! Format: {initials}_{unit}_{softskill}_{version}."
    elif base_score >= 80:
        comments = f"Good file naming with minor issues: {'; '.join(issues)}"
    elif base_score >= 60:
        comments = f"File naming needs attention: {'; '.join(issues)}"
    else:
        comments = f"File naming has major issues: {'; '.join(issues)}"
    
    return (max(0, base_score), comments)

def test_filename_validation():
    """Test various file name scenarios"""
    
    # Test cases: (filename, expected_score_range, description)
    test_cases = [
        # Perfect examples
        ("AB_U01_SS01_V01", (95, 100), "Perfect format without iteration"),
        ("ABC_U01_SS01_V01_01", (95, 100), "Perfect format with underscore iteration"),
        ("AB_U01_SS01_V01.0001", (95, 100), "Perfect format with dot iteration"),
        ("JD_U01_SS01_V02_05", (95, 100), "Perfect format with different version/iteration"),
        
        # Maya file extensions (should be handled)
        ("AB_U01_SS01_V01.ma", (95, 100), "Perfect format with Maya ASCII extension"),
        ("AB_U01_SS01_V01.mb", (95, 100), "Perfect format with Maya Binary extension"),
        
        # Version variations (should work)
        ("AB_U01_SS01_V02", (95, 100), "Different version number"),
        ("AB_U01_SS01_V10", (95, 100), "Double digit version"),
        ("AB_U01_SS01_V30_15", (95, 100), "High version and iteration numbers"),
        
        # Initials variations (should work)
        ("A_U01_SS01_V01", (30, 70), "Single initial (invalid)"),  # Should fail - needs 2-3
        ("ABCD_U01_SS01_V01", (30, 70), "Four initials (invalid)"),  # Should fail - needs 2-3
        
        # Critical errors (should fail significantly)
        ("AB_U02_SS01_V01", (50, 70), "Wrong unit number"),
        ("AB_U01_SS02_V01", (50, 70), "Wrong SoftSkill number"),
        ("AB_U01_SS01_B01", (70, 90), "Missing V in version"),
        
        # Format errors
        ("AB-U01-SS01-V01", (0, 30), "Using dashes instead of underscores"),
        ("ABU01SS01V01", (0, 30), "Missing underscores"),
        ("AB_U01_SS01", (60, 80), "Missing version"),
        
        # Empty/invalid
        ("", (0, 10), "Empty filename"),
        ("random_file_name", (0, 30), "Completely wrong format"),
    ]
    
    print("Testing FDMA 2530 U01_SS01 File Name Validation")
    print("=" * 60)
    
    all_passed = True
    
    for filename, expected_range, description in test_cases:
        try:
            score, comments = validate_file_name(filename)
            min_expected, max_expected = expected_range
            
            # Check if score falls within expected range
            if min_expected <= score <= max_expected:
                status = "✓ PASS"
            else:
                status = "✗ FAIL"
                all_passed = False
            
            print(f"{status} '{filename}' -> {score}% (expected {min_expected}-{max_expected}%)")
            print(f"    {description}")
            print(f"    Comments: {comments}")
            print()
            
        except Exception as e:
            print(f"✗ ERROR '{filename}' -> Exception: {e}")
            all_passed = False
            print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed - check validation logic")

if __name__ == "__main__":
    test_filename_validation()
