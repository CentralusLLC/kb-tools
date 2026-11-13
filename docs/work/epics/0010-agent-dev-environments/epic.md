---
type: Epic
id: "0010"
title: "Agent dev environments"
description: "Agents build and test each project inside its own dev container on the Paperclip host, instead of in the Paperclip container or not at all."
tags: [epic]
status: draft
work_status: in_progress
priority: critical
owner: ""
target: ""
links: 
  github: ""
  jira: ""
  paperclip: ""
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-05T07:12:28Z
---

# Epic 0010: Agent dev environments

## Problem / business need

Paperclip agents ran in the Paperclip server's own container. It has none of a project's
toolchain (kb-tools needs LibreOffice and its fonts, for example), and installing packages there
means a custom Paperclip image and a restart for every package. So agents either couldn't run
the tests or relied on outside CI. Giving them Docker would hand them every container on the
host, including Paperclip's database and secrets. Agents now write most of the code, so every
untested change costs a review cycle.

## Outcome and success measures

Every project gets an isolated dev container, built from its own `.devcontainer/`, that its
agents run in through Paperclip's SSH execution environment and can set up themselves (with
approval for installs). Measured by:

- an agent run in a project's dev container runs that project's tests and pushes its commit
  (done for kb-tools on 2026-11-05: 0010-05, CEN-6);
- a new project gets an environment without changes to Paperclip (0010-08);
- agents run `tools/kb` in their dev container (0010-14);
- kb-tools can be published and installed in any Paperclip environment (0010-10..13, 0010-15, 0010-16).

## Scope

- Host side: the isolated `agentdev` account with rootless Docker and egress rules (0010-01), the
  agent overlay (0010-02), the devenv manager and its MCP tools (0010-03), approval-gated
  installs (0010-06).
- kb-tools' own dev container (0010-04, trial in 0010-05), the scaffold template's
  `.devcontainer/` (0010-07), detecting projects without an environment (0010-08), and the kb CLI
  inside project dev containers (0010-14).
- Public-release prep, so other Paperclip environments can install kb-tools: audit (0010-11),
  configurable settings (0010-13), history purge (0010-10), licence (0010-12), upgrade path
  (0010-15), Librarian process (0010-16).
- Later: a sandbox-provider plugin (0010-09).

## Non-goals

- A shared Paperclip image with every project's toolchain, or Docker socket access for agents
  (both rejected in the [plan](plan.md#approach)).
- Running Paperclip itself in a dev container, or changing Paperclip's code (platform problems
  such as CEN-8 go to the Paperclip maintainers).
- CI for project repositories (epic 0004).

## Acceptance

The board accepts, through Chief, by reviewing the success measures: the SSH trial and the
items' evidence for the dev containers, and the public-release items for installing kb-tools
elsewhere. Record the acceptance here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
