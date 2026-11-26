"""Serve the NYT front page at the dimensions expected by the Visionect display."""

from datetime import date, timedelta
import logging
import os
from pathlib import Path
import tempfile
import time

from bottle import Bottle, HTTPResponse, run, static_file
from pdf2image import convert_from_bytes
import requests

app = Bottle()
LOGGER = logging.getLogger(__name__)
IMAGE_PATH = Path(os.environ.get("IMAGE_PATH", str(Path(__file__).with_name("nyt_fp.png"))))


def refresh_image(today=None):
    """Try today, yesterday, then the day before; replace the PNG only on success."""
    today = today or date.today()
    for days_ago in range(3):
        edition = today - timedelta(days=days_ago)
        url = f"https://static01.nyt.com/images/{edition:%Y/%m/%d}/nytfrontpage/scan.pdf"
        with requests.get(url, timeout=(10, 30)) as response:
            if response.status_code == 404:
                continue
            response.raise_for_status()
            images = convert_from_bytes(
                response.content, dpi=600, fmt="png", grayscale=True,
                size=(1480, None), use_cropbox=True, hide_annotations=True,
                first_page=1, last_page=1, timeout=60,
            )
        IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=IMAGE_PATH.parent, suffix=".png", delete=False) as output:
                temporary = Path(output.name)
            images[0].save(temporary, "png")
            temporary.replace(IMAGE_PATH)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            for image in images:
                image.close()
        return
    raise RuntimeError("No NYT front page found for the last three days")


@app.get('/healthz')
def health():
    return {"status": "ok"}


@app.get('/image/<filename>')
def server_static(filename):
    if filename != "nyt_fp.png":
        return HTTPResponse(status=404, body="Not found")
    return static_file(IMAGE_PATH.name, root=str(IMAGE_PATH.parent))


@app.get('/')
def main():
    try:
        refresh_image()
    except Exception:
        LOGGER.exception("Unable to refresh NYT front page")
        if not IMAGE_PATH.is_file():
            return HTTPResponse(status=502, body="<body>Error fetching NYT front page</body>")
        # Keep the display usable during an upstream outage.
    return (
        '<body style="margin-left: -23px; margin-top: -35px;">'
        f'<img src="image/nyt_fp.png?{time.time()}" />'
        '</body>'
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(app=app, host='0.0.0.0', port=8001)
