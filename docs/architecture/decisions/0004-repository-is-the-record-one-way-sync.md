---
type: Decision Record
title: "ADR 0004: The repository is the record for work; trackers are synced one way"
description: Epics, plans, items and release notes live in the repository; GitHub, Jira and Paperclip mirror them with one-way sync, each field having one owner.
tags: [adr, work-tracking, sync, trackers]
status: stable
decision_status: accepted
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T00:00:00Z
---

# ADR 0004: The repository is the record for work; trackers are synced one way

## Context

Agents write implementation plans in Markdown anyway, and every agent sees the repository.
Projects may also use GitHub Issues, Jira or Paperclip. Two-way sync between them is where
such setups usually break down.

## Decision

- Epics (`epic.md`, `plan.md`) and items live in `docs/work/`, with permanent IDs.
- Field ownership: the repository owns scope, plans, acceptance criteria and the final state;
  trackers own the assignee, live progress and discussion.
- Sync is one way, repository to trackers, after merges; the other direction is a drift report
  for triage. External descriptions link to item files and never copy them.

## Consequences

- No conflicts over which system is right.
- Live progress is invisible in the repository until merge, by design.
- Sync is still to be built ([roadmap](../../work/index.md)).
