#!/usr/bin/env python
"""
Test script to verify that the Recalculate button re-runs validations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prof.tools.auto_grader.assignments.fdma2530.u01_ss01_primitives import (
    RUBRIC_CRITERIA, validate_file_name, validate_outliner_organization,
    validate_primitive_design_principles, validate_technical_execution,
    validate_effort_professionalism
)
from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric

def test_recalculate_functionality():
    print("=== TESTING RECALCULATE FUNCTIONALITY ===")
    print()
    
    # Create a rubric instance (without Maya UI)
    rubric = LessonRubric(
        assignment_name="FDMA 2530 - U01_SS01: Test File",
        assignment_display_name="Test File",
        total_points=10,
        project_name="Primitive Modeling"
    )
    
    # Add criteria with validation functions (simulating new approach)
    test_file_name = "AS_U01_SS01_V01"  # Good file name
    
    # Map of validation function names to actual functions
    validation_function_map = {
        "validate_file_name": validate_file_name,
        "validate_outliner_organization": validate_outliner_organization,
        "validate_primitive_design_principles": validate_primitive_design_principles,
        "validate_technical_execution": validate_technical_execution,
        "validate_effort_professionalism": validate_effort_professionalism
    }
    
    for criterion in RUBRIC_CRITERIA:
        validation_func = validation_function_map.get(criterion["validation_function"])
        validation_args = [test_file_name] if criterion["validation_function"] == "validate_file_name" else []
        
        rubric.add_criterion(
            name=criterion["name"],
            point_value=criterion["points"],
            description=criterion["description"],
            validation_function=validation_func,
            validation_args=validation_args
        )
    
    print("Step 1: Initial state (before validation)")
    file_names_criterion = rubric.criteria["File Names"]
    print(f"  File Names Score: {file_names_criterion['percentage']}%")
    print(f"  File Names Comments: '{file_names_criterion['comments']}'")
    print(f"  Manual Override: {file_names_criterion['manual_override']}")
    print()
    
    # Step 2: Run initial validation manually (simulating what happens in create_u01_ss01_rubric)
    score, comments = validate_file_name(test_file_name)
    rubric.criteria["File Names"]["percentage"] = score
    rubric.criteria["File Names"]["comments"] = comments
    rubric.criteria["File Names"]["manual_override"] = False
    
    print("Step 2: After initial validation")
    print(f"  File Names Score: {score}%")
    print(f"  File Names Comments: '{comments}'")
    print()
    
    # Step 3: Manually adjust the score (simulating instructor override)
    rubric.criteria["File Names"]["percentage"] = 75
    rubric.criteria["File Names"]["comments"] = "Manually adjusted by instructor"
    rubric.criteria["File Names"]["manual_override"] = True
    
    print("Step 3: After manual adjustment")
    file_names_criterion = rubric.criteria["File Names"]
    print(f"  File Names Score: {file_names_criterion['percentage']}%")
    print(f"  File Names Comments: '{file_names_criterion['comments']}'")
    print(f"  Manual Override: {file_names_criterion['manual_override']}")
    print()
    
    # Step 4: Test re-running validations (simulating Recalculate button)
    print("Step 4: Re-running validations (Recalculate button)")
    updated_count = rubric.re_run_validations()
    print(f"  Updated {updated_count} criteria")
    
    final_criterion = rubric.criteria["File Names"]
    print(f"  File Names Score: {final_criterion['percentage']}%")
    print(f"  File Names Comments: '{final_criterion['comments']}'")
    print(f"  Manual Override: {final_criterion['manual_override']}")
    print()
    
    # Verification
    if final_criterion['manual_override'] and final_criterion['percentage'] == 75:
        print("✅ SUCCESS: Manual overrides are preserved during recalculation!")
    else:
        print("❌ FAILURE: Manual overrides were not preserved!")
    
    print()
    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_recalculate_functionality()
