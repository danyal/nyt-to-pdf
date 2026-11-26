"""Run inside the image; generates its own PDF and needs no network."""
import io
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch

from PIL import Image
import nyt_server as server

pdf = io.BytesIO()
with Image.new('RGB', (148, 266), 'white') as original:
    original.save(pdf, 'PDF', resolution=72.0)
response = Mock(status_code=200, content=pdf.getvalue())
response.__enter__ = Mock(return_value=response)
response.__exit__ = Mock(return_value=False)
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'nyt_fp.png'
    with patch.object(server, 'IMAGE_PATH', path), patch.object(server.requests, 'get', return_value=response):
        server.refresh_image()
    with Image.open(path) as rendered:
        assert rendered.format == 'PNG', rendered.format
        assert rendered.size == (1480, 2660), rendered.size
        print('Real Poppler render passed:', rendered.size, rendered.mode)
