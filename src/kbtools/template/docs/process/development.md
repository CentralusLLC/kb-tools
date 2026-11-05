---
type: Process
title: Development process
description: "Branching, pull requests, code layout, testing and coding standards for {{PROJECT}}."
tags: [process, development, git]
status: draft
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Development process

## Repository layout

| Path | Purpose |
| --- | --- |
| `docs/` | Knowledge base (this bundle) |
| `data/` | Structured research data ([Research data](../architecture/research-data.md)) |
| `tools/` | Scripts for agents and people ([tools/README.md](../../tools/README.md)) |
| `extracted/` | Working extraction output (git-ignored) |

> TODO: Add the code layout once decided (record it in an [ADR](../architecture/decisions/index.md)).

## Branches and pull requests

- One feature branch per change; open a pull request against the default branch.
- Update the knowledge base in the same pull request when behaviour, setup or rules change,
  and run `tools/kb check`.

- Branch per work item: `NNNN-NN-short-slug` (for example `0007-02-email-verification`).
- Pull request title: `[NNNN-NN] Title`. The same pull request updates the item file
  (`work_status`, acceptance criteria) and closes tracker issues (`Closes #41`).
  See [Work tracking](work-tracking.md#lifecycle).

> TODO: Commit message style, review requirements, merge strategy.

## Testing

> TODO: Test strategy and how to run the tests.

## Coding standards

> TODO: Languages, formatters, linters, conventions.
