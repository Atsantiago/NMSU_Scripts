import unittest
from unittest.mock import patch, MagicMock
import sys

class TestShelfBuilder(unittest.TestCase):
    def setUp(self):
        patcher_cmds = patch.dict('sys.modules', {'maya.cmds': MagicMock(), 'maya.mel': MagicMock(), 'maya.utils': MagicMock()})
        self.addCleanup(patcher_cmds.stop)
        patcher_cmds.start()
        from fdma_shelf.shelf import builder
        self.builder = builder

    def test_expand_version_tokens_str(self):
        result = self.builder._expand_version_tokens('Tool v{version}')
        self.assertIn(self.builder.PACKAGE_VERSION, result)

    def test_expand_version_tokens_dict(self):
        data = {'label': 'Tool v{version}'}
        result = self.builder._expand_version_tokens(data)
        self.assertIn(self.builder.PACKAGE_VERSION, result['label'])

    def test_expand_version_tokens_list(self):
        data = ['Tool v{version}', 'Other']
        result = self.builder._expand_version_tokens(data)
        self.assertIn(self.builder.PACKAGE_VERSION, result[0])

    def test_hash_text(self):
        h1 = self.builder._hash_text('abc')
        h2 = self.builder._hash_text('abc')
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 32)

    def test_read_json_invalid(self):
        with patch('builtins.open', side_effect=IOError):
            result = self.builder._read_json('fake.json')
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
