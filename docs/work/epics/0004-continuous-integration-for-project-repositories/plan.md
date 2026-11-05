---
type: Implementation Plan
epic: "0004"
title: "Plan: Continuous integration for project repositories"
description: "Draft plan for epic 0004: approach, design, sequencing, risks and verification."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T06:36:44Z
---

# Plan: Continuous integration for project repositories

> **Draft.** Not ready for development; review before setting the epic to `planned`.

## Approach

A composite action that pulls the published image (epic 0002) and runs `kb check`. A new `kb check --pr <base>` mode compares the branch with its base: items newly set to done need a matching line in Unreleased (except kinds that need none), and changed pages need a fresh catalog.

## Design

The action takes the image version as an input; failures print the check output as a job summary.

## Items and sequencing

0004-01 after epic 0002 publishes images; 0004-02 after that.

## Risks and open questions

Checks that are too strict will be bypassed; start with errors only for clear breakages and warnings for the rest.

## Verification

A test repository's pull requests pass and fail as expected.
