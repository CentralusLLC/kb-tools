---
type: Epic
id: "0003"
title: "Paperclip ingestion end to end"
description: "Make document ingestion work end to end for Paperclip agents: MCP connection, repository workspace, review packet, and a real trial."
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
  at: 2026-11-05T06:36:39Z
---

# Epic 0003: Paperclip ingestion end to end

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

The kb-tools sidecar runs next to Paperclip, but no agent has used it: the MCP connection and tool policy are not set up, no Paperclip project has a repository workspace, and the review packet step is manual.

## Outcome and success measures

- A Paperclip agent ingests a real document from an issue attachment into a project repository, opens a pull request, and attaches a review packet, using only kb_* tools.
- Measure: one successful trial on gameworld with no manual steps beyond approving the pull request.

## Scope

Connection and policy setup, a project workspace, a review-packet command, the trial, and the documentation updates it reveals.

## Non-goals

Changes to Paperclip itself; automating issue creation (see epic 0001).

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
