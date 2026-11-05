---
type: Process
title: Project management
description: "How kb-tools work is planned and prioritised, who decides, and how agents take part."
tags: [process, planning]
status: stable
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Project management

## Planning and tracking

Work is planned and tracked in this repository: the [roadmap](../work/index.md) and its
epics, plans and items, following [Work tracking](work-tracking.md). Epics recorded on
2026-11-05 capture the direction discussed while building v0.1.0; they are `proposed` and
not ready for development until planned.

## Stakeholders and decision rights

| Person or role | Interest | Decides or approves |
| --- | --- | --- |
| Owner (CentralusLLC) | Direction, conventions across all projects | Scope, priorities, epic acceptance |

## Agents

Every agent working on this project follows [Agent workflow](agent-workflow.md), plans in
`docs/work/`, and runs the tests in Docker before a pull request ([Testing](testing.md)).

## Cadence

- **Retrospectives:** every epic closes with one (in `epic.md`); a project retrospective runs
  periodically and turns repeated lessons into process changes or work items.

> TODO: Release cadence and how priorities are set.
