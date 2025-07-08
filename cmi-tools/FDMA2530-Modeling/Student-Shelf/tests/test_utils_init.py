import unittest
from unittest.mock import patch, MagicMock
import sys

class TestUtilsInit(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict('sys.modules', {'maya.cmds': MagicMock(), 'maya.mel': MagicMock(), 'maya.utils': MagicMock()})
        self.addCleanup(patcher.stop)
        patcher.start()
        import fdma_shelf.utils as utils_init
        self.utils_init = utils_init

    def test_module_import(self):
        self.assertTrue(hasattr(self.utils_init, '__file__') or hasattr(self.utils_init, '__path__'))

    def test_docstring(self):
        self.assertIsInstance(self.utils_init.__doc__, str)

    def test_dir(self):
        self.assertIsInstance(dir(self.utils_init), list)

if __name__ == '__main__':
    unittest.main()
