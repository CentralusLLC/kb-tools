---
type: Environment
title: Local development
description: "How to set up and run kb-tools on a local machine, including the kb-tools prerequisites."
tags: [environments, local, setup]
status: stable
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Local development

## Prerequisites

- Git.
- Docker, for `tools/kb` (kb-tools). Build the `kb-tools:latest` image once per machine
  ([tools/README.md](../../tools/README.md)).

Nothing else: Python, LibreOffice and fonts live in the image.

## Setup

```sh
git clone <kb-tools repository> ~/workspace/kb-tools
docker build -t kb-tools:latest ~/workspace/kb-tools
```

## Run

From any repository: `~/workspace/kb-tools/bin/kb <command>` (or that repository's `tools/kb`).
As an MCP server: `docker run -p 8765:8765 -v <data>:/data kb-tools:latest serve --allowed-root /data`.

## Test

See [Testing](../process/testing.md#current-state).
