# Assignment Grading Rubric System

A comprehensive grading rubric system for Maya assignments that provides standardized, efficient, and fair grading with auto-generated feedback.

## 📁 Directory Structure

- `lessonRubric_template.py` - Core rubric framework and template
- `example_assignment_rubrics.py` - Example rubric implementations  
- `fdma1510/` - FDMA 1510 course assignment rubrics
- `fdma2530/` - FDMA 2530 course assignment rubrics

**Note:** All test files should be placed in `prof-tools/prof/tests/` directory, not in the assignments folder.

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
from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric

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
prof/tools/auto_grader/assignments/
├── __init__.py                      # Package initialization
├── README.md                       # This documentation
├── lessonRubric_template.py        # 🎯 Core rubric framework
├── example_assignment_rubrics.py   # Dialog system and example rubrics
├── fdma1510/                       # FDMA 1510 course assignments
│   ├── __init__.py
│   └── (assignments coming soon)
└── fdma2530/                       # FDMA 2530 course assignments
    ├── __init__.py
    └── u01_ss01_primitives.py      # U01_SS01 Primitives assignment
```

## Development Guide

### Creating New Course Assignments

#### 1. Create Course Directory
```bash
# Create new course folder
mkdir prof/tools/auto_grader/assignments/fdma1510
touch prof/tools/auto_grader/assignments/fdma1510/__init__.py
```

#### 2. Create Assignment Rubric
```python
# prof/tools/auto_grader/assignments/fdma1510/u01_animation_basics.py
from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric

def create_u01_animation_rubric():
    rubric = LessonRubric("FDMA 1510 - U01: Animation Basics", total_points=10)
    
    # Add criteria (must total 10 points)
    rubric.add_criterion("Keyframe Timing", 2.5, "Proper spacing and timing")
    rubric.add_criterion("Animation Principles", 2.5, "Squash/stretch, anticipation")
    rubric.add_criterion("Technical Execution", 2.0, "Clean curves, proper setup")
    rubric.add_criterion("File Organization", 1.5, "Naming, scene structure")
    rubric.add_criterion("Creative Interpretation", 1.5, "Artistic choices")
    
    rubric.show_rubric_ui()
    return rubric
```

#### 3. Update Menu System
Add the new assignment to `prof/ui/builder.py`:
```python
# Add menu item in appropriate course section
def _build_grading_section(self, parent):
    # ... existing code ...
    
    # FDMA 1510 submenu
    fdma1510_menu = cmds.menuItem(
        label="FDMA 1510",
        subMenu=True,
        parent=grading_menu
    )
    
    cmds.menuItem(
        label="U01_Animation_Basics",
        command=lambda *args: self._open_u01_animation_rubric(),
        parent=fdma1510_menu
    )

def _open_u01_animation_rubric(self):
    """Open the FDMA 1510 U01 Animation Basics rubric."""
    try:
        from prof.tools.auto_grader.assignments.fdma1510.u01_animation_basics import create_u01_animation_rubric
        create_u01_animation_rubric()
    except Exception as e:
        logger.error(f"Failed to open U01 Animation rubric: {e}")
```

#### 4. Update Assignment Dialog
Add to the dialog in `example_assignment_rubrics.py`:
```python
# Add button to FDMA 1510 section
cmds.button(
    label="U01_Animation_Basics",
    command=lambda *args: _select_and_close_assignment("u01_animation", window_name),
    height=30,
    parent=fdma1510_layout
)

# Add routing logic
def _select_and_close_assignment(assignment_type, window_name):
    cmds.deleteUI(window_name, window=True)
    
    if assignment_type == "u01_animation":
        from prof.tools.auto_grader.assignments.fdma1510.u01_animation_basics import create_u01_animation_rubric
        return create_u01_animation_rubric()
    # ... existing routing ...
```

### Best Practices

#### For Rubric Design
1. **Point Distribution**: Always total exactly 10 points
2. **Criterion Balance**: 
   - Technical skills: 40-60% of points
   - Creative/artistic: 20-30% of points  
   - Organization/process: 15-25% of points
3. **Clear Descriptions**: Specific, measurable criteria
4. **Course Alignment**: Match learning objectives

#### For Code Organization
1. **Naming Convention**: `course_assignment_type.py` (e.g., `u01_primitives.py`)
2. **Function Names**: `create_[assignment]_rubric()` format
3. **Documentation**: Include assignment overview and point breakdown
4. **Error Handling**: Graceful fallbacks for import/execution errors

#### For User Experience
1. **Consistency**: Use standardized criteria across similar assignments
2. **Clarity**: Provide clear descriptions for each criterion
3. **Fairness**: Use percentage ranges consistently
4. **Documentation**: Export results for gradebook integration
5. **Feedback**: Use auto-generated comments as starting points

### For Grading Workflow
1. **Setup**: Create assignment-specific rubrics in advance
2. **Efficiency**: Use interactive performance indicators for quick scoring
3. **Review**: Double-check auto-calculations before finalizing
4. **Export**: Save results before closing Maya
5. **Consistency**: Apply same standards across all students

## Future Enhancements

### Planned Features
- **Batch Grading**: Process multiple files automatically
- **LMS Integration**: Direct export to Canvas/Blackboard gradebooks
- **Custom Comments**: Save and reuse frequent feedback templates
- **Rubric Analytics**: Track grade distributions and common issues
- **Scene Validation**: Automated technical requirement checking

### Technical Improvements
- **Performance**: Optimize for large scene files and complex geometry
- **UI/UX**: Enhanced interface with better visual feedback and accessibility
- **Validation**: Improved error handling and input validation
- **Documentation**: Interactive tutorials and video guides

## Version History

**v0.3.5** (Current)
- ✅ Interactive performance indicators with click-to-score
- ✅ Course-organized assignment structure
- ✅ Enhanced rubric UI with real-time updates
- ✅ Multi-Maya version compatibility

**v0.3.0-0.3.4**
- ✅ Core rubric system with 5-tier scoring
- ✅ Assignment dialog organization
- ✅ Export capabilities and auto-comments
- ✅ Maya integration and menu system

## Support & Contributing

### Getting Help
- **Documentation**: [Prof-Tools Wiki](https://github.com/Atsantiago/NMSU_Scripts/wiki)
- **Issues**: [GitHub Issues](https://github.com/Atsantiago/NMSU_Scripts/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Atsantiago/NMSU_Scripts/discussions)

### Contributing
1. **Fork** the repository
2. **Create** a feature branch
3. **Add** your assignment rubrics or improvements
4. **Test** thoroughly with actual Maya scenes
5. **Submit** a pull request with clear description

### Development Environment
```bash
# Clone repository
git clone https://github.com/Atsantiago/NMSU_Scripts.git
cd NMSU_Scripts/prof-tools

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest prof/tests/
```

## 👨‍💻 Author

**Alexander T. Santiago**  
Creative Media Institute, New Mexico State University  
GitHub: [@Atsantiago](https://github.com/Atsantiago)  
Portfolio: [ArtStation](https://atsantiago.artstation.com/)

---

**Version**: 0.3.5  
**Compatible with**: Maya 2020+ (Python 3.x)  
**License**: MIT

> *Built by educators, for educators - streamlining the grading process while maintaining academic rigor and providing meaningful feedback to students.*

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
