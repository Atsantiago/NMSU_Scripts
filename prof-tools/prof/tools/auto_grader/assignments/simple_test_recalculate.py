#!/usr/bin/env python
"""
Simple test for enhanced recalculate functionality without Maya dependencies.
"""

import sys
import os

# Mock Maya for testing
class MockCmds:
    @staticmethod
    def ls(*args, **kwargs):
        return ['pCube1', 'pSphere1', 'pCylinder1']  # Mock scene objects

# Inject mock Maya
sys.modules['maya'] = type('module', (), {})()
sys.modules['maya.cmds'] = MockCmds()
sys.modules['maya.mel'] = type('module', (), {})()

# Add the prof-tools path to sys.path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lessonRubric_template import LessonRubric

def test_validation_function_1():
    """Standard tuple return"""
    return (95, "Excellent work")

def test_validation_function_2():
    """Score only return"""
    return 75

def test_validation_function_3():
    """Dictionary return"""
    return {'score': 85, 'comments': 'Good work'}

def test_validation_with_args(expected_count):
    """Function with arguments"""
    return (100, f"Found {expected_count} items")

def test_broken_function():
    """Function that raises exception"""
    raise ValueError("Test error")

def simple_test():
    """Simple test of enhanced functionality"""
    print("Testing Enhanced Recalculate Functionality")
    print("=" * 50)
    
    # Create test rubric
    rubric = LessonRubric("Test Assignment", total_points=10)
    
    # Add various types of criteria
    rubric.add_criterion("Standard", 2.0, "Standard test", test_validation_function_1)
    rubric.add_criterion("Score Only", 2.0, "Score only test", test_validation_function_2)  
    rubric.add_criterion("Dict Return", 2.0, "Dict test", test_validation_function_3)
    rubric.add_criterion("With Args", 2.0, "Args test", test_validation_with_args, [5])
    rubric.add_criterion("Error Test", 1.0, "Error test", test_broken_function)
    rubric.add_criterion("No Validation", 1.0, "No validation")
    
    # Mark one as manual override
    rubric.criteria["Score Only"]["manual_override"] = True
    rubric.criteria["Score Only"]["percentage"] = 50
    
    print("\nBefore recalculate:")
    for name, criterion in rubric.criteria.items():
        manual = " (MANUAL)" if criterion.get('manual_override') else ""
        print(f"  {name}: {criterion['percentage']}%{manual}")
    
    print(f"\nTotal before: {rubric.calculate_total_score():.1f}")
    
    # Test recalculate
    updated_count = rubric.re_run_validations()
    
    print(f"\nUpdated {updated_count} criteria")
    print("\nAfter recalculate:")
    for name, criterion in rubric.criteria.items():
        manual = " (MANUAL)" if criterion.get('manual_override') else ""
        comments = criterion.get('comments', '')[:30]
        print(f"  {name}: {criterion['percentage']}% - {comments}...{manual}")
    
    print(f"\nTotal after: {rubric.calculate_total_score():.1f}")
    
    # Test convenience methods
    print("\n" + "="*30)
    print("Testing Convenience Methods")
    print("="*30)
    
    rubric2 = LessonRubric("Convenience Test", total_points=5)
    
    # Test add_validated_criterion
    rubric2.add_validated_criterion("Simple", 2.0, "Simple", test_validation_function_1)
    rubric2.add_validated_criterion("With Args", 3.0, "Args", test_validation_with_args, 7)
    
    # Test batch method
    criteria_batch = [
        {'name': 'Batch 1', 'point_value': 2.0, 'validation_function': test_validation_function_1},
        {'name': 'Batch 2', 'point_value': 3.0, 'validation_function': test_validation_function_3}
    ]
    
    rubric3 = LessonRubric("Batch Test", total_points=5)
    rubric3.add_criteria_batch(criteria_batch)
    
    print(f"\nConvenience rubric updated: {rubric2.re_run_validations()} criteria")
    print(f"Batch rubric updated: {rubric3.re_run_validations()} criteria")
    
    print("\nTest complete! Enhanced recalculate system is working.")
    return True

if __name__ == "__main__":
    simple_test()
