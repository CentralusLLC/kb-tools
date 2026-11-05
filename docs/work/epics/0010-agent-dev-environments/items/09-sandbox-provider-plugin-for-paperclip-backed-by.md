---
type: Work Item
id: "0010-09"
epic: "0010"
title: "Sandbox-provider plugin for Paperclip backed by the devenv manager"
description: "Not ready for development: a Paperclip sandbox-provider plugin (environment driver) that uses the devenv manager as its backend, so projects just pick an environment."
tags: [work-item]
status: draft
kind: story
work_status: backlog
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T15:52:02Z
---

# 0010-09: Sandbox-provider plugin for Paperclip backed by the devenv manager

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

The most native form of agent dev environments. Paperclip would own leases, probes, file sync
and deletes, and show them in its UI. Agents would never call the manager, which removes the
bearer-token concern and the per-project SSH key and registration steps.

## Acceptance criteria

- [ ] A plugin declaring an environment driver of kind `sandbox_provider`, configured with the
      manager URL and token as secret refs.
- [ ] Lease acquire/resume/release/destroy map to the manager's container lifecycle; execution
      runs through the manager (docker exec), not SSH.
- [ ] Native file sync hooks (`environmentSyncIn`/`Out`) or the base64 fallback.
- [ ] `.devcontainer/` builds become the environment's image.

## Notes

Contract: Paperclip's `doc/plugins/SANDBOX_PROVIDER_CAPABILITIES.md`, `SANDBOX_FILE_SYNC_HOOKS.md`
and `PLUGIN_SPEC.md` (in the Paperclip image under `/app/doc/plugins/`); the bundled providers in
`packages/plugins/sandbox-providers/` (kubernetes, daytona, e2b and others) and
`paperclip-plugin-fake-sandbox` are reference implementations. Start once the SSH approach
(0010-05) has proven itself.
