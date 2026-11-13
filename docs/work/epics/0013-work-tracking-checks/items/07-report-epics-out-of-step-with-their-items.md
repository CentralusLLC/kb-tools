---
type: Work Item
id: "0013-07"
epic: "0013"
title: "Report epics out of step with their items"
description: "Warn in kb check about open epics whose items are all closed, and about skipped item ids."
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
  at: 2026-11-13T20:13:10Z
---

# 0013-07: Report epics out of step with their items

Part of [epic 0013](../epic.md) ([plan](../plan.md)).

## What and why

Nothing reports an epic that is `in_progress` with every item done, or a skipped item id
(gameworld has no 0001-02 item; finding 13).

## Acceptance criteria

- [ ] `kb check` warns about a `planned` or `in_progress` epic with at least one item, all `done`
      or `cancelled`.
- [ ] `kb check` warns about gaps in an epic's item numbers (ids are never reused; cancel
      instead of deleting).
- [ ] Tests cover both, and pass.

## Notes

Unmerged branches for missing items (gameworld's `0001-02-import-domain-knowledge`) are out of
scope: the gap warning already points at them.
