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
| Paperclip host, Paperclip's compose stack (service `kb-tools`) | MCP server at `<kb-mcp-url>` on the stack network, image built on the host from a kb-tools checkout; set up as in [Install kb-tools as an add-on in a Paperclip environment](paperclip-add-on.md). Its values are in the host's untracked `.env` ([Configuration](configuration.md)). |
| Paperclip host, `agentdev` account | The devenv manager ([Agent dev environments](agent-dev-environments.md)) |

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
