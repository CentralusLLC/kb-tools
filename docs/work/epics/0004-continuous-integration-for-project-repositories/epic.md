---
type: Epic
id: "0004"
title: "Continuous integration for project repositories"
description: "Run kb check and definition-of-done checks in project repositories' CI so conventions are enforced on every pull request."
tags: [epic]
status: draft
work_status: proposed
priority: medium
owner: ""
target: ""
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:44Z
---

# Epic 0004: Continuous integration for project repositories

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

kb check runs only when someone remembers. Stale catalogs, broken links, invalid work items or missing release-note lines can merge.

## Outcome and success measures

- A reusable GitHub Action runs kb check on every pull request in projects that opt in.
- Pull requests that complete an item without its release-note line, or that leave the catalog stale, fail with a clear message.

## Scope

A reusable action or workflow template, PR-level checks tied to the definition of done, and `kb scaffold` adding the workflow optionally.

## Non-goals

Running extraction in CI: sources are git-ignored by design (ADR 0002 in each project), so CI cannot see them.

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
