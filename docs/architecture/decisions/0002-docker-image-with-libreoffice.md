---
type: Decision Record
title: "ADR 0002: Ship kb-tools as one Docker image with LibreOffice, used as CLI and MCP server"
description: kb-tools runs in a Docker image bundling LibreOffice and fonts, called through a per-project wrapper or as an MCP sidecar, rather than installed into each environment.
tags: [adr, docker, libreoffice, mcp]
status: stable
decision_status: accepted
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T00:00:00Z
---

# ADR 0002: One Docker image with LibreOffice, used as CLI and MCP server

## Context

Faithful rendering of PowerPoint, Word and Excel needs LibreOffice and matching fonts, plus
several Python packages. Laptops differ (the owner's Mac had Python 3.9), and Paperclip agents
run in a container without any of it. The owner asked for the tools not to depend on local
environments.

## Decision

- One image (`python:3.12-slim` with LibreOffice and Carlito, Caladea, Liberation and Noto fonts)
  contains everything.
- Projects call it through `tools/kb`, a wrapper that runs it as the calling user, with the
  repository at `/work` and no network.
- Agent platforms run the same image as an MCP server (`kb serve`) sharing their data volume,
  restricted to allowed roots. Tools carry MCP annotations (read-only checks, non-destructive
  writes) so Paperclip does not quarantine them.
- The MCP SDK is pinned below 2.0, which renamed the FastMCP API.

## Consequences

- Same results everywhere; Docker is the only requirement.
- The image is about 1.6 GB, and each machine builds it until images are published.
- Server mode runs `kb` as a subprocess per call, so a failure never takes the server down.
