---
type: Epic
id: "0001"
title: "Tracker sync"
description: "Mirror repository epics and items to GitHub Issues, Paperclip and Jira one way, and report drift back for triage."
tags: [epic]
status: draft
work_status: proposed
priority: high
owner: ""
target: ""
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:30Z
---

# Epic 0001: Tracker sync

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

Projects use outside trackers for assignment, notifications and live progress, but plans and items live in the repository (ADR 0004). Today external issues are created and closed by hand, so they drift and IDs are not written back.

## Outcome and success measures

- Every epic and item with `links` configured has a matching external issue, created and updated automatically after merges.
- External IDs are written back into `links`.
- Drift (tracker says blocked, issues filed outside the repo) appears in a report, never as silent edits.
- Measure: zero hand-maintained external issues in projects that enable sync.

## Scope

GitHub Issues (with sub-issues or labels), Paperclip issues (parent and child, planning mode), Jira (epics and stories); a drift report; validation of `docs/work/trackers.yaml`.

## Non-goals

Two-way sync of scope or status; syncing comments; replacing tracker workflows.

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
