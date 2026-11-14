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
- [0010-13] `kb --version` shows the git ref and commit it was installed from, for example `0.1.0+dev.b3e23c9`.
- [0010-11] `kb check` scans tracked files for secrets (errors) and private or tailnet addresses (warnings), with an optional deny list outside the repository (`KB_SCAN_DENYLIST`) for organisation-specific names.
- [0010-15] `kb scaffold --tools-only` upgrades a project's `tools/kb` to the installed version's and adds a missing `tools/kb.conf`; the add-on guide has an upgrade section.
- [0010-12] kb-tools is MIT-licensed (`LICENSE`, package metadata and the image's `org.opencontainers.image.licenses` label). Third-party licences are listed in `docs/architecture/third-party-licences.md`; projects created with `kb scaffold` choose their own licence.
- [0010-16] Every new project's knowledge base routes document ingestion, source requests and research to the ingesting agent (for example a Librarian): `docs/process/sources-and-research.md` and an `AGENTS.md` section in the scaffold template, and add-on guide steps to give that agent a checkout of each project.
- [0013-01] `kb work set ID STATUS --pr URL` records the pull request that delivers an item, and `--github`, `--jira` and `--paperclip` record tracker links (also on the `kb_work_set` MCP tool). `kb check` warns about `backlog`, `todo` or `in_review` items whose pull request is merged, read from the local git history.
- [0013-02] `kb check` and `kb work set ... done` warn about done items whose acceptance criteria aren't all ticked.
- [0013-03] `kb work new-item` and `new-epic` (and their MCP tools) take `--description` and tracker links, so new pages need no hand edits; `kb check` warns about TODO placeholders left on work that has started.
- [0013-04] `kb work new-epic` and `new-item` (and their MCP tools) take `--slug`; without it, folder and file names are cut at a word boundary instead of mid-word.
- [0013-05] `kb work rename ID --slug SLUG [--title TITLE]` (and the `kb_work_rename` MCP tool) renames an epic folder or item file, keeps its id, rewrites links to it and regenerates the roadmap and catalog.
- [0013-06] `kb work set` keeps OKF `status` in step with the work: `stable` once an item or epic is done or cancelled, `draft` again if it reopens. The work-tracking page explains both status fields.
- [0013-07] `kb check` warns about `planned` or `in_progress` epics whose items are all done or cancelled, and about skipped item ids in an epic.
- [0013-08] New projects' templates say which parts are Paperclip-specific and optional on another agent platform: an "Agent platforms" section in `docs/process/agent-workflow.md`, and notes on the dev-environment "Agents" section (`devenv_*` tools), Hindsight memory, the Paperclip ingestion flow and the `paperclip` section of `trackers.yaml`.
- [0011-01] The `kb_catalog` MCP tool can regenerate `docs/catalog.md` (`write=true`), like `kb catalog --write`.

## Changed

- [0010-13] `tools/kb --install` is a light install by default (about 17 MB instead of 330 MB), with what `check`, `work`, `catalog`, `report`, `log` and `inventory` need; `--install --full` adds extraction. It reads its source from the project's `tools/kb.conf` (written by `kb scaffold`), so `KB_TOOLS_SOURCE` is no longer required.
- [0010-13] Every deployment-specific value is a setting with a neutral default: `kb serve` reads `KB_MCP_HOST` (default `127.0.0.1`), `KB_MCP_PORT`, `KB_REPOS_ROOT` and `KB_ALLOWED_ROOTS`; the devenv manager's compose file takes all its values from an untracked `.env` (see `devenv/.env.example`), with the new `DEVENV_MANAGER_PORT`.
- [0010-13] MCP tool failures (unknown repository, a command that exits non-zero) are now reported as tool errors, and name the repositories the server can see. Absolute `repo` paths must be under `KB_REPOS_ROOT` or an allowed root.

- [0012-01] Contributing: work pull requests now target `dev`, where Chief merges them; `main` is the release branch, changed only by board-approved release pull requests.

## Fixed

- [0010-15] `tools/kb --install` finds the source of an install made before `tools/kb.conf` existed, and says when the project's `tools/kb` is older than the installed one.
- [0010-15] `kb scaffold` records the ref kb-tools was installed from in `tools/kb.conf` (for example `dev`), instead of always `main`.
- [0010-15] The `kb check` scan skips untracked files in Paperclip's `.paperclip-runtime/` folder (a file committed there is still scanned), so agent workspaces no longer get a warning; the docs now say untracked, not ignored files are scanned.
- [0010-17] `docker build --target test` runs the whole test suite again: the test stage installs git and copies `bin/`. The runtime image is unchanged. The suite also passes under `docker run -u` with a uid that has no `/etc/passwd` entry, and `tools/kb` no longer prints `id: cannot find name` there.

## Deprecated

## Removed

## Security
