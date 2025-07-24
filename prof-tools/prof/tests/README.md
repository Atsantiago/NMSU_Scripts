# Prof-Tools Test Suite

Comprehensive automated testing framework for the Prof-Tools Maya plugin, ensuring code quality, reliability, and compatibility across Maya versions.

## 🎯 Overview

This test suite provides thorough coverage of prof-tools functionality with a focus on educational tool reliability. Tests are designed to run both within Maya and in standalone Python environments for CI/CD integration.

## 📁 Directory Structure

```
prof/tests/
├── __init__.py                    # Test package initialization
├── README.md                     # This documentation
├── test_core/                    # Core functionality tests
│   ├── __init__.py
│   ├── test_version_utils.py     # Version management and comparison
│   ├── test_updater.py           # Update system and error handling
│   ├── test_setup.py             # Installation and configuration
│   └── test_dev_prefs.py         # Developer preferences and settings
├── test_ui/                      # User interface tests
│   ├── __init__.py
│   ├── test_update_dialog.py     # Update dialog functionality
│   ├── test_builder.py           # Menu system and UI components
│   └── test_assignment_dialog.py # Assignment selection interfaces
├── test_tools/                   # Grading system tests
│   ├── __init__.py
│   ├── test_auto_grader/         # Auto-grader system tests
│   │   ├── test_rubric_template.py    # Core rubric functionality
│   │   ├── test_assignments.py       # Assignment-specific rubrics
│   │   └── test_scoring_system.py    # Scoring logic and calculations
│   └── test_core_tools/          # Future: workflow utility tests
└── test_utils/                   # Testing utilities and helpers
    ├── __init__.py
    ├── maya_test_helpers.py       # Maya environment simulation
    ├── mock_data.py               # Sample data and fixtures
    └── test_fixtures.py           # Reusable test components
```

## 🚀 Running Tests

### **Quick Test Commands**
```bash
# Run all tests
python -m pytest prof/tests/

# Run specific test categories
python -m pytest prof/tests/test_core/          # Core functionality
python -m pytest prof/tests/test_ui/            # User interface
python -m pytest prof/tests/test_tools/         # Grading tools

# Run specific test file
python -m pytest prof/tests/test_core/test_version_utils.py

# Run with detailed output
python -m pytest prof/tests/ -v --tb=short

# Run with coverage reporting
python -m pytest prof/tests/ --cov=prof --cov-report=html
```

### **Maya Environment Testing**
```python
# From within Maya's script editor
import sys
sys.path.append('path/to/prof-tools')

# Run tests within Maya
exec(open('prof/tests/run_maya_tests.py').read())
```

## 📋 Testing Guidelines

### **Test Organization**
- **Naming Convention**: All test files prefixed with `test_`
- **Class Structure**: Inherit from `unittest.TestCase` or use pytest fixtures
- **Method Naming**: `test_` prefix with descriptive names
- **Documentation**: Clear docstrings explaining test purpose

### **Maya Integration Testing**
```python
import unittest
from prof.tests.test_utils.maya_test_helpers import MockMayaEnvironment

class TestRubricSystem(unittest.TestCase):
    def setUp(self):
        self.maya_mock = MockMayaEnvironment()
        self.maya_mock.setup()
    
    def test_rubric_creation(self):
        # Test rubric functionality with mocked Maya
        pass
    
    def tearDown(self):
        self.maya_mock.cleanup()
```

### **Error Handling Tests**
- **Edge Cases**: Test boundary conditions and unusual inputs
- **Error Recovery**: Verify graceful failure and recovery mechanisms  
- **User Experience**: Ensure errors provide helpful feedback
- **Compatibility**: Test across different Maya versions when possible

### **Performance Testing**
```python
def test_large_scene_performance(self):
    """Test grading performance with complex Maya scenes."""
    # Load test scene with 10,000+ objects
    # Time rubric operations
    # Assert performance within acceptable bounds
```

## 🔧 Test Utilities

### **Maya Test Helpers** (`maya_test_helpers.py`)
```python
# Mock Maya environment for standalone testing
class MockMayaEnvironment:
    def setup(self): # Simulate Maya cmds
    def create_test_scene(self): # Generate test geometry
    def cleanup(self): # Clean up test data

# Decorators for Maya-specific tests  
@requires_maya
def test_maya_functionality():
    pass

@mock_maya_environment
def test_without_maya():
    pass
```

