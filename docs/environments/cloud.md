---
type: Environment
title: Cloud and hosted environments
description: "kb-tools's deployment targets (for example AWS, Cloudflare, an internal server) and what each environment page must record."
tags: [environments, cloud, deployment]
status: draft
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Cloud and hosted environments

| Environment | What runs there |
| --- | --- |
| the Paperclip host, Paperclip stack (`<stack folder>`, service `kb-tools`) | MCP sidecar at `http://<kb-mcp-url>` on the stack network, allowed root `/paperclip/instances/default`; image built on the Paperclip host from `<stack folder>` |

No image registry yet; see the [roadmap](../work/index.md).

## For each environment, record

Give each environment its own page (`environments/<name>.md`, `type: Environment`) covering:

- **Purpose:** dev, staging or production; what runs there.
- **Provider, account and region:** identifiers only, never credentials.
- **Resources:** services, domains, storage, databases.
- **Deploy:** how to deploy, how to roll back, and what does it (CI or a person).
- **Access:** who has access, and where secrets are stored.
- **Cost:** budget and alerts.
- **Monitoring:** dashboards and alerts ([Operations](../process/operations.md)).
