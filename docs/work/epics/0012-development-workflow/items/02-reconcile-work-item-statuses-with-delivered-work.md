---
type: Work Item
id: "0012-02"
epic: "0012"
title: "Reconcile work-item statuses with delivered work"
description: "Make every epic and item status in docs/work match what is actually done, checked against code, merged pull requests and Paperclip tasks."
tags: [work-item]
status: draft
kind: chore
work_status: done
priority: high
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-33"
generated: 
  by: paperclip/kb-tools-developer
  at: 2026-11-12T22:10:52Z
---

# 0012-02: Reconcile work-item statuses with delivered work

Part of [epic 0012](../epic.md) ([plan](../plan.md)).

## What and why

The board wants `docs/work/` on `dev` to be the source of truth for what is done (CEN-12,
comment of 2026-11-12). Chief found epics with every item done still `in_progress`, and
epic 0010 items left `in_progress` after their work finished.

## Acceptance criteria

- [x] Every epic and item status is checked against the code on `dev`, merged pull requests
      and Paperclip tasks (CEN-5, CEN-6, CEN-8, CEN-10, CEN-11, CEN-15, CEN-23).
- [x] Completed epics 0011 and 0012 are closed, with acceptance and retrospective recorded.
- [x] Every 0010 item that isn't done says what remains.
- [x] `tools/kb check` passes; `docs/work/index.md` and `docs/catalog.md` are regenerated.

## Notes

Changes (2026-11-12):

| Item | Old | New | Evidence |
| --- | --- | --- | --- |
| 0010-03 | in_progress | done | Deployed since 2026-11-05 and used by Chief through Paperclip (CEN-5, CEN-11) |
| 0010-05 | in_progress | done | CEN-6 done: 18 tests passed in `devenv-kb-tools`, commit `0df7159` pushed back |
| 0010-06 | in_progress | blocked | "Ask first" set but bypassed by Paperclip (CEN-8, backlog) |
| 0010-07 | in_progress | todo | Template files on `dev`; the scaffold test is missing and nobody is working on it |
| 0010-08 | in_progress | done | Template workflow rule and create steps; gameworld environment created (CEN-11) |
| 0011 | in_progress | done | Only item 0011-01 done (PR #2, CEN-10) |
| 0012 | in_progress | done | 0012-01 done (PR #4, CEN-15), 0012-02 (this item) |

Unchanged after checking: epics 0001–0009 (`proposed`, no implementation on `dev`), 0010
(`in_progress`), 0010-01, -02, -04, -14 (`done`), 0010-09 (`backlog`), and 0010-10..13
(`todo`; PR #3 only planned them, and there is no LICENSE yet).
