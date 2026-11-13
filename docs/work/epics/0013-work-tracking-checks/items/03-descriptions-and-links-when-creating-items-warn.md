---
type: Work Item
id: "0013-03"
epic: "0013"
title: "Descriptions and links when creating items; warn about TODO placeholders"
description: "Add --description and tracker-link options to kb work new-item and new-epic, and warn about TODO placeholders on work that has started."
tags: [work-item]
status: draft
kind: story
work_status: done
priority: high
depends_on: []
links: 
  github: "#1"
  jira: ""
  paperclip: "CEN-50"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T20:13:08Z
---

# 0013-03: Descriptions and links when creating items; warn about TODO placeholders

Part of [epic 0013](../epic.md) ([plan](../plan.md)).

## What and why

`kb work new-item` writes `description: "TODO: ..."` and `> TODO:` sections that `kb check`
accepts, and has no options for a description or tracker links, so every new item needs a
manual edit (findings 9 and 21).

## Acceptance criteria

- [x] `new-item` and `new-epic` take `--description`, `--github`, `--jira` and `--paperclip`;
      so do the `kb_work_new_item` and `kb_work_new_epic` MCP tools.
- [x] `kb check` warns about a TODO description or a `> TODO` placeholder on items
      `in_progress`, `in_review` or `done` and epics `in_progress` or `done` (the Retrospective
      placeholder is exempt until the epic is done).
- [x] kb-tools' own epic 0010 pages have no TODO placeholders left, and `kb check` on kb-tools
      and on a fresh scaffold is clean.
- [x] Tests cover the options and the warning, and pass.
- [x] Work-tracking docs (kb-tools and template) and the user guide describe the options.
