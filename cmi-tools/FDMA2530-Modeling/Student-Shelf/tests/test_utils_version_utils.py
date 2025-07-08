import unittest
from fdma_shelf.utils import version_utils

class TestVersionUtils(unittest.TestCase):
    def test_is_valid_semantic_version(self):
        self.assertTrue(version_utils.is_valid_semantic_version("1.2.3"))
        self.assertFalse(version_utils.is_valid_semantic_version("1.2"))
        self.assertFalse(version_utils.is_valid_semantic_version("foo"))

    def test_parse_semantic_version(self):
        v = version_utils.parse_semantic_version("1.2.3-alpha+build")
        self.assertEqual(v['major'], 1)
        self.assertEqual(v['minor'], 2)
        self.assertEqual(v['patch'], 3)
        self.assertEqual(v['prerelease'], 'alpha')
        self.assertEqual(v['build'], 'build')

    def test_compare_versions(self):
        self.assertEqual(version_utils.compare_versions("1.2.3", "1.2.3"), 0)
        self.assertEqual(version_utils.compare_versions("1.2.4", "1.2.3"), 1)
        self.assertEqual(version_utils.compare_versions("1.2.2", "1.2.3"), -1)

if __name__ == '__main__':
    unittest.main()
