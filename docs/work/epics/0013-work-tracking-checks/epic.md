---
type: Epic
id: "0013"
title: "Work tracking checks"
description: "Make kb check and kb work catch work-tracking drift: stale statuses, unchecked criteria, TODO placeholders, broken renames and epics out of step with their items."
tags: [epic]
status: draft
work_status: in_progress
priority: high
owner: ""
target: ""
links: 
  github: ""
  jira: ""
  paperclip: "CEN-50"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T20:13:07Z
---

# Epic 0013: Work tracking checks

## Problem / business need

gameworld, the first project to use kb-tools for work tracking, found that `kb check` stays
clean while `docs/work/` drifts from reality (gameworld `docs/environments/kb-tools-feedback.md`,
findings 7–13 and 21):

- items stayed `in_review` after their pull requests merged, and nothing links an item to its
  pull request;
- items were `done` with unchecked acceptance criteria;
- `kb work new-item` leaves `TODO` placeholders that `kb check` accepts, and has no options
  for a description or tracker links, so every new item needs a manual edit;
- generated filenames are cut mid-word, and renaming a file breaks links and the catalog;
- nobody knows whether OKF `status` should change when `work_status` does;
- epics stay `in_progress` after every item is done, and skipped item ids go unnoticed.

kb-tools has the same drift itself (0010-12 and 0010-13 are `in_review` with PRs #10 and #8
merged in the old repository, now `CentralusLLC/kb-tools-private`). The repository is meant to be the source of truth for what is done (ADR 0004), so
these gaps cost every project reviews and status clean-ups (0012-02 was one). Finding 15 adds a
related documentation gap: the templates describe Paperclip as if it were required.

## Outcome and success measures

`kb check` and `kb work` catch the drift above as it happens, and creating or closing an item
takes one command, with no hand edits. Measured by:

- each finding 7–13 has a check, warning or option that reproduces it in a test;
- `kb check` on kb-tools and on a fresh scaffold is clean after the epic, with no TODO
  placeholders left in kb-tools' in-progress and done work pages;
- gameworld's re-check of findings 7–13 and 15 on the next kb-tools release finds them fixed.

## Scope

- [0013-01](items/01-link-items-to-pull-requests-and-report-merged-bu.md): record pull requests
  and tracker links on items; warn about items whose pull request merged but are not done (finding 7).
- [0013-02](items/02-warn-about-done-items-with-unchecked-acceptance.md): warn about done items
  with unchecked acceptance criteria (finding 8).
- [0013-03](items/03-descriptions-and-links-when-creating-items-warn.md): `--description` and
  link options on `new-item` and `new-epic`; warn about TODO placeholders on started work (findings 9, 21).
- [0013-04](items/04-cut-generated-filenames-at-a-word-boundary.md): cut filenames at a word
  boundary, and a `--slug` option (finding 10).
- [0013-05](items/05-rename-an-item-or-epic-safely.md): `kb work rename` (finding 11).
- [0013-06](items/06-explain-the-two-status-fields-of-work-items.md): explain `status` and
  `work_status` (finding 12).
- [0013-07](items/07-report-epics-out-of-step-with-their-items.md): warn about epics whose items
  are all closed, and about skipped item ids (finding 13).
- [0013-08](items/08-mark-paperclip-specific-template-parts-optional.md): mark the
  Paperclip-specific template parts optional (finding 15).

## Non-goals

- Syncing with or reading from outside trackers: that is epic 0001 (the tracker-based drift
  report is [0001-04](../0001-tracker-sync/items/04-drift-report-from-trackers.md)). This epic
  only reads the local git history.
- Redeploying the MCP server (gameworld findings 2 and 20): deploys are a separate board decision.
- Blocking merges in CI: that is [0004-02](../0004-continuous-integration-for-project-repositories/items/02-definition-of-done-checks-for-pull-requests.md).

## Acceptance

Chief accepts for the board (Paperclip CEN-50, approved in CEN-12), by reviewing the merged
pull requests and a clean `kb check` on kb-tools. gameworld's re-check of its findings confirms it.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
- Source: gameworld `docs/environments/kb-tools-feedback.md`, findings 7–13, 15 and 21
