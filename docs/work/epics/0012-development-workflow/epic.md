---
type: Epic
id: "0012"
title: "Development workflow"
description: "How changes reach kb-tools: branches, pull requests, who merges, and how releases reach main."
tags: [epic]
status: draft
work_status: in_progress
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
- Later, as items: protect `main` once the GitHub plan allows it; CI checks for the merge
  rules (with epic 0004).

## Non-goals

- Deployment: deploying a release stays a separate board approval.
- The scaffold template (`src/kbtools/template/`): projects choose their own branch model.

## Acceptance

The board accepts, by reviewing the merged instructions and the first pull requests that
follow them. Record the acceptance here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
