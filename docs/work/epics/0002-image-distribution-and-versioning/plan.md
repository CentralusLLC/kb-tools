---
type: Implementation Plan
epic: "0002"
title: "Plan: Image distribution and versioning"
description: "Draft plan for epic 0002: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:35Z
---

# Plan: Image distribution and versioning

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

GitHub Actions workflow: on pull requests build the test target for both architectures (QEMU or native arm runners); on tags push the runtime image with `vX.Y.Z` and `latest` tags. The wrapper reads `KB_TOOLS_IMAGE` or a version line in `tools/kb` and pulls on first use.

## Design

The wrapper gains a pinned default such as `ghcr.io/<owner>/kb-tools:0.2.0`; `kb scaffold` writes the version it was run with. The Paperclip host's sidecar switches from a local build to the published image.

## Items and sequencing

0002-01 build and test in CI; 0002-02 publish (depends on 01); 0002-03 wrapper pinning (depends on 02); 0002-04 release process alongside.

## Risks and open questions

- arm64 builds under QEMU are slow (LibreOffice install): prefer native arm runners or cache layers.
- The registry must be reachable from the Paperclip host and laptops; private images need a token.

## Verification

A tag produces both architectures; a clean machine runs the wrapper; the Paperclip host runs the published image.
