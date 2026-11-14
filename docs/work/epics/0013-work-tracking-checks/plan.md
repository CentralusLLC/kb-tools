---
type: Implementation Plan
epic: "0013"
title: "Plan: Work tracking checks"
description: "How epic 0013 will be delivered: approach, design, risks and sequencing of its items."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T20:13:07Z
---

# Plan: Work tracking checks

## Approach

Every change goes into the existing modules: checks into `work.validate` (so `kb check`, the
MCP `kb_check` tool and CI all get them), options into `kb work` in `cli.py` and the matching
`kb_work_*` MCP tools. New checks are **warnings**, not errors: they point at likely drift, and
there are legitimate exceptions (an item delivered over several pull requests). `kb check --strict`
already turns warnings into failures for projects that want that.

Merged pull requests are found **offline**, from the local git history, not the GitHub API:
GitHub squash merges are titled `[NNNN-NN] Title (#N)` and merge commits
`Merge pull request #N from owner/NNNN-NN-slug`, both by our naming rules. This needs no
network, token or new dependency, and works for any host that keeps those titles. Where `git`
or `.git` is missing (the `kb-tools` runtime image has no git), the check is skipped silently.
Comparing with the tracker's own state stays in [0001-04](../0001-tracker-sync/items/04-drift-report-from-trackers.md);
these links (`links.github`) are what 0001-04 will read.

Alternatives considered: calling the GitHub API (needs network and a token in a container
that runs with `--network none`); errors instead of warnings (would block multi-PR items).

## Design

| Finding | Item | Change |
| --- | --- | --- |
| 7 | 0013-01 | `kb work set ID STATUS --pr URL\|#N` and `--github/--jira/--paperclip VALUE` write `links`; `kb check` warns about `backlog`/`todo`/`in_review` items with a merged pull request in the git history |
| 8 | 0013-02 | `kb check` warns about `done` items with `- [ ]` in Acceptance criteria; `kb work set ... done` prints the same warning |
| 9, 21 | 0013-03 | `new-item`/`new-epic --description` and link options; `kb check` warns about a TODO description or `> TODO` placeholder on started work |
| 10 | 0013-04 | Slugs cut at the last word boundary within 48 characters; `--slug` on `new-item`/`new-epic` |
| 11 | 0013-05 | `kb work rename ID --slug S [--title T]` moves the file or folder, rewrites relative links to it, and regenerates the roadmap and catalog |
| 12 | 0013-06 | Work-tracking page and template explain `status`; `kb work set` marks a closed item or epic `stable` |
| 13 | 0013-07 | `kb check` warns about an open epic whose items are all closed, and about gaps in item numbers |
| 15 | 0013-08 | Template pages mark Paperclip-specific sections optional |

"Started work" (0013-03) means items `in_progress`, `in_review` or `done`, and epics
`in_progress` or `done`. An epic's Retrospective placeholder is exempt until the epic is done
(the existing retrospective check covers that).

## Items and sequencing

Items live in [items/](items/), one file each. Order, as set by Chief in CEN-50:

1. 0013-01, 0013-02, 0013-03: the checks that hurt in practice. 0013-03 also fills in the TODO
   placeholders in kb-tools' own epic 0010 pages, so `kb check` on kb-tools stays clean.
2. 0013-04 to 0013-07, in order (0013-05 builds on 0013-04's `--slug`).
3. 0013-08, docs only.

One pull request into `dev` per item, or small groups, each updating its item's `work_status`.

## Risks and open questions

- The merged-PR heuristic depends on GitHub's default squash and merge titles. Projects that
  rename squash commits lose the warning, but never get a false one.
- New warnings show up in existing projects on upgrade (gameworld will see some). That is the
  point, and each message says how to fix it.
- kb-tools' own 0010-12 and 0010-13 are `in_review` with merged pull requests; the new check
  will flag them, and Chief decides whether they are done.

## Verification

Unit tests per check and option in `tests/test_kb.py`, using temporary repositories (with a
real `git init` for 0013-01); `python -m pytest -q` in the kb-tools dev container; `kb check`
on kb-tools and on a fresh `kb scaffold` after each item.
