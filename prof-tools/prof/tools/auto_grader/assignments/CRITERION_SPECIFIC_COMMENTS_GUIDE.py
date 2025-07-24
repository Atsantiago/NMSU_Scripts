"""
CRITERION-SPECIFIC PERFORMANCE COMMENTS SYSTEM
==============================================

This document explains the enhanced rubric system that provides tailored feedback
comments based on each criterion's specific scoring methodology.

OVERVIEW:
=========

The system now supports criterion-specific performance comments that provide
meaningful, relevant feedback based on the actual scoring criteria for each
rubric item. When instructors manually adjust scores (via dropdown, text field,
or performance level buttons), the comments automatically update to reflect
the specific meaning of that score for that particular criterion.

KEY FEATURES:
============

1. CRITERION-SPECIFIC FEEDBACK
   - Each criterion can define its own performance level comments
   - Comments reflect the actual scoring methodology (e.g., "2 errors" for 70%)
   - Provides specific guidance relevant to that criterion

2. FLEXIBLE SCORE MATCHING
   - Exact score matches (e.g., 100% → specific comment)
   - Closest score matching for intermediate values
   - Level name matching ("Full Marks", "High Marks", etc.)

3. AUTOMATIC FALLBACK
   - Generic comments when no specific comments are defined
   - Maintains consistency across all rubrics
   - No breaking changes to existing rubrics

4. WORKS WITH ALL INTERACTION METHODS
   - Dropdown percentage selection
   - Manual text input
   - Performance level button clicks

USAGE EXAMPLES:
===============

EXAMPLE 1: File Naming Criterion (U01_SS01)
-------------------------------------------

The File Names criterion uses an error-count based scoring system:
- 0 errors = 100%
- 1 error = 90%  
- 2 errors = 70%
- 3+ errors = 50%

Performance comments are defined to match this scoring:

```python
file_name_comments = {
    100: "Perfect file naming! Follows XX_U01_SS01_V##[_##|.####] format exactly.",
    90: "Good file naming with 1 minor error. Review naming convention on Canvas.",
    70: "File naming has 2 errors. Check the required format: XX_U01_SS01_V##[_##|.####]",
    50: "File naming has 3+ errors. Please review the naming instructions on Canvas carefully.",
    0: "No valid file name found or completely incorrect format."
}

rubric.add_criterion(
    "File Names",
    2.0,
    "Proper naming conventions",
    validation_function=validate_file_name,
    validation_args=[file_name],
    general_performance_comments=file_name_comments
)
```

WHEN USER SELECTS:
- 75% → System finds closest match (70%) → "File naming has 2 errors..."
- 90% → Exact match → "Good file naming with 1 minor error..."
- 65% → Closest match (50%) → "File naming has 3+ errors..."

EXAMPLE 2: Outliner Organization Criterion
------------------------------------------

```python
outliner_comments = {
    100: "Excellent outliner organization! Clean hierarchy with logical grouping and naming.",
    90: "Good organization with 1 minor issue. Objects well-grouped with mostly clear naming.",
    70: "Basic organization present but 2 areas need improvement (grouping/naming/hierarchy).",
    50: "Poor organization with 3+ issues. Review outliner best practices on Canvas.",
    0: "No clear organization visible. Objects scattered without logical structure."
}
```

EXAMPLE 3: Using Batch Addition
-------------------------------

```python
criteria_batch = [
    {
        'name': 'Modeling Quality',
        'point_value': 3.0,
        'description': 'Clean geometry and techniques',
        'general_performance_comments': {
            100: "Perfect modeling! Clean topology and professional techniques.",
            90: "Excellent modeling with 1 minor technique issue.",
            70: "Good modeling but 2 areas need refinement.",
            50: "Basic modeling with 3+ technical issues to address."
        }
    },
    {
        'name': 'Creative Design',
        'point_value': 2.5,
        'description': 'Originality and artistic vision',
        'general_performance_comments': {
            100: "Outstanding creativity! Innovative design exceeds expectations.",
            90: "Strong creative vision with professional execution.",
            70: "Good creativity shown but could push design further.",
            50: "Limited creativity evident. Needs more artistic development."
        }
    }
]

rubric.add_criteria_batch(criteria_batch)
```

IMPLEMENTATION DETAILS:
======================

SCORE MATCHING ALGORITHM:
1. Check for exact percentage match
2. If not found, find closest numerical match
3. Support level name matching ("Full Marks", etc.)
4. Fallback to generic comments if no specific comments defined

COMMENT GENERATION FLOW:
1. User adjusts score (dropdown/field/button)
2. System calls _generate_performance_level_comments()
3. Method checks for criterion-specific comments
4. Applies score matching logic
5. Returns appropriate comment
6. UI updates with new comment

BACKWARDS COMPATIBILITY:
=======================

✅ Existing rubrics continue to work unchanged
✅ Generic comments used when no specific comments defined
✅ All existing functionality preserved
✅ New features are purely additive

BENEFITS FOR INSTRUCTORS:
========================

1. MEANINGFUL FEEDBACK
   - Comments match the actual scoring criteria
   - Students get specific guidance on improvements
   - Consistent messaging across all grading

2. TIME SAVINGS
   - Automatic comment generation based on score
   - No need to manually type feedback for each score level
   - Standardized feedback reduces grading time

3. EDUCATIONAL VALUE
   - Students understand exactly what the score means
   - Clear connection between score and specific issues
   - Directed guidance for improvement

IMPLEMENTATION FOR NEW RUBRICS:
===============================

1. DEFINE PERFORMANCE COMMENTS for each criterion based on your scoring methodology
2. USE THE ENHANCED add_criterion() method with performance_comments parameter
3. ALTERNATIVELY use add_criteria_batch() for complex rubrics
4. COMMENTS AUTOMATICALLY WORK with all user interactions

SAMPLE TEMPLATE FOR NEW RUBRICS:
================================

```python
# Define criterion-specific comments based on your scoring methodology
criterion_comments = {
    100: "Perfect! Meets all requirements exactly.",
    90: "Excellent with 1 minor area for improvement.",
    70: "Good work but 2 specific areas need attention.",
    50: "Basic work with 3+ areas requiring improvement.",
    0: "Significant work needed. Please review requirements."
}

# Add to rubric
rubric.add_criterion(
    "Your Criterion Name",
    point_value,
    "Description",
    validation_function=your_validation_function,
    general_performance_comments=criterion_comments
)
```

TESTING AND VALIDATION:
=======================

The system has been tested with:
✅ Exact score matches
✅ Intermediate score matching (finds closest)
✅ Generic fallback functionality  
✅ Batch addition with performance comments
✅ All user interaction methods (dropdown, field, buttons)
✅ Manual override preservation during recalculation

FUTURE ENHANCEMENTS:
===================

The system is designed to support future enhancements such as:
- Range-based comments (e.g., {(85,100): "Excellent range"})
- Conditional comments based on other criteria
- Templated comments with variable substitution
- Multi-language support

CONCLUSION:
===========

This enhancement provides meaningful, criterion-specific feedback that helps
students understand exactly what their scores mean and how to improve. The
system maintains full backwards compatibility while adding powerful new
capabilities for creating more educational and useful rubrics.
"""

