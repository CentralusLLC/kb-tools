---
type: Epic
id: "0006"
title: "Extraction improvements"
description: "Close the extraction gaps from the earlier extraction guide: OCR for raster pages, duplicate detection, web capture, Word tracked-change views, and better Excel rendering."
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
  at: 2026-11-05T06:36:50Z
---

# Epic 0006: Extraction improvements

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

The extraction guide calls for capabilities kb-tools does not have yet: raster-only pages produce no text, duplicate decks are not detected, web pages have no capture command, Word tracked changes are only flagged, and workbook rendering relies on LibreOffice print layout.

## Outcome and success measures

Each capability is available as part of `kb extract` or a sibling command, offline, with manifest entries recording what was done.

## Scope

Local OCR (no cloud), duplicate detection, web capture, Word markup and accepted views, an evaluation of ExStruct or Excel-native rendering.

## Non-goals

Cloud OCR or model-based image description by default.

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
