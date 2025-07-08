import unittest
from unittest.mock import patch, Mock
from fdma_shelf.utils import updater

class TestUpdater(unittest.TestCase):
    @patch('fdma_shelf.utils.updater.urllib.request.urlopen')
    def test_get_releases_manifest(self, mock_urlopen):
        mock_response = Mock()
        mock_response.read.return_value = b'{"current_version": "1.2.3", "releases": [{"version": "1.2.3", "download_url": "url"}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        result = updater._get_releases_manifest()
        self.assertEqual(result['current_version'], '1.2.3')
        self.assertEqual(result['releases'][0]['version'], '1.2.3')

    def test_is_newer(self):
        self.assertTrue(updater._is_newer('1.2.4', '1.2.3'))
        self.assertFalse(updater._is_newer('1.2.3', '1.2.4'))
        self.assertFalse(updater._is_newer('1.2.3', '1.2.3'))

    @patch('fdma_shelf.utils.updater.cmds')
    def test_update_button_color_no_cmds(self, mock_cmds):
        mock_cmds.shelfLayout.return_value = False
        self.assertFalse(updater._update_button_color('up_to_date'))

if __name__ == '__main__':
    unittest.main()
