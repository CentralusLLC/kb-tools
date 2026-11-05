---
type: Work Item
id: "0010-03"
epic: "0010"
title: "devenv manager MCP service (create, status, rebuild, install, stop)"
description: "An MCP service in the agentdev account that creates, rebuilds, installs into, stops and deletes per-project dev containers, with per-project keys and builds from the synced worktree."
tags: [work-item]
status: draft
kind: story
work_status: in_progress
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:32Z
---

# 0010-03: devenv manager MCP service (create, status, rebuild, install, stop)

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

Agents need a complete dev environment per project, set up without the owner touching the Paperclip host.
The manager gives agents lifecycle tools behind Paperclip approval cards.

## Acceptance criteria

- [x] Tools: `devenv_status`, `devenv_create`, `devenv_rebuild`, `devenv_install`, `devenv_stop`, `devenv_delete` (destructive).
- [x] Bearer token required; agents cannot call it directly.
- [x] Per-project public key on `devenv_create`; no shared key needed for new projects.
- [x] No GitHub credential: `devenv_rebuild` builds `.devcontainer/` from the worktree Paperclip synced in.
- [x] Container swap waits until no agent session runs.
- [x] Unit tests (`devenv/tests`).
- [ ] Deployed and exercised by an agent through Paperclip (0010-05).

## Notes

See the [plan](../plan.md) for the 2026-11-05 revision (no clone, per-project keys).
