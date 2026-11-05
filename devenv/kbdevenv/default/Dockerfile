# Default dev image for repositories without .devcontainer/: Debian with Python, uv,
# build tools and common CLIs. Projects should add their own .devcontainer/ when they
# need more (the agent overlay adds sshd, node and the claude CLI on top).
FROM python:3.12-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git curl jq ripgrep unzip make \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir uv pytest
