---
type: Decision Record
title: "ADR 0001: Keep project knowledge in an OKF knowledge base under docs/"
description: Curated project knowledge lives in docs/ as an OKF bundle read by people and all agents, maintained with kb-tools; sources stay out of git; verification is optional and tracked.
tags: [adr, knowledge-base, okf, agents, tools]
status: stable
decision_status: accepted
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# ADR 0001: Keep project knowledge in an OKF knowledge base under docs/

## Context

Several people and AI agents work on kb-tools, each tool reading a different instruction
file. The project needs one source of truth that people and agents can read, that travels with
the repository, and that is not tied to a single tool.

## Decision

- **Knowledge base:** curated knowledge lives in `docs/` as an Open Knowledge Format v0.2 bundle,
  in the sections architecture, business, domains, environments and process. `AGENTS.md`
  (with `CLAUDE.md` and `.github/copilot-instructions.md` pointing to it) directs every agent there.
- **Ingestion:** documents are ingested with the shared kb-tools toolkit (`tools/kb`, or its MCP
  server). Original sources (`docs/sources/`) and extraction output (`extracted/`) stay out of git;
  the ingest log records each source's hash and origin.
- **Graphics:** key graphics become figures with element tables, and relationships become Mermaid
  diagrams with node and edge tables (visible versus inferred).
- **Verification:** optional and never blocks work. Verification level and recency are tracked
  per page, and agents weigh pages by them.
- **Agent memory:** holds working context only. Durable knowledge reaches `docs/` through
  pull requests.

## Consequences

- Any agent can be told "read docs/ first" and get the same rules and context.
- Knowledge changes get the same history as code.
- Fresh clones lack the original sources; re-fetch them from their recorded origin.
- The trust report shows where verification would add the most value.

