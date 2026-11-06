---
type: Work Item
id: "0010-12"
epic: "0010"
title: "Add an MIT license"
description: "License kb-tools under MIT: a root LICENSE, pyproject metadata, a README section and the image label."
tags: [work-item]
status: draft
kind: chore
work_status: todo
priority: critical
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-06T12:54:25Z
---

# 0010-12: Add an MIT license

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

A public repository needs a license. The owner chose MIT.

## Acceptance criteria

- [ ] A root `LICENSE` file (MIT), with the copyright holder confirmed by the owner (for
      example "Centralus LLC, 2026").
- [ ] `pyproject.toml` has `license = "MIT"` and the MIT classifier.
- [ ] A license section in `README.md`.
- [ ] The Dockerfile sets the label `org.opencontainers.image.licenses=MIT`.
- [ ] A recorded decision on whether the scaffold template ships a license (default: no).
- [ ] Third-party license compatibility is noted (LibreOffice in the image is MPL).

## Notes

- Comes last in the public-release prep, after the audit (0010-11) and purge (0010-10), so the
  license lands on the rewritten history.
- Open question: the copyright holder's exact name.
