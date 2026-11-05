---
type: Process
title: Operations
description: "Release, deployment, monitoring, incident and access processes for {{PROJECT}}."
tags: [process, operations, release]
status: draft
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Operations

> TODO: Fill in once [environments](../environments/index.md) exist.

## Releases

Versioning, release notes and the record of what is deployed where:
[Release notes](release-notes.md) and [releases/](../releases/index.md).

> TODO: Release checklist (beyond release notes).

## Deployments

> TODO: How each environment is deployed, by whom or what, and how to roll back. Every
> deployment adds a row to the release's Deployments table ([Release notes](release-notes.md#3-when-a-release-is-deployed)).

## Monitoring and alerting

> TODO: What is monitored, where alerts go, service levels.

## Incidents

> TODO: Severity levels, response steps, post-incident review.

## Secrets and access

See [Security](security.md). Never put secrets in this knowledge base.
