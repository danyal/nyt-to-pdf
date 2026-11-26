# Visionect / NYT renderer audit — November 25, 2026

## Before migration

- Custom container: `nyt-to-image`, ID `88f6b923d113`.
- Image: `danyal711/nyt-to-image:v1.3`.
- Image ID: `sha256:daeebf83c337f4ca9f3af2621578fa46ebbc0b1f7dfe2280fc313a17b4bdc229`.
- Docker Hub digest: `sha256:7ea00aa1bee7af0766cb805f0dd809832b19ba3ad4bc6b7d9a516fee2b975790`.
- Bridge network, TCP 10070 → 8001, no mounts, restart policy `no`; listed in
  Unraid autostart. Docker logging capped at one 50 MB file.
- Python 3.8.12, Bottle 0.12.19, pdf2image 1.16.0, Pillow 8.4.0, Requests 2.26.0.
- Separate vendor container: `Visionect-Software-Suite`, image
  `visionect/visionect-server-v3:7.6.5`. Its database/Redis/display settings are
  outside this migration.

## Verified live edits

`docker diff` marked `/app/nyt_server.py` modified and showed an installed nano
editor. Comparison against the original v1.3 image confirmed functional edits:
crop-box rendering, hidden PDF annotations, revised fallback/error handling, and
HTML offsets. The local script already contained most of these edits; it lacked
the live `margin-top: -35px`. The live file was copied locally and committed
unchanged before cleanup (`946233c`).

The live and local Dockerfile, requirements, and old compose file were byte-for-
byte identical. The only other changed `/app` file was generated `nyt_fp.png`.
No bind mounts could be hiding a second source version. Remaining writable-layer
changes were editor packages, package-manager bookkeeping, Python bytecode and
temporary files, rather than additional application code.

SHA-256 of live `nyt_server.py` before cleanup:
`a7265c28d14eaa14760568ef8a49040d06f2227d4ce9a978489fd46a0941c7b5`.
Local script before reconciliation:
`cd4e5fc2031c5385f4a2e1a38423fc6b4beaf4762759eed6d1f9e638140cb0d3`.

The old HTTP endpoint successfully refreshed the November 25 edition and served
the recovered HTML offsets. Baseline image: PNG, RGB, 1480 × 2665.

## Cleanup

- Preserve live rendering options and HTML placement.
- Repair unreachable fallback logic: 404s are checked before attempting PDF
  conversion, with dates correctly handling month/year boundaries.
- Add download/render timeouts, explicit HTTP errors, useful error logging,
  atomic image replacement, and cached-image fallback during upstream failures.
- Add a side-effect-free health endpoint and import-safe server startup.
- Replace end-of-life Python/Debian and hand-compiled 2021 Poppler with Python
  3.13, Debian Trixie distribution packages, and pinned Python dependencies.
- Run as UID 1000; persist the rendered PNG outside the container writable layer.
- Exclude the old environment, sample assets, and audit files from Git and Docker.
  Preserve the old exploratory script under `.local/legacy/`.
- Replace the historical vendor-stack compose file with a standalone app compose
  file; original remains backed up locally. Do not apply it to the vendor stack.

## Backup and rollback

Local audit directory: `.local/migration-2026-11-25/` (ignored by Git), including
original local files, exact live `/app`, original-image script, and deployment
inspection/template/autostart. It contains generated newspaper assets and is not
part of the public repository or image.

The production replacement must retain the original container under
`nyt-to-image-before-ghcr-20261125` and back up the DockerMan template under
`/mnt/user/appdata/nyt-to-image/migration-20261125/`.

To roll back, stop the new `nyt-to-image`, rename it aside, restore the original
container's name, start it, and restore the backed-up XML template. Keep the
original container: merely recreating Docker Hub v1.3 would lose the recovered
live edits. Keep the original image and old container until the user is satisfied.

Deployment results and exact release digest will be appended after verification.

## Local validation before publication

Eight regression tests passed. A generated-PDF smoke test exercised real Poppler
inside the replacement image without network access. The replacement also fetched
and rendered the November 25 edition successfully over HTTP. Its PNG remained
1480 × 2665, RGB. Compared with the saved production rendering, 98.59% of pixels
were identical; the mean per-channel difference was 0.081 on a 0–255 scale. A
visual inspection confirmed the full-page layout; minor raster differences are
expected with updated Poppler. Both recovered HTML offsets were unchanged.
