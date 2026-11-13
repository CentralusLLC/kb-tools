---
type: Process
title: Project management
description: "How {{PROJECT}} work is planned, tracked and prioritised, and the roles of people and agents."
tags: [process, planning]
status: draft
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Project management

## Planning and tracking

Work is planned and tracked in the repository: the [roadmap](../work/index.md) and its
epics, plans and items, following [Work tracking](work-tracking.md). Outside trackers mirror it.

## Stakeholders and decision rights

| Person or role | Interest | Decides or approves |
| --- | --- | --- |
| TODO (owner) | | Scope, priorities, epic acceptance |

Epics name their accepting stakeholder in their Acceptance section.

## Agents

Every agent working on this project:

- follows [Agent workflow](agent-workflow.md);
- treats this knowledge base as the source of truth, and agent memory as working context
  ([Knowledge base maintenance](knowledge-base.md));
- proposes knowledge base changes by pull request, and runs `kb check` first;
- uses kb-tools for ingestion and checks, not one-off scripts: `tools/kb` in project containers, the
  `kb_*` MCP tools only for agents on the Paperclip machine.

> TODO: List the agents (or agent platform company), their roles and permissions.

## Cadence

- **Retrospectives:** every epic closes with one (in `epic.md`). A project retrospective runs
  periodically, reviews the epic retrospectives and process pages, and turns repeated lessons
  into changes to process pages or new work items.

> TODO: Milestones, check-ins, retrospective frequency, and how priorities are set.
