# kb-tools: document ingestion and knowledge-base checks, with LibreOffice for rendering.
#
#   docker build -t kb-tools .                     # runtime image
#   docker build --target test -t kb-tools:test .  # runs the test suite during the build
#
#   docker run --rm -u "$(id -u):$(id -g)" -v "$PWD:/work" kb-tools inventory --by human:me
#   docker run -d -p 8765:8765 -v /data:/data kb-tools serve --allowed-root /data

FROM python:3.12-slim-bookworm AS base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SAL_USE_VCLPLUGIN=svp \
    HOME=/tmp

# LibreOffice (headless rendering) plus fonts that match common Office documents:
# Carlito/Caladea are metric-compatible with Calibri/Cambria, Liberation with Arial/Times/Courier.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libreoffice-impress libreoffice-writer libreoffice-calc libreoffice-draw \
      fonts-dejavu fonts-liberation fonts-liberation2 fonts-crosextra-carlito fonts-crosextra-caladea \
      fonts-noto-core fonts-noto-cjk fontconfig ca-certificates tini \
 && rm -rf /var/lib/apt/lists/* \
 && fc-cache -f

WORKDIR /opt/kb-tools
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install ".[server]"

FROM base AS test
RUN pip install ".[dev]"
COPY tests ./tests
RUN python -m pytest -q

# Development environment (used by .devcontainer and agent dev containers): the base
# toolchain plus test dependencies. Source comes from the mounted or synced workspace;
# run tests with `python -m pytest` (pytest finds src/ through pythonpath).
FROM base AS dev
RUN pip install ".[dev,server]" \
 && apt-get update \
 && apt-get install -y --no-install-recommends git make \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace

FROM base AS runtime
LABEL org.opencontainers.image.title="kb-tools" \
      org.opencontainers.image.description="Document ingestion and OKF knowledge-base tools"
WORKDIR /work
EXPOSE 8765
ENTRYPOINT ["/usr/bin/tini", "--", "kb"]
CMD ["--help"]
