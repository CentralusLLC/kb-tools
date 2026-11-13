---
type: Process
title: Sources and research
description: "Who handles {{PROJECT}}'s source documents: the ingesting agent (for example a Librarian) ingests documents attached to tasks, answers developers' requests for the exact source material behind a page, and takes long-running research, and where the original documents are kept."
tags: [process, ingestion, sources, research, agents]
status: stable
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Sources and research

One agent owns {{PROJECT}}'s source material: the **ingesting agent** (for example a
Librarian). It runs on the machine with the kb-tools MCP server and is the only one that runs
the heavy kb-tools steps (extraction, renders, figures). Developers work in
[dev containers](../environments/dev-environment.md) and use only the light `tools/kb`
commands (`check`, `catalog`, `work`, `report`).

| Who | Where they work | Uses | Sees the originals? |
| --- | --- | --- | --- |
| Ingesting agent | Its own checkout of {{PROJECT}} on the kb-tools server's machine, under the server's repos root | The kb-tools MCP tools: `kb_inventory`, `kb_extract`, `kb_figure`, `kb_log`, `kb_check` | Yes, in its checkout's `docs/sources/` and on the source task |
| Developers | Dev containers | `tools/kb check`, `catalog`, `work`, `report` | No. They read the knowledge base pages, and ask the ingesting agent for the original when they need it |
| People who supply documents | Your agent platform | Attach documents to tasks; approve sensitive material | Yes |

The ingesting agent asks the people responsible for the project (see
[Project management](project-management.md)) for anything that needs a decision. It opens
pull requests like any other contributor ([Branches and pull requests](development.md#branches-and-pull-requests)).

> TODO: Name the ingesting agent and who it goes to for decisions, if that differs from the
> above.

Three kinds of request go to the ingesting agent, always as a task assigned to it in your
agent platform:

1. [Ingestion](#ingestion): someone attaches documents to be turned into knowledge.
2. [Source requests](#source-requests): a developer needs to see the original behind a
   knowledge base reference.
3. [Research](#research): long-running web or document research.

## Ingestion

Someone attaches the documents to a task assigned to the ingesting agent. The agent then
follows [Ingestion](ingestion.md):

1. **Intake.** Copy each attachment into `docs/sources/` in its checkout with a dated name,
   then run `kb_inventory` with its own `by` and the task as `origin`
   (`paperclip:<task>` or your platform's equivalent).
2. **Extract.** Run `kb_extract` on the pending sources, and read the manifest warnings.
3. **Reconcile.** Look at every render and fill in `review.md`
   ([Reconcile](ingestion.md#3-reconcile)).
4. **Write.** Write or update knowledge base pages, capture key graphics with `kb_figure`,
   and put reusable facts in `data/`.
5. **Log.** Run `kb_log` to set each source's final status and outputs.
6. **Check.** Run `kb_check`; it must report 0 errors.
7. **Pull request**, titled with the work item (`[NNNN-NN] Ingest ...`). The description
   lists:
   - the documents (file name, origin task, ingest-log status);
   - the pages, figures and data files added or changed;
   - anything flagged: manifest warnings left open, pages or slides not reviewed,
     discrepancies, duplicates, and possibly sensitive material.

**Sensitive material is approved before merge.** If a document holds personal data,
confidential business terms, credentials, or anything marked restricted, the ingesting agent
says so in the pull request and on the task, and asks the people responsible to approve before
it is merged. Pages are committed, so they must hold only what may be in git. A source can be
logged as `skipped` with a note instead of ingested ([Security](security.md)).

Originals and `extracted/` output never go into git. Only pages, figures, data files and the
ingest log do.

## Source requests

Knowledge base pages cite their sources (`docs/sources/<file>`, page or slide). Those files are
not in git, so a developer cannot open them. When a developer needs to see the original:

1. **The developer creates a task assigned to the ingesting agent.** Title it
   `Source request: <document>, <page/slide/sheet>`, and in the description name:
   - the document, as the page cites it (`docs/sources/2026-01-10-product-overview.pptx`);
   - the page, slide, sheet or cell range;
   - the knowledge base page that pointed there, if any;
   - the question: what you need to know or check;
   - what form helps most: page image, crop, extracted text or cell values.

   Link the task to the developer's own task, and keep working on what does not depend on it.

2. **The ingesting agent answers on that task with attachments**, taken from its checkout:
   - the page or slide image, from `extracted/<slug>/renders/`;
   - a crop of the part that matters;
   - the extracted text, from `pages.md` or `slides.md`, or cell values and formulas
     from `workbook.json`.

   It answers the question in words as well, and says if the source is unclear or contradicts
   the page.

3. **One-off answers stay on the task, not in the repository.** If the request shows that a
   page is missing something other developers will need (a value, a table, a diagram, a
   figure), the ingesting agent also fixes the page, or adds a figure or data file, in a
   follow-up pull request, and links it from the request task.

Developers do not copy originals or attachments into the repository. If you need something
from a source in code or data, ask for it to be added to `data/` or a page.

## Research

Long-running web and document research goes to the ingesting agent as a task: comparisons,
market surveys, rules or standards to read, background on a topic. The task names the
question, why it matters, and when the answer is needed.

The ingesting agent records the findings in the knowledge base with sources: a page in the
matching section (for example [domains](../domains/index.md) or
[business](../business/index.md)), or data in `data/`. It cites every claim, marks what is
inferred or uncertain, and opens a pull request. Web pages it relies on are kept as dated
captures in `docs/sources/` and logged with `kb_inventory`, like any other source. A research
question that is part of planned work can also be a `spike` work item
([Work tracking](work-tracking.md#item-kinds)).

Quick lookups while coding stay with the developer: an API reference, an error message, a
library's options.

## Where the originals are kept

Originals are git-ignored, so git does not back them up. Each one is kept in two places:

1. **The task it was attached to.** This is the `origin` in the ingest log, and the copy
   anyone can re-fetch.
2. **`docs/sources/` in the ingesting agent's checkout**, where the kb-tools MCP server
   reads it.

The ingest log holds each file's SHA-256 hash, so any copy can be checked against it. Until a
backup of the ingesting agent's `docs/sources/` exists on its host, the task attachments are
the backup: never delete an attachment from a source task.

> TODO: Record where the host backup of `docs/sources/` is, once there is one.
