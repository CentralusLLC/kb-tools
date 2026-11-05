---
type: Work Item
id: "0010-07"
epic: "0010"
title: ".devcontainer in the scaffold template"
description: "kb scaffold gives every new project a generic .devcontainer/ that the devenv manager can build."
tags: [work-item]
status: draft
kind: task
work_status: in_progress
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:36Z
---

# 0010-07: .devcontainer in the scaffold template

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

The devenv manager builds a project's `.devcontainer/` (or a default image). The scaffold
template ships a generic `dot-devcontainer/` (installed as `.devcontainer/`) and a
dev-environment page, so projects scaffolded by kb-tools start with a buildable dev
environment and the rule to run tests in it.

## Acceptance criteria

- [x] Template ships `dot-devcontainer/` (Dockerfile, devcontainer.json) and
  `docs/environments/dev-environment.md`.
- [ ] A test checks that `kb scaffold` installs `.devcontainer/`.

## Notes

Project-specific dev containers (for example a downstream project's Node or Flutter
toolchain) belong to that project's own repository and roadmap, not to kb-tools. kb-tools
only provides the generic template.
