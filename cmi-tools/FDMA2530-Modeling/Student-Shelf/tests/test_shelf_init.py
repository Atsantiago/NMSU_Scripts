import unittest
from unittest.mock import patch, MagicMock
import sys

class TestShelfInit(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict('sys.modules', {'maya.cmds': MagicMock(), 'maya.mel': MagicMock(), 'maya.utils': MagicMock()})
        self.addCleanup(patcher.stop)
        patcher.start()
        import fdma_shelf.shelf as shelf_init
        self.shelf_init = shelf_init

    def test_module_import(self):
        self.assertTrue(hasattr(self.shelf_init, '__file__') or hasattr(self.shelf_init, '__path__'))

    def test_docstring(self):
        self.assertIsInstance(self.shelf_init.__doc__, str)

    def test_dir(self):
        self.assertIsInstance(dir(self.shelf_init), list)

if __name__ == '__main__':
    unittest.main()
