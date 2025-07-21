# Assignment Grading Rubric System

A comprehensive grading rubric system for Maya assignments that provides standardized, efficient, and fair grading with auto-generated feedback.

## Features

### 🎯 5-Tier Scoring System
- **No Marks** (0-5%): Criterion not met or not attempted
- **Low Marks** (6-15%): Minimal effort, significant improvements needed  
- **Partial Marks** (16-45%): Basic requirements met, some improvement needed
- **High Marks** (46-75%): Good work with minor areas for improvement
- **Full Marks** (76-100%): Excellent work, all requirements exceeded

### 📊 Smart Percentage Scoring
- Dropdown with preset percentages: `0%, 10%, 30%, 50%, 70%, 85%, 95%, 100%`
- Manual entry capability for custom percentages
- Auto-calculation of points based on percentage and criterion weight
- Real-time score updates

### 🔍 Empty File Detection
- Automatically detects empty or minimal Maya files
- Defaults scores to "Low Marks" (10%) for empty files
- Provides visual warning in the interface
- Generates appropriate comments for empty submissions

### 📋 Professional UI
- **Column 1**: Criteria names and descriptions
- **Column 2**: Percentage score (dropdown + manual entry)
- **Column 3**: Visual performance level indicators
- **Column 4**: Points earned/total for each criterion
- Auto-generated comments for each criterion
- Real-time total score calculation (rounded up to nearest tenth)

### 📤 Export & Documentation
- Export detailed grading results to text format
- Includes all criteria scores, percentages, levels, and comments
- Professional formatting suitable for student feedback
- Integration with Maya scene information

## Usage

### Quick Start
1. Open Maya with a student assignment
2. Access via **Prof-Tools Menu → Grading Tools → Assignment Grading Rubric**
3. Select assignment type or use custom rubric
4. Grade each criterion using the percentage dropdowns
5. Export results for documentation

### Creating Custom Rubrics

#### Basic Template Usage
```python
from prof.tools.assignments.lessonRubric_template import LessonRubric

# Create rubric instance
rubric = LessonRubric(assignment_name="My Assignment", total_points=10)

# Add criteria (point values should sum to total_points)
rubric.add_criterion("Technical Execution", 3.0, "Proper modeling techniques")
rubric.add_criterion("Creative Design", 2.5, "Originality and artistic vision")
rubric.add_criterion("File Organization", 1.5, "Proper naming and structure")
rubric.add_criterion("Requirements", 2.0, "Met assignment specifications")
rubric.add_criterion("Quality", 1.0, "Final presentation quality")

# Display the grading interface
rubric.show_rubric_ui()
```

#### Pre-built Assignment Types
The system includes ready-to-use rubrics for common assignment types:

- **Modeling Basics**: For introductory 3D modeling assignments
- **Character Modeling**: Advanced character creation projects  
- **Environment Modeling**: Scene and environment assignments
- **Custom**: Flexible template for any assignment type

### Customization Guidelines

#### Point Distribution
- All assignments standardized to **10 points total**
- Distribute points based on assignment complexity and learning objectives
- Typically: Major criteria (2-3 points), Minor criteria (0.5-1.5 points)

#### Criteria Examples
```python
# Technical criteria
rubric.add_criterion("Mesh Quality", 2.5, "Clean topology, proper edge flow")
rubric.add_criterion("UV Mapping", 1.5, "Efficient UV layout, minimal distortion")

# Creative criteria  
rubric.add_criterion("Design Originality", 2.0, "Creative interpretation of brief")
rubric.add_criterion("Visual Appeal", 1.0, "Aesthetic quality and composition")

# Process criteria
rubric.add_criterion("File Management", 1.0, "Proper naming, organization, cleanup")
rubric.add_criterion("Documentation", 0.5, "Reference usage, process notes")
```

## File Structure

```
prof-tools/prof/tools/assignments/
├── __init__.py                     # Module initialization
├── lessonRubric_template.py        # Main rubric system
├── example_assignment_rubrics.py   # Pre-built assignment rubrics
└── README.md                       # This documentation
```

## Technical Details

### Scoring Algorithm
1. **Percentage Input**: User selects or enters percentage (0-100%)
2. **Level Classification**: Percentage mapped to performance level
3. **Point Calculation**: `score = (percentage / 100) * criterion_point_value`
4. **Total Calculation**: Sum of all criterion scores, rounded up to nearest tenth

### Empty File Detection
The system analyzes the Maya scene for:
- Default cameras and lights
- Primitive objects vs. custom geometry
- Scene complexity indicators
- If ≤5 non-default objects found → flagged as empty

### Performance Levels
| Level | Range | Description | Visual Indicator |
|-------|-------|-------------|------------------|
| No Marks | 0-5% | Not attempted | Red |
| Low Marks | 6-15% | Minimal effort | Orange |
| Partial | 16-45% | Basic completion | Yellow |
| High | 46-75% | Good work | Light Green |
| Full | 76-100% | Excellent | Green |

## Integration

### Menu Integration
The rubric system is integrated into the Prof-Tools menu:
```
Prof-Tools → Grading Tools → Assignment Grading Rubric
```

### Course-Specific Integration
Can be customized for specific courses:
- FDMA 1510: Basic modeling and animation
- FDMA 2530: Advanced modeling and texturing
- Custom course requirements

## Best Practices

### For Instructors
1. **Consistency**: Use standardized criteria across similar assignments
2. **Clarity**: Provide clear descriptions for each criterion
3. **Fairness**: Use percentage ranges consistently
4. **Documentation**: Export results for gradebook integration
5. **Feedback**: Use auto-generated comments as starting points

### For Grading Workflow
1. **Setup**: Create assignment-specific rubrics in advance
2. **Efficiency**: Use keyboard shortcuts and quick selections
3. **Review**: Double-check auto-calculations before finalizing
4. **Export**: Save results before closing Maya
5. **Consistency**: Apply same standards across all students

## Future Enhancements

### Planned Features
- **Batch Grading**: Process multiple files automatically
- **Gradebook Export**: Direct integration with Canvas/Blackboard
- **Custom Comments**: Save and reuse frequent feedback comments
- **Rubric Templates**: Save and share rubric configurations
- **Analytics**: Track common issues across assignments

### Technical Improvements
- **Performance**: Optimize for large scene files
- **UI/UX**: Enhanced interface with better visual feedback
- **Validation**: Improved error handling and input validation
- **Documentation**: Video tutorials and interactive guides

## Support

For questions, issues, or feature requests:
- **Repository**: [NMSU_Scripts](https://github.com/Atsantiago/NMSU_Scripts)
- **Author**: Alexander T. Santiago
- **Contact**: [Portfolio](https://atsantiago.artstation.com/resume)

---

**Version**: 0.2.4  
**Compatible with**: Maya 2018+  
**Python**: 2.7+ / 3.x
