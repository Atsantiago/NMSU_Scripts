"""
Prof-Tools Test Suite

This directory contains organized unit tests for the Prof-Tools Maya plugin.

Directory Structure:
-------------------
prof/tests/
├── __init__.py              # Test package initialization
├── README.md               # This file - testing documentation
├── test_core/              # Tests for core functionality
│   ├── __init__.py
│   ├── test_version_utils.py    # Version management tests
│   ├── test_updater.py          # Update system tests
│   └── test_dev_prefs.py        # Developer preferences tests
├── test_ui/                # Tests for UI components
│   ├── __init__.py
│   ├── test_update_dialog.py    # Update dialog tests
│   └── test_builder.py          # UI builder tests
└── test_utils/             # Test utilities and helpers
    ├── __init__.py
    ├── maya_test_helpers.py     # Maya testing utilities
    └── mock_data.py             # Mock data for testing

Running Tests:
--------------
From the prof-tools directory, run:

```bash
# Run all tests
python -m pytest prof/tests/

# Run specific test file
python -m pytest prof/tests/test_core/test_version_utils.py

# Run with coverage
python -m pytest prof/tests/ --cov=prof --cov-report=html
```

Testing Guidelines:
------------------
1. All test files should be named with the `test_` prefix
2. Test classes should inherit from `unittest.TestCase` or use pytest fixtures
3. Mock Maya cmds when testing UI components (Maya may not be available)
4. Use the test utilities in `test_utils/` for common testing patterns
5. Include both positive and negative test cases
6. Test error handling and edge cases

Dependencies for Testing:
------------------------
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
