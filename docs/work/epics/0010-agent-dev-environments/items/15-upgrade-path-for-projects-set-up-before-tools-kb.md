---
type: Work Item
id: "0010-15"
epic: "0010"
title: "Upgrade path for projects set up before tools/kb.conf"
description: "Fix the issues found by gameworld's reinstall check of 0010-13 and 0010-11 on dev: upgrading a project set up by an older kb-tools, the ref scaffold records, the scan's scope, and updating tools/kb from a project container."
tags: [work-item]
status: draft
kind: bug
work_status: done
priority: critical
depends_on: ["0010-13", "0010-11"]
links: 
  github: "https://github.com/CentralusLLC/kb-tools/pull/12"
  jira: ""
  paperclip: "CEN-34"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T06:15:49Z
---

# 0010-15: Upgrade path for projects set up before tools/kb.conf

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

The gameworld Developer reinstalled gameworld from `dev` at `b9aa775` using only the add-on
guide (CEN-35, gameworld PR #12). 0010-13 and 0010-11 work in a project container; four
findings remain against them:

- **16. Upgrading a project set up before `tools/kb.conf`.** Re-running the old install's
  `kb scaffold` does not write `tools/kb.conf`, and the new wrapper's `--install` then stops
  with "no kb-tools source". Fix: `--install` also reads the source from pip's record of an
  existing install, and the guide gives the order that works.
- **17. `kb scaffold` writes `ref=main`** even when kb-tools was installed from `dev`, so the
  next bare `tools/kb --install` drops to `main`. Fix: write the ref kb-tools was installed
  from (pip's record), `main` when unknown.
- **18. The scan reads untracked files**, which the docs did not say, and every Paperclip
  workspace has an untracked `.paperclip-runtime/` holding runtime MCP settings, so each
  project got a warning and `--strict` failed. Fix: skip `.paperclip-runtime/`, and document
  that untracked, not ignored files are scanned.
- **19. `kb scaffold` cannot update `tools/kb`**, so upgrading the wrapper needed a kb-tools
  checkout. Fix: `kb scaffold --tools-only` replaces `tools/kb` with the installed version's
  and adds a missing `tools/kb.conf`; `--install` says when the project's `tools/kb` differs.

## Acceptance criteria

- [x] `tools/kb --install` finds the source of an install made before `tools/kb.conf` (test).
- [x] `kb scaffold` writes the installed ref to `tools/kb.conf` (test).
- [x] `kb scaffold --tools-only` replaces only `tools/kb` and adds a missing `tools/kb.conf`;
      plain `kb scaffold` still never overwrites (tests).
- [x] `kb check` scans untracked, not ignored files but not untracked files in
      `.paperclip-runtime/`; a tracked file there is still scanned (tests). The security page
      and add-on guide say so.
- [x] The add-on guide has an upgrade section that a project can follow from its container.
- [x] The gameworld Developer confirms the upgrade path on CEN-35 once this is on `dev`
      (confirmed on `dev` `7f84de1`, gameworld PR #13).

## Notes

- Finding 20 (the deployed MCP server still returns `isError: false`) needs the Paperclip
  host's kb-tools sidecar to be redeployed from `dev`; that is a deployment step with board
  approval, not a code change.
- Work-tracking findings 7–13 and 15 belong to epic 0011.
