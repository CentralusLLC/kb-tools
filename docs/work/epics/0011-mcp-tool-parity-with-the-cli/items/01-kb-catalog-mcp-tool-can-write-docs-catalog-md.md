---
type: Work Item
id: "0011-01"
epic: "0011"
title: "kb_catalog MCP tool can write docs/catalog.md"
description: "The kb_catalog MCP tool gains a write option that regenerates docs/catalog.md, matching kb catalog --write."
tags: [work-item]
status: draft
kind: story
work_status: done
priority: low
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-10"
generated: 
  by: paperclip/kb-tools-developer
  at: 2026-11-06T11:58:56Z
---

# 0011-01: kb_catalog MCP tool can write docs/catalog.md

Part of [epic 0011](../epic.md) ([plan](../plan.md)).

## What and why

`kb catalog --write` regenerates `docs/catalog.md` from page front matter, but the `kb_catalog`
MCP tool could only list pages, so MCP-only agents edited catalog rows by hand and the rows
drifted from front matter. Add `write` to `kb_catalog` so they regenerate it instead.

## Acceptance criteria

- [x] `kb_catalog` accepts `write` (default `false`); `write=true` runs `kb catalog --write`
  and returns its output; filters and format are ignored, as in the CLI.
- [x] Without `write`, the tool only lists pages and changes no files.
- [x] The tool's MCP annotation is no longer read-only.
- [x] Test: `test_mcp_kb_catalog_write_regenerates_catalog` calls the tool through the MCP
  server and checks a hand-edited catalog is regenerated.

## Notes

Reported on Paperclip CEN-10 by the gameworld Developer (CEN-9). See the plan's risk on
re-annotating the tool.
