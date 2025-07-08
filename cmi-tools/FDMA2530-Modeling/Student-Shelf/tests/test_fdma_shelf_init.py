import unittest
from unittest.mock import patch, MagicMock
import sys

class TestFdmaShelfInit(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict('sys.modules', {'maya.cmds': MagicMock(), 'maya.mel': MagicMock(), 'maya.utils': MagicMock()})
        self.addCleanup(patcher.stop)
        patcher.start()
        import fdma_shelf
        self.fdma_shelf = fdma_shelf

    def test_module_import(self):
        self.assertTrue(hasattr(self.fdma_shelf, '__file__') or hasattr(self.fdma_shelf, '__path__'))

    def test_docstring(self):
        self.assertIsInstance(self.fdma_shelf.__doc__, str)

    def test_dir(self):
        self.assertIsInstance(dir(self.fdma_shelf), list)

if __name__ == '__main__':
    unittest.main()
