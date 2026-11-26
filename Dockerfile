# syntax=docker/dockerfile:1
FROM python:3.13-slim-trixie

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=America/Los_Angeles \
    IMAGE_PATH=/data/nyt_fp.png

RUN apt-get update \
    && apt-get install -y --no-install-recommends poppler-utils poppler-data tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --no-create-home app \
    && mkdir /data && chown app:app /data

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY nyt_server.py ./

LABEL org.opencontainers.image.source="https://github.com/danyal/nyt-to-pdf" \
      org.opencontainers.image.description="NYT front-page PDF to PNG service for a Visionect display"

USER app
EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/healthz', timeout=3)"
CMD ["python", "nyt_server.py"]
