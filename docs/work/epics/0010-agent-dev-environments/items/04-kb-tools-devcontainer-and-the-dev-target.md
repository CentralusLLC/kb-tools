---
type: Work Item
id: "0010-04"
epic: "0010"
title: "kb-tools .devcontainer and the dev target"
description: "A dev stage in kb-tools' Dockerfile and a .devcontainer that uses it, so people and agents run the tests with LibreOffice and every dependency against the workspace source."
tags: [work-item]
status: draft
kind: task
work_status: done
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:33Z
---

# 0010-04: kb-tools .devcontainer and the dev target

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

kb-tools' tests need LibreOffice, fonts and every extraction dependency. A `dev` Dockerfile
stage with those (and no installed copy of kb-tools, so tests import the workspace's `src/`)
gives people (VS Code, Codespaces) and agents (devenv manager) the same environment.

## Acceptance criteria

- [x] The Dockerfile has a `dev` stage with the runtime and test dependencies, git and make,
      and without kb-tools itself installed.
- [x] `.devcontainer/devcontainer.json` builds that stage.
- [x] `python -m pytest -q` passes in it (18 tests on 2026-11-05).
- [x] Documented in [Dev environment](../../../../environments/dev-environment.md).

## Notes

The devenv manager builds `devenv-kb-tools` from this `.devcontainer/` plus the overlay (0010-02).
