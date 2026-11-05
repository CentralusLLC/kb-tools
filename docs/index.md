---
okf_version: "0.2"
---

# kb-tools knowledge base

This directory is the project's curated knowledge base: the source of truth for
what kb-tools is, how it is built, and how work gets done. People and every AI
agent read it. It is an [Open Knowledge Format (OKF) v0.2](conventions.md#open-knowledge-format)
bundle that travels with the repository.

## Start here (agents and new contributors)

1. Read [Agent workflow](process/agent-workflow.md): the rules for every task.
   Use the [catalog](catalog.md) (every page, one line each) to find pages.
2. Open the section index that matches your task and read the pages it points to.
   Do not read the whole bundle up front.
3. When sources disagree, follow [precedence](process/agent-workflow.md#precedence).

## Sections

| Section | What it holds |
| --- | --- |
| [architecture/](architecture/index.md) | System architecture, structured research data, and architecture decision records |
| [business/](business/index.md) | Vision, branding, users and customers, business model and rules |
| [design/](design/index.md) | User flows, screens and the design system |
| [domains/](domains/index.md) | Sub-wikis of domain knowledge by topic, and the glossary |
| [environments/](environments/index.md) | Where the project runs: local development and deployment targets |
| [process/](process/index.md) | Agent workflow, development, testing, security, project management, work tracking, release notes, operations, ingestion, knowledge-base maintenance |
| [work/](work/index.md) | Epics, implementation plans and work items, with the roadmap |
| [user/](user/index.md) | User-facing documentation: guides, how-tos, reference |
| [releases/](releases/index.md) | Release notes: unreleased changes, each release, and where it is deployed |

## About this bundle

- [Catalog](catalog.md): every page with type, description, tags and trust (generated).
- [Conventions](conventions.md): page format, front matter, verification and trust, figures, diagrams, linking.
- [log.md](log.md): changes to the knowledge base, newest first.
- [sources/](sources/index.md): inbox for raw files to ingest (not committed), tracked in
  `sources/ingest-log.csv`. See [Ingestion](process/ingestion.md).
- Structured research data lives in the repository's `data/` folder ([Research data](architecture/research-data.md)).
- `tools/kb` runs the shared kb-tools toolkit; extraction output goes to the git-ignored
  `extracted/` folder ([tools/README.md](../tools/README.md)).
- `references/templates/` holds page templates.
