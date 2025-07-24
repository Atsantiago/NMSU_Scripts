# Prof Package - Core Python Package

The main Python package containing all prof-tools functionality for Maya instructor grading tools. This package provides a comprehensive, modular architecture for educational tool development.

## 📁 Module Overview

### **`core/`** - Foundation Systems
- **Installation & Setup**: Drag-and-drop installer, userSetup.mel management
- **Version Management**: Semantic versioning, update system, release tracking
- **System Utilities**: Maya integration, platform detection, error handling
- **Developer Tools**: Preferences management, debugging utilities

### **`ui/`** - User Interface Components
- **Menu Builder**: Maya menu system integration and management
- **Dialog Systems**: Update dialogs, assignment selection interfaces
- **Interface Components**: Reusable UI elements and layouts
- **Event Handling**: User interaction management and callbacks

### **`tools/`** - Core Functionality Hub
- **`auto-grader/`**: Complete assignment grading ecosystem
  - **`assignments/`**: Course-specific rubrics and grading logic
    - **`fdma1510/`**: Introduction to 3D Animation assignments
    - **`fdma2530/`**: Introduction to 3D Modeling assignments
    - **`lessonRubric_template.py`**: Base rubric framework
    - **`example_assignment_rubrics.py`**: Dialog system and routing
- **`core-tools/`**: Essential Maya workflow utilities *(future)*
- **`dev-tools/`**: Development and maintenance utilities *(future)*
- **`configs/`**: Configuration files and settings

### **`utils/`** - Shared Utilities
- **Helper Functions**: Common operations used across modules
- **Data Processing**: File handling, text processing, validation
- **Maya Utilities**: Scene analysis, object manipulation, UI helpers
- **System Integration**: Cross-platform compatibility functions

### **`tests/`** - Quality Assurance
- **Unit Tests**: Automated testing for all major components
- **Integration Tests**: End-to-end functionality validation
- **Mock Data**: Test fixtures and sample data
- **Test Utilities**: Testing helpers and Maya environment simulation

## 🏗️ Architecture Principles

### **Modular Design**
Each module has a single, well-defined purpose with minimal dependencies, enabling easy maintenance and testing.

### **Configuration-Driven**
Rubric data and system settings are separated from core logic, allowing customization without code changes.

### **Maya Integration**
Built specifically for Maya's Python environment while maintaining compatibility across Maya versions.

### **Educational Focus**
Designed with instructors and students in mind, prioritizing usability and educational workflow enhancement.

## 🔧 Usage Patterns

### **Standard Import Structure**
```python
# UI components
from prof.ui.builder import create_menu_system

# Grading tools
from prof.tools.auto_grader.assignments.lessonRubric_template import LessonRubric

# Core utilities
from prof.core.version_utils import get_current_version
from prof.utils.maya_helpers import get_scene_info
```

### **Extension Points**
```python
# Adding new assignments
def create_custom_rubric():
    rubric = LessonRubric("Custom Assignment", total_points=10)
    rubric.add_criterion("Criterion Name", 2.0, "Description")
    return rubric

# Adding new tools
class CustomTool:
    def __init__(self):
        # Integration with existing prof-tools framework
        pass
```

## 🛡️ Development Guidelines

### **Code Standards**
- **Python 3.x** compatibility (Maya 2020+)
- **PEP 8** style guidelines for consistency
- **Type hints** where appropriate for clarity
- **Comprehensive docstrings** for all public interfaces

### **Maya Integration**
- **Non-destructive** operations on student work
- **Graceful fallbacks** when Maya is unavailable
- **Version compatibility** across Maya 2020+
- **UI consistency** with Maya's interface standards

### **Testing Requirements**
- **Unit tests** for all core functionality
- **Mock Maya** environment for CI/CD compatibility
- **Error handling** validation
- **Performance testing** for large scenes

### **Documentation Standards**
- **Inline documentation** for complex algorithms
- **Usage examples** for public APIs
- **Architecture decisions** recorded in code comments
- **README files** for each major module

## 🔄 Integration with Maya

### **Menu System**
The package integrates seamlessly with Maya's menu bar, providing familiar access patterns for instructors.

### **Python Environment**
Designed to work within Maya's Python 3.x environment with proper import handling and error recovery.

### **Scene Interaction**
All tools are designed to analyze and grade student work without modifying the original files.

## 📈 Development Status

**Current State**: Production-ready core with active development  
**Test Coverage**: Core functionality covered  
**Documentation**: Comprehensive inline and external docs  
**Stability**: Stable API with semantic versioning

### **Completed Systems**
- ✅ Complete rubric framework with interactive UI
- ✅ Multi-Maya version installation system
- ✅ Course-organized assignment structure
- ✅ Professional export and reporting system

### **In Development**
- 🔄 Additional course assignments
- 🔄 Batch grading capabilities
- 🔄 Advanced scene analysis tools
- 🔄 LMS integration systems

## 👨‍💻 Author

**Alexander T. Santiago**  
Creative Media Institute, New Mexico State University  
GitHub: [@Atsantiago](https://github.com/Atsantiago)

---

> *A thoughtfully architected system designed to grow with educational needs while maintaining code quality and user experience.*