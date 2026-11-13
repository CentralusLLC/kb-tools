---
type: Work Item
id: "0010-06"
epic: "0010"
title: "Approval-gated system package installs"
description: "Agents install system packages into their dev container with devenv_install, and Paperclip asks a human first for that and the other lifecycle tools."
tags: [work-item]
status: draft
kind: story
work_status: blocked
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-8"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:35Z
---

# 0010-06: Approval-gated system package installs

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

An agent that needs a system package now can get it without waiting for a rebuild, but only
with a human's approval: agents must not change their own environment unchecked. The plan
gates `devenv_create`, `devenv_rebuild` and `devenv_install` with a Paperclip "ask first" policy.

## Acceptance criteria

- [x] `devenv_install` installs system packages into a running container and persists them
      for rebuilds (built with [0010-03](03-devenv-manager-mcp-service-create-status-rebuild.md)).
- [x] The template's [dev-environment page](../../../../../src/kbtools/template/docs/environments/dev-environment.md)
      tells agents to add packages to `.devcontainer/Dockerfile` in a pull request and to use
      `devenv_install` with a reason only when blocked.
- [x] "Ask first" is set on `devenv_create`, `devenv_delete`, `devenv_install`,
      `devenv_rebuild` and `devenv_stop` in Paperclip's Tools screen (CEN-8).
- [ ] Paperclip actually shows an approval card before those tools run, checked with one call.

## Notes

**Blocked (2026-11-12) on Paperclip CEN-8 (backlog), a Paperclip platform problem, not kb-tools
code.** The gate is configured but bypassed: `devenv_rebuild` and `devenv_create` ran with no
approval card on 2026-11-05 (CEN-5, CEN-8). The likely cause is a policy rule that ranks above
the `require_approval` entries. Until it is fixed, Chief asks for an explicit OK in the issue
thread before calling these tools.

Remaining: once CEN-8 is fixed, make one gated call, confirm the card appears, tick the last
criterion and close this item.
