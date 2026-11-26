# NYT renderer migration — November 25, 2026

## Source recovery

The deployed application had edits beyond its published Docker Hub image. Its
PDF crop-box setting, hidden-annotation setting, and HTML placement were recovered
before cleanup. Most were already in the local script; the missing top offset
was restored. The exact recovered script was committed before refactoring
(`946233c`). Original files and deployment evidence are retained locally and
excluded from the public repository.

## Application cleanup

- Preserve 1480px width, 600 DPI, grayscale conversion, PDF crop box, hidden
  annotations, and HTML offsets of left -23px / top -35px.
- Fix unreachable fallback logic, trying three dates one day at a time.
- Add HTTP/render timeouts, explicit HTTP errors, error logging, atomic image
  replacement, and fallback to the last good cached image during upstream failure.
- Add a health endpoint without download side effects and import-safe startup.
- Update to Python 3.13, Debian Trixie distribution Poppler, pinned dependencies,
  a non-root user, and a persistent image cache.
- Exclude old environments, generated newspaper assets, and audit files from Git
  and Docker. Replace the historical vendor-stack compose file with an app-only
  compose file; the separate vendor services remain unchanged.

## Validation and release

Eight regression tests passed locally and in GitHub Actions. A generated-PDF
smoke test exercised real Poppler without network access. Today's NYT front page
also rendered successfully in the local image and published amd64 image.
The output remained 1480 × 2665 pixels, RGB. Compared with the previous rendering,
98.59% of pixels were identical and the mean channel difference was 0.081 on a
0–255 scale. Visual inspection confirmed the full-page layout and HTML offsets.

Public repository: https://github.com/danyal/nyt-to-pdf

Release: https://github.com/danyal/nyt-to-pdf/releases/tag/v1.4.0

Publishing run: https://github.com/danyal/nyt-to-pdf/actions/runs/45744483828

The release workflow passed testing, amd64 build, real PDF conversion, and GHCR
publishing. Anonymous image pulls work. Production has been switched to
`ghcr.io/danyal/nyt-to-pdf:stable`; health, HTML, and PNG responses were verified
after replacement. The original edited container and deployment configuration
are retained for rollback, with detailed access and rollback instructions in the
local ignored audit directory. The physical e-paper panel was not observed.

Publishing a full GitHub release advances `stable`. Applying that update in
Unraid is a separate operation; this migration did not enable an automatic
installation schedule.
