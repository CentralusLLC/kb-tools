---
type: Work Item
id: "0010-13"
epic: "0010"
title: "Make deployment-specific settings configurable"
description: "Keep the devenv manager and the the Paperclip host deployment, but supply every deployment-specific host, IP, port and URL through environment variables with neutral defaults, so the public repository carries no Centralus values."
tags: [work-item]
status: draft
kind: story
work_status: todo
priority: critical
depends_on: ["0010-11"]
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-06T13:01:03Z
---

# 0010-13: Make deployment-specific settings configurable

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

The owner wants to keep the devenv manager and the the Paperclip host deployment in kb-tools, not delete them,
so the public repository has to stop hard-coding Centralus' values (private IPs, ports,
hostnames, internal MCP URLs) and read them from configuration instead. Environment variables
are the preferred mechanism. Centralus' real values live outside the repository; Chief
coordinates where (possibly Paperclip-side) and posts the answer before this item runs.

Proposal:

- Keep the existing `DEVENV_*` variables (`DEVENV_TOKEN`, `DEVENV_HOST_IP`, `DEVENV_PORTS`,
  `DEVENV_DATA`, `DEVENV_PUBKEY`, `DEVENV_MEMORY`, `DEVENV_CPUS`, `DEVENV_PIDS`,
  `DEVENV_SWAP_WAIT`) and add `DEVENV_MANAGER_PORT` (the manager's published MCP port).
- Add `KB_MCP_HOST` and `KB_MCP_PORT` for `kb serve` (today `--port` defaults to 8765 and
  the host is hard-coded in `src/kbtools/server.py`); command-line flags still override them.
- Neutral defaults: `127.0.0.1` and no internal IPs, hostnames or ports. Where a container must
  listen on all interfaces, its Dockerfile or compose file sets that explicitly.
- `devenv/compose.yaml` takes every deployment value through `${VAR}` interpolation from an
  untracked `devenv/.env`; commit a `devenv/.env.example` with placeholders and make sure
  `.env` is git-ignored.
- Docs (`README.md`, `devenv/README.md`, `docs/environments/*`) use placeholders such as
  `<host-ip>` and `<kb-mcp-url>`, with one table listing every variable, its default and what
  it controls (in `docs/environments/configuration.md`).

## Acceptance criteria

- [ ] No Centralus value remains in code, compose files or docs touched here; the 0010-11
      scan is clean for them.
- [ ] Defaults are neutral (`127.0.0.1`, no internal IPs or hosts).
- [ ] `devenv/compose.yaml` uses `${VAR}` interpolation only; `devenv/.env.example` is
      committed and `devenv/.env` is git-ignored.
- [ ] `DEVENV_MANAGER_PORT`, `KB_MCP_HOST` and `KB_MCP_PORT` exist alongside the existing
      `DEVENV_*` variables.
- [ ] Docs use placeholders and include one table of every variable.
- [ ] Tests cover the defaults and environment overrides for both the devenv manager and
      `kb serve`.
- [ ] The the Paperclip host deployment is verified working with its values supplied externally (record
      the check in the epic plan's Verification section).

## Notes

- Sequencing: after the 0010-11 audit (which lists what to make configurable) and before the
  0010-10 history rewrite, so the rewrite can replace the old values in history once.
- Where Centralus' real values and any private deployment docs live is still open with the
  owner; Chief will answer on CEN-14 before this item runs. Don't commit real values here.
- Changing published ports or bind addresses on the Paperclip host affects live Paperclip connections
  (the devenv manager and kb-tools MCP URLs); verify both after redeploying.
