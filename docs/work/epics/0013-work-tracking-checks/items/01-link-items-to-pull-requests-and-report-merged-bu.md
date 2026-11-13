---
type: Work Item
id: "0013-01"
epic: "0013"
title: "Link items to pull requests and report merged but open items"
description: "Record a pull request and tracker links on an item with kb work set, and warn when an item's pull request has merged but the item is not done."
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
  at: 2026-11-13T20:13:07Z
---

# 0013-01: Link items to pull requests and report merged but open items

Part of [epic 0013](../epic.md) ([plan](../plan.md)).

## What and why

gameworld items 0001-05 and 0002-11..13 stayed `in_review` after their pull requests (#8, #9)
merged, and `kb check` was clean (finding 7). Nothing links an item to its pull request:
`kb work set` can't record one, so `links.github` stays empty.

## Acceptance criteria

- [ ] `kb work set ID STATUS --pr URL` (or `#N`) records the pull request in `links.github`;
      `--github`, `--jira` and `--paperclip` set those links on items and epics.
- [ ] The `kb_work_set` MCP tool takes the same links.
- [ ] `kb check` warns about a `backlog`, `todo` or `in_review` item whose pull request is merged
      in the local git history (squash title `[NNNN-NN] ... (#N)` or a merge commit from
      branch `NNNN-NN-...`); no warning without git.
- [ ] Tests cover the options and the warning (with a real `git init`), and pass.
- [ ] Work-tracking docs (kb-tools and template) and the user guide describe both.

## Notes

`in_progress` and `blocked` items are not flagged: an item can take several pull requests
(0010-10 took #11 and #15). The tracker-based drift report stays in
[0001-04](../../0001-tracker-sync/items/04-drift-report-from-trackers.md).
