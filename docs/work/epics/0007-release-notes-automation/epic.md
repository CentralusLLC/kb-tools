---
type: Epic
id: "0007"
title: "Release notes automation"
description: "Automate the release-notes process: cut a release from Unreleased and record deployments."
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
  at: 2026-11-05T06:36:56Z
---

# Epic 0007: Release notes automation

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

Cutting a release and recording deployments are manual edits to several files (move entries, reset Unreleased, update the release index, add deployment rows), which agents and people get wrong.

## Outcome and success measures

`kb release cut <version>` and `kb release deploy <version> <environment>` make those edits, and kb check validates release pages.

## Scope

Two commands, validation of release pages, MCP tools.

## Non-goals

Publishing to GitHub Releases or Jira versions (could follow epic 0001).

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
