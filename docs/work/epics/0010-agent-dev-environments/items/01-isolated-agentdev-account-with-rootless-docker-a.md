---
type: Work Item
id: "0010-01"
epic: "0010"
title: "Isolated agentdev account with rootless Docker and egress rules"
description: "A dedicated agentdev account on the Paperclip host with its own rootless Docker and egress rules, so agent dev containers can't reach Paperclip or its secrets."
tags: [work-item]
status: draft
kind: task
work_status: done
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:29Z
---

# 0010-01: Isolated agentdev account with rootless Docker and egress rules

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

Agent dev containers need a Docker daemon, but the host's daemon also runs Paperclip, its
database and its secrets. A separate account with its own rootless Docker keeps agents' builds
and installs away from them, and egress rules keep them off the LAN and internal services.

## Acceptance criteria

- [x] An `agentdev` account with a locked password, no sudo, no groups, and lingering.
- [x] Rootless Docker for that account; the devenv manager uses only its socket.
- [x] Egress limited to the internet, DNS, the model gateway and Paperclip's public URL; the LAN,
      other accounts' ports and internal services are rejected.
- [x] Documented in [Agent dev environments](../../../../environments/agent-dev-environments.md#isolation).

## Notes

Set up on the Paperclip host on 2026-11-05 and used by every dev container since (0010-03,
0010-05). Why Paperclip's public URL stays open is explained on the environment page: SSH runs
fetch their GitHub credentials from it.