### **Mock Data** (`mock_data.py`)
```python
# Sample rubric data
SAMPLE_RUBRICS = {
    'modeling_basic': {
        'criteria': [...],
        'point_values': [...],
        'descriptions': [...]
    }
}

# Test scene configurations
TEST_SCENES = {
    'empty_scene': {...},
    'complex_scene': {...},
    'invalid_scene': {...}
}
```

### **Test Fixtures** (`test_fixtures.py`)
```python
# Reusable test components
class RubricTestCase(unittest.TestCase):
    def setUp(self):
        # Standard rubric setup for tests
        pass

@pytest.fixture
def sample_assignment():
    # Return configured test assignment
    pass
```

## 📊 Coverage Goals

### **Target Coverage Levels**
- **Core Systems**: 95%+ coverage (version management, installation)
- **UI Components**: 85%+ coverage (menu systems, dialogs)
- **Grading Tools**: 90%+ coverage (rubrics, scoring, export)
- **Utilities**: 85%+ coverage (helpers, data processing)

### **Critical Path Testing**
- ✅ Installation and setup processes
- ✅ Menu system integration and navigation
- ✅ Rubric creation and scoring logic
- ✅ Export and reporting functionality
- ✅ Error handling and recovery
- ✅ Version compatibility checks

## 🔍 Continuous Integration

### **Automated Testing Pipeline**
```yaml
# Example GitHub Actions workflow
name: Prof-Tools Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: [ubuntu-latest, windows-latest, macos-latest]
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, 3.10]
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run tests
        run: pytest prof/tests/ --cov=prof
```

### **Quality Gates**
- **All tests must pass** before merge to master
- **Coverage cannot decrease** below current levels
- **Performance tests** must meet response time requirements
- **Code style** must pass linting checks

## 🛠️ Development Workflow

### **Test-Driven Development**
1. **Write Test**: Create failing test for new functionality
2. **Implement**: Write minimal code to pass the test
3. **Refactor**: Improve code while maintaining test coverage
4. **Validate**: Run full test suite to ensure no regressions

### **Adding New Tests**
```python
# 1. Choose appropriate test directory
# 2. Create test file with descriptive name
# 3. Import necessary modules and test utilities
# 4. Write test class with setup/teardown
# 5. Implement test methods with assertions
# 6. Add to CI pipeline if needed

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_feature_basic_functionality(self):
        """Test basic feature operation."""
        pass
    
    def test_feature_error_handling(self):
        """Test feature error conditions."""
        pass
```

## 📚 Dependencies for Testing

```
# Testing Framework
pytest>=6.0.0
pytest-cov>=2.0.0
pytest-mock>=3.0.0

# Mocking and Test Utilities  
mock>=4.0.0
unittest-xml-reporting>=3.0.0

# Performance Testing
pytest-benchmark>=3.0.0

# Maya Testing (when available)
maya-python>=2020.0.0
```

## 🙏 Best Practices

- **Isolated Tests**: Each test should be independent and repeatable
- **Clear Assertions**: Use descriptive assertion messages
- **Mock External Dependencies**: Avoid relying on external services
- **Test Documentation**: Explain complex test scenarios
- **Regular Maintenance**: Keep tests updated with code changes

## 👨‍💻 Author

**Alexander T. Santiago**  
Creative Media Institute, New Mexico State University  
GitHub: [@Atsantiago](https://github.com/Atsantiago)

---

> *Comprehensive testing ensures that educational tools work reliably for instructors and students, maintaining the quality that educators deserve.*
- pytest: Main testing framework
- pytest-cov: Coverage reporting
- mock: For mocking Maya and external dependencies
- unittest.mock: Built-in mocking (Python 3.3+)

Example Test File:
-----------------
```python
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add prof-tools to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from prof.core.version_utils import get_prof_tools_version

class TestVersionUtils(unittest.TestCase):
    
    def test_get_version_returns_string(self):
        \"\"\"Test that get_prof_tools_version returns a string.\"\"\"
        version = get_prof_tools_version()
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)
    
    @patch('prof.core.version_utils.get_manifest_data')
    def test_get_version_with_mock_manifest(self, mock_manifest):
        \"\"\"Test version retrieval with mocked manifest data.\"\"\"
        mock_manifest.return_value = {'current_version': '1.0.0'}
        version = get_prof_tools_version()
        self.assertEqual(version, '1.0.0')

if __name__ == '__main__':
    unittest.main()
```

Notes:
------
- Tests should not depend on Maya being installed for core functionality
- UI tests should mock Maya cmds appropriately
- Keep test data and fixtures in the test_utils directory
- Ensure tests are isolated and don't depend on each other
"""
