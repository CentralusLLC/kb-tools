# tools/

Scripts that agents and people run instead of writing one-off code.

## kb (knowledge-base tools)

`tools/kb` runs the shared **kb-tools** Docker image (the `kb-tools`
repository) against this repository. It handles document ingestion (inventory,
extraction, renders, figures, ingest log) and knowledge-base checks and trust reports.
Its only requirement is Docker.

One-time setup per machine:

```sh
git clone <kb-tools repository> ~/workspace/kb-tools
docker build -t kb-tools:latest ~/workspace/kb-tools
```

Everyday use, from anywhere in this repository:

```sh
tools/kb inventory --by human:<name> --origin "<where the files came from>"
tools/kb extract --pending
tools/kb figure extracted/<pkg>/renders/page-003.png --crop <l,t,r,b> --out docs/<section>/assets/<name>.png --page docs/<section>/<page>.md
tools/kb log <source> --status ingested --by <you> --outputs "<path>;<path>"
tools/kb check
tools/kb report
```

The method these commands support is [docs/process/ingestion.md](../docs/process/ingestion.md).
Paperclip agents use the same commands as `kb_*` MCP tools.

`tools/kb` is copied from `kb-tools/bin/kb`; update it from there.

## Adding a tool

- Ask before adding new tooling ([agent workflow](../docs/process/agent-workflow.md#ask-before-you-build)).
- If it is useful beyond this project, add it to kb-tools instead.
- Each tool gets a short entry in this file covering what it does, how to run it, and its
  requirements.
