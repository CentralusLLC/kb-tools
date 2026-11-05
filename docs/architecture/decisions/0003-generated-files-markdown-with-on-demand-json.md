---
type: Decision Record
title: "ADR 0003: Committed generated files are Markdown; machine output is produced on demand"
description: The catalog and roadmap are committed as generated Markdown with drift-free fields; JSON or JSON Lines is printed on demand by commands rather than stored.
tags: [adr, catalog, roadmap, formats]
status: stable
decision_status: accepted
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T00:00:00Z
---

# ADR 0003: Generated files are Markdown; machine output on demand

## Context

Agents need a compact page list to orient themselves, and sometimes filtered,
machine-readable lists. A stored JSON copy would duplicate the pages, drift, and add diff
noise, and `jq` is missing in many agent environments.

## Decision

- `docs/catalog.md` and the roadmap in `docs/work/index.md` are generated Markdown between
  markers, holding only fields that change when pages change (no ages or time-based flags).
- `kb catalog` and `kb work list` print filtered `md`, `json` or `jsonl` on demand, straight from
  front matter.
- `kb check` warns when a generated file is stale; commands that change pages regenerate them.

## Consequences

- One committed form, readable by people and agents, and diff-friendly.
- Scripts call the command instead of reading a file.
