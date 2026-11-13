# kb-tools

Shared tooling for repositories that keep an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog)
(OKF) knowledge base in `docs/`. It turns source documents (PowerPoint, Word, PDF,
Excel, images) into auditable extraction packages, helps curate key graphics into
the knowledge base, and checks and reports on the knowledge base's trust.

It runs in Docker, so it works the same on a laptop, in CI, and next to Paperclip
agents. The image bundles LibreOffice and a font set for faithful rendering.

The method behind it (preserve, extract, render, reconcile, normalise, write) was
worked out on earlier projects. Each project documents it in `docs/process/ingestion.md`.

## Build

```sh
docker build -t kb-tools:latest .            # runtime image
docker build --target test -t kb-tools:test . # runs the test suite
```

## Start a new project

`kb scaffold` installs a generic knowledge-base layout into a repository. It never
overwrites existing files. Run it once with kb-tools' own wrapper, since the project has
no `tools/kb` yet:

```sh
cd <project repository>
~/workspace/kb-tools/bin/kb scaffold --project "Project Name"   # --dry-run to preview
tools/kb check
```

It installs:

| Path | Contents |
| --- | --- |
| `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/pull_request_template.md` | Agent entry points that point into `docs/` (existing files are kept; the command prints a snippet to add) |
| `docs/index.md`, `catalog.md`, `log.md`, `conventions.md` | OKF v0.2 bundle root, change log, conventions (verification and trust, figures, diagrams) |
| `docs/architecture/` | System overview, quality attributes (non-functional requirements), research-data conventions, decisions with ADR 0001 (adopting the knowledge base) |
| `docs/design/` | User flows, screens and the design system |
| `docs/user/` | User-facing documentation (publishable on its own) |
| `docs/business/` | Vision, audience, branding, business model and rules |
| `docs/domains/` | Glossary, plus how to add topic sub-wikis |
| `docs/environments/` | Local development, configuration reference, cloud and hosted environments |
| `docs/process/` | Agent workflow (rules, precedence, trust), development, testing, security, project management, work tracking, release notes, operations, ingestion, knowledge-base maintenance |
| `docs/releases/` | Release notes: `unreleased.md` (filled as items complete) and one page per release with a deployments table |
| `docs/work/` | Roadmap (`index.md`, generated), `trackers.yaml` for GitHub, Jira and Paperclip, and `epics/` |
| `docs/references/templates/` | Concept, decision and diagram templates |
| `docs/sources/` | Git-ignored intake folder with its index and `ingest-log.csv` |
| `data/`, `tools/` (with `tools/kb` and `tools/kb.conf`), `extracted/` | Research data, tools (`tools/kb.conf` records where `tools/kb --install` gets kb-tools from), and git-ignored extraction output |

The template is generic, with no project-specific content. It lives in
`src/kbtools/template/`; files named `dot-*` install as `.*`. Placeholders are `{{PROJECT}}`,
`{{DATE}}`, `{{NOW}}`, `{{ACTOR}}`, `{{VERSION}}` and `{{KB_TOOLS_SOURCE}}`. A test checks that a scaffolded repository
passes `kb check` cleanly, and that the template's `tools/kb` matches `bin/kb`.

## Use from a project

`kb scaffold` puts [`bin/kb`](bin/kb) into the project as `tools/kb`; `kb scaffold
--tools-only` replaces it with the installed version's (and adds a missing `tools/kb.conf`)
when upgrading a project. With Docker and the
`kb-tools:latest` image it mounts the repository root into the container, runs as your
user, and has no network access.

Without Docker (agent dev containers), it runs a local install in `~/.kb-tools` instead
(the home directory from the password database, so it persists when a run's `$HOME` is
temporary). Create or update that install once per container volume, at a branch or tag
(default `main`):

```sh
tools/kb --install          # light: check, work, catalog, report, log, inventory (about 17 MB)
tools/kb --install --full   # also extract and figure (about 330 MB; LibreOffice for Office files)
tools/kb --version          # kb-tools 0.1.0+<ref>.<commit>
```

