---
type: Work Item
id: "0010-18"
epic: "0010"
title: "Devenv previews: publish app ports for people to test"
description: "devenv_expose and devenv_unexpose publish an app port from a dev container through a forwarder container so people can test previews, and rebuild swaps wait only for open SSH sessions."
tags: [work-item]
status: stable
kind: story
work_status: done
priority: medium
depends_on: []
links: 
  github: "#9"
  jira: ""
  paperclip: "CEN-61"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-15T01:06:32Z
---

# 0010-18: Devenv previews: publish app ports for people to test

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

People need to try what an agent built (a dev server, a built game) without access to the dev
container. `devenv_expose(project, port)` publishes an app port through a small forwarder
container (`alpine/socat`) on a `devenv` network; the forwarder reaches the dev container by
name, so a preview survives rebuilds. An admin then serves it on the tailnet over HTTPS.
`devenv_unexpose` stops it, and `devenv_delete` removes a project's forwarders.

Rebuild swaps used to wait for any process running as `agent`, so a preview server left
running blocked a rebuild for the whole `DEVENV_SWAP_WAIT`. They now wait only for open SSH
sessions (`sshd: agent`); servers end with the old container and must be restarted.

## Acceptance criteria

- [x] `devenv_expose` publishes a container port on `DEVENV_HOST_IP` with a free port from
      `DEVENV_PREVIEW_PORTS`, and reuses the host port when the same port is exposed again
- [x] Forwarders reach the dev container by name and are reconnected after a rebuild
- [x] `devenv_unexpose` and `devenv_delete` remove the forwarders; `devenv_status` lists previews
- [x] Rebuild swaps wait only for open SSH sessions
- [x] `DEVENV_PREVIEW_PORTS` and `DEVENV_FORWARDER_IMAGE` have neutral defaults and are in
      `compose.yaml`, `.env.example` and [Configuration](../../../../environments/configuration.md)
- [x] Tests; docs in [Agent dev environments](../../../../environments/agent-dev-environments.md),
      `devenv/README.md` and the template's dev-environment page

## Notes

- Re-landed from an unmerged commit on the old `0010-agent-dev-environments` branch (written
  under 0010-03 on 2026-11-06), on the board's decision in CEN-61. That version hard-coded
  the deployment's preview port range and listed its current previews; this one uses the
  neutral default `24100-24199` (right after `DEVENV_PORTS`) and no deployment-specific
  list. The old branch is deleted.
- Deployments that already run previews set `DEVENV_PREVIEW_PORTS` in their `.env` to keep
  their existing host ports.
