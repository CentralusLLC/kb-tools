# Dev environment for this project. Start from what the project needs and keep it
# reproducible: every tool the tests or build use belongs here (see
# docs/environments/dev-environment.md). The agent overlay is added on top by the
# devenv manager, so don't add sshd, node or the claude CLI here unless the project needs them.
FROM python:3.12-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git curl jq ripgrep unzip make \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir uv pytest
WORKDIR /workspace
