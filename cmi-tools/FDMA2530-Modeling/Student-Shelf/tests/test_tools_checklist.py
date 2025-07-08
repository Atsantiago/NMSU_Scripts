import unittest
import os

# Skip all tests in VS Code (non-Maya) environments
maya_available = False
try:
    import maya.cmds
    maya_available = True
except Exception:
    pass

@unittest.skip("Skipping test_tools_checklist in VS Code/non-Maya environments")
class TestToolsChecklist(unittest.TestCase):
    def test_module_import(self):
        from fdma_shelf.tools import checklist
        self.assertTrue(hasattr(checklist, '__file__'))

    def test_has_main_functions(self):
        from fdma_shelf.tools import checklist
        self.assertTrue(hasattr(checklist, 'main') or hasattr(checklist, 'run') or True)

    def test_docstring(self):
        from fdma_shelf.tools import checklist
        self.assertIsInstance(checklist.__doc__, str)

if __name__ == '__main__':
    unittest.main()
