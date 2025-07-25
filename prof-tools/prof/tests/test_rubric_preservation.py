#!/usr/bin/env python
"""
Test script to verify that validation function comments are preserved in the rubric
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prof.tools.auto_grader.assignments.fdma2530.u01_ss01_primitives import RUBRIC_CRITERIA, validate_file_name
from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric

def test_rubric_comment_preservation():
    print("=== TESTING RUBRIC COMMENT PRESERVATION ===")
    print()
    
    # Create a rubric instance (without Maya UI)
    rubric = LessonRubric(
        assignment_name="FDMA 2530 - U01_SS01: Test File",
        assignment_display_name="Test File",
        total_points=10,
        project_name="Primitive Modeling"
    )
    
    # Add criteria
    for criterion in RUBRIC_CRITERIA:
        rubric.add_criterion(
            criterion["name"],
            criterion["points"],
            criterion["description"]
        )
    
    # Test with a file name that has validation issues
    test_file_name = "AS_U02_SS01_V01"  # Has wrong unit number
    
    # Run validation and apply results (simulating what happens in the real rubric)
    score, comments = validate_file_name(test_file_name)
    print(f"Validation function returned:")
    print(f"  Score: {score}%")
    print(f"  Comments: {comments}")
    print()
    
    # Apply validation results to rubric
    rubric.criteria["File Names"]["percentage"] = score
    rubric.criteria["File Names"]["comments"] = comments
    rubric.criteria["File Names"]["manual_override"] = False
    
    # Test that _generate_comments preserves the existing comments
    generated_comments = rubric._generate_comments("File Names")
    print(f"Generated comments (should be same as validation): {generated_comments}")
    print()
    
    # Test that the comments are preserved
    file_names_criterion = rubric.criteria["File Names"]
    print(f"Final criterion data:")
    print(f"  Percentage: {file_names_criterion['percentage']}%")
    print(f"  Comments: '{file_names_criterion['comments']}'")
    print(f"  Manual Override: {file_names_criterion['manual_override']}")
    print()
    
    # Verify the comments match
    if file_names_criterion['comments'] == comments:
        print("✅ SUCCESS: Validation comments are preserved!")
    else:
        print("❌ FAILURE: Validation comments were overwritten!")
        print(f"Expected: '{comments}'")
        print(f"Got: '{file_names_criterion['comments']}'")
    
    print()
    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_rubric_comment_preservation()
