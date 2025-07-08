import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys

class TestUtilsCache(unittest.TestCase):
    def setUp(self):
        patcher_cmds = patch.dict('sys.modules', {'maya.cmds': MagicMock()})
        self.addCleanup(patcher_cmds.stop)
        patcher_cmds.start()
        from fdma_shelf.utils import cache
        self.cache = cache

    def test_get_config_hash_consistency(self):
        h1 = self.cache.get_config_hash('abc')
        h2 = self.cache.get_config_hash('abc')
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 32)

    def test_write_and_read_local_config(self):
        with patch('fdma_shelf.utils.cache._get_cache_path', return_value='test_cache.json'):
            with patch('builtins.open', mock_open()) as m:
                self.assertTrue(self.cache.write_local_config({'a': 1}))
                m.assert_called()
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data='{"a": 1}')):
                    result = self.cache.read_local_config()
                    self.assertIsInstance(result, dict)

    def test_clear_cache(self):
        with patch('fdma_shelf.utils.cache._get_cache_path', return_value='test_cache.json'):
            with patch('os.path.exists', return_value=True):
                with patch('os.remove') as rm:
                    self.assertTrue(self.cache.clear_cache())
                    rm.assert_called()

if __name__ == '__main__':
    unittest.main()
