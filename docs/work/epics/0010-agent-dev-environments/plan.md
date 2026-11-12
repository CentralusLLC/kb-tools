---
type: Implementation Plan
epic: "0010"
title: "Plan: Agent dev environments"
description: "How agents get complete dev environments in Paperclip: an isolated account, a devenv manager building per-project dev containers from .devcontainer, Paperclip SSH environments, and approval-gated installs."
tags: [plan]
status: draft
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:28Z
---

# Plan: Agent dev environments

## Approach

Agents run inside per-project dev containers through Paperclip's SSH execution environment
(the claude_local adapter supports remote targets and seeds its config and credentials there).
Containers are built from each repository's `.devcontainer/` plus an agent overlay, by a
devenv manager exposed over MCP. Paperclip only lets instance admins register environments,
so the owner does one registration step per project; everything else is done by the agent
through Paperclip approval cards.

Revised 2026-11-05 (after Chief's review of native Paperclip features): the manager holds no
GitHub credential and never clones. Paperclip already syncs the worktree into SSH environments
and writes commits back, and its managed GitHub launchers handle pushes, so the manager builds
`.devcontainer/` from the synced worktree. Keys are per project: the agent generates them and
stores the private half through a secret proposal. Lifecycle tools are gated with "ask first".

Alternatives rejected:
- A custom Paperclip image with all toolchains: one image for every project, and a Paperclip
  restart for every package.
- Giving agents the Docker socket: control of every centralus container, including the database
  and secrets.
- A sandbox-provider plugin: the most native option, deferred until this has proven itself
  (0010-09, backlog). Paperclip ships providers for Kubernetes, Daytona, E2B and others, but
  none for plain Docker.
- A read-only GitHub token or per-call clone tokens for the manager: a long-lived credential on
  the Paperclip host, or raw tokens in agent hands, which Paperclip's managed GitHub design avoids.

## Design

See [Agent dev environments](../../../environments/agent-dev-environments.md):
- account `agentdev` (its own uid) with rootless Docker and org egress rules;
- manager on `<host-ip>:<manager-port>`, protected by a bearer token;
- dev containers on `<host-ip>:<port-range>`, each with a home volume, stable host keys and limits;
- tools: `devenv_status`, `devenv_create`, `devenv_rebuild`, `devenv_install` (system packages,
  persisted for rebuilds), `devenv_stop`, and `devenv_delete` (destructive, so Paperclip
  quarantines it).

## Items and sequencing

Public-release prep (first): 0010-11 audit → 0010-13 make deployment-specific settings
configurable → 0010-10 purge with a single history rewrite → 0010-12 license.

1. Done: account (0010-01), overlay (0010-02), kb-tools dev target (0010-04), the manager
   (0010-03, deployed and used through Paperclip), the SSH trial (0010-05, CEN-6), and
   detecting projects without an environment (0010-08, through the agent workflow rule).
2. Blocked: approval-gated installs (0010-06). "Ask first" is set, but Paperclip doesn't
   enforce it (CEN-8, a Paperclip platform problem).
3. To do: a scaffold test for the template's `.devcontainer/` (0010-07); the template files
   are done.
4. kb CLI in project dev containers (0010-14, CEN-23): built as option a with a full install
   (board, 2026-11-12); gameworld adopts it next.

## kb CLI in project dev containers (0010-14)

Board decision on CEN-5 (2026-11-07): agents inside a project's dev container must be able to
run `kb check`, `kb catalog`, `kb work` and `kb report` on that repository. `tools/kb` needs
Docker, which dev containers lack by design, and the kb-tools MCP server reads only host paths.
The install mechanism needs the board's choice (CEN-23) before building.

Facts checked 2026-11-07 in the kb-tools dev container:

- `check`, `catalog`, `work` and `report` run with only PyYAML installed. A full install
  (markitdown, pdfium, magika and so on) is 326 MB and 42 packages; PyYAML alone is 17 MB.
  `extract` and `figure` also need LibreOffice and fonts, which project images don't have.
- `pip install git+https://github.com/CentralusLLC/kb-tools@<ref>` works in a container run
  through Paperclip's GitHub credentials (13 s for a full install).
- In a Paperclip run, `$HOME` is a per-run temporary directory. `/home/agent` is the persistent
  volume. A default `uv tool install` or `pip install --user` would therefore be lost after the
  run and isn't on `PATH`, so a run-time install must name its location explicitly.

Options:

| Option | How | Works today | Cost |
| --- | --- | --- | --- |
| a. Run-time install | The template's dev-environment page documents one command that installs kb-tools into a venv on the persistent home volume (`/home/agent/.kb-tools`), pinned to a ref (`main`, the release branch, by default). The template's `tools/kb` uses that install when Docker is missing, so `tools/kb check` works on the host and in the container. | Yes | Each agent runs one step once per container volume. Updates are manual (re-run with a new ref). |
| b. Build-time install | One `RUN pip install ...` line in the template's `.devcontainer/Dockerfile`. | No: the repository is private and the image build has no GitHub credential. Possible after 0010-10..13. | Pinned at image build; a rebuild updates it. |
| c. Published package or image | Install from PyPI or GHCR (epic 0002). | No | Needs release and versioning work first. |
| d. Vendor into each project | Copy kb-tools' source into the project repository. | Yes | Rejected: copies drift and every project carries kb-tools code. |

Light install: rather than changing kb-tools' dependencies now, install with `--no-deps` plus
PyYAML. That needs no packaging change. A test then guards that `check`, `catalog`, `work` and
`report` import without the extraction dependencies. A proper `kb-tools[extract]` extra
belongs with packaging in epic 0002.

Proposal: a now, with the light install. When the repository is public, add b as the same
command moved into the template Dockerfile, with no credential needed. Move to c with epic 0002.

Board decision (CEN-23, 2026-11-12): option a; no light install, a full install with every
dependency; default ref `main`.

Built: `tools/kb` (= `bin/kb`) uses the Docker image when Docker has it, otherwise
`$KB_TOOLS_HOME/bin/kb`. `tools/kb --install [ref]` creates that install: a venv (recreated
each time) with `pip install $KB_TOOLS_SOURCE@<ref>`. `KB_TOOLS_HOME` defaults to `.kb-tools`
in the user's home from the password database (`/home/agent` in agent containers), not
`$HOME`. The source URL comes from `KB_TOOLS_SOURCE` because the template stays free of
deployment values. The template's dev-environment page documents the step.

## Risks and open questions

- The public-release history rewrite (0010-10) force-pushes every branch and tag and changes
  all commit hashes: it needs the owner's explicit approval first, happens only once (with the
  0010-11 audit's history findings, after 0010-13 has made the deployment values
  configurable), and every clone, open PR and the v0.1.0 tag must be
  re-synced afterwards.
