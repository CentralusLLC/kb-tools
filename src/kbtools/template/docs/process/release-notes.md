---
type: Process
title: Release notes
description: "How {{PROJECT}} release notes are written as work items complete, cut into versioned releases, and updated as each release is deployed to each environment."
tags: [process, releases, changelog, deployment]
status: stable
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Release notes

Release notes live in [`docs/releases/`](../releases/index.md), next to the work they
describe, so every person and agent sees what shipped and where.

## 1. When a work item is completed

The pull request that sets an item to `done` ([Work tracking](work-tracking.md#lifecycle))
also adds one line to [Unreleased](../releases/unreleased.md), under the right heading:

| Heading | For |
| --- | --- |
| Added | New capabilities |
| Changed | Changes to existing behaviour |
| Fixed | Bug fixes |
| Deprecated | Things that will be removed |
| Removed | Things that were removed |
| Security | Vulnerability fixes and security-relevant changes |

Format: `- [NNNN-NN] What changed, in the user's words. (#PR)`.

Example: `- [0007-02] New accounts must verify their email before signing in. (#41)`.
Internal-only changes (refactoring, tests, tooling) get no entry unless users or operators notice them.
By [item kind](work-tracking.md#item-kinds): `bug` goes under Fixed, `spike` gets no entry, and
`chore` gets one only if users or operators notice.

## 2. When a release is cut

1. Choose the version (semantic versioning: breaking changes raise the major number, new
   features the minor number, fixes the patch number) and create `releases/vX.Y.Z.md`
   (`type: Release Notes`, `version`, `released_at`).
2. Move every entry from Unreleased into it. Add a two- or three-sentence summary at the
   top, plus upgrade or migration notes if any. Reset Unreleased to its empty headings.
3. Add the release to the top of the table in [releases/index.md](../releases/index.md).
4. Tag the commit `vX.Y.Z`.

## 3. When a release is deployed

Each release page has a **Deployments** table. Add a row every time the release reaches an
environment (see [Environments](../environments/index.md) and [Operations](operations.md)):

| Environment | Date | Deployed by | Commit or tag | Notes |
| --- | --- | --- | --- | --- |
| staging | 2026-01-20 | ci | v1.4.0 | |
| production | 2026-01-22 | human:alex | v1.4.0 | |

A rollback is a new row with a note, not a deletion. The newest production row tells anyone,
person or agent, what is live.

## Outside systems

GitHub Releases, Jira versions or a public changelog are copies made from these pages
when a release is cut. They are never the place where notes are first written.

> TODO: Who cuts releases, how often, and where release notes are published.
