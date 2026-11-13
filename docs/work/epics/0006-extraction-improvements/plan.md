---
type: Implementation Plan
epic: "0006"
title: "Plan: Extraction improvements"
description: "Draft plan for epic 0006: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:50Z
---

# Plan: Extraction improvements

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

OCR with a local engine (for example Tesseract) only on pages without a text layer, writing text marked as OCR. Duplicate detection compares hashes, page counts, normalised text and render similarity against other packages. Web capture renders a URL to PDF with a headless browser at a recorded time. Word views come from accepting or rejecting revisions in a copy before conversion.

## Design

Each step records its tool, version and confidence in the manifest; OCR text never overwrites extracted text.

## Items and sequencing

Independent; start with OCR (0006-01) and duplicate detection (0006-02), which the earlier extraction guide found most valuable.

## Risks and open questions

Image size grows with OCR and browser engines; consider an optional image variant.

## Verification

Each item adds tests with real fixtures (scanned page, duplicate deck pair, tracked-changes document).
