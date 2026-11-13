---
type: Work Item
id: "0010-12"
epic: "0010"
title: "Add an MIT license"
description: "License kb-tools under MIT: a root LICENSE, pyproject metadata, a README section and the image label."
tags: [work-item]
status: draft
kind: chore
work_status: in_review
priority: critical
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-34"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-06T12:54:25Z
---

# 0010-12: Add an MIT license

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

A public repository needs a license. The owner chose MIT.

## Acceptance criteria

- [x] A root `LICENSE` file (MIT): "Copyright (c) 2026 Centralus LLC".
- [x] `pyproject.toml` has `license = "MIT"` and the MIT classifier.
- [x] A license section in `README.md`.
- [x] The Dockerfile sets the label `org.opencontainers.image.licenses=MIT`.
- [x] A recorded decision on whether the scaffold template ships a license (default: no).
- [x] Third-party license compatibility is noted (LibreOffice in the image is MPL).

## Notes

- Comes last in the public-release prep, after the audit (0010-11) and purge (0010-10), so the
  license lands on the rewritten history.
- Order changed (CEN-34 plan): the license lands before the 0010-10 purge. The single
  history rewrite in 0010-10 rewrites this commit too, so the license is still on the
  rewritten history.
- Delivered: `LICENSE`; `pyproject.toml` `license = "MIT"`, `license-files` and the MIT
  classifier (hatchling ≥ 1.27 for PEP 639 metadata; the built wheel carries
  `License-Expression: MIT` and `LICENSE`); README section; image label; decision in
  [ADR 0006](../../../../architecture/decisions/0006-mit-license-template-ships-none.md)
  (template ships no licence); compatibility in
  [Third-party licences](../../../../architecture/third-party-licences.md).
- Copyright holder confirmed by the owner on 2026-11-06 (CEN-13): Centralus LLC, 2026.
