---
type: Release Notes
title: Unreleased
description: "Changes completed in kb-tools but not yet released; each merged work item adds its entry here."
tags: [releases, changelog]
status: stable
version: unreleased
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Unreleased

Entries are added in the pull request that completes a work item. Write each for the people
who use the product: what changed for them, not how it was built.

## Added

- [0010-01] Isolated `agentdev` account on the Paperclip host with its own rootless Docker and egress rules, for agent dev containers.
- [0010-02] Agent overlay that adds sshd, git, node and the claude CLI to any project's dev image.
- [0010-04] `.devcontainer/` and a `dev` Dockerfile stage for kb-tools; tests run against the workspace source.
- devenv manager (`devenv/`): per-project agent dev containers managed over MCP, with per-project SSH keys and builds from the worktree Paperclip syncs in (no GitHub credential); in progress, epic 0010.
- Template: `.devcontainer/` and a dev-environment page; agents run tests in the dev environment instead of outside CI.
- [0010-14] `tools/kb` works in dev containers without Docker: `tools/kb --install` sets up a local kb-tools install (default ref `main`) that persists in the agent's home, and the template's dev-environment page documents it.
- [0011-01] The `kb_catalog` MCP tool can regenerate `docs/catalog.md` (`write=true`), like `kb catalog --write`.

## Changed

- [0012-01] Contributing: work pull requests now target `dev`, where Chief merges them; `main` is the release branch, changed only by board-approved release pull requests.

## Fixed

## Deprecated

## Removed

## Security
