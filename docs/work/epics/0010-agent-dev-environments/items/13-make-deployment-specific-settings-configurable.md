---
type: Work Item
id: "0010-13"
epic: "0010"
title: "Make deployment-specific settings configurable"
description: "Keep the devenv manager and the Paperclip host deployment, but supply every deployment-specific host, IP, port and URL through environment variables with neutral defaults, so the public repository carries no Centralus values."
tags: [work-item]
status: draft
kind: story
work_status: blocked
priority: critical
depends_on: []
links: 
  github: "#8"
  jira: ""
  paperclip: "CEN-34"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-06T13:01:03Z
---

# 0010-13: Make deployment-specific settings configurable

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

The owner wants to keep the devenv manager and the Paperclip host deployment in kb-tools, not delete them,
so the public repository has to stop hard-coding Centralus' values (private IPs, ports,
hostnames, internal MCP URLs) and read them from configuration instead. Environment variables
are the preferred mechanism. Centralus' real values live outside the repository: non-secret
values only in the untracked `.env` on the Paperclip host, secrets only in Paperclip secrets (decided
2026-11-06; see Notes).

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

Added scope (2026-11-12, CEN-34): the gameworld add-on validation (CEN-35, feedback 1-4) and
the board's deployment model (CEN-12: heavy extraction only on the Paperclip machine through
the MCP server, light `tools/kb` in project containers):

- MCP server: `KB_REPOS_ROOT` (default `/repos`) where `repo=<name>` or `<owner>/<name>`
  resolves; `KB_ALLOWED_ROOTS` for absolute paths; errors and the server instructions list
  what the server can see; failures are MCP tool errors (`isError: true`).
- `tools/kb --install` is light by default (PyYAML only); `--full` / `KB_TOOLS_EXTRAS=extract`
  adds the `[extract]` extra. `kb extract` / `kb figure` without it say where to run them.
- The kb-tools source is recorded once per project in `tools/kb.conf` (written by
  `kb scaffold`) and per install in `$KB_TOOLS_HOME/install.conf`.
- `kb --version` reports `0.1.0+<ref>.<commit>`.
- `kb check` stays clean when an ingested original is not present locally (regression test).
- An add-on install guide (`docs/environments/paperclip-add-on.md`) that says plainly which
  tools are for which agents.

## Acceptance criteria

- [x] No Centralus value remains in code, compose files or docs touched here; the 0010-11
      scan is clean for them. (One deliberate exception for 0010-11 to confirm: the public
      repository URL as the fallback install source in `src/kbtools/version.py`.)
- [x] Defaults are neutral (`127.0.0.1`, no internal IPs or hosts).
- [x] `devenv/compose.yaml` uses `${VAR}` interpolation only; `devenv/.env.example` is
      committed and `devenv/.env` is git-ignored.
- [x] `DEVENV_MANAGER_PORT`, `KB_MCP_HOST` and `KB_MCP_PORT` exist alongside the existing
      `DEVENV_*` variables.
- [x] Docs use placeholders and include one table of every variable.
- [x] Tests cover the defaults and environment overrides for both the devenv manager and
      `kb serve`.
- [x] `repo=<name>` resolves under `KB_REPOS_ROOT`; MCP failures are tool errors.
- [x] Light install by default, `--full` for extraction; light commands tested without the
      extraction libraries.
- [x] `kb --version` includes the ref and commit; the install source is stored, not repeated.
- [x] Before merge, the exact list of variables the Paperclip host's `.env` needs (names and what each
      holds, no values) is posted on the Paperclip task so the admin agent can write it on
      the host; anything needed on the Paperclip host or in Paperclip is requested through Chief.
- [ ] The Paperclip host deployment is verified working with its values supplied externally (record
      the check in the epic plan's Verification section).

## Notes

- Sequencing changed (CEN-34, 2026-11-12): done before 0010-11, because the gameworld
  validation needed the MCP and install fixes first; 0010-11 then audits the result.
  Original note: after the 0010-11 audit (which lists what to make configurable) and before the
  0010-10 history rewrite, so the rewrite can replace the old values in history once.
- Decided 2026-11-06 (owner via Chief, CEN-12/CEN-14): no private repository for now.
  Centralus' real non-secret values (host IP, ports, host names, MCP address) live only in
  the untracked `.env` on the Paperclip host; real secrets stay in Paperclip secrets. Nothing goes in any
  repository. Internal-only deployment notes removed from the public docs go into a
  Paperclip task document, not the repository.
- Changing published ports or bind addresses on the Paperclip host affects live Paperclip connections
  (the devenv manager and kb-tools MCP URLs); verify both after redeploying.
- Blocked (2026-11-13, 0013-01): PR #8 is merged into `dev`; the last criterion, verifying the
  Paperclip host deployment, waits for the board, which has deferred deploys (CEN-12).
