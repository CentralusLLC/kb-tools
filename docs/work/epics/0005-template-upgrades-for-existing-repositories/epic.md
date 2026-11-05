---
type: Epic
id: "0005"
title: "Template upgrades for existing repositories"
description: "Let repositories scaffolded from an older template see and adopt template changes without overwriting their own edits."
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
  at: 2026-11-05T06:36:47Z
---

# Epic 0005: Template upgrades for existing repositories

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

kb scaffold never overwrites, which protects project edits but means template improvements (new sections, changed process pages) reach existing repositories only by hand, as happened with gameworld.

## Outcome and success measures

- Each scaffolded repository records the template version it came from.
- `kb scaffold --diff` lists new template files and shows changes to template pages since that version, for a person or agent to merge.

## Scope

A template version stamp, a diff command, and an upgrade guide.

## Non-goals

Automatic merging into edited pages.

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
