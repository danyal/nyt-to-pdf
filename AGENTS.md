# Project instructions

## Purpose and scope

This local folder is `/Users/danyal/Source/visionect`; its public GitHub repository
is `danyal/nyt-to-pdf`. It owns the custom NYT PDF-to-PNG HTTP renderer, not the
proprietary Visionect Software Suite. The runtime container retains the name
`nyt-to-image` so existing Unraid and display configuration keeps working.

## Architecture

- `nyt_server.py`: Bottle WSGI app, HTTP downloader, Poppler conversion, atomic PNG
  replacement. Importing the module must not start the HTTP server.
- `requirements.txt`: pinned Python dependencies, used for tests and Docker.
- `Dockerfile`: Python 3.13 / Debian Trixie, distribution Poppler packages,
  non-root UID 1000, port 8001, cache `/data/nyt_fp.png`, HTTP health check.
- `docker-compose.yml`: standalone renderer for local use; not the production
  definition for Unraid's separate Visionect/Postgres/Redis stack.
- `.github/workflows/publish-image.yml`: test, render smoke test, and GHCR publish.
- `tests/`: stdlib unittest regression coverage plus a real-Poppler smoke script.
- `docs/MIGRATION-2026-11-25.md`: recovered edits, audit evidence, rollback.

## Preserve display behavior

Preserve width 1480, DPI 600, grayscale conversion, `use_cropbox=True`,
`hide_annotations=True`, first page only, and both recovered HTML offsets:
left -23px and top -35px. Keep `/` and `/image/nyt_fp.png` working. Do not change
these settings based on generic formatting preferences. Render real output when
changing dependencies or conversion behavior; inspect dimensions and layout.

The date follows `America/Los_Angeles`. Missing PDFs should fall back one day at
a time, up to three editions. Failed downloads/conversions must preserve the last
good PNG. `/healthz` must not cause upstream requests or image conversion.

## Validate changes

Run `python -m unittest discover -s tests -v` in an isolated environment and build
the container for runtime/dependency changes. Run the real Poppler smoke script
inside the built image. For deployment, verify `/healthz`, `/`, the PNG's format
and dimensions, logs, and the actual image digest; process health is not evidence
of newspaper freshness. GitHub builds amd64 for Unraid; local Apple Silicon
verification may use arm64. Keep workflows and external actions pinned by commit.

## Release and deployment

Publish only from this repository to `ghcr.io/danyal/nyt-to-pdf`. Main updates
`edge`; non-prerelease GitHub releases update `stable`/`latest` and version tags.
Do not repoint stable from an ordinary main push or a prerelease. Use the
workflow's `GITHUB_TOKEN`. Keep the repository and package public as requested.

Unraid: `root@192.168.1.104` (`RacksOnRacks`), container `nyt-to-image`, bridge
network, host port 10070 to container 8001. Its persistent DockerMan template is
`/boot/config/plugins/dockerMan/templates-user/my-nyt-to-image.xml` and must agree
with the running image. Preserve labels, port mapping, autostart, and the PNG
cache mapping during replacement. The separate `Visionect-Software-Suite`, Redis,
and Postgres containers are outside this app's deployment scope.

Before replacing a live container, inspect `docker diff`, compare `/app` source
against Git and the original image, back up its configuration/cache/template, and
keep a rollback container/image. The user previously edited production directly;
reconcile such edits before recreation. Future source changes belong in Git.

## Local-only data

`.local/` holds private audit backups (including original source, Docker inspect,
template, and generated image). Root `bin/`, `include/`, `lib/`, and `pyvenv.cfg`
are a pre-existing virtual environment. `test_images/`, `test.pdf`, and `nyt_fp.png`
are old/generated newspaper assets. Keep them out of Git and Docker contexts;
do not delete them merely to clean the repository. The Docker context explicitly
allows only the Dockerfile, server, and dependency file. Never publish real
configuration secrets, newspaper PDFs/PNGs, or local audit archives.
