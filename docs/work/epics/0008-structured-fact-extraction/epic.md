---
type: Epic
id: "0008"
title: "Structured fact extraction"
description: "Optional schema-driven fact extraction from extraction packages with LangExtract, using the local model by default."
tags: [epic]
status: draft
work_status: proposed
priority: low
owner: ""
target: ""
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:37:00Z
---

# Epic 0008: Structured fact extraction

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

Repeated facts (parties, dates, metrics) across many documents are extracted by hand into data/. An earlier project's LangExtract tool showed grounded extraction helps, but it is not in kb-tools.

## Outcome and success measures

`kb facts` runs a profile over extraction packages and writes grounded facts (with source offsets) for review and conversion into datasets.

## Scope

The command, profiles, output format, and local-model defaults.

## Non-goals

Unreviewed automatic writes to data/.

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
