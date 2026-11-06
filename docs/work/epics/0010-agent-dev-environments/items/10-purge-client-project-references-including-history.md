---
type: Work Item
id: "0010-10"
epic: "0010"
title: "Purge client-project references from the repository, including history"
description: "Remove every client-project reference from the working tree and from git history with one filter-repo rewrite, approved by the owner before the force-push."
tags: [work-item]
status: draft
kind: chore
work_status: todo
priority: critical
depends_on: ["0010-11", "0010-13"]
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-06T12:54:24Z
---

# 0010-10: Purge client-project references from the repository, including history

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

kb-tools is going public. client-project is a client/project name and must not appear in the tree
or in git history. This is the single history rewrite for the public release: it also removes
the history findings from the audit (0010-11), so the repository is rewritten and force-pushed
only once.

Known tree hits (2026-11-06):

- `README.md:12`
- `docs/business/vision.md:21`
- `docs/releases/v0.1.0.md:18`
- `docs/catalog.md` (the 0006 row)
- epics 0006 and 0008 (`epic.md` and `plan.md`)
- `tests/test_kb.py:191`, the template-leak guard word list, which also names gameworld,
  centralus and reviewer
- this item itself (title, file name, and its rows in `docs/work/index.md` and
  `docs/catalog.md`): retitle or generalise it as part of the purge

## Acceptance criteria

- [ ] `git grep -i client-project` is empty.
- [ ] `git log --all -p -i -G client-project` is empty after a `git filter-repo` rewrite
      (`--replace-text` and `--replace-message`) over all branches and tags, including v0.1.0.
- [ ] The template-leak guard still works without naming internal projects in the repository
      (for example an untracked or environment-supplied denylist).
- [ ] The owner explicitly approves the force-push before it happens.
- [ ] Open PRs, other clones (the the Paperclip host sidecar, agent workspaces, dev containers) and the v0.1.0
      provenance (commit 449e64f) are listed, and each is handled (rebased, re-cloned or
      re-tagged).

## Notes

- Rewrite history once, combined with 0010-11's history findings; don't start this before
  the audit's findings list exists and 0010-13 has made the deployment values configurable
  (so the rewrite can replace the old values in history too).
- A rewrite changes every commit hash: the v0.1.0 tag, release notes and any links to
  commits need updating, and every clone must be re-cloned or hard-reset.
- Open question: whether the leak guard's denylist lives in an untracked file or an
  environment variable. There is no private repository (decided 2026-11-06), so it must not
  rely on one; if CI needs it, supply it as a secret.
