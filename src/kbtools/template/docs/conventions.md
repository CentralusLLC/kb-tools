---
type: Guide
title: Knowledge base conventions
description: How pages in this knowledge base are structured, linked, attributed and reviewed.
tags: [knowledge-base, okf, conventions]
status: draft
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Knowledge base conventions

## Open Knowledge Format

This directory is an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog)
(OKF) v0.2 bundle: a tree of markdown files with YAML front matter. OKF is
deliberately minimal. Only `type` is required, and consumers must accept
unknown types, unknown keys and broken links.

Reserved files:

- `index.md`: lists a directory's contents for progressive disclosure. It has no front
  matter, except the root `index.md`, which declares `okf_version`.
- `log.md`: change history. Flat list, ISO dates (`YYYY-MM-DD`), newest first. Only
  the root log is kept.

Non-page directories:

- `references/` holds templates and external material, not knowledge pages.
- `sources/` is the inbox of raw files waiting to be ingested
  ([Ingestion](process/ingestion.md)). Its files are ignored by git and are not part
  of the bundle; only `sources/index.md` and `sources/ingest-log.csv` are committed.
- `**/assets/` folders hold curated figures for the pages beside them (see
  [Figures](#figures)).

## Page front matter

```yaml
---
type: Domain Concept            # required; see "Page types" below
title: Order lifecycle          # recommended
description: One sentence an agent can use to decide whether to read the page.
tags: [orders, lifecycle]       # recommended
status: stable                  # draft | stable | deprecated  (OKF default: stable)
stale_after: 2027-05-01T00:00:00Z   # optional: re-check by this date
generated:                      # who wrote the current content, and when
  by: human:alex                # or <producer>/<version>, e.g. claude-code/opus-5.5
  at: 2026-01-15T00:00:00Z
verified:                       # optional check events; see "Verification and trust"
  - by: human:alex
    at: 2026-01-20T00:00:00Z
    note: Checked against the deck renders   # optional: what was checked
sources:                        # where claims come from; cite with footnotes [^id]
  - id: spec
    resource: sources/2026-01-10-order-spec.pdf
    title: Order handling specification
---
```

Always set `status` explicitly. It describes the content, not whether anyone
has checked it:

- `draft`: incomplete or still being written, for example with open TODOs or
  extraction not yet reconciled.
- `stable`: complete for its purpose, and passed the ingestion quality gates where it
  came from a source. Agents set this themselves; no review is needed.
- `deprecated`: superseded; keep it for history and link to its replacement.

## Page types

Use these types consistently. OKF does not register types centrally, so this
list is the project's vocabulary. Add new types here before using them.

| Type | Use for |
| --- | --- |
| `Overview` | The top page of a section or sub-wiki that summarises it (not `index.md`) |
| `Guide` | How-to and reference material for contributors |
| `Policy` | Rules people and agents must follow |
| `Process` | Repeatable workflows (development, release, operations) |
| `Architecture` | System and component descriptions |
| `Decision Record` | Architecture and product decisions (ADRs) |
| `Domain Concept` | One concept in the project's domain (a rule, entity, workflow) |
| `Persona` | A player or customer profile |
| `Environment` | A place the project runs or deploys to |
| `Glossary` | Term definitions |
| `Notes` | Raw or unstructured notes awaiting curation |
| `Template` | Page templates in `references/templates/` |

## Verification and trust

**Verification is optional and never blocks work.** Pages are published, used and
updated without anyone checking them. People verify what matters to them, when it
matters. The level and age of verification then tell agents how much to rely on a page.

**Levels** (OKF trust tiers, taken from `verified`):

- **Unverified:** no `verified` entry. Most agent-written pages stay here.
- **Machine-verified:** checked only by non-human actors. Examples: a second agent
  re-checked the page against the source renders, or a test confirmed a fact.
- **Human-verified:** at least one `human:` entry.

**Recency.** `kb report` (see [tools](process/ingestion.md#tools)) lists each page's
tier, last verification date and age, with these flags:

- `changed-since-verified`: the page was rewritten (`generated.at`) after its last
  verification, so the verification covers an older version.
- `verification-old`: the last verification is more than a year old.
- `stale`: past `stale_after`.
- `deprecated`.

**Rules:**

- A verification entry records who checked the page and when, and optionally a `note` saying
  what was checked. Add it after the check, and keep earlier entries.
- An agent never verifies its own content. A different agent or run may add a
  machine entry after independently checking the page against its sources.
- Only people add `human:` entries.
- When you substantially change a verified page, update `generated` and leave the old
  `verified` entries; the report will flag `changed-since-verified`.

How agents weigh this is described in
[Agent workflow](process/agent-workflow.md#precedence).

## Figures

Key graphics from sources belong in the knowledge base, not only in text.

- Store each figure in an `assets/` folder next to the page that uses it
  (`domains/orders/assets/order-states.png`). PNG for diagrams and screenshots,
  JPEG/WebP for photos; at most 1600 px wide.
- Create figures with `kb figure`, which crops a region out of a page or slide render, or
  takes an embedded image, and prints the Markdown to paste.
- Every figure has:
  - meaningful alt text;
  - an italic caption line naming its source and page or slide;
  - an **element table or list** describing what the figure shows, so the knowledge is not
    locked in pixels.
- Use a figure for things that text loses: layout, maps, UI, art direction, charts. Do not
  add decorative images.

## Diagrams

When relationships matter, draw them as Mermaid diagrams. These are text, diffable and
readable by agents. **Every diagram is followed by a description of its elements:**

- a **nodes** table or list: each element, what it is, and its source; and
- an **edges** table or list: from, to, the relationship, and whether the edge is **visible**
  in the source or **inferred**.

Never turn spatial closeness into a relationship. Label inferred edges as inferred,
and say what evidence they rest on. `kb check` warns about a diagram with no element
description after it. A template is in `references/templates/diagram.md`.

## Linking

- Link pages with ordinary relative markdown links (`../domains/glossary.md`).
  OKF also allows bundle-relative links that start with `/`, but those break on
  GitHub and in IDE previews, where `/` is the repository root.
- Links are untyped. Say in the sentence why you are linking ("refund rules
  are defined in the payments page").
- Prefer linking to a page over repeating its content. Each fact should live on
  one page.
- Cite sources for claims with footnotes whose labels match `sources[].id`.

## Writing for people and agents

- Put the answer first. Lead each page with a short summary, then the detail.
- Keep each page to one concept. Split a page when it gets long or covers several topics.
- Write `description` so an agent can tell from the front matter alone whether the
  page is relevant.
- Mark unknowns explicitly with `> TODO:` or `> Open question:` blockquotes. Do not invent facts to fill a gap.
- Keep the text ASCII-friendly and avoid binaries. Images go in `references/` and need owner approval.
