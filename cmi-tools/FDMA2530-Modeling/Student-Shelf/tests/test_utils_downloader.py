import unittest
from unittest.mock import patch, MagicMock
from fdma_shelf.utils import downloader

class TestUtilsDownloader(unittest.TestCase):
    def test_download_raw_success(self):
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'data'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            result = downloader.download_raw('http://test', timeout=1)
            self.assertIn(result, [b'data', 'data'])

    def test_download_raw_failure(self):
        with patch('urllib.request.urlopen', side_effect=Exception):
            result = downloader.download_raw('http://fail', timeout=1)
            self.assertIsNone(result)

    def test_download_raw_timeout(self):
        with patch('urllib.request.urlopen', side_effect=TimeoutError):
            result = downloader.download_raw('http://timeout', timeout=0.01)
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
