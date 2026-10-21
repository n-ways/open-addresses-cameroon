# N-Ways Addressing for Cameroon: the registry server.
# Build from the repository root:  docker build -f server/Dockerfile -t nways-addresses-cm .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ADDRESSES_DB=/data/addresses.sqlite \
    REGISTRY_DIR=/app/registry \
    HOST=0.0.0.0 \
    PORT=8080

RUN groupadd --system --gid 10001 addresses \
 && useradd --system --uid 10001 --gid addresses --home-dir /app --shell /usr/sbin/nologin addresses \
 && mkdir -p /data \
 && chown addresses:addresses /data

WORKDIR /app
# What the server reads: the reference engine and its data, the arrondissement
# outlines and frames, and the published registry it imports on first start.
COPY --chown=addresses:addresses engine/reference/cm_engine.py engine/reference/cm_border.py engine/reference/plate_names.py engine/reference/
COPY --chown=addresses:addresses engine/data/ engine/data/
COPY --chown=addresses:addresses model/zones.json model/
COPY --chown=addresses:addresses model/units/ model/units/
COPY --chown=addresses:addresses model/areas/name-ranges.json model/areas/
COPY --chown=addresses:addresses registry/ registry/
COPY --chown=addresses:addresses server/__init__.py server/__main__.py server/api.py server/geo.py server/register.py server/service.py server/store.py server/

USER addresses
VOLUME ["/data"]
EXPOSE 8080
# The first start imports 7.2 million codes (about three minutes) before it serves.
HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
  CMD ["python3", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/v1/health' % os.environ.get('PORT', '8080'), timeout=4)"]
CMD ["python3", "-m", "server", "start"]
