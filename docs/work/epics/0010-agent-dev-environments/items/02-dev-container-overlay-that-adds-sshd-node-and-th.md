---
type: Work Item
id: "0010-02"
epic: "0010"
title: "Dev container overlay that adds sshd, node and the claude CLI to any project image"
description: "An image layer added on top of any project's dev image with sshd, node, git and the claude CLI, so Paperclip can run agents in it over SSH."
tags: [work-item]
status: draft
kind: story
work_status: done
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:30Z
---

# 0010-02: Dev container overlay that adds sshd, node and the claude CLI to any project image

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

Paperclip runs agents in a remote environment over SSH, with node and the claude CLI on the
target. Projects shouldn't have to put these in their own `.devcontainer/`, so the devenv
manager adds them as an overlay on top of whatever image the project builds.

## Acceptance criteria

- [x] The overlay (`devenv/kbdevenv/overlay/`) adds sshd (user `agent`, key-only, no sudo),
      node, git and the claude CLI to any project dev image.
- [x] The container keeps stable host keys and a home volume across rebuilds.
- [x] An agent run reaches the container over SSH and runs the project's tests (2026-11-05:
      node 22, Claude Code 2.1.318, git, no sudo; 18 tests passed).

## Notes

Built and used through the devenv manager (0010-03); the SSH trial is 0010-05 (CEN-6).
