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

## Agents

Every agent working on this project:

- follows [Agent workflow](agent-workflow.md);
- treats this knowledge base as the source of truth, and agent memory as working context
  ([Knowledge base maintenance](knowledge-base.md));
- proposes knowledge base changes by pull request, and runs `kb check` first;
- uses kb-tools (`tools/kb` or the `kb_*` MCP tools) for ingestion, not one-off scripts.

> TODO: List the agents (or agent platform company), their roles and permissions.

## Cadence

> TODO: Milestones, check-ins, and how priorities are set.
