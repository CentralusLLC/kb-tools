# devenv manager

Per-project dev containers for AI agents, used through Paperclip's **SSH execution
environment**. See epic 0010 in `docs/work/` and `docs/environments/agent-dev-environments.md`.

- Builds each project's dev image from its `.devcontainer/` (image or Dockerfile build, with
  target and args) or, without one, from `kbdevenv/default/`.
- Adds the **agent overlay** (`kbdevenv/overlay/`): sshd (key-only, user `agent`, no sudo),
  git, tar, node and the `claude` CLI.
- Runs one container per project with sshd on `DEVENV_HOST_IP:<port>` (<port-range>), a
  persistent home volume, a stable host-key volume, and memory, CPU and pids limits.
- Exposes MCP tools behind a bearer token: `devenv_status` (read), `devenv_create`,
  `devenv_rebuild`, `devenv_install` (system packages; approval in Paperclip), `devenv_stop`,
  and `devenv_delete` (destructive).

Runs as the isolated `agentdev` account (its own rootless Docker), so agents' builds cannot
reach Paperclip, its database or its secrets.
