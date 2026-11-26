from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from wsgiref.util import setup_testing_defaults

from PIL import Image
import requests

import nyt_server as server


def response(status=200, content=b"pdf"):
    result = Mock(status_code=status, content=content)
    result.__enter__ = Mock(return_value=result)
    result.__exit__ = Mock(return_value=False)
    return result


def get(path):
    environ = {}
    setup_testing_defaults(environ)
    environ['PATH_INFO'] = path
    captured = {}
    def start(status, headers, exc_info=None):
        captured['status'] = status
    body = server.app(environ, start)
    try:
        return captured, b''.join(body)
    finally:
        if hasattr(body, 'close'):
            body.close()


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'nyt_fp.png'
        self.patch = patch.object(server, 'IMAGE_PATH', self.path)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    @patch.object(server, 'convert_from_bytes')
    @patch.object(server.requests, 'get')
    def test_missing_editions_fall_back_across_month_boundary(self, download, convert):
        download.side_effect = [response(404), response(404), response()]
        convert.return_value = [Image.new('RGB', (1480, 2000))]
        server.refresh_image(date(2026, 3, 1))
        self.assertEqual([call.args[0].split('/images/')[1] for call in download.call_args_list], [
            '2026/03/01/nytfrontpage/scan.pdf', '2026/02/28/nytfrontpage/scan.pdf',
            '2026/02/27/nytfrontpage/scan.pdf',
        ])
        self.assertEqual(convert.call_args.kwargs['size'], (1480, None))
        self.assertTrue(convert.call_args.kwargs['use_cropbox'])
        self.assertTrue(convert.call_args.kwargs['hide_annotations'])
        with Image.open(self.path) as image:
            self.assertEqual(image.size, (1480, 2000))

    @patch.object(server.requests, 'get')
    def test_three_missing_editions_fail_cleanly(self, download):
        download.side_effect = [response(404), response(404), response(404)]
        with self.assertRaises(RuntimeError):
            server.refresh_image(date(2026, 1, 1))
        self.assertEqual(download.call_count, 3)
        self.assertFalse(self.path.exists())

    @patch.object(server, 'convert_from_bytes', side_effect=ValueError('invalid PDF'))
    @patch.object(server.requests, 'get', return_value=response())
    def test_conversion_failure_preserves_existing_image(self, download, convert):
        self.path.write_bytes(b'last good image')
        with self.assertRaises(ValueError):
            server.refresh_image()
        self.assertEqual(self.path.read_bytes(), b'last good image')

    @patch.object(server, 'convert_from_bytes')
    @patch.object(server.requests, 'get')
    def test_http_errors_are_not_passed_to_pdf_converter(self, download, convert):
        failed = response(503)
        failed.raise_for_status.side_effect = requests.HTTPError('503')
        download.return_value = failed
        with self.assertRaises(requests.HTTPError):
            server.refresh_image()
        convert.assert_not_called()

    @patch.object(server, 'refresh_image', side_effect=requests.Timeout())
    def test_outage_serves_cached_image_and_preserves_display_offsets(self, refresh):
        self.path.write_bytes(b'cached')
        with self.assertLogs(server.LOGGER, level='ERROR'):
            captured, body = get('/')
        self.assertEqual(captured['status'], '200 OK')
        self.assertIn(b'margin-left: -23px; margin-top: -35px;', body)
        self.assertIn(b'image/nyt_fp.png?', body)

    @patch.object(server, 'refresh_image', side_effect=requests.Timeout())
    def test_outage_without_cached_image_returns_502(self, refresh):
        with self.assertLogs(server.LOGGER, level='ERROR'):
            captured, body = get('/')
        self.assertEqual(captured['status'], '502 Bad Gateway')

    @patch.object(server.requests, 'get')
    def test_health_does_not_fetch_or_render_newspaper(self, download):
        captured, body = get('/healthz')
        self.assertEqual(captured['status'], '200 OK')
        self.assertIn(b'"ok"', body)
        download.assert_not_called()

    def test_image_route_only_serves_expected_png(self):
        self.path.write_bytes(b'cached png')
        captured, body = get('/image/nyt_fp.png')
        self.assertEqual(captured['status'], '200 OK')
        self.assertEqual(body, b'cached png')
        captured, body = get('/image/anything-else')
        self.assertTrue(captured['status'].startswith('404'))


if __name__ == '__main__':
    unittest.main()
