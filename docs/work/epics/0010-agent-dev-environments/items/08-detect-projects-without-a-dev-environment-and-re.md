---
type: Work Item
id: "0010-08"
epic: "0010"
title: "Detect projects without a dev environment and request one"
description: "Agents notice when their project has no working dev environment and get one created through the devenv manager, instead of skipping tests."
tags: [work-item]
status: draft
kind: story
work_status: done
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-11"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:37Z
---

# 0010-08: Detect projects without a dev environment and request one

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

A project scaffolded by kb-tools may have no dev container yet. Agents must not respond by
skipping tests or relying on outside CI; they should get the environment created. The epic plan
chose to do this through the agent workflow rule, not an automatic check.

## Acceptance criteria

Written on 2026-11-12 from the epic plan's scope ("through the agent workflow rule"), when the
item was reconciled (0012-02); the original file had none.

- [x] The template's agent workflow says to run tests in the project's dev environment and, if
      that isn't possible, to get it fixed or created instead of skipping tests
      (`src/kbtools/template/docs/process/agent-workflow.md`, "While working").
- [x] The template's dev-environment page ("No environment yet?") lists the steps: a key pair,
      a secret proposal, `devenv_create`, `devenv_status`, environment registration, then
      `devenv_rebuild`.
- [x] Proven on a second project: gameworld got its dev container through `devenv_create` and
      was rebuilt from its own `.devcontainer/` (Paperclip CEN-5, CEN-11, 2026-11-05).

## Notes

An automatic check, such as `kb check` warning when `.devcontainer/` is missing, was not in the
plan. Add it as a new item if agents miss the rule in practice.
