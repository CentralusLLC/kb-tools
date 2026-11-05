---
type: Epic
id: "0009"
title: "Semantic search through Hindsight"
description: "Deferred: semantic search over knowledge bases through a per-repository Hindsight bank, only when grep and the catalog fall short."
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
  at: 2026-11-05T06:37:03Z
---

# Epic 0009: Semantic search through Hindsight

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

Grep, the catalog and glossary aliases cover current wiki sizes. Semantic search may pay off for large or synonym-heavy wikis, for people asking 'things like this', and for search across all projects.

## Outcome and success measures

If the triggers are met: `kb sync-index` keeps a disposable Hindsight bank per repository in step with docs/, and agents can search it, including across repositories.

## Scope

Measurement first; then indexing and cross-repository search.

## Non-goals

A new vector database; treating the index as a source of truth.

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
