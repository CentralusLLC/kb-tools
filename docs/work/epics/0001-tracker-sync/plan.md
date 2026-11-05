---
type: Implementation Plan
epic: "0001"
title: "Plan: Tracker sync"
description: "Draft plan for epic 0001: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:30Z
---

# Plan: Tracker sync

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

One `kb work sync --tracker <name>` command per tracker, sharing a core that computes the desired external state from the work tree (title, short description linking the item file, labels, parent, open or closed) and applies a minimal diff. External IDs go back into `links` through a commit the caller makes. `kb work pull` reads trackers and prints drift as a Markdown or JSON report.

## Design

Adapters per tracker behind a small interface (find, create, update, close, read status). GitHub through `gh` or its REST API with a token; Paperclip through its REST API (projects, issues, parent issues, `workspace_file` work products); Jira through its REST API with an API token and the `status_map` in `trackers.yaml`. Credentials come from the environment, never files in the repository. The MCP server exposes sync to agents only if credentials are configured in the sidecar.

## Items and sequencing

0001-05 (config validation) first, then GitHub (0001-01), the simplest; then the drift report (0001-04) on GitHub; then Paperclip (0001-02); Jira (0001-03) last, only when a project needs it.

## Risks and open questions

- Rate limits and partial failures: make sync idempotent and resumable.
- Paperclip's API is large and evolving: pin to tested endpoints.
- Writing IDs back creates commits: decide whether CI commits them or the person running sync does.

## Verification

Sync a test repository to a sandbox GitHub repository and a Paperclip test project; running sync twice changes nothing; closing an item closes its issue.
