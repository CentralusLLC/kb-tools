---
type: Work Item
id: "0010-11"
epic: "0010"
title: "Audit for Centralus secrets and internal references"
description: "Find Centralus secrets and internal references (local LLM endpoints, hostnames, private IPs, internal URLs, IDs, names, tokens) in the tree and full history, fix each one, and add a repeatable scan."
tags: [work-item]
status: draft
kind: task
work_status: todo
priority: critical
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: ""
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

- local LLM references: endpoints, hosts and model names (local model server, local model server, `:<model-port>`,
  OpenAI-compatible base URLs);
- hostnames (the Paperclip host, `*.ts.net`);
- private IPs and ports (`<host-ip>`, <manager-port>, <port-range>);
- internal MCP URLs (`http://<kb-mcp-url>`);
- Paperclip and company IDs;
- internal people and project names;
- tokens and keys: gitleaks or trufflehog over the full history, plus GitHub secret scanning.

Known tree hits (2026-11-06): `devenv/` (`compose.yaml`, `kbdevenv/server.py` defaults),
`docs/environments/*`, epic 0010's plan and item 03, epic 0002, epic 0003 item 02, the release
notes, `docs/process/development.md`, `docs/process/project-management.md`, `pyproject.toml`
and `tests/test_kb.py`. The working tree has no local-LLM hits; history has not been checked.

## Acceptance criteria

- [ ] A findings list (file or commit, kind, action).
- [ ] Each finding is removed, made configurable (see 0010-13) or, for internal-only
      deployment notes worth keeping, moved to a Paperclip task document (not any repository).
- [ ] Any real secret found is rotated.
- [ ] A repeatable scan in CI or `kb check` prevents regressions.
- [ ] History findings are handed to the single 0010-10 rewrite.

## Notes

- Do this first: 0010-13 makes the deployment findings configurable, and 0010-10's rewrite
  depends on the history findings.
- Keep the findings list out of the public repository if it quotes the sensitive values;
  record kinds and locations, not the values (a Paperclip task document can hold more).
- Decided 2026-11-06 (owner via Chief, CEN-12/CEN-14): no private repository. Real non-secret
  values live only in the Paperclip host's untracked `.env`; real secrets, including any rotated ones, live
  in Paperclip secrets.
- Decided 2026-11-06 (owner, CEN-13): keep the devenv manager and the the Paperclip host deployment and
  make their settings configurable through environment variables (0010-13), rather than
  removing them.
