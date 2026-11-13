---
type: Implementation Plan
epic: "0003"
title: "Plan: Paperclip ingestion end to end"
description: "Draft plan for epic 0003: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:39Z
---

# Plan: Paperclip ingestion end to end

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

Configure the connection (application, connection with remote HTTP to `<kb-mcp-url>`, catalog refresh, profile bound to agents, a policy allowing the non-destructive write tools without per-call approval). Create a Paperclip project whose workspace is a gameworld checkout. Add `kb review-packet <source>` producing a Markdown summary and a contact sheet of renders for upload as a work product. Then run the trial and record findings.

## Design

The review packet is generated from the extraction package (manifest warnings, review.md, a contact sheet image of all renders, links to the pages written). Upload uses Paperclip's attachment and work-product API from the agent side.

## Items and sequencing

0003-01 and 0003-02 are setup tasks for the owner (connections need a signed-in user); 0003-03 can be built in parallel; 0003-04 runs after setup.

## Risks and open questions

- Write tools may still require approval per call if the policy is not set.
- Paths: agents must pass their checkout path as the sidecar sees it (same volume path).

## Verification

The trial issue shows the pull request link, the review packet, and a passing kb check.
