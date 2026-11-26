Recover live Visionect display settings and migrate image publishing from Docker Hub to GHCR.

- Preserve 1480px rendering, crop-box/annotation options, and -23px/-35px display offsets.
- Fix date fallback and add timeouts, cached-image recovery, and atomic PNG writes.
- Update Python, Poppler, and Python dependencies; run as a non-root user.
- Add tests, health checks, project instructions, and release-based image publishing.
- Keep the separately deployed Visionect Software Suite unchanged.
