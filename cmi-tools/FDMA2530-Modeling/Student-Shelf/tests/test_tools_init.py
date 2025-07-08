import unittest
from unittest.mock import patch, MagicMock
import sys

class TestToolsInit(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict('sys.modules', {'maya.cmds': MagicMock(), 'maya.mel': MagicMock(), 'maya.utils': MagicMock()})
        self.addCleanup(patcher.stop)
        patcher.start()
        import fdma_shelf.tools as tools_init
        self.tools_init = tools_init

    def test_module_import(self):
        self.assertTrue(hasattr(self.tools_init, '__file__') or hasattr(self.tools_init, '__path__'))

    def test_docstring(self):
        self.assertIsInstance(self.tools_init.__doc__, str)

    def test_dir(self):
        self.assertIsInstance(dir(self.tools_init), list)

if __name__ == '__main__':
    unittest.main()
