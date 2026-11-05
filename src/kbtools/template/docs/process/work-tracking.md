---
type: Process
title: Work tracking
description: "How {{PROJECT}} work is planned and tracked in the repository (epics, implementation plans, work items in docs/work/) and mirrored to outside trackers such as GitHub Issues, Jira or Paperclip."
tags: [process, planning, work-tracking, epics]
status: stable
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Work tracking

Work is planned and tracked **in this repository**, under [`docs/work/`](../work/index.md).
Every person and agent working on the project can see it, it is versioned with the code,
and outside trackers (GitHub Issues, Jira, Paperclip) are **views of it**, not separate plans.

## Levels

| Level | What it is | In the repository | Paperclip | GitHub | Jira |
| --- | --- | --- | --- | --- | --- |
| Project | The big idea: this repository | `docs/business/vision.md` and the [roadmap](../work/index.md) | Project, with this repo as its workspace | Repository (optionally a Projects board) | Project |
| Epic | A smaller idea that addresses one business need | `docs/work/epics/NNNN-slug/epic.md` + `plan.md` | Parent issue (planning mode) | Issue labelled `epic`, or a milestone | Epic |
| Item | A story or task that delivers part of an epic | `docs/work/epics/NNNN-slug/items/NN-slug.md` | Child issue | Sub-issue | Story / Task under the epic |
| Decision | A choice that outlives the work | [ADR](../architecture/decisions/index.md) | | | |

## Files

```
docs/work/
  index.md               roadmap: generated table of epics (do not edit between the markers)
  trackers.yaml          which outside trackers this repository mirrors to
  epics/
    0007-self-serve-onboarding/
      epic.md            the business need: problem, outcome and success measures, scope, non-goals
      plan.md            the implementation plan: approach, design, items and sequencing, risks, verification
      items/
        01-signup-form.md          one story or task: what and why, acceptance criteria, notes
        02-email-verification.md
```

- **IDs are permanent:** epic `0007`, item `0007-02`. They appear in branch names, pull
  requests and every external copy. Never renumber; cancel instead.
- **One file per item** keeps changes small and avoids merge conflicts between agents.
- **Plans are knowledge pages** (`type: Epic`, `Implementation Plan`, `Work Item`). Decisions
  that outlive the work become ADRs.
- **Two status fields:** `status` is OKF page maturity (`draft`/`stable`), `work_status` is the
  work state:

| Epic `work_status` | Item `work_status` |
| --- | --- |
| `proposed`, `planned`, `in_progress`, `done`, `cancelled` | `backlog`, `todo`, `in_progress`, `in_review`, `blocked`, `done`, `cancelled` |

Front matter of an item:

```yaml
type: Work Item
id: "0007-02"
epic: "0007"
title: "Email verification"
work_status: todo
priority: high            # critical | high | medium | low
depends_on: ["0007-01"]
links:                    # external copies, filled in by sync (or by hand)
  github: "#41"
  jira: PRJ-118
  paperclip: PRJ-23
```

## Commands

Use `tools/kb work` (or the `kb_work_*` MCP tools) rather than creating files by hand:

```sh
tools/kb work new-epic "Self-serve onboarding" --by <you> --priority high
tools/kb work new-item 0007 "Email verification" --by <you> --depends-on 0007-01
tools/kb work set 0007-02 in_progress
tools/kb work list --open
tools/kb work index          # regenerate the roadmap (new-epic, new-item and set do it too)
```

`tools/kb check` validates the work tree: IDs match folders and files, statuses are valid,
dependencies exist, closed epics have no open items, planned epics have a plan, and the
roadmap is current.

## Lifecycle

1. **Propose:** `new-epic` and fill in `epic.md`: the business need and how success is measured.
2. **Plan:** write `plan.md`, create the items, and set the epic to `planned`. A plan that
   changes architecture gets an ADR.
3. **Deliver:** for each item, branch `NNNN-NN-slug`, then open a pull request titled
   `[NNNN-NN] Title`. In that one pull request, change:
   - the code and its tests ([Testing](testing.md));
   - the item file (`work_status: done`, acceptance criteria ticked);
   - any affected knowledge pages;
   - a line in [Unreleased](../releases/unreleased.md) ([Release notes](release-notes.md)).
4. **Close:** when every item is `done` or `cancelled`, set the epic to `done` and record
   what was learned (an ADR, or an update to the relevant pages).

## Outside trackers

Each field has **one owner**, so systems never fight over it:

| Owned by the repository | Owned by the tracker |
| --- | --- |
| Scope, plan, acceptance criteria | Assignee |
| Item and epic existence and IDs | Live progress (`in_progress`, `in_review`, `blocked`) |
| Final state (`done`, `cancelled`), set in the delivering pull request | Discussion, notifications, time tracking |

- **Sync is one way, repository to tracker,** after changes reach the default branch. It creates
  missing external issues, updates titles, short descriptions and links, closes issues the
  repository marks done, and writes the external IDs back into `links`. External
  descriptions link to the item file; they never copy the plan.
- **The other direction is report-only.** Drift (a tracker says `blocked`) and issues filed
  outside the repository arrive as a list to triage. Accepting one means a pull request that
  adds or updates an item file.
- **Pull requests close tracker issues** through their own keywords (`Closes #41`, Jira smart
  commits), so the merge is the single moment work becomes done.
- Paperclip issues reference the item or plan file with a `workspace_file` link, so reviewers
  read the plan in place.

Trackers in use are configured in [`docs/work/trackers.yaml`](../work/trackers.yaml).

> TODO: Sync is not automated yet. Until it is, update external issues by hand when an item
> is created or closed, and record their IDs in `links`.
