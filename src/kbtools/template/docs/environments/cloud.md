---
type: Environment
title: Cloud and hosted environments
description: "{{PROJECT}}'s deployment targets (for example AWS, Cloudflare, an internal server) and what each environment page must record."
tags: [environments, cloud, deployment]
status: draft
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Cloud and hosted environments

> TODO: List the environments, or note that none exist yet. Choose providers through an
> [ADR](../architecture/decisions/index.md).

## For each environment, record

Give each environment its own page (`environments/<name>.md`, `type: Environment`) covering:

- **Purpose:** dev, staging or production; what runs there.
- **Provider, account and region:** identifiers only, never credentials.
- **Resources:** services, domains, storage, databases.
- **Deploy:** how to deploy, how to roll back, and what does it (CI or a person).
- **Access:** who has access, and where secrets are stored.
- **Cost:** budget and alerts.
- **Monitoring:** dashboards and alerts ([Operations](../process/operations.md)).
