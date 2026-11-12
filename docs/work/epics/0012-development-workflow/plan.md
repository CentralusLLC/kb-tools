---
type: Implementation Plan
epic: "0012"
title: "Plan: Development workflow"
description: "How epic 0012 will be delivered: approach, design, risks and sequencing of its items."
tags: [plan]
status: draft
generated: 
  by: paperclip/kb-tools-developer
  at: 2026-11-06T15:37:20Z
---

# Plan: Development workflow

## Approach

Write the branch model down where agents read it: a short summary in `AGENTS.md` (which
`CLAUDE.md` includes), and the full rules in [Development](../../../process/development.md#branches-and-pull-requests),
with [Work tracking](../../../process/work-tracking.md#lifecycle) and
[Agent workflow](../../../process/agent-workflow.md) pointing to it.

GitHub branch protection would enforce "never push to `main`", but the organisation is on
GitHub Free, where private repositories can't protect branches. Until then the rule is
written, not enforced.

## Design

Docs only: `AGENTS.md`, `docs/process/development.md`, `docs/process/work-tracking.md`,
`docs/process/agent-workflow.md`, `docs/process/release-notes.md`.

## Items and sequencing

Items live in [items/](items/), one file each. Create them with
`tools/kb work new-item 0012 "Title"`. 0012-01 is the only item so far.

## Risks and open questions

- `main` is unprotected, so a mistaken push isn't blocked. Mitigation: the rule appears in
  `AGENTS.md`, which every agent reads first.
- No CI yet, so Chief relies on the developer's test report (epic 0004 adds checks).

## Verification

`tools/kb check` passes, a search finds no instruction that points normal work at `main`, and
this epic's own pull request is the first one merged into `dev` under the new rules.
