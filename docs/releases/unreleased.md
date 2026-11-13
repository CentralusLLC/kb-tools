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
- [0010-03] devenv manager (`devenv/`): per-project agent dev containers managed over MCP, with per-project SSH keys and builds from the worktree Paperclip syncs in (no GitHub credential).
- Template: `.devcontainer/` and a dev-environment page; agents run tests in the dev environment instead of outside CI.
- [0010-14] `tools/kb` works in dev containers without Docker: `tools/kb --install` sets up a local kb-tools install (default ref `main`) that persists in the agent's home, and the template's dev-environment page documents it.
- [0010-13] Guide for installing kb-tools as an add-on in any Paperclip environment (`docs/environments/paperclip-add-on.md`), and one table of every setting (`docs/environments/configuration.md`).
- [0010-13] MCP tools accept a repository name (`repo=gameworld` or `owner/gameworld`), looked up under the server's `KB_REPOS_ROOT` (default `/repos`).
- [0010-13] `kb --version` shows the git ref and commit it was installed from, for example `0.1.0+dev.3061f26`.
- [0010-11] `kb check` scans tracked files for secrets (errors) and private or tailnet addresses (warnings), with an optional deny list outside the repository (`KB_SCAN_DENYLIST`) for organisation-specific names.
- [0011-01] The `kb_catalog` MCP tool can regenerate `docs/catalog.md` (`write=true`), like `kb catalog --write`.

## Changed

- [0010-13] `tools/kb --install` is a light install by default (about 17 MB instead of 330 MB), with what `check`, `work`, `catalog`, `report`, `log` and `inventory` need; `--install --full` adds extraction. It reads its source from the project's `tools/kb.conf` (written by `kb scaffold`), so `KB_TOOLS_SOURCE` is no longer required.
- [0010-13] Every deployment-specific value is a setting with a neutral default: `kb serve` reads `KB_MCP_HOST` (default `127.0.0.1`), `KB_MCP_PORT`, `KB_REPOS_ROOT` and `KB_ALLOWED_ROOTS`; the devenv manager's compose file takes all its values from an untracked `.env` (see `devenv/.env.example`), with the new `DEVENV_MANAGER_PORT`.
- [0010-13] MCP tool failures (unknown repository, a command that exits non-zero) are now reported as tool errors, and name the repositories the server can see. Absolute `repo` paths must be under `KB_REPOS_ROOT` or an allowed root.

- [0012-01] Contributing: work pull requests now target `dev`, where Chief merges them; `main` is the release branch, changed only by board-approved release pull requests.

## Fixed

## Deprecated

## Removed

## Security
