---
type: Implementation Plan
epic: "0009"
title: "Plan: Semantic search through Hindsight"
description: "Draft plan for epic 0009: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:37:03Z
---

# Plan: Semantic search through Hindsight

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

First measure: log cases where agents fail to find an existing page. Only if that happens regularly, upsert each page (keyed by path, with type, trust and commit metadata) into a dedicated Hindsight bank after merges, skipping deprecated pages.

## Design

Reuse Hindsight's embeddings, keyword search and reranker; the bank is rebuildable from the repository at any time.

## Items and sequencing

0009-01 decides whether the rest happens.

## Risks and open questions

Index drift if not rebuilt after merges; duplicated content competing with pages in agent memory recall (keep it in a separate bank).

## Verification

Searches with synonyms find the right pages that grep missed.
