# Architecture decisions

Architecture decision records (ADRs), numbered in order. Never delete or rewrite an
accepted ADR: supersede it with a new one, and set the old one's `status` to `deprecated`.

Template: `references/templates/decision.md`.

| ADR | Decision | Status |
| --- | --- | --- |
| [0001](0001-knowledge-base.md) | Keep project knowledge in an OKF knowledge base under `docs/`, maintained with kb-tools | Accepted |
| [0002](0002-docker-image-with-libreoffice.md) | One Docker image with LibreOffice, used as CLI and MCP server | Accepted |
| [0003](0003-generated-files-markdown-with-on-demand-json.md) | Committed generated files are Markdown; machine output on demand | Accepted |
| [0004](0004-repository-is-the-record-one-way-sync.md) | The repository is the record for work; trackers are synced one way | Accepted |
