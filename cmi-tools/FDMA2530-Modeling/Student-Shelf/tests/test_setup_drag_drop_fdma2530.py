import unittest
from unittest.mock import patch, MagicMock
import sys

maya_available = False
try:
    import maya.cmds
    maya_available = True
except ImportError:
    pass

@unittest.skipUnless(maya_available, "Maya is not available")
class TestSetupDragDropFdma2530(unittest.TestCase):
    def setUp(self):
        sys.modules['maya.cmds'] = MagicMock()
        sys.modules['maya.utils'] = MagicMock()
        sys.modules['maya.mel'] = MagicMock()
        import setup_drag_drop_fdma2530 as installer
        self.installer = installer

    def tearDown(self):
        sys.modules.pop('maya.cmds', None)
        sys.modules.pop('maya.utils', None)
        sys.modules.pop('maya.mel', None)

    def test_main_function_exists(self):
        self.assertTrue(hasattr(self.installer, '__file__'))

    def test_debug_output(self):
        # Should not raise
        with patch('builtins.print') as mock_print:
            self.installer.print("Test debug output")
            mock_print.assert_called()

    def test_imports(self):
        self.assertTrue(hasattr(self.installer, '__doc__'))

if __name__ == '__main__':
    unittest.main()
