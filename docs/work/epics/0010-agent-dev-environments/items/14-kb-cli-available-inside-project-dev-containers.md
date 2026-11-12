---
type: Work Item
id: "0010-14"
epic: "0010"
title: "kb CLI available inside project dev containers"
description: "Make the kb CLI (check, catalog, work, report) runnable inside a project's dev container against its own repository, through the scaffold template, without Docker in the container."
tags: [work-item]
status: draft
kind: story
work_status: done
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-23"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-07T19:31:46Z
---

# 0010-14: kb CLI available inside project dev containers

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

The board decided on CEN-5 (2026-11-07) that agents working inside a project's dev container
must be able to run `kb check`, `kb catalog`, `kb work` and the other commands on that
project's repository. Today they can't: `tools/kb` needs Docker, which dev containers don't
have by design, and the kb-tools MCP server only reads host paths. kb-tools stays
project-agnostic, so this is a scaffold-template and packaging change. The install mechanism
is chosen by the board before building (see [the plan](../plan.md#kb-cli-in-project-dev-containers-0010-14)).

## Acceptance criteria

- [x] The board has picked the install mechanism (recorded in Notes).
- [x] The scaffold template (`src/kbtools/template/dot-devcontainer/` and/or the template's
      `docs/environments/dev-environment.md`) installs the kb CLI or documents the one step that does.
- [x] `kb check` runs inside a project dev container built from the template (or set up by the
      documented step) against that project's repository.
- [x] Tests cover the template change; they pass in the kb-tools dev container.
- [x] kb-tools docs and a release-note line are updated.

## Notes

- Board decision (CEN-23, 2026-11-12): run-time install (option a), full install with every
  dependency (no light install), default ref `main`. Built as `tools/kb --install [ref]`
  with `KB_TOOLS_SOURCE`; see [the plan](../plan.md#kb-cli-in-project-dev-containers-0010-14).
- Verified 2026-11-12: in the kb-tools dev container (no Docker), a scaffolded project
  installed kb-tools from GitHub `main` and `tools/kb check` reported 0 errors, 0 warnings.

- Verified 2026-11-07 in the kb-tools dev container: `check`, `catalog`, `work list` and
  `report` run with only PyYAML installed (no markitdown, LibreOffice or pdfium), and
  `pip install git+https://github.com/CentralusLLC/kb-tools@dev` succeeds with the run's
  GitHub credentials.
