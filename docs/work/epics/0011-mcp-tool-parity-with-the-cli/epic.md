---
type: Epic
id: "0011"
title: "MCP tool parity with the CLI"
description: "Agents that use kb-tools through MCP can do what the kb CLI does, so they stop hand-editing generated files."
tags: [epic]
status: draft
work_status: done
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

The board accepts. Success measure checked on 2026-11-12: the one gap reported (Paperclip
CEN-10, `kb_catalog` couldn't write) is closed by [0011-01](items/01-kb-catalog-mcp-tool-can-write-docs-catalog-md.md),
merged in PR #2, and `test_mcp_kb_catalog_write_regenerates_catalog` calls the tool through
the MCP server. No other gaps have been reported. The board asked for completed epics to be
closed (CEN-12, CEN-33); closed in [0012-02](../0012-development-workflow/items/02-reconcile-work-item-statuses-with-delivered-work.md).

## Retrospective

- Worked: an agent reported the gap from real use (CEN-10), and one small item with an
  MCP-level test closed it.
- Didn't: the epic was open-ended ("further gaps as agents report them"), so it had no
  natural end and stayed `in_progress` after its only item was done.
- Action: no new item. Report future MCP gaps as items in a new epic, not by reopening this
  one.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
