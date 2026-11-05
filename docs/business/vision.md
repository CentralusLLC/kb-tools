---
type: Overview
title: Vision
description: "Why kb-tools exists, its goals, scope and non-goals."
tags: [business, vision, product]
status: stable
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Vision

kb-tools gives every project repository a knowledge base that people and AI agents share:
one layout, one way to ingest documents, one way to plan and record work, and the same
commands everywhere (laptop, CI, agent platforms). Agents stop reinventing extraction scripts
and project conventions, and knowledge stays in the repository where every agent can see it.

## Goals

- **One shared toolkit** instead of per-repository scripts (client-project already had two diverging copies).
- **Faithful ingestion:** text, page and slide renders, structure, figures and diagrams, with provenance.
- **Repository as the record** for knowledge, plans, work items and release notes; outside
  trackers are views.
- **Lean:** the smallest set of conventions that covers a project's phases, enforced by
  `kb check` rather than by review.
- **Runs anywhere Docker runs,** including as an MCP sidecar for agents in other containers.

## Scope

Project scaffolding, document ingestion, knowledge-base checks and trust reporting, a page
catalog, repository-native work tracking, and (planned) sync with outside trackers.

## Non-goals

- A hosted service or user interface; it is a CLI and an MCP server.
- Replacing trackers such as GitHub Issues, Jira or Paperclip.
- A vector database of its own; semantic search, if needed, reuses Hindsight
  (see the [roadmap](../work/index.md)).
