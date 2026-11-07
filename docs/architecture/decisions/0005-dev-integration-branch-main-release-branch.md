---
type: Decision Record
title: "ADR 0005: dev is the integration branch; main is the release branch"
description: "Work pull requests target dev and Chief merges them; main changes only through board-approved dev-to-main release pull requests."
tags: [adr, branching, pull-requests, releases]
status: stable
decision_status: accepted
generated:
  by: paperclip/kb-tools-developer
  at: 2026-11-06T15:45:00Z
---

# ADR 0005: dev is the integration branch; main is the release branch

## Context

Several agents open pull requests in kb-tools. Until now they all targeted `main`, and only
the board merged them, so every change waited for the board and `main` held unreleased work.
The board approved a new model in Paperclip CEN-12.

## Decision

- `dev` is the integration branch and the GitHub default. Work branches start from `dev`,
  and work pull requests target it.
- Chief merges work pull requests into `dev` (squash) when they meet the merge rules in
  [Development](../../process/development.md#branches-and-pull-requests), and escalates
  sensitive ones to the board.
- `main` is the release branch. It changes only through a `dev` → `main` release pull request
  that the board approves. Agents never push to `main` or open other pull requests into it.
- Deploying a release stays a separate board approval.

## Consequences

- Routine work merges without waiting for the board; the board reviews releases and the
  escalated cases.
- `main` always holds released code.
- `main` isn't protected yet (GitHub Free), so the rule is written, not enforced.
- Without CI, Chief relies on the developer's report that tests were run and pass.
