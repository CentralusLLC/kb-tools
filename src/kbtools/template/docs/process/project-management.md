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

## Planning

> TODO: Where the roadmap lives (a page here, or issues in a tracker linked from here).

## Work tracking

> TODO: System of record for tasks, workflow states, and how tasks link to pull requests.

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
