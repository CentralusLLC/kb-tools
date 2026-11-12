---
type: Work Item
id: "0010-05"
epic: "0010"
title: "Run the kb-tools test suite through a Paperclip SSH environment"
description: "Proves a Paperclip agent can run the kb-tools test suite in its remote dev container and push the result back to GitHub."
tags: [work-item]
status: draft
kind: spike
work_status: done
priority: medium
depends_on: []
links: 
  github: ""
  jira: ""
  paperclip: "CEN-6"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:34Z
---

# 0010-05: Run the kb-tools test suite through a Paperclip SSH environment

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

Question: can a Paperclip agent run the kb-tools test suite inside its remote dev container,
through a Paperclip SSH environment, and push its commits back to GitHub?

Answer: **yes** (Paperclip CEN-6, done 2026-11-05). The run below passed 18 tests in the dev
container and pushed commit `7e79ded` from it. Agent runs in the kb-tools project still execute
in that container (`devenv-kb-tools`).

## Acceptance criteria

- [x] Question answered: the run result below, the epic plan's
      [Verification](../plan.md#verification) section, and the setup in
      [Agent dev environments](../../../../environments/agent-dev-environments.md).

## Notes

The one follow-up, `tools/kb` not working inside dev containers, was solved by
[0010-14](14-kb-cli-available-inside-project-dev-containers.md).

### Run result, 2026-11-05 (Paperclip CEN-6)

The kb-tools Developer agent ran this through Paperclip's SSH environment:

- **Where:** `hostname` `devenv-kb-tools`, user `agent`, run workspace
  `/home/agent/workspace/.paperclip-runtime/runs/1c1270d1-…/workspace`. The container is
  the Dockerfile `dev` stage (PyYAML, python-docx, python-pptx, openpyxl, Pillow, mcp and
  `soffice` present). `pip show kb-tools`: not installed in the image.
- **Branch:** `git fetch origin` through the Paperclip GitHub broker worked. Checked out
  `0010-agent-dev-environments` at `1a46eca`.
- **Tests:** `python -m pytest -q -p no:cacheprovider` → **18 passed, 0 failed, 0 skipped**
  in 9.88s (wall time 11.0s). LibreOffice tests ran; nothing was skipped.
- **Workspace import:** a probe test run with the repository's pytest config printed
  `kbtools` from `<run workspace>/src/kbtools/__init__.py`. Without pytest's
  `pythonpath = ["src"]`, `import kbtools` fails, so no copy is installed in the image.
- **`tools/kb check`:** exits 1 in the container with `kb: Docker image kb-tools:latest not
  found`. The wrapper runs kb-tools through Docker, and the dev container has no Docker.
  The in-container equivalent, `PYTHONPATH=src python -m kbtools.cli check`, printed
  `0 errors, 0 warnings` (exit 0, 0.4s).
- **Earlier attempt (run `0a35d3e5`):** blocked. The container was the default overlay
  image (`ModuleNotFoundError: No module named 'yaml'`), and the GitHub broker was
  unreachable (`broker_transport_unavailable`). Chief fixed both by running `devenv_rebuild`
  and opening the agentdev firewall to Paperclip's API port.

Open: `tools/kb` doesn't work inside dev containers. Either fall back to
`python -m kbtools.cli` when `docker` is absent, or document the in-container command.
This commit, pushed from the container, is the "commits come back" proof.
