# kb-tools

Shared tooling for repositories that keep an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog)
(OKF) knowledge base in `docs/`. It turns source documents (PowerPoint, Word, PDF,
Excel, images) into auditable extraction packages, helps curate key graphics into
the knowledge base, and checks and reports on the knowledge base's trust.

It runs in Docker, so it works the same on a laptop, in CI, and next to Paperclip
agents. The image bundles LibreOffice and a font set for faithful rendering.

The method behind it (preserve, extract, render, reconcile, normalise, write) comes from
the client-project extraction guide. Each project documents it in `docs/process/ingestion.md`.

## Build

```sh
docker build -t kb-tools:latest .            # runtime image
docker build --target test -t kb-tools:test . # runs the test suite
```

## Use from a project

Copy [`bin/kb`](bin/kb) into the project as `tools/kb`. It mounts the repository
root into the container, runs as your user, and has no network access:

```sh
tools/kb init                                   # docs/sources (git-ignored), ingest log, extracted/
tools/kb inventory --by human:reviewer --origin "drive:Design/2026"
tools/kb extract --pending                      # build extraction packages
tools/kb figure extracted/<pkg>/renders/page-004.png --crop 0.16,0.15,0.47,0.87 \
    --out docs/domains/world/assets/layers.png --page docs/domains/world/world-model.md \
    --alt "..." --caption "..." --source "docs/sources/deck.pptx, slide 4"
tools/kb log deck.pptx --status ingested --by claude-code/opus-5.5 \
    --outputs "docs/domains/world/world-model.md;data/terrain/terrain.csv"
tools/kb check                                  # log, OKF, links, images, diagram descriptions
tools/kb report                                 # verification level and age per page
```

## Commands

| Command | What it does |
| --- | --- |
| `init` | Creates `docs/sources/` (git-ignored except `index.md`, `.gitignore`, `ingest-log.csv`), the ingest log, and `extracted/` (git-ignored). |
| `inventory` | Hashes new files in `docs/sources/` and logs them as `pending`. It also reports files that changed since they were logged, and logged files that aren't present locally. |
| `extract` | Builds `extracted/<slug>/` for a source; see the table below. Moves the log row to `extracted`. |
| `figure` | Crops or resizes a render or embedded image into `docs/`. Prints a Markdown snippet with alt text, a caption, the source, and an element table to fill in. |
| `log` | Updates one ingest-log row safely (status, outputs, notes, rehash). |
| `check` | Checks the ingest log (statuses, hashes, outputs), OKF front matter, links, images (alt text), and that every Mermaid diagram is followed by an element list or table. Exits non-zero on errors. |
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

## Paperclip (MCP sidecar)

Run the image as a service next to Paperclip, mounting the volume that holds the
agents' workspaces at the same path the agents see:

```yaml
  kb-tools:
    image: kb-tools:latest
    command: ["serve", "--allowed-root", "/paperclip"]
    volumes:
      - paperclip-data:/paperclip
```

Then add an MCP connection in Paperclip for `http://<kb-mcp-url>`. Agents call
`kb_inventory`, `kb_extract`, `kb_figure`, `kb_log`, `kb_check` and `kb_report`, passing
`repo` as the absolute path of their checkout. Requests for paths outside `--allowed-root`
are refused.

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
