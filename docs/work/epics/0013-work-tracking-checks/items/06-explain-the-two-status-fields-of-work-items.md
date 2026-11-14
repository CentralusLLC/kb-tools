---
type: Work Item
id: "0013-06"
epic: "0013"
title: "Explain the two status fields of work items"
description: "Explain what OKF status means on work pages, and have kb work set mark closed items and epics stable."
tags: [work-item]
status: draft
kind: task
work_status: todo
priority: high
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-50"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T20:13:09Z
---

# 0013-06: Explain the two status fields of work items

Part of [epic 0013](../epic.md) ([plan](../plan.md)).

## What and why

Every item has OKF `status: draft` next to `work_status: done`, and nothing says whether
`status` should change (finding 12).

## Acceptance criteria

- [x] The work-tracking page (kb-tools and template) explains both fields and when `status` changes.
- [x] `kb work set ID done` or `cancelled` sets `status: stable`, since the page no longer changes;
      reopening sets it back to `draft`.
- [x] Tests cover it, and pass.
