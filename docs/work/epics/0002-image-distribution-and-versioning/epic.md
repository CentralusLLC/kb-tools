---
type: Epic
id: "0002"
title: "Image distribution and versioning"
description: "Build, test and publish versioned multi-architecture kb-tools images so projects stop building the image locally and pin a known version."
tags: [epic]
status: draft
work_status: proposed
priority: high
owner: ""
target: ""
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:35Z
---

# Epic 0002: Image distribution and versioning

> **Status: proposed, not ready for development.** Recorded on 2026-11-05 to capture direction
> discussed while building v0.1.0. Review the plan and set the epic to `planned` before starting.

## Problem / business need

Every machine builds the 1.6 GB image itself, and the Paperclip host is updated by copying the source over. Projects cannot pin a version, and the README's claim of an amd64 build for CI is not yet true.

## Outcome and success measures

- Tagged releases publish `ghcr.io/<owner>/kb-tools:<version>` for arm64 and amd64.
- `tools/kb` uses a pinned version and pulls it when missing.
- Measure: a fresh machine runs `tools/kb check` with only Docker installed.

## Scope

CI build and tests on both architectures, publishing to GitHub Container Registry, version pinning in the wrapper, a release process for kb-tools itself.

## Non-goals

Other registries; signing beyond what GitHub offers by default (revisit later).

## Acceptance

The owner accepts the outcome by reviewing the success measures above. To be recorded here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
