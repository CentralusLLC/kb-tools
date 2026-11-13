---
type: Work Item
id: "0010-11"
epic: "0010"
title: "Audit for Centralus secrets and internal references"
description: "Find Centralus secrets and internal references (local LLM endpoints, hostnames, private IPs, internal URLs, IDs, names, tokens) in the tree and full history, fix each one, and add a repeatable scan."
tags: [work-item]
status: draft
kind: task
work_status: in_review
priority: critical
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-34"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-06T12:54:25Z
---

# 0010-11: Audit for Centralus secrets and internal references

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

Before kb-tools goes public, nothing internal to Centralus may remain in the tree or history.
The audit produces a findings list, fixes the tree, and hands history findings to the single
rewrite in 0010-10.

Check for:

- local LLM references: endpoints, hosts and model names (local model servers, their
  default ports, OpenAI-compatible base URLs);
- host names (the Paperclip host, tailnet names);
- private IPs and published ports;
- internal MCP URLs;
- Paperclip and company IDs;
- internal people and project names;
- tokens and keys: gitleaks or trufflehog over the full history, plus GitHub secret scanning.

Known tree hits (2026-11-06): `devenv/` (`compose.yaml`, `kbdevenv/server.py` defaults),
`docs/environments/*`, epic 0010's plan and item 03, epic 0002, epic 0003 item 02, the release
notes, `docs/process/development.md`, `docs/process/project-management.md`, `pyproject.toml`
and `tests/test_kb.py`. The working tree has no local-LLM hits; history has not been checked.

## Acceptance criteria

- [x] A findings list (file or commit, kind, action).
- [x] Each finding is removed, made configurable (see 0010-13) or, for internal-only
      deployment notes worth keeping, moved to a Paperclip task document (not any repository).
- [x] Any real secret found is rotated. (None found.)
- [x] A repeatable scan in CI or `kb check` prevents regressions.
- [x] History findings are handed to the single 0010-10 rewrite.

## Findings (2026-11-13)

Kinds and locations only. The values, with the history replacement list for 0010-10, are in
the Paperclip task document `audit-findings` on CEN-34.

Scanned: the tree on `dev` at `7c72bb2`, and the full history (all branches, pull request
refs and the v0.1.0 tag, 32 commits) with gitleaks 8.30.1 and with `git log -G` for each kind.

**Secrets:** gitleaks found none in the tree or history, so nothing needed rotating. The only
key-shaped text is a private-key header used as test data in `devenv/tests/test_server.py`,
now marked `kb-scan: allow`.

**Tree (fixed in this item):**

| Location | Kind | Action |
| --- | --- | --- |
| `docs/process/development.md`, `docs/releases/*`, epics 0002 and 0010 (plan, items 03, 10, 11, 13) | Paperclip host name | replaced with "the Paperclip host" |
| epic 0010 `plan.md` (Design) | private IP and published ports | placeholders and the `DEVENV_*` settings |
| epic 0010 `plan.md` (Alternatives) | internal account name | reworded |
| `docs/process/development.md` | internal account path | reworded |
| `docs/releases/v0.1.0.md`, epic 0003 `plan.md` | internal MCP URL | `<kb-mcp-url>` |
| epic 0010 item 05 | Paperclip run id | `<run-id>` |
| item 11 (this item) | example host, IP, ports, MCP URL, local LLM names | described by kind |
| `tests/test_kb.py` (verified entry) | person name | `human:reviewer` |
| `tests/test_deployment.py` | private IP as test data | documentation address (`192.0.2.1`) |

**Left for 0010-10:** the references that item purges, and the template-leak guard word list in
`tests/test_kb.py` (it also names a person); `KB_SCAN_DENYLIST` gives that guard a home outside
the repository.

**Kept on purpose (Chief/board to confirm):**

- The owner's public organisation name and the public repository URL: `pyproject.toml`
  authors, the fallback install source in `src/kbtools/version.py`, the license holder
  (0010-12), and clone URLs in work items.
- Paperclip issue identifiers (`CEN-n`) in work items and docs. They are the work items'
  `links.paperclip` field by design and resolve only inside the owner's Paperclip instance.
  No Paperclip or company UUIDs are in the tree or history.

**History only (for the 0010-10 rewrite):** the Paperclip host name (15 commits), the tailnet
host name and a tailnet IP address (6), the private IP (7) and published ports (6), the
internal MCP URL (5), an internal service URL with its port, internal account paths (3),
a person's name in docs and tests (6), and local LLM names (1, in this item's old text).
Commit metadata: 14 commits carry a company and a personal e-mail address as author and
committer; a `.mailmap`-based rewrite to the GitHub no-reply address is proposed.

**Regression scan:** `kb check` now runs `kbtools/scan.py` over tracked files: secrets are
errors; private and tailnet addresses and tailnet host names are warnings; organisation-
specific names come from a deny list outside the repository (`KB_SCAN_DENYLIST`). With the
owner's deny list, the tree is clean apart from the 0010-10 items above.

## Notes

- Do this first: 0010-13 makes the deployment findings configurable, and 0010-10's rewrite
  depends on the history findings.
- Keep the findings list out of the public repository if it quotes the sensitive values;
  record kinds and locations, not the values (a Paperclip task document can hold more).
- Decided 2026-11-06 (owner via Chief, CEN-12/CEN-14): no private repository. Real non-secret
  values live only in the Paperclip host's untracked `.env`; real secrets, including any rotated ones, live
  in Paperclip secrets.
- Decided 2026-11-06 (owner, CEN-13): keep the devenv manager and the Paperclip host deployment and
  make their settings configurable through environment variables (0010-13), rather than
  removing them.
