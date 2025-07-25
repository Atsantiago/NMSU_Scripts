#!/usr/bin/env python
"""
Test script to verify that manual score changes update comments appropriately
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prof.tools.auto_grader.assignments.fdma2530.u01_ss01_primitives import RUBRIC_CRITERIA, validate_file_name
from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric

def test_manual_score_comment_updates():
    print("=== TESTING MANUAL SCORE COMMENT UPDATES ===")
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
    
    # Step 1: Apply validation results (simulating automatic scoring)
    score, comments = validate_file_name(test_file_name)
    rubric.criteria["File Names"]["percentage"] = score
    rubric.criteria["File Names"]["comments"] = comments
    rubric.criteria["File Names"]["manual_override"] = False
    
    print("Step 1: Initial validation results")
    print(f"  Score: {score}%")
    print(f"  Comments: '{comments}'")
    print(f"  Manual Override: {rubric.criteria['File Names']['manual_override']}")
    print()
    
    # Step 2: Verify that _generate_comments preserves validation comments
    generated_comments = rubric._generate_comments("File Names")
    print("Step 2: Generated comments (should preserve validation)")
    print(f"  Generated: '{generated_comments}'")
    print(f"  Match validation: {generated_comments == comments}")
    print()
    
    # Step 3: Simulate manual score change (like user clicking "Full Marks")
    print("Step 3: Simulating manual score change to 100% (Full Marks)")
    rubric._update_percentage_value("File Names", 100)
    
    final_criterion = rubric.criteria["File Names"]
    print(f"  New Score: {final_criterion['percentage']}%")
    print(f"  New Comments: '{final_criterion['comments']}'")
    print(f"  Manual Override: {final_criterion['manual_override']}")
    print()
    
    # Step 4: Verify comments now reflect the performance level, not validation
    expected_full_marks_comment = "Excellent work, all requirements exceeded."
    comments_match_level = expected_full_marks_comment in final_criterion['comments']
    
    print("Step 4: Verification")
    print(f"  Comments reflect Full Marks level: {comments_match_level}")
    print(f"  Expected to contain: '{expected_full_marks_comment}'")
    print(f"  Actual: '{final_criterion['comments']}'")
    
    if comments_match_level and final_criterion['manual_override']:
        print("✅ SUCCESS: Manual score changes update comments appropriately!")
    else:
        print("❌ FAILURE: Manual score changes did not work as expected!")
    
    print()
    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_manual_score_comment_updates()
