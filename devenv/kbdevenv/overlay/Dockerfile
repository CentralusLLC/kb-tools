# Agent overlay: adds what Paperclip's SSH execution environment needs to any project
# dev image (Debian/Ubuntu based): sshd, git, tar, node and the claude CLI, and an
# unprivileged `agent` user. Built by the devenv manager on top of the project image.
ARG BASE
FROM ${BASE}
USER root
ARG EXTRA_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends openssh-server git tar ca-certificates curl gnupg procps ${EXTRA_PACKAGES}; \
    if ! command -v node >/dev/null 2>&1; then \
      curl -fsSL https://deb.nodesource.com/setup_22.x | bash -; \
      apt-get install -y --no-install-recommends nodejs; \
    fi; \
    rm -rf /var/lib/apt/lists/*; \
    npm install -g @anthropic-ai/claude-code; \
    if ! id agent >/dev/null 2>&1; then \
      if getent passwd 1000 >/dev/null; then useradd -m -s /bin/bash agent; \
      else useradd -m -s /bin/bash -u 1000 agent; fi; \
    fi; \
    mkdir -p /etc/devenv /run/sshd
COPY sshd_config /etc/ssh/sshd_config.d/devenv.conf
COPY authorized_keys /etc/devenv/authorized_keys
COPY entrypoint.sh /usr/local/bin/devenv-entrypoint
RUN chmod 0644 /etc/devenv/authorized_keys && chmod 0755 /usr/local/bin/devenv-entrypoint
# Agent-owned installs (pip --user, npm -g) stay in the persistent home volume.
ENV NPM_CONFIG_PREFIX=/home/agent/.npm-global
EXPOSE 22
ENTRYPOINT ["/usr/local/bin/devenv-entrypoint"]
