---
type: Work Item
id: "0012-01"
epic: "0012"
title: "Document the dev-branch workflow"
description: "AGENTS.md and the process pages describe the dev-branch workflow: branch from and PR into dev, Chief merges, dev to main releases need board approval."
tags: [work-item]
status: draft
kind: chore
work_status: done
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-15"
generated: 
  by: paperclip/kb-tools-developer
  at: 2026-11-06T15:37:21Z
---

# 0012-01: Document the dev-branch workflow

Part of [epic 0012](../epic.md) ([plan](../plan.md)).

## What and why

The board approved a new branch model (Paperclip CEN-12): `dev` is the integration branch
and GitHub default, and `main` is the release branch. `dev` already exists and is the default.
The instructions still described one default branch with no merge or release rules, so
agents need them updated before the next pull request.

## Acceptance criteria

- [x] No instruction in the repository tells agents to branch from, open pull requests into,
  or push to `main` for normal work.
- [x] `AGENTS.md` says: branch from `dev`, open pull requests into `dev`, Chief merges,
  `dev` → `main` releases need board approval, and lists when Chief escalates to the board.
- [x] The process pages give the full rules: Chief's merge conditions, the escalation list,
  sent-back pull requests, releases and deployment.
- [x] Docs only; `tools/kb check` passes.

## Notes

Paperclip CEN-15, from the CEN-12 plan approved by the board. Protecting `main` is deferred
(GitHub Free). The scaffold template is unchanged: it doesn't prescribe a branch model.
