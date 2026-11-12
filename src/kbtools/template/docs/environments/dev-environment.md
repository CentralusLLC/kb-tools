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
- **No environment yet?** Generate an ed25519 key pair and submit the private key as a secret
  proposal (never print it). Call `devenv_create` with the project name, the public key and the
  secret's name (it needs approval), poll `devenv_status`, then post the Paperclip environment
  settings it returns on the issue for whoever registers environments. After the first run in it
  has synced the repository, call `devenv_rebuild` to build `.devcontainer/`.
- **Project dependencies** (Python packages with `uv`, npm packages): install them yourself in
  the workspace and commit the lockfile changes; no approval needed.
- **System packages** (apt): add them to `.devcontainer/Dockerfile` in a pull request, then call
  `devenv_rebuild` (it needs approval and uses the files in your workspace). If you are blocked
  now, `devenv_install` with a reason installs them at once (approval), but still make the pull request.
- **Rebuilds wait for you:** the container is replaced only after no agent session is running in
  it, so finish your run; the next run gets the new environment.

## kb-tools in the dev container

The dev container has no Docker, so `tools/kb` uses a local kb-tools install instead of the
Docker image. Install it once per container volume; it goes into `~/.kb-tools` in the
container user's home (`/home/agent/.kb-tools` for agents), which persists across runs:

```sh
KB_TOOLS_SOURCE=git+https://github.com/<owner>/kb-tools tools/kb --install main
tools/kb check
```

- `main` is kb-tools' release branch. Pass a tag or branch instead to pin another version;
  run the same command again to update (it replaces the install).
- The install needs Python 3.11 or later, git and network access, and credentials for the
  kb-tools repository if it is private (an agent run's GitHub credentials work).
- It is a full install (about 330 MB). `check`, `catalog`, `work`, `report`, `inventory` and
  `log` work fully. `extract` and `figure` also use LibreOffice and fonts for some formats,
  which this image doesn't have unless the project adds them.
- `KB_TOOLS_HOME` changes the install location; `KB_TOOLS_REF` the default ref.

## Rules

- Run the tests in the dev environment before every pull request ([Testing](../process/testing.md)).
  If you cannot (missing tools, wrong environment), fix the environment as above. Do not skip
  tests or push them to outside CI.
- Never install tools outside `.devcontainer/` that the project then silently depends on. The
  kb-tools install above is the documented exception: it is knowledge-base tooling, not
  something the project's build or tests depend on.
