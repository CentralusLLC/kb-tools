---
type: Implementation Plan
epic: "0008"
title: "Plan: Structured fact extraction"
description: "Draft plan for epic 0008: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:37:00Z
---

# Plan: Structured fact extraction

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

Port an earlier project's LangExtract tool as an optional extra (`kb-tools[facts]`), reading pages.md and text.md from packages and writing JSON with citations.

## Design

Model is always explicit; the default points at the local gateway model so documents stay on-premises.

## Items and sequencing

0008-01 then 0008-02.

## Risks and open questions

Local model quality for extraction; keep grounded:false results visible.

## Verification

Run on a fixture with known facts and compare.
