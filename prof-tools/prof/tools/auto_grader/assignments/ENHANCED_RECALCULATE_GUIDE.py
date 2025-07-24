"""
Enhanced Recalculate Functionality - Documentation and Examples

This document shows the improvements made to the recalculate system
to ensure it works with any and all future rubrics you create.

KEY ENHANCEMENTS:
================

1. FLEXIBLE VALIDATION FUNCTION HANDLING
   - Supports multiple return types: tuple (score, comments), score only, or dictionary
   - Handles various argument patterns: no args, single arg, multiple args, list args
   - Graceful error handling - validation failures don't crash the system

2. ROBUST ARGUMENT PROCESSING
   - Normalizes validation arguments to consistent format
   - Supports both list and single argument patterns
   - Backwards compatible with existing rubrics

3. COMPREHENSIVE ERROR HANDLING
   - Invalid return types are caught and logged
   - Broken validation functions don't affect other criteria
   - Out-of-range scores are validated and rejected safely

4. CONVENIENCE METHODS FOR FUTURE RUBRICS
   - add_validated_criterion() for easy single criterion addition
   - add_criteria_batch() for bulk criterion setup
   - Flexible argument handling in both methods

USAGE PATTERNS FOR FUTURE RUBRICS:
==================================

# Pattern 1: Simple validation function (no arguments)
def check_basic_requirement():
    # Your validation logic here
    return (95, "All requirements met")

rubric.add_criterion("Basic Check", 2.0, "Description", check_basic_requirement)

# Pattern 2: Validation with arguments
def check_object_count(expected_count):
    # Your validation logic here
    actual = len(get_scene_objects())
    if actual == expected_count:
        return (100, f"Perfect! Found {expected_count} objects")
    else:
        return (70, f"Expected {expected_count}, found {actual}")

rubric.add_criterion("Object Count", 3.0, "Check count", check_object_count, [5])

# Pattern 3: Multiple arguments
def check_complex_requirement(min_val, max_val, object_type):
    # Your validation logic here
    return (85, f"Validated {object_type} objects in range {min_val}-{max_val}")

rubric.add_criterion("Complex Check", 2.0, "Description", 
                    check_complex_requirement, [1, 10, "mesh"])

# Pattern 4: Using convenience method
rubric.add_validated_criterion("Easy Check", 2.0, "Description", 
                              check_basic_requirement)

# Pattern 5: Batch addition for complex rubrics
criteria_list = [
    {
        'name': 'Modeling Quality',
        'point_value': 3.0,
        'description': 'Clean geometry and proper techniques',
        'validation_function': check_modeling_quality
    },
    {
        'name': 'Object Count',
        'point_value': 2.0,
        'description': 'Correct number of objects',
        'validation_function': check_object_count,
        'validation_args': [5]
    },
    {
        'name': 'Naming Convention',
        'point_value': 1.0,
        'description': 'Proper naming used',
        'validation_function': check_naming_convention,
        'validation_args': ['prefix', 'suffix']
    }
]

rubric.add_criteria_batch(criteria_list)

SUPPORTED VALIDATION FUNCTION RETURN TYPES:
==========================================

# Type 1: Standard tuple (score, comments) - RECOMMENDED
def standard_validation():
    return (95, "Detailed feedback about the work")

# Type 2: Score only (auto-generates generic comments)
def score_only_validation():
    return 85

# Type 3: Dictionary with 'score' key
def dict_validation():
    return {'score': 90, 'comments': 'Custom feedback'}

# Type 4: Dictionary with 'percentage' key (alternative)
def dict_percentage_validation():
    return {'percentage': 95, 'comments': 'Another format'}

ERROR HANDLING:
===============

The enhanced system handles these error conditions gracefully:
- Validation functions that raise exceptions
- Invalid return types or values
- Missing validation functions
- Corrupted criterion data
- Out-of-range scores (0-100 enforced)

When errors occur:
- The specific criterion keeps its existing values
- Other criteria continue to update normally
- Errors are logged for debugging
- The UI shows appropriate feedback

MANUAL OVERRIDE PRESERVATION:
============================

The system preserves instructor manual adjustments:
- Criteria marked as 'manual_override' are skipped during recalculation
- This allows instructors to make adjustments that persist through recalculation
- Only auto-validated criteria are updated when recalculate is pressed

BACKWARDS COMPATIBILITY:
=======================

All existing rubrics will continue to work without modification:
- Old validation function patterns still work
- Existing argument structures are supported
- No breaking changes to the core API

The enhancements are additive - they extend functionality without
breaking existing code patterns.

BENEFITS FOR FUTURE RUBRICS:
============================

1. More Flexible: Support any validation function pattern you might need
2. More Robust: Handles errors gracefully without crashing
3. Easier to Use: Convenience methods reduce boilerplate code
4. Better Feedback: Enhanced error reporting and user feedback
5. Consistent Behavior: Standardized handling across all rubric types
6. Future-Proof: Designed to handle new patterns as they emerge

IMPLEMENTATION DETAILS:
======================

The enhanced re_run_validations() method:
- Checks for manual overrides and skips them
- Validates that validation functions are callable
- Handles multiple argument formats automatically
- Processes different return types intelligently
- Provides comprehensive error logging
- Returns count of updated criteria for user feedback

This ensures that no matter how you structure your future rubrics,
the recalculate functionality will work reliably and provide
meaningful feedback to instructors.
"""

def demonstrate_patterns():
    """
    This function demonstrates various patterns that will work
    with the enhanced recalculate system.
    """
    
    # Example validation functions that return different types
    
    def pattern1_standard():
        """Standard (score, comments) tuple - most common pattern"""
        return (95, "Excellent work meeting all requirements")
    
    def pattern2_score_only():
        """Just return a score - system will generate generic comments"""
        return 80
    
    def pattern3_dict_score():
        """Dictionary with score key"""
        return {
            'score': 90,
            'comments': 'Very good work with minor improvements needed'
        }
    
    def pattern4_dict_percentage():
        """Dictionary with percentage key (alternative naming)"""
        return {
            'percentage': 85,
            'comments': 'Good work, meets most requirements'
        }
    
    def pattern5_with_args(expected_value):
        """Function that takes arguments"""
        # Simulate checking something
        if expected_value == 5:
            return (100, f"Perfect! Found exactly {expected_value} items")
        else:
            return (75, f"Expected {expected_value}, but close enough")
    
    def pattern6_multiple_args(min_val, max_val, object_type):
        """Function with multiple arguments"""
        return (88, f"Validated {object_type} objects in range {min_val}-{max_val}")
    
    print("Enhanced Recalculate System - Pattern Examples")
    print("=" * 50)
    print("These validation function patterns will all work with the enhanced system:")
    print()
    print("1. Standard tuple return:", pattern1_standard())
    print("2. Score only return:", pattern2_score_only())
    print("3. Dictionary score return:", pattern3_dict_score())
    print("4. Dictionary percentage return:", pattern4_dict_percentage())
    print("5. Function with args:", pattern5_with_args(5))
    print("6. Multiple args:", pattern6_multiple_args(1, 10, "mesh"))
    print()
    print("All of these patterns are supported by the enhanced recalculate system!")
    print("Your future rubrics can use any combination of these patterns.")

if __name__ == "__main__":
    demonstrate_patterns()