The source comes from `KB_TOOLS_SOURCE`, else `source=` in the project's `tools/kb.conf`
(written by `kb scaffold`), else the last install or pip's record of an existing install. In Paperclip, extraction and figures run
on the Paperclip machine through the MCP server, so project containers only need the light
install. `KB_TOOLS_HOME`, `KB_TOOLS_REF` and `KB_TOOLS_EXTRAS` override the location, default
ref and extras ([configuration](docs/environments/configuration.md)).

Everyday use is the same either way:

```sh
tools/kb init                                   # docs/sources (git-ignored), ingest log, extracted/
tools/kb inventory --by human:<name> --origin "drive:Design/2026"
tools/kb extract --pending                      # build extraction packages
tools/kb figure extracted/<pkg>/renders/page-004.png --crop 0.16,0.15,0.47,0.87 \
    --out docs/domains/world/assets/layers.png --page docs/domains/world/world-model.md \
    --alt "..." --caption "..." --source "docs/sources/deck.pptx, slide 4"
tools/kb log deck.pptx --status ingested --by claude-code/opus-5.5 \
    --outputs "docs/domains/world/world-model.md;data/terrain/terrain.csv"
tools/kb check                                  # log, OKF, links, images, diagrams, secrets
tools/kb report                                 # verification level and age per page
```

## Commands

| Command | What it does |
| --- | --- |
| `scaffold` | Installs the generic knowledge-base layout (see above). |
| `init` | Creates `docs/sources/` (git-ignored except `index.md`, `.gitignore`, `ingest-log.csv`), the ingest log, and `extracted/` (git-ignored). |
| `inventory` | Hashes new files in `docs/sources/` and logs them as `pending`. It also reports files that changed since they were logged, and logged files that aren't present locally. |
| `extract` | Builds `extracted/<slug>/` for a source; see the table below. Moves the log row to `extracted`. |
| `figure` | Crops or resizes a render or embedded image into `docs/`. Prints a Markdown snippet with alt text, a caption, the source, and an element table to fill in. |
| `log` | Updates one ingest-log row safely (status, outputs, notes, rehash). |
| `work new-epic` / `new-item` / `set` / `list` / `index` | Repository-native work tracking in `docs/work/`: epics (`NNNN`) with `epic.md` (including acceptance and retrospective) and `plan.md`, items (`NNNN-NN`, `kind` story/task/bug/spike/chore) in `items/`, `work_status` per epic and item, and a generated roadmap. `--description` and `--github`/`--jira`/`--paperclip` fill in new pages; `set --pr` records the delivering pull request. See the template's `docs/process/work-tracking.md`. |
| `catalog` | One record per page: path, section, type, title, description, tags, status, `work_status`, trust tier, last verification. `--write` regenerates the committed `docs/catalog.md` (Markdown grouped by section; only fields that change with the pages, so it never drifts on its own). Filters (`--type`, `--section`, `--tag`, `--tier`, `--status`, `--work-status`, `--text`) print `md`, `json` or `jsonl` on demand, so no JSON copy is stored and `jq` is optional. |
| `check` | Checks the ingest log (statuses, hashes, outputs), OKF front matter, links, images (alt text), that every Mermaid diagram is followed by an element list or table, the work tree (IDs, statuses, dependencies, roadmap freshness; warnings for done items with unticked criteria, TODO placeholders on started work, and open items whose pull request merged), catalog freshness, and tracked files for secrets (errors) and private addresses (warnings), plus any `KB_SCAN_DENYLIST` patterns. Exits non-zero on errors. |
| `report` | Gives each page a trust tier (human, machine or unverified), its last verification, its age, and flags (`changed-since-verified`, `stale`, `verification-old`, `deprecated`). |
| `serve` | Runs an MCP server (streamable HTTP) exposing the commands as tools. |

### Extraction package

