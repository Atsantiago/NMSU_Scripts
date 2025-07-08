import unittest
from fdma_shelf.utils import system_utils

class TestSystemUtils(unittest.TestCase):
    def test_platform_detection(self):
        # Should return one of the known platforms
        self.assertIn(system_utils.get_os_name(), ['windows', 'macos', 'linux', 'unknown'])

    def test_is_windows_linux_macos(self):
        # Only one should be True
        results = [system_utils.is_windows(), system_utils.is_linux(), system_utils.is_macos()]
        self.assertEqual(sum(results), 1)

    def test_get_platform_info(self):
        info = system_utils.get_platform_info()
        self.assertIsInstance(info, dict)
        self.assertIn('os_name', info)

if __name__ == '__main__':
    unittest.main()
