# nyt-to-pdf

A small service for a Visionect e-paper display. It downloads the New York Times
front-page **PDF**, converts its first page to **PNG**, and serves an HTML wrapper.
The repository name describes the source document; the display consumes PNG/HTML.

## Endpoints and display settings

- `GET /`: refresh the front page and return the display HTML.
- `GET /image/nyt_fp.png`: return the last successfully rendered image.
- `GET /healthz`: process health, without downloading or rendering a newspaper.

The renderer tries today, yesterday, and the day before when an edition returns
404. Other download/render failures are logged. An existing image is served on
failure; without one, `/` returns HTTP 502. Health alone does not prove freshness.
Downloads use connect/read timeouts; rendering has a 60-second timeout.

Rendering preserves the recovered deployment's settings: 1480-pixel width,
600 DPI, grayscale conversion, PDF crop box, hidden annotations, and HTML offsets
of `margin-left: -23px; margin-top: -35px;`. Height follows the PDF aspect ratio.
The November 25, 2026 baseline was 1480 × 2665 pixels.

## Run

```sh
docker compose up -d
# Or build the current local source:
docker compose up -d --build
```

Open `http://localhost:10070/`. The container listens on port 8001 and runs as UID
1000. Compose stores the rendered PNG in the `nyt-cache` volume at `/data`.
`TZ` defaults to `America/Los_Angeles`; `IMAGE_PATH` defaults to `/data/nyt_fp.png`
inside Docker. No NYT or Visionect credentials are required.

The historical compose file in this folder described the separate proprietary
Visionect Software Suite, Postgres, and Redis. It was not the deployment for this
app. The replacement compose file runs only this custom renderer. Existing Unraid
vendor containers remain managed separately.

## Development and tests

Use Python 3.13 and Poppler (`poppler-utils` / Homebrew `poppler`). Keep the
environment in `.venv/`, rather than putting it directly in the project root.

```sh
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
docker build -t nyt-to-pdf:qa .
docker run --rm -i --network none --entrypoint python nyt-to-pdf:qa - < tests/smoke_render.py
```

Unit tests exercise missing-edition fallback, HTTP errors, cached-image survival,
display offsets, static-image restrictions, and health behavior. The container
smoke test also exercises real Poppler with a generated PDF, without NYT access.

## Publishing and updating

Repository: https://github.com/danyal/nyt-to-pdf

Image: `ghcr.io/danyal/nyt-to-pdf`

GitHub Actions tests changes and builds a Linux amd64 image for Unraid. Pull
requests build and test without publishing. Main-branch pushes publish `edge`
and `sha-<commit>`; version tags publish the version. Publishing a non-prerelease
GitHub release additionally advances `stable` and `latest`. Thus ordinary code
pushes do not change the image followed by the display.

```sh
git tag v1.4.0
git push origin v1.4.0
gh release create v1.4.0 --title 'v1.4.0' --notes-file RELEASE_NOTES.md
```

Create a fresh release-notes file for the release you are publishing. Release
publishing uses the workflow's built-in `GITHUB_TOKEN`, with `packages: write`;
no personal registry token is stored. The container package must be public for
anonymous Unraid pulls. Existing version tags are for rollback; do not move them.

Unraid's `nyt-to-image` container follows `ghcr.io/danyal/nyt-to-pdf:stable` on
host port 10070. Publishing and installing are separate operations: Unraid can
detect a new image; applying an update recreates the container. This migration
does not enable scheduled automatic installation. Keep persistent cache ownership
compatible with UID 1000. See `docs/MIGRATION-2026-11-25.md` for audit and rollback.
