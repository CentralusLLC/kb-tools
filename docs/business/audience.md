---
type: Persona
title: Audience
description: "Who uses kb-tools: the project owner, coding agents in a checkout, and agent-platform agents using the MCP server."
tags: [business, audience, personas]
status: stable
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Audience

## Persona: project owner

- **Who:** runs several project repositories (consulting-style projects) with a mix of people and AI agents.
- **Goals:** consistent structure across projects; knowledge, plans and release notes that agents keep current.
- **Frustrations:** agents rewriting extraction scripts; knowledge scattered across tools; review as a bottleneck.
- **Needs:** `kb scaffold` for new repositories, trustworthy ingestion, a trust report showing what to verify.

## Persona: coding agent (Claude Code, Codex, Copilot)

- **Who:** works in a checkout, reads `AGENTS.md` first.
- **Needs:** clear rules, a catalog to find pages, commands with predictable output (`tools/kb`).

## Persona: agent-platform agent (Paperclip)

- **Who:** runs in a container without LibreOffice or Python packages.
- **Needs:** the same commands as MCP tools (`kb_*`), working on its checkout through the shared volume.
