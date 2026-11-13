---
type: Decision Record
title: "ADR 0006: kb-tools is MIT-licensed; the scaffold template ships no licence"
description: "kb-tools is released under the MIT licence (Centralus LLC, 2026); projects created with kb scaffold choose their own licence, so the template adds none."
tags: [adr, licence, public-release, scaffold]
status: stable
decision_status: accepted
generated:
  by: paperclip/kb-tools-developer
  at: 2026-11-13T06:03:34Z
---

# ADR 0006: kb-tools is MIT-licensed; the scaffold template ships no licence

## Context

kb-tools is being prepared for a public repository (epic 0010), and a public repository needs a
licence. The owner chose MIT, with Centralus LLC as the copyright holder (confirmed 2026-11-06,
Paperclip CEN-13). Until now `pyproject.toml` said "Proprietary".

`kb scaffold` copies a template into new projects. Those projects belong to whoever creates
them, may be private or commercial, and may need a different licence, or none.

## Decision

- kb-tools is licensed under MIT: a root `LICENSE` file ("Copyright (c) 2026 Centralus LLC"),
  `license = "MIT"` in `pyproject.toml` (with the MIT classifier, and `LICENSE` included in
  the wheel), and the `org.opencontainers.image.licenses=MIT` label on the Docker image.
- The scaffold template ships **no** licence file and sets no licence. The MIT licence covers
  the template text as part of kb-tools, but a scaffolded project chooses its own licence.
  The template's security page already asks projects to check licences of what they add.
- Third-party components keep their own licences; they are listed in
  [Third-party licences](../third-party-licences.md).

## Consequences

- Anyone can use, change and redistribute kb-tools, including in closed projects, keeping the
  copyright notice.
- New projects don't silently inherit a licence they didn't choose.
- The Docker image bundles LibreOffice (MPL-2.0) and other packages under their own licences;
  redistributing the image means honouring those too (see the third-party page).
- A new dependency, or a new package in the image, adds a row to the third-party page in the
  same pull request.
