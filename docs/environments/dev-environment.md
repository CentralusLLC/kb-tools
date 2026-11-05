---
type: Environment
title: Dev environment
description: "kb-tools' development environment: the Dockerfile's dev stage via .devcontainer, with LibreOffice, fonts and test tools; how people and agents run the tests in it."
tags: [environments, development, devcontainer, agents]
status: stable
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T00:00:00Z
---

# Dev environment

kb-tools' dev environment is the `dev` stage of its [Dockerfile](../../Dockerfile), referenced by
[`.devcontainer/devcontainer.json`](../../.devcontainer/devcontainer.json). It has Python 3.12,
LibreOffice, the Office-compatible fonts, every runtime and test dependency, git and make, but
**not** kb-tools itself, so tests always import the workspace's `src/`.

- **People:** open the repository in VS Code (Dev Containers) or Codespaces; or run
  `docker build --target dev -t kb-tools:dev . && docker run --rm -v "$PWD:/workspace" kb-tools:dev python -m pytest -q`.
- **Agents in Paperclip:** the kb-tools project's agent dev container (`devenv-kb-tools`, built by
  the devenv manager) runs this image plus the agent overlay. Run `python -m pytest -q` in the
  workspace. See [Agent dev environments](agent-dev-environments.md) for how it is operated.

Installing packages: Python dependencies go in `pyproject.toml`; system packages go in the
Dockerfile's `base` stage (needed at run time) or `dev` stage (development only). In Paperclip,
`devenv_install` installs them immediately with approval; the pull request makes them permanent.
