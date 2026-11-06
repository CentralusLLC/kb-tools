---
type: Implementation Plan
epic: "0011"
title: "Plan: MCP tool parity with the CLI"
description: "How epic 0011 will be delivered: approach, design, risks and sequencing of its items."
tags: [plan]
status: draft
generated: 
  by: paperclip/kb-tools-developer
  at: 2026-11-06T11:58:56Z
---

# Plan: MCP tool parity with the CLI

## Approach

Add the missing option to the existing MCP tool, mapping it to the same CLI arguments, rather
than adding separate tools. Tools keep running the CLI as a subprocess (`server._run`), so
behaviour stays identical to `tools/kb`.

## Design

`src/kbtools/server.py` only. A tool that gains an option that writes files changes its MCP
annotation from read-only to `write` (non-destructive, idempotent), so clients that gate
writes see an honest hint.

## Items and sequencing

Items live in [items/](items/), one file each. Create them with
`tools/kb work new-item 0011 "Title"`. Items are independent of each other.

## Risks and open questions

- Re-annotating a listing tool as a write tool may make clients that gate writes (Paperclip)
  ask for approval on plain listings too. If that gets in the way, split the write into its
  own tool instead.

## Verification

Each item adds a pytest test that calls the tool through `FastMCP.call_tool`, run in the
kb-tools dev environment.
