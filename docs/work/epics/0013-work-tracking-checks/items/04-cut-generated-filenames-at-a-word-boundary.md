---
type: Work Item
id: "0013-04"
epic: "0013"
title: "Cut generated filenames at a word boundary"
description: "Cut generated epic and item filenames at a word boundary, and add a --slug option."
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

# 0013-04: Cut generated filenames at a word boundary

Part of [epic 0013](../epic.md) ([plan](../plan.md)).

## What and why

Filenames are cut at 48 characters mid-word, for example `06-validate-kb-tools-as-an-add-on-development-proce.md`
and this epic's own `01-link-items-to-pull-requests-and-report-merged-bu.md` (finding 10).

## Acceptance criteria

- [x] Generated slugs are cut at the last word boundary within the length limit.
- [x] `new-item` and `new-epic` (and their MCP tools) take `--slug`.
- [x] Existing files are not renamed by this item (0013-05 adds the safe way).
- [x] Tests cover both, and pass.
