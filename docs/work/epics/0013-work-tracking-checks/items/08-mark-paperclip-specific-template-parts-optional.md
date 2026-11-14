---
type: Work Item
id: "0013-08"
epic: "0013"
title: "Mark Paperclip-specific template parts optional"
description: "Say in the scaffold templates which Paperclip-specific parts are optional when a project uses another agent platform."
tags: [work-item]
status: draft
kind: chore
work_status: todo
priority: high
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-50"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T20:13:10Z
---

# 0013-08: Mark Paperclip-specific template parts optional

Part of [epic 0013](../epic.md) ([plan](../plan.md)).

## What and why

Paperclip is the only agent platform the templates describe in detail (finding 15). That suits
an add-on to Paperclip environments, but a project on another platform can't tell what to skip.

## Acceptance criteria

- [x] The template's dev-environment page marks its "Agents" section and the `devenv_*` tools as
      Paperclip-specific and optional.
- [x] Template pages that mention Hindsight memory say it is optional.
- [x] The `trackers.yaml` template marks the Paperclip section optional.
- [x] A fresh `kb scaffold` passes `kb check`.