| File | Contents |
| --- | --- |
| `manifest.json` | Source path, SHA-256, size, tool versions (including LibreOffice), options, counts, warnings, errors |
| `text.md` | MarkItDown conversion of the whole file |
| `pages.md` | One section per page or slide, with the rendered PDF's text and a link to the render |
| `slides.md`, `slides.json` | PowerPoint only. Per slide: title, text boxes, tables, charts (with data), pictures (exported to `media/`), drawn shapes, speaker notes, hidden flag, and connectors with the shapes they're glued to. Every item has a position (`[left, top, right, bottom]` as slide fractions) to use with `figure --crop`. |
| `workbook.json`, `sheets/*.csv` | Excel only. Every non-empty cell with its formula, cached value and number format; hidden sheets, merged ranges, defined names; formulas without a cached value are flagged. |
| `renders/page-NNN.png` | Every page or slide at 120 dpi (16:9 slides come out about 1600 px wide) |
| `media/` | Embedded images: candidate key graphics |
| `rendered.pdf` | The LibreOffice PDF of an Office file |
| `review.md` | Checklist for visual reconciliation, one row per page or slide |

Warnings point at what the text can't show:
- raster-only pages
- hidden slides
- slides that contain diagrams
- tracked changes and comments
- hidden sheets
- missing cached values

## Paperclip (add-on)

kb-tools installs as an add-on to any Paperclip environment; the full guide is
[docs/environments/paperclip-add-on.md](docs/environments/paperclip-add-on.md). In short:

- **On the Paperclip machine**, run the image as an MCP server next to Paperclip, with the
  ingesting agent's checkouts mounted at `/repos` (`KB_REPOS_ROOT`):

  ```yaml
    kb-tools:
      image: kb-tools:latest
      command: ["serve"]
      volumes:
        - <checkouts-on-the-host>:/repos
  ```

  Add an MCP connection in Paperclip for `http://<kb-mcp-host>:8765/mcp` and bind it to the
  agents that work on the Paperclip machine (the agent that ingests documents, Chief). They
  call `kb_scaffold`, `kb_catalog`, `kb_work_list`, `kb_work_new_epic`, `kb_work_new_item`,
  `kb_work_set`, `kb_inventory`, `kb_extract`, `kb_figure`, `kb_log`, `kb_check` and
  `kb_report` with `repo` set to a repository name under the repos root (`gameworld` or
  `owner/gameworld`). Failures come back as MCP tool errors that list what the server can see.
- **In project containers**, agents and developers use `tools/kb` with the light install
  (`tools/kb --install`): `check`, `work`, `catalog`, `report`, `log`. The MCP server cannot see
  files inside those containers, so the two are not interchangeable.

Every setting (`KB_MCP_HOST`, `KB_MCP_PORT`, `KB_REPOS_ROOT`, `KB_ALLOWED_ROOTS`, the
`KB_TOOLS_*` wrapper settings and the devenv manager's `DEVENV_*`) is listed in
[docs/environments/configuration.md](docs/environments/configuration.md).

## Development

```sh
docker build --target base -t kb-tools:base .
docker run --rm -v "$PWD/src:/opt/kb-tools/src:ro" -v "$PWD/tests:/opt/kb-tools/tests:ro" \
  -e PYTHONPATH=/opt/kb-tools/src -w /opt/kb-tools kb-tools:base \
  sh -c 'pip install -q pytest python-docx && python -m pytest -q'
```

Extraction never uses the network, cloud OCR or a language model. LangExtract
(`pip install .[facts]`) is an optional follow-on for schema-driven fact extraction.
Point it at a local model unless the material may leave the machine.

## License

kb-tools is released under the [MIT License](LICENSE). Copyright (c) 2026 Centralus LLC.

Its dependencies and the packages in the Docker image (including LibreOffice, MPL-2.0) keep
their own licences; see [Third-party licences](docs/architecture/third-party-licences.md).
Projects created with `kb scaffold` don't inherit a licence: choose your own
([ADR 0006](docs/architecture/decisions/0006-mit-license-template-ships-none.md)).
