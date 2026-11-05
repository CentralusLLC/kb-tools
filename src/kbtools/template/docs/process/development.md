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
| `apps/<app>/src/`, `apps/<app>/tests/` | Each application's code and its tests ([Testing](testing.md)) |
| `tests/` | Cross-app tests: end-to-end, contract, smoke |
| `docs/` | Knowledge base (this bundle) |
| `data/` | Structured research data ([Research data](../architecture/research-data.md)) |
| `tools/` | Scripts for agents and people ([tools/README.md](../../tools/README.md)) |
| `extracted/` | Working extraction output (git-ignored) |

> TODO: Confirm the code layout, or replace the default above, in an [ADR](../architecture/decisions/index.md).

## Branches and pull requests

- One feature branch per change; open a pull request against the default branch.
- Update the knowledge base in the same pull request when behaviour, setup or rules change,
  and run `tools/kb check`.

- Branch per work item: `NNNN-NN-short-slug` (for example `0007-02-email-verification`).
- Pull request title: `[NNNN-NN] Title`. The same pull request updates the item file
  (`work_status`, acceptance criteria) and closes tracker issues (`Closes #41`).
  See [Work tracking](work-tracking.md#lifecycle).

> TODO: Commit message style, review requirements, merge strategy.

## Testing and security

Every change follows [Testing](testing.md) and [Security](security.md).

## Coding standards

> TODO: Languages, formatters, linters, conventions.
