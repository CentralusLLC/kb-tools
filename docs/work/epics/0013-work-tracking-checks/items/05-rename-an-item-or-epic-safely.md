---
type: Work Item
id: "0013-05"
epic: "0013"
title: "Rename an item or epic safely"
description: "Add kb work rename, which renames an item or epic file and updates links to it, the roadmap and the catalog."
tags: [work-item]
status: draft
kind: story
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

# 0013-05: Rename an item or epic safely

Part of [epic 0013](../epic.md) ([plan](../plan.md)).

## What and why

Renaming an item file by hand breaks links and the catalog until `kb catalog --write` runs
(finding 11). `kb work set` already regenerates the roadmap and catalog; renaming should be just
as safe.

## Acceptance criteria

- [x] `kb work rename ID --slug SLUG [--title TITLE]` renames an item file or epic folder,
      keeps the id, updates the title if given, rewrites relative Markdown links to it in
      `docs/`, and regenerates the roadmap and catalog.
- [x] A `kb_work_rename` MCP tool does the same.
- [x] `kb check` is clean after a rename; tests cover items and epics, and pass.
- [x] Work-tracking docs describe it.

## Notes

Depends on 0013-04 for the slug rules.
