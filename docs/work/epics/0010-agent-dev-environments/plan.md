---
type: Implementation Plan
epic: "0010"
title: "Plan: Agent dev environments"
description: "How agents get complete dev environments in Paperclip: an isolated account, a devenv manager building per-project dev containers from .devcontainer, Paperclip SSH environments, and approval-gated installs."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:28Z
---

# Plan: Agent dev environments

## Approach

Agents run inside per-project dev containers through Paperclip's SSH execution environment
(the claude_local adapter supports remote targets and seeds its config and credentials there).
Containers are built from each repository's `.devcontainer/` plus an agent overlay, by a
devenv manager exposed over MCP. Paperclip only lets instance admins register environments,
so the owner does one registration step per project; everything else is automated.

Alternatives rejected:
- A custom Paperclip image with all toolchains: one image for every project, and a Paperclip
  restart for every package.
- Giving agents the Docker socket: control of every centralus container, including the database
  and secrets.
- A sandbox-provider plugin: the most native option, deferred until this has proven itself.

## Design

See [Agent dev environments](../../../environments/agent-dev-environments.md):
- account `agentdev` (its own uid) with rootless Docker and org egress rules;
- manager on `<host-ip>:<manager-port>`, protected by a bearer token;
- dev containers on `<host-ip>:<port-range>`, each with a home volume, stable host keys and limits;
- tools: `devenv_status`, `devenv_create`, `devenv_rebuild`, `devenv_install` (system packages,
  persisted for rebuilds), `devenv_stop`, and `devenv_delete` (destructive, so Paperclip
  quarantines it).

## Items and sequencing

1. Done: account (0010-01), overlay (0010-02), kb-tools dev target (0010-04).
2. In progress: the manager (0010-03) needs a GitHub token for private repositories; the SSH trial
   (0010-05) passed by hand and still needs Paperclip registration; approval-gated installs
   (0010-06) need a Paperclip policy.
3. Then: template support (0010-07), and detecting projects without an environment (0010-08,
   through the agent workflow rule).

## Risks and open questions

- Paperclip's SSH driver is its least-exercised path; probe after registration and keep "local"
  as the fallback.
- Approval: the connection does not gate write tools by default (kb-tools' `kb_init` ran
  without approval), so a Paperclip policy must require approval for `devenv_create`,
  `devenv_rebuild` and `devenv_install`.
- One SSH key serves all dev containers; per-project keys are a later hardening step.
- Images are large (kb-tools' is about 2 GB); watch disk space in the agentdev account.

## Verification

- 2026-11-05: from the Paperclip container, SSH as `agent` reached the kb-tools dev container,
  which has node 22, Claude Code 2.1.318, git and LibreOffice and no sudo; `python -m pytest`
  passed 18 tests in 5.5 s.
- Still to verify: an agent run through the registered Paperclip environment executes there and
  its commits come back.
