---
type: Work Item
id: "0013-02"
epic: "0013"
title: "Warn about done items with unchecked acceptance criteria"
description: "Warn in kb check and in kb work set when a done item still has unchecked acceptance criteria."
tags: [work-item]
status: draft
kind: task
work_status: done
priority: high
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-50"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T20:13:08Z
---

# 0013-02: Warn about done items with unchecked acceptance criteria

Part of [epic 0013](../epic.md) ([plan](../plan.md)).

## What and why

gameworld's 0002-01 was `done` with an open `- [ ]` criterion (finding 8). The definition of
done says criteria are met and ticked, but nothing checks it.

## Acceptance criteria

- [x] `kb check` warns about a `done` item with `- [ ]` in its Acceptance criteria section.
- [x] `kb work set ID done` prints the same warning (the status is still set).
- [x] Tests cover both, and pass.
- [x] Work-tracking docs mention the check.

## Notes

Only the Acceptance criteria section counts; checklists elsewhere (notes, plans) are ignored.