# Example implementation showing the complete pattern
def example_implementation():
    """Example of how to implement criterion-specific comments in a new rubric"""
    
    from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric
    
    # Create rubric
    rubric = LessonRubric("Example Assignment", total_points=10)
    
    # Example 1: Simple criterion with specific comments
    rubric.add_criterion(
        "File Organization",
        2.0,
        "Proper file structure and naming",
        general_performance_comments={
            100: "Perfect organization! All files properly named and structured.",
            90: "Well organized with 1 minor naming issue.",
            70: "Basic organization but 2 areas need improvement.", 
            50: "Poor organization with multiple issues. Review guidelines.",
            0: "No clear organization present."
        }
    )
    
    # Example 2: Using batch addition
    criteria = [
        {
            'name': 'Technical Quality',
            'point_value': 3.0,
            'description': 'Clean geometry and proper techniques',
            'general_performance_comments': {
                100: "Flawless technical execution!",
                90: "Excellent with 1 minor technical issue.",
                70: "Good technique but 2 areas need refinement.",
                50: "Basic technique with several issues to address."
            }
        }
    ]
    
    rubric.add_criteria_batch(criteria)
    
    return rubric

if __name__ == "__main__":
    print("Criterion-Specific Performance Comments System Documentation")
    print("See function docstrings and examples above for implementation details.")
