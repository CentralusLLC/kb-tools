---
type: Epic
id: "0013"
title: "Work tracking checks"
description: "Make kb check and kb work catch work-tracking drift: stale statuses, unchecked criteria, TODO placeholders, broken renames and epics out of step with their items."
tags: [epic]
status: stable
work_status: done
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

Checked on 2026-11-14: all eight items are merged into `dev`: 0013-01..03 in PR #1, 0013-04..07
in PR #5 (both merged by Chief), and 0013-08 in the pull request that closes this epic. Each of
findings 7–13 has a test in `tests/test_work_tracking.py`. `kb check` reports 0 errors and
0 warnings on a fresh scaffold, and 0 errors on kb-tools. Its one warning there is the new
merged-pull-request check doing its job: it flags 0010-17 (PR #4 merged, item still `in_review`),
which that item's own task closes. No TODO placeholders are left in kb-tools' started work pages. gameworld's re-check waits for the next kb-tools release, which also
needs the deferred MCP server redeploy.

## Retrospective

- Worked: the new checks found the same drift in kb-tools itself (0010-12 and 0010-13) as soon as
  they ran, and filling in epic 0010's placeholders proved the placeholder check on real pages.
  Grouping the items into three pull requests kept the branches from conflicting.
- Didn't: moving to the new public repository restarted pull request numbers, so links like `#8`
  became ambiguous, and the merged-pull-request check had to learn to ignore old squash titles
  (0013-01's follow-up). A squash title with no work id can still collide.
- Actions: the tracker-based report in [0001-04](../0001-tracker-sync/items/04-drift-report-from-trackers.md)
  replaces the git-history guess once trackers sync; CI should run `kb check` on pull requests
  ([0004-02](../0004-continuous-integration-for-project-repositories/items/02-definition-of-done-checks-for-pull-requests.md)).
  No new items.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
- Source: gameworld `docs/environments/kb-tools-feedback.md`, findings 7–13, 15 and 21
