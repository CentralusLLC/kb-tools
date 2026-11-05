---
type: Environment
title: Dev environment
description: "{{PROJECT}}'s development environment, defined in .devcontainer/ and used by people and AI agents alike; how agents get one, install packages, and run tests in it."
tags: [environments, development, devcontainer, agents]
status: draft
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Dev environment

The development environment is **defined in the repository**, in [`.devcontainer/`](../../.devcontainer/devcontainer.json)
(the standard devcontainer format). People open it in VS Code or Codespaces; agents get the
same environment as a dedicated container. Every test, build and tool the project needs runs
there, so nobody depends on an outside service to test.

> TODO: Add the project's toolchain to `.devcontainer/Dockerfile`, and list the test and build
> commands in [Local development](local.md).

## Agents (agent platforms such as Paperclip)

- Each project has one agent dev container, built from `.devcontainer/` by the **devenv manager**
  (`devenv_*` MCP tools), with sshd, node and the claude CLI added on top. The agent platform runs
  the agent inside it through an SSH execution environment.
- **No environment yet?** Call `devenv_create` with the project name and repository URL (it needs
  approval), poll `devenv_status`, then post the Paperclip environment settings it returns on the
  issue: an instance admin registers the SSH environment and assigns it to the project.
- **Project dependencies** (Python packages with `uv`, npm packages): install them yourself in
  the workspace and commit the lockfile changes; no approval needed.
- **System packages** (apt): call `devenv_install` with a reason (it needs approval), then add the
  packages to `.devcontainer/Dockerfile` in a pull request so the environment stays reproducible.
- **After `.devcontainer/` changes reach the default branch,** call `devenv_rebuild`.

## Rules

- Run the tests in the dev environment before every pull request ([Testing](../process/testing.md)).
  If you cannot (missing tools, wrong environment), fix the environment as above. Do not skip
  tests or push them to outside CI.
- Never install tools outside `.devcontainer/` that the project then silently depends on.
