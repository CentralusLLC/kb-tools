---
type: Implementation Plan
epic: "0007"
title: "Plan: Release notes automation"
description: "Draft plan for epic 0007: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:56Z
---

# Plan: Release notes automation

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

`cut` moves entries from unreleased.md into vX.Y.Z.md with a summary placeholder, resets Unreleased, and updates the index table. `deploy` appends a Deployments row with the date, actor and tag.

## Design

Release pages get structured front matter (version, released_at); the Deployments table stays Markdown.

## Items and sequencing

0007-01 then 0007-02.

## Risks and open questions

Hand-edited release pages must still parse; be tolerant and warn.

## Verification

Tests cut and deploy a release in a scaffolded repository, and kb check stays clean.
