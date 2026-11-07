# devenv manager

Per-project dev containers for AI agents, used through Paperclip's **SSH execution
environment**. See epic 0010 in `docs/work/` and `docs/environments/agent-dev-environments.md`.

- Holds **no GitHub credential and never clones**. Paperclip's SSH environment syncs the
  project worktree into the container on every run. `devenv_create` starts the project from
  `kbdevenv/default/`; `devenv_rebuild` then builds the `.devcontainer/` (image or Dockerfile
  build, with target and args) from that synced worktree. The container is swapped only once no
  agent session is running in it.
- **Previews:** `devenv_expose` publishes an app port through a small forwarder container on
  `DEVENV_HOST_IP:<port-range>`; an admin serves it on the tailnet (`tailscale serve`).
- **Per-project SSH keys:** `devenv_create` takes the public key; the agent stores the private
  half in Paperclip through an approved secret proposal.
- Adds the **agent overlay** (`kbdevenv/overlay/`): sshd (key-only, user `agent`, no sudo),
  git, tar, node and the `claude` CLI.
- Runs one container per project with sshd on `DEVENV_HOST_IP:<port>` (<port-range>), a
  persistent home volume, a stable host-key volume, and memory, CPU and pids limits.
- Exposes MCP tools behind a bearer token: `devenv_status` (read), `devenv_create`,
  `devenv_rebuild`, `devenv_install` (system packages; approval in Paperclip), `devenv_stop`,
  and `devenv_delete` (destructive).

Runs as the isolated `agentdev` account (its own rootless Docker), so agents' builds cannot
reach Paperclip, its database or its secrets.

Tests (need Python 3.12):
`docker run --rm -v "$PWD:/src" -w /src python:3.12-slim sh -c "pip -q install pytest && PYTHONPATH=. python -m pytest -q tests"`
