---
type: Epic
id: "0011"
title: "MCP tool parity with the CLI"
description: "Agents that use kb-tools through MCP can do what the kb CLI does, so they stop hand-editing generated files."
tags: [epic]
status: draft
work_status: in_progress
priority: low
owner: ""
target: ""
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: paperclip/kb-tools-developer
  at: 2026-11-06T11:58:56Z
---

# Epic 0011: MCP tool parity with the CLI

## Problem / business need

Agents in Paperclip use kb-tools through its MCP tools, not the `kb` CLI. Where a CLI option has
no MCP equivalent, they work around it by hand. The gameworld Developer, bootstrapping
gameworld's knowledge base (Paperclip CEN-9), had to edit `docs/catalog.md` rows by hand
because `kb_catalog` could only list pages; hand-edited rows drift from page front matter
(reported as Paperclip CEN-10).

## Outcome and success measures

Each MCP gap found in use is closed with a tool option that matches the CLI and a test that
calls the tool through the MCP server.

## Scope

- [0011-01](items/01-kb-catalog-mcp-tool-can-write-docs-catalog-md.md): `kb_catalog` writes `docs/catalog.md`.
- Further gaps as agents report them, one item each.

## Non-goals

- A full audit of every CLI flag up front; gaps are fixed as they are found.
- Tracker sync and other new commands (other epics).

## Acceptance

> TODO: Who accepts the outcome (see stakeholders in project management), and how
> (demo, review of success measures). Record the acceptance here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
