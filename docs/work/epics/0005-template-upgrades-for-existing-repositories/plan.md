---
type: Implementation Plan
epic: "0005"
title: "Plan: Template upgrades for existing repositories"
description: "Draft plan for epic 0005: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:47Z
---

# Plan: Template upgrades for existing repositories

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

Write the kb-tools version into `docs/log.md` and a small stamp file at scaffold time. `--diff` renders the old and current template (from the image's history or a bundled copy of past templates) and diffs them per file, alongside the repository's current file.

## Design

Bundle each released template version in the package (they are small), keyed by version.

## Items and sequencing

0005-01 stamp first; 0005-02 diff; 0005-03 guide.

## Risks and open questions

Placeholders differ per repository; diff after substitution.

## Verification

Upgrade gameworld from the template it effectively has to the current one using only the diff output.