- Paperclip's SSH driver is its least-exercised path; probe after registration and keep "local"
  as the fallback.
- Approval: the connection does not gate write tools by default (kb-tools' `kb_init` ran
  without approval), so a Paperclip policy must require approval for `devenv_create`,
  `devenv_rebuild` and `devenv_install`.
- Rebuilding replaces the container, which would end the calling agent's own session, so the
  swap waits until no `agent` process runs (up to 6 hours, `DEVENV_SWAP_WAIT`).
- The build context is agent-controlled (the synced worktree). Builds run in the isolated
  rootless Docker, the context is extracted with tarfile's data filter, and devcontainer paths
  must stay inside the repository; the approval card is the human gate.
- kb-tools still uses the shared fallback key; move it to its own key.
- Images are large (kb-tools' is about 2 GB); watch disk space in the agentdev account.

## Verification

- 2026-11-05: from the Paperclip container, SSH as `agent` reached the kb-tools dev container,
  which has node 22, Claude Code 2.1.318, git and LibreOffice and no sudo; `python -m pytest`
  passed 18 tests in 5.5 s.
- 2026-11-12 (0010-14), in the kb-tools dev container without Docker: a freshly scaffolded
  project ran `tools/kb --install` from GitHub `main` with the run's credentials (17 s,
  326 MB, kb-tools 0.1.0), then `tools/kb check` (0 errors, 0 warnings), `work list`,
  `catalog` and `report` through the local install.
- 2026-11-05 (0010-05, CEN-6): an agent run through the registered Paperclip SSH environment
  executed in `devenv-kb-tools`, passed 18 tests and pushed its commit (`7e79ded`) back.
