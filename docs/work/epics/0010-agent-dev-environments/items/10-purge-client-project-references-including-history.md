---
type: Work Item
id: "0010-10"
epic: "0010"
title: "Purge client-project references from the repository, including history"
description: "Remove every reference to an earlier client project from the working tree and from git history with one filter-repo rewrite, approved by the owner before the force-push."
tags: [work-item]
status: draft
kind: chore
work_status: in_progress
priority: critical
depends_on: ["0010-11", "0010-13"]
links: 
  github: ""
  jira: ""
  paperclip: "CEN-34"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-06T12:54:24Z
---

# 0010-10: Purge client-project references from the repository, including history

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

kb-tools is going public. kb-tools was ported from an earlier client project, whose name
must not appear in the tree or in git history. The name itself is kept out of the repository:
it is an entry in the scan deny list (`KB_SCAN_DENYLIST`, outside the repository; the
suggested list is in the Paperclip `audit-findings` document on CEN-34). This is the single history rewrite for the public release: it also removes
the history findings from the audit (0010-11), so the repository is rewritten and force-pushed
only once.

Known tree hits (2026-11-06):

- `README.md:12`
- `docs/business/vision.md:21`
- `docs/releases/v0.1.0.md:18`
- `docs/catalog.md` (the 0006 row)
- epics 0006 and 0008 (`epic.md` and `plan.md`)
- `tests/test_kb.py:191`, the template-leak guard word list, which also named other
  internal names
- this item itself (title, file name, and its rows in `docs/work/index.md` and
  `docs/catalog.md`): retitle or generalise it as part of the purge

## Acceptance criteria

- [x] `git grep -i` for the client-project name (deny-list entry) is empty, and `kb check` with
      `KB_SCAN_DENYLIST` set reports no deny-list hit.
- [x] `git log --all -p -i -G <name>` is empty after a `git filter-repo` rewrite
      (`--replace-text` and `--replace-message`) over all branches and tags, including v0.1.0.
- [x] The template-leak guard still works without naming internal projects in the repository
      (for example an untracked or environment-supplied denylist).
- [x] The owner explicitly approves the force-push before it happens.
- [ ] Open PRs, other clones (the Paperclip host's sidecar, agent workspaces, dev containers) and the v0.1.0
      provenance (commit 449e64f, now b22e03b) are listed, and each is handled (rebased, re-cloned or
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

## Progress

Two steps, both for board review through Chief:

1. **Tree purge (pull request into `dev`).** Done when it merges:
   - the README, vision and v0.1.0 notes, and epics 0006 and 0008 say "an earlier project" instead of the name;
   - this item is retitled and renamed;
   - the template-leak guard in `tests/test_kb.py` applies the generic scan rules and, when `KB_SCAN_DENYLIST` is set, the deny list. It no longer names anything.
2. **History rewrite.** This is prepared and verified on a copy and reported on CEN-34. It is **not pushed**: the force-push of `main`, `dev` and the tags waits for the board's explicit approval.
   - It uses the `--replace-text` list from the 0010-11 audit, so the history findings are removed in the same single rewrite.
   - The board decided (CEN-40) to rewrite the commit author e-mails to the GitHub no-reply
     address with `--mailmap` in the same rewrite, and to keep the display name.
3. **Force-push (2026-11-13, approved by the board on CEN-12).** The rewrite was re-run on a fresh
   mirror and gave exactly the approved commits, then pushed atomically with a lease on every ref:
   - `dev` a37b076 → c6d2556, `main` fbbb800 → a62e948, tag `v0.1.0` 449e64f → b22e03b.
   - `0010-agent-dev-environments` is kept (rewritten; its `[0010-03]` commit is not on `dev`).
     The other ten merged work branches are deleted.
   - The deny-list audit over all refs of a fresh clone is 0. Author and committer e-mails are only
     the GitHub no-reply addresses.
   - This pull request updates the commit ids cited in the docs.
4. **Sidecar rebuilt (2026-11-13, deploy approved by the board on CEN-12).** The Paperclip host's
   kb-tools sidecar was rebuilt from the rewritten `main` 59a7906 (the release merge of PR #2), so
   it no longer runs a pre-rewrite build. Recorded in the
   [v0.1.0 Deployments table](../../../../releases/v0.1.0.md#deployments).
   - Image `sha256:ec1e69377e4c74a18c66ca8883535b95a71fb910c98831fcaf8a4cce00107903` replaces
     `sha256:a98e04feb2937533624e6ac34413bb6d894e0ee97ae09340431d840160f1ee94` (the fbd2c21 build).
   - The full suite passed in the `dev` image (83 passed). The `test` stage was skipped because it
     could not run the newer tests; [0010-17](17-dockerfile-test-stage-runs-the-full-suite-git-an.md) fixed it.
   - The container is healthy with 0 restarts, and its settings (`KB_REPOS_ROOT`, `KB_ALLOWED_ROOTS`,
     `KB_MCP_HOST`) are unchanged.
   - MCP check: 13 tools. `kb_catalog` and `kb_report` work for `repo=gameworld` and by full path;
     `/etc` is refused; an unknown repository name gives the `KB_REPOS_ROOT` error. From Paperclip,
     `kb_check repo=gameworld` returns 0 errors (3 private-address warnings from the new scan).
   - The pre-rebuild rollback image is removed now that the build is confirmed.

Still open before this item is done (the last acceptance criterion):
- GitHub Support has to remove the cached `refs/pull/*` of PRs #1–#14, which still point at the
  old commits. This must happen before the repository is made public.
- Every older clone is re-cloned or hard-reset. The Paperclip host's sidecar is done (step 4);
  still to confirm: agent workspaces, the `devenv-kb-tools` container, and gameworld's `tools/kb`
  install (`tools/kb --install` again).

