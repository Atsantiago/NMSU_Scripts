#!/usr/bin/env python
"""
Test script to verify that validation function comments are preserved
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prof.tools.auto_grader.assignments.fdma2530.u01_ss01_primitives import validate_file_name

def test_validation_comments():
    print("=== TESTING FILE NAME VALIDATION COMMENTS ===")
    print()
    
    # Test case 1: Perfect file name
    print("Test 1: Perfect file name")
    score, comments = validate_file_name('AS_U01_SS01_V01')
    print(f"File name: AS_U01_SS01_V01")
    print(f"Score: {score}%")
    print(f"Comments: {comments}")
    print()
    
    # Test case 2: File name with one error
    print("Test 2: File name with unit error")
    score, comments = validate_file_name('AS_U02_SS01_V01')
    print(f"File name: AS_U02_SS01_V01")
    print(f"Score: {score}%")
    print(f"Comments: {comments}")
    print()
    
    # Test case 3: File name with multiple errors
    print("Test 3: Completely wrong file name")
    score, comments = validate_file_name('WrongName')
    print(f"File name: WrongName")
    print(f"Score: {score}%")
    print(f"Comments: {comments}")
    print()
    
    print("=== VALIDATION COMMENTS TEST COMPLETE ===")

if __name__ == "__main__":
    test_validation_comments()
