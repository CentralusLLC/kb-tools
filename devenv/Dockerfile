# devenv manager: builds and runs per-project agent dev containers through the
# (rootless) Docker socket of the account it runs in.
FROM python:3.12-slim-bookworm
ENV PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg git tini \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
 && echo "deb [signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli docker-buildx-plugin \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/devenv
COPY pyproject.toml ./
COPY kbdevenv ./kbdevenv
RUN pip install .
EXPOSE 8780
# Listen on all interfaces inside the container; compose publishes it on DEVENV_HOST_IP only.
ENTRYPOINT ["/usr/bin/tini", "--", "devenv-manager", "--host", "0.0.0.0"]
