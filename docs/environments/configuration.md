---
type: Environment
title: Configuration
description: "Every setting kb-tools reads (environment variables, config files, command-line flags) for the CLI wrapper, the MCP server and the devenv manager, with its purpose and neutral default; never deployment values or secrets."
tags: [environments, configuration, settings]
status: draft
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Configuration

Every deployment-specific value is a setting. The repository only holds neutral defaults
and placeholders; a deployment's real values live outside it (non-secret values in an
untracked `.env` on the host, secrets in the platform's secret store, such as Paperclip
secrets). Keep this table complete: a new setting in code adds a row in the same pull request.
Secret values never appear here ([Security](../process/security.md)).

## `tools/kb` (project wrapper and local install)

| Setting | Purpose | Default | Secret? |
| --- | --- | --- | --- |
| `KB_TOOLS_IMAGE` | Docker image the wrapper runs when Docker has it | `kb-tools:latest` | no |
| `KB_TOOLS_HOME` | Local install used without Docker (dev containers) | `~/.kb-tools` (home from the password database) | no |
| `KB_TOOLS_SOURCE` | pip source for `tools/kb --install` | `source=` in `tools/kb.conf`, then the last install's `$KB_TOOLS_HOME/install.conf` | no (never put credentials in it) |
| `KB_TOOLS_REF` | Ref installed when `--install` has no ref argument | `ref=` in `tools/kb.conf`, else `main` | no |
| `KB_TOOLS_EXTRAS` | Extras to install; `extract` is the same as `--install --full` | empty (light install) | no |
| `tools/kb.conf` | Per-project `source=` and `ref=`, written by `kb scaffold` from where kb-tools was installed (else the public repository) | written by `kb scaffold` | no |

## `kb serve` (MCP server)

Command-line flags override the environment.

| Setting | Flag | Purpose | Default | Secret? |
| --- | --- | --- | --- | --- |
| `KB_MCP_HOST` | `--host` | Listen address | `127.0.0.1` (the image sets `0.0.0.0` inside its container) | no |
| `KB_MCP_PORT` | `--port` | Listen port | `8765` | no |
| `KB_REPOS_ROOT` | | Where `repo=<name>` and `repo=<owner>/<name>` are looked up; always an allowed root | `/repos` | no |
| `KB_ALLOWED_ROOTS` | `--allowed-root` (repeatable) | More directories absolute `repo` paths may be under (`:`-separated) | none | no |

## devenv manager (`devenv/`)

`devenv/compose.yaml` reads every value from the untracked `devenv/.env`; copy
[`devenv/.env.example`](../../devenv/.env.example) to start.

| Setting | Purpose | Default | Secret? |
| --- | --- | --- | --- |
| `DEVENV_TOKEN` | Bearer token Paperclip sends to the manager (at least 24 characters) | none, required | **yes**: platform secret store and the host's `.env` |
| `DEVENV_HOST_IP` | Host address the manager and dev containers' sshd are published on; must be reachable from the Paperclip server and private | `127.0.0.1` | no |
| `DEVENV_MANAGER_PORT` | Host port of the manager's MCP endpoint (`http://<host-ip>:<manager-port>/mcp`) | `8780` | no |
| `DEVENV_PORTS` | Host port range for dev containers' sshd, one per project | `24000-24099` | no |
| `DEVENV_DATA` | State, logs and build contexts inside the manager container | `/data` | no |
| `DEVENV_PUBKEY` | Fallback SSH public key for projects created without one | `/data/keys/paperclip.pub` (optional) | no |
| `DEVENV_MEMORY` / `DEVENV_CPUS` / `DEVENV_PIDS` | Per-container limits | `8g` / `6` / `4096` | no |
| `DEVENV_SWAP_WAIT` | Seconds a rebuild waits for agent sessions to end | `21600` | no |
| `--host` / `--port` | Where the manager listens inside its container | `127.0.0.1` / `8780` (the image passes `--host 0.0.0.0`) | no |
