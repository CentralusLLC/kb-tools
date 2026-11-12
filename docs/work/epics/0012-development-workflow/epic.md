---
type: Epic
id: "0012"
title: "Development workflow"
description: "How changes reach kb-tools: branches, pull requests, who merges, and how releases reach main."
tags: [epic]
status: draft
work_status: done
priority: medium
owner: ""
target: ""
links: 
  github: ""
  jira: ""
  paperclip: "CEN-12"
generated: 
  by: paperclip/kb-tools-developer
  at: 2026-11-06T15:37:20Z
---

# Epic 0012: Development workflow

## Problem / business need

Several agents now open pull requests in kb-tools, and the board was the only one merging
them, straight into `main`. Every change waited for the board, and `main` held unreleased
work. The board approved a new branch model (Paperclip CEN-12): `dev` is the integration
branch and GitHub default, Chief merges work pull requests into it, and `main` becomes the
release branch, changed only by board-approved `dev` → `main` release pull requests.

## Outcome and success measures

Every agent follows the same flow, because the repository's instructions describe it: work
pull requests target `dev` and are merged by Chief, and `main` changes only through approved
release pull requests. Measured by: no instruction in the repository points normal work at
`main`, and work pull requests merge into `dev` without the board.

## Scope

- [0012-01](items/01-document-the-dev-branch-workflow.md): document the dev-branch workflow in
  `AGENTS.md` and the process pages.
- [0012-02](items/02-reconcile-work-item-statuses-with-delivered-work.md): reconcile work-item
  statuses with delivered work.
- Moved out at closing: protecting `main` (see [0002-04](../0002-image-distribution-and-versioning/items/04-kb-tools-release-process.md))
  and CI checks for the merge rules ([0004-02](../0004-continuous-integration-for-project-repositories/items/02-definition-of-done-checks-for-pull-requests.md)).

## Non-goals

- Deployment: deploying a release stays a separate board approval.
- The scaffold template (`src/kbtools/template/`): projects choose their own branch model.

## Acceptance

The board accepts, by reviewing the merged instructions and the first pull requests that
follow them.

Checked on 2026-11-12: the instructions were merged into `dev` (PR #4, 0012-01). Later work
followed them: [0010-14](../0010-agent-dev-environments/items/14-kb-cli-available-inside-project-dev-containers.md)
went into `dev` (PR #5), and `main` changed only through the release pull request PR #6.
No instruction points normal work at `main`. The board asked for completed epics to be
closed (CEN-12, CEN-33); closed in [0012-02](items/02-reconcile-work-item-statuses-with-delivered-work.md).

## Retrospective

- Worked: a docs-only change was enough. Agents read `AGENTS.md` and followed the new flow
  from the next pull request on.
- Didn't: statuses drifted. Items were merged without their epics being closed, and
  in-progress items weren't updated when the work finished outside the repository
  (Paperclip runs and deployments). 0012-02 cleaned this up.
- Actions: protecting `main` is noted on [0002-04](../0002-image-distribution-and-versioning/items/04-kb-tools-release-process.md)
  (possible once the repository is public, after 0010-10..12); CI checks for the merge
  rules are [0004-02](../0004-continuous-integration-for-project-repositories/items/02-definition-of-done-checks-for-pull-requests.md).

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
