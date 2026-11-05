---
type: Process
title: Ingestion
description: How source documents (PowerPoint, Word, PDF, Excel, images, web pages) become knowledge pages, figures and research data, using kb-tools, with every source tracked in docs/sources/ingest-log.csv.
tags: [process, ingestion, sources, data, figures, diagrams, tools]
status: stable
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Ingestion

Source documents become knowledge in seven steps:

1. Preserve the original.
2. Extract the text and structure.
3. Render every page or slide.
4. Reconcile the extraction against the renders.
5. Capture key figures and diagrams.
6. Put reusable facts into structured data.
7. Write or update pages.

The central lesson is that **automated conversion produces an extraction, not
knowledge**. Knowledge needs visual reconciliation and editorial synthesis.

Every source has a row in [`docs/sources/ingest-log.csv`](../sources/ingest-log.csv).
Human verification is **optional and never blocks** ingestion (see
[Verification and trust](../conventions.md#verification-and-trust)).

## Where things live

| What | Where | In git? |
| --- | --- | --- |
| Original files | `docs/sources/` | **No.** The log records each file's hash and `origin`, so it can be re-fetched |
| Ingest log | `docs/sources/ingest-log.csv` | Yes |
| Extraction packages (text, renders, media) | `extracted/<slug>/` | **No.** It is reproducible working output |
| Curated figures | `docs/**/assets/` | Yes |
| Knowledge pages | `docs/` | Yes |
| Structured data | `data/<dataset>/` ([Research data](../architecture/research-data.md)) | Yes |

Because originals are not in git, always record an `origin` that someone else
could use to get the file again. Examples: a shared drive path, a URL, or an issue
in your agent platform (`paperclip:PRJ-12`).

## Tools

All steps use **kb-tools**, the shared knowledge-base toolkit. It runs in Docker, with
LibreOffice and fonts built in, so results are the same on every machine:

- **In a terminal or IDE:** `tools/kb <command>`. The wrapper is in this repository; the
  `kb-tools:latest` image must be built once per machine. See [`tools/README.md`](../../tools/README.md).
- **In Paperclip:** the `kb_*` MCP tools (`kb_inventory`, `kb_extract`, `kb_figure`, `kb_log`,
  `kb_check`, `kb_report`). Pass `repo` as the absolute path of your checkout.

Do not write one-off extraction scripts. If a tool is missing a capability, improve
kb-tools.

## Steps

### 1. Intake

Put the file in `docs/sources/` with a dated, descriptive name
(`2026-01-10-product-overview.pptx`). If both a PPTX and its PDF export exist, add both.
Then log it:

```sh
tools/kb inventory --by human:<name> --origin "<where it came from>"
```

New files are logged as `pending`. `inventory` also reports files that changed since
they were logged. Never edit a source; a new version is a new file.

### 2. Extract and render

```sh
tools/kb extract --pending
```

Each source gets `extracted/<slug>/`, and its log row moves to `extracted`:

| File | Use it for |
| --- | --- |
| `pages.md` | Page-by-page text from the rendered PDF, each with its render. The main reading view; page and slide breaks are preserved |
| `slides.md` | PowerPoint structure per slide: titles, text boxes, tables, chart data, pictures, speaker notes, hidden slides, drawn shapes, and connectors with the shapes they're glued to. Every item has a position for cropping |
| `workbook.json`, `sheets/` | Excel: formulas, cached values and number formats. Hidden sheets and missing cached values are flagged |
| `text.md` | MarkItDown conversion, for search |
| `renders/page-NNN.png` | Every page or slide as an image, **the visual control** |
| `media/` | Embedded images, candidate figures |
| `manifest.json` | Hashes, tool versions, counts, **warnings** |
| `review.md` | The reconciliation checklist to fill in |

Read the manifest warnings first. They point at what the text cannot show: raster-only
pages, hidden slides, slides with diagrams, tracked changes, comments, hidden sheets,
and formulas without cached values.

### 3. Reconcile

Look at **every** render, not only those that seem important from the text. Use
`review.md` as the checklist:

- **Counts:** pages, slides, sheets and tables agree across formats. A PDF export can
  drop hidden slides; a deck can hold notes the PDF lacks.
- **Text:** reading order, headings, labels, units and dates match what the render shows.
  Rasterised text exists only in the render.
- **Tables and charts:** compare cells and series with the render.
- **Diagrams:** identify every node and visible arrow. Connectors glued to shapes in
  `slides.md` are direct evidence of an edge; others must be read from the render.
- **Duplicates:** if a source matches one already ingested (same slides or pages after
  comparing counts, text and renders), keep one canonical summary and record the
  duplicate as `superseded` or `skipped`.

Record discrepancies; do not silently fix them. Set the log row to `reconciled`
(`tools/kb log <source> --status reconciled`).

### 4. Capture figures and diagrams

- **Figures:** for each key graphic, run `tools/kb figure` on the render, with a crop
  position from `slides.md` or pixels, or on a file in `media/`. Save it to the page's
  `assets/` folder. Paste the printed snippet and fill in the alt text, caption, source,
  and the element table. See [Figures](../conventions.md#figures).
- **Diagrams:** where relationships matter, reconstruct them in Mermaid and follow each
  one with node and edge tables. Mark each edge as visible or inferred. See
  [Diagrams](../conventions.md#diagrams).

### 5. Structure reusable facts

Repeated records, metrics and schedules go into `data/` as CSV with a
`datapackage.json` ([Research data](../architecture/research-data.md)). Record the
source page, slide or cell for each row where it matters. Keep formula, cached,
displayed and corrected values distinct.

### 6. Write the knowledge

Edit the existing page that covers the topic, or create one from
`references/templates/concept.md`:

- **Lead with the interpretation**, not with converter output.
- **Cite** the source and page or slide in `sources` and footnotes.
- **Keep statements separate:** current, historical, planned, inferred, disputed and
  unknown, each with its speaker and date where relevant.
- **Link** to structured data, figures and related pages.
- **State what was not reviewed**, for example speaker notes, hidden sheets or embedded files.
- Set `status: stable` when the page is complete and the quality gates pass. No review is
  needed.

Then link new pages from their section `index.md`, and add a line to [log.md](../log.md).

### 7. Record and check

```sh
tools/kb log <source> --status ingested --by <you> --outputs "docs/...md;data/.../x.csv"
tools/kb check
```

`check` must report 0 errors. Open a pull request with the pages, figures, data and
log changes. Merging does not wait for page-by-page human review.

## Agent platform flow (Paperclip)

1. A person attaches a file to a Paperclip issue ("Ingest the product overview deck").
2. The agent copies it into `docs/sources/` in its checkout and runs `kb_inventory`
   with `origin: paperclip:<issue>`.
3. It runs steps 2 to 7 with the `kb_*` tools. It reviews renders directly from
   `extracted/<slug>/renders/`.
4. It attaches a **review packet** to the issue as a work product. The packet holds the
   reconciliation notes and key renders, plus `workspace_file` references to the new pages.
   The packet is for convenient optional review; the repository stays the record.
5. It opens the pull request, and stores a pointer in memory (`hindsight_retain`), for
   example "product overview deck ingested into docs/…".

Paperclip attachments are never cited; pages cite `docs/sources/<file>`.

## Status values

| Status | Meaning |
| --- | --- |
| `pending` | Logged, not yet extracted |
| `extracted` | Extraction package built |
| `reconciled` | Visual reconciliation done; writing in progress |
| `ingested` | Pages, figures and data written; `outputs` lists them |
| `partial` | Some content processed; `notes` says what remains |
| `skipped` | Deliberately not ingested; `notes` says why (duplicate, irrelevant, sensitive) |
| `superseded` | Replaced by a newer version; `notes` names it |

## Quality gates

A source is ingested when:

1. The original is logged with its hash and an origin that lets someone re-fetch it.
2. The extraction package was built, and its warnings were read and dealt with.
3. Every page or slide render was reviewed, or what was not reviewed is stated on the page.
4. Tables, diagrams, charts, formulas, notes and revisions were reconciled or explicitly excluded.
5. Key graphics are captured as figures with element descriptions. Relationships are diagrams
   with node and edge tables, and inferred edges are labelled.
6. Reusable facts are in `data/` with a descriptor and source lineage.
7. Pages lead with interpretation, cite sources, keep claim status, and list open questions.
8. Pages are linked from an index, `log.md` is updated, the log row is final, and
   `kb check` reports no errors.

## Format notes

- **PowerPoint:** use the PPTX for structure and notes and its PDF export, if any, for
  reading order. The renders control interpretation. Mind hidden slides and charts with data.
- **PDF:** text order is unreliable for multi-column layouts, and some pages have no text
  layer. Use OCR only on raster pages, and verify it against the render.
- **Word:** decide between the markup and accepted views when there are tracked changes.
  Comments are reviewer discussion, not document claims.
- **Excel:** a workbook is a calculation, not just values. Keep formulas, cached values,
  number formats and hidden sheets in view. Do not flatten all sheets into one table.
- **Images and web pages:** keep a dated capture. Describe what is visible separately
  from your interpretation.

