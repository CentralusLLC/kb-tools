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

Code follows one of two common layouts. Choose one in an ADR:

- **One deployable app:** `src/` for code and `tests/` for its tests.
- **Several apps (monorepo):** `apps/<app>/src/` and `apps/<app>/tests/` per app,
  `packages/<pkg>/` for shared code, and a top-level `tests/` for cross-app tests.

| Path | Purpose |
| --- | --- |
| `src/` + `tests/`, or `apps/` + `packages/` + `tests/` | Code and tests ([Testing](testing.md)) |
| `.devcontainer/` | The dev environment for people and agents ([Dev environment](../environments/dev-environment.md)) |
| `docs/` | Knowledge base (this bundle), including user documentation in `docs/user/` |
| `data/` | Structured research data ([Research data](../architecture/research-data.md)) |
| `tools/` | Scripts for agents and people ([tools/README.md](../../tools/README.md)) |
| `extracted/` | Working extraction output (git-ignored) |

> TODO: Record the chosen layout in an [ADR](../architecture/decisions/index.md).

## Documentation

- Internal knowledge (how the system works, why, how we work) goes in the knowledge base.
- **User-facing documentation** (guides, how-tos, reference) goes in [`docs/user/`](../user/index.md),
  and is updated in the same pull request as the change users will notice.
- API reference generated from code is published from the code. Link to it from `docs/user/`.

## Branches and pull requests

- One feature branch per change; open a pull request against the default branch.
- Update the knowledge base in the same pull request when behaviour, setup or rules change,
  and run `tools/kb check`.

- Branch per work item: `NNNN-NN-short-slug` (for example `0007-02-email-verification`).
- Pull request title: `[NNNN-NN] Title`. The same pull request updates the item file
  (`work_status`, acceptance criteria) and closes tracker issues (`Closes #41`).
  See [Work tracking](work-tracking.md#lifecycle).

- Every pull request meets the [definition of done](work-tracking.md#definition-of-done).
  The pull request template repeats it as a checklist.

## Code review

- Reviewers check the definition of done, readability, test quality, security
  ([Security](security.md)), and whether the knowledge base and user docs match the change.
- An agent may review another agent's pull request. Changes to authentication, authorisation,
  cryptography, payments or data deletion need a human reviewer.

> TODO: Commit message style, required approvals, merge strategy.

## Testing and security

Every change follows [Testing](testing.md) and [Security](security.md).

## Coding standards

> TODO: Languages, formatters, linters, conventions.
