# tools/

Scripts that agents and people run instead of writing one-off code.

## kb (knowledge-base tools)

`tools/kb` runs the shared **kb-tools** (the `kb-tools` repository) against this
repository. It handles document ingestion (inventory, extraction, renders, figures, ingest
log) and knowledge-base checks and trust reports. It uses the kb-tools Docker image when
Docker has it, and otherwise a local install (dev containers, which have no Docker).

One-time setup per machine with Docker:

```sh
git clone <kb-tools repository> ~/workspace/kb-tools
docker build -t kb-tools:latest ~/workspace/kb-tools
```

One-time setup in a dev container (no Docker; see
[Dev environment](../docs/environments/dev-environment.md#kb-tools-in-the-dev-container)):

```sh
tools/kb --install          # light install; the source is in tools/kb.conf
```

The light install has `check`, `work`, `catalog`, `report`, `log` and `inventory`.
`extract` and `figure` run on the Paperclip machine (or after `tools/kb --install --full`).

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
Agents on the Paperclip machine (such as the agent that ingests documents) have the same
commands as `kb_*` MCP tools; those tools only see checkouts on that machine, so agents in
this project's containers use `tools/kb`.

`tools/kb` is copied from `kb-tools/bin/kb`; update it from there. `tools/kb.conf` says where
`tools/kb --install` gets kb-tools from (`source=`) and which ref (`ref=`).

## Adding a tool

- Ask before adding new tooling ([agent workflow](../docs/process/agent-workflow.md#ask-before-you-build)).
- If it is useful beyond this project, add it to kb-tools instead.
- Each tool gets a short entry in this file covering what it does, how to run it, and its
  requirements.
