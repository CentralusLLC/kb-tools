# Environments

Where kb-tools runs. Each environment page says what runs there, how to set it up and
deploy to it, and who has access. Never put secrets here; say where they are stored.

- [Dev environment](dev-environment.md): the `.devcontainer/` (Dockerfile `dev` stage) where tests run.
- [Install kb-tools as an add-on in a Paperclip environment](paperclip-add-on.md): the MCP server on the Paperclip machine, the light `tools/kb` install in project containers, and how a project starts.
- [Agent dev environments](agent-dev-environments.md): the devenv manager and per-project agent dev containers on the Paperclip host.
- [Local development](local.md): running the project on your own machine.
- [Configuration](configuration.md): every setting, its purpose and neutral default (no deployment values or secrets).
- [Cloud and hosted environments](cloud.md): deployment targets, and what each environment page records.
