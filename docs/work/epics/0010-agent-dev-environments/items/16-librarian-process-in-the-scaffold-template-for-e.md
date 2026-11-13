---
type: Work Item
id: "0010-16"
epic: "0010"
title: "Librarian process in the scaffold template for every project"
description: "Every scaffolded project routes ingestion, source requests and research to the ingesting agent (for example a Librarian): a template process page, an AGENTS.md section, and add-on guide steps."
tags: [work-item]
status: draft
kind: task
work_status: done
priority: medium
depends_on: []
links: 
  github: "https://github.com/CentralusLLC/kb-tools/pull/14"
  jira: ""
  paperclip: "CEN-45"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T12:49:41Z
---

# 0010-16: Librarian process in the scaffold template for every project

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

The board asked (CEN-12) that the Librarian does document ingestion and research for every
project that uses kb-tools, not just gameworld. gameworld added its process by hand
(`docs/process/librarian.md` and an AGENTS.md section). The scaffold template only had
`ingestion.md`, with no source-request or research process, so a new project would not tell
its developers to route that work to the ingesting agent.

- Template page `docs/process/sources-and-research.md`, generalized from gameworld's
  `librarian.md` and free of deployment values: who uses what, ingestion (steps in
  `ingestion.md`), source requests, research, and where originals are kept.
- Template `AGENTS.md` section "Source documents, source requests and research" and a
  quick-reference line; links from `docs/process/index.md` and `ingestion.md`.
- Add-on guide: section 2 says the ingesting agent takes source requests and research for
  every project; section 3 adds giving it a checkout of each new project and confirming
  `kb_work_list repo=<name>`; the upgrade section says how existing projects pick up the page.

## Acceptance criteria

- [x] A freshly scaffolded project has the page and the AGENTS.md section, with no
      deployment-specific values (test).
- [x] `kb scaffold` on an existing project adds the page and overwrites nothing (test).
- [x] The add-on guide tells the operator to add each new project to the ingesting agent's
      checkouts.
- [x] Tests pass; `tools/kb check` reports 0 errors.

## Notes

- gameworld keeps its own `docs/process/librarian.md`; it is not changed here. A project
  that already has such a page can delete the added `sources-and-research.md`.
- Existing projects add the AGENTS.md section and index links by hand, because scaffold never
  overwrites files.
