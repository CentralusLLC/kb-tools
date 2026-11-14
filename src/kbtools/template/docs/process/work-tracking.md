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
kind: story               # story | task | bug | spike | chore
work_status: todo
priority: high            # critical | high | medium | low
depends_on: ["0007-01"]
links:                    # external copies, filled in by sync (or by hand)
  github: "#41"
  jira: PRJ-118
  paperclip: PRJ-23
```

## Item kinds

Every item has a `kind`:

| Kind | Use for | Notes |
| --- | --- | --- |
| `story` | A user-visible capability | Acceptance criteria in the user's terms |
| `task` | Technical work that enables stories | |
| `bug` | Behaviour that differs from what it should be | Starts with a failing test; release note goes under Fixed |
| `spike` | A time-boxed question (research, prototype, comparison) | Done when the question is answered in a research page or ADR, linked from the item; no release note |
| `chore` | Maintenance: upgrades, clean-up, tooling | Release note only if users or operators notice |

## Definition of done

**An item is done** when its pull request has:

- [ ] acceptance criteria met and ticked, and `work_status: done`
- [ ] tests added or updated, and run, with the result reported ([Testing](testing.md))
- [ ] the security rules followed ([Security](security.md))
- [ ] knowledge base pages updated where behaviour, setup or rules changed; `tools/kb check` passes
- [ ] user docs updated if users will notice ([User documentation](../user/index.md))
- [ ] a line in [Unreleased](../releases/unreleased.md), unless its kind needs none

**An epic is done** when:

- [ ] every item is `done` or `cancelled`;
- [ ] its success measures are checked, and the outcome is accepted by the stakeholder
  named in the epic (its Acceptance section);
- [ ] its Retrospective section is filled in, with each action turned into a work item,
  a process-page change or an ADR.

## Commands

Use `tools/kb work` (on the Paperclip machine, the `kb_work_*` MCP tools) rather than creating files by hand:

```sh
tools/kb work new-epic "Self-serve onboarding" --by <you> --priority high \
  --description "New customers can't sign up without our help." --paperclip PRJ-20
tools/kb work new-item 0007 "Email verification" --by <you> --kind story --depends-on 0007-01 \
  --description "Users confirm their email address before their first login." --github "#41"
tools/kb work set 0007-02 in_progress
tools/kb work set 0007-02 done --pr https://github.com/<owner>/<repo>/pull/57
tools/kb work list --open
tools/kb work index          # regenerate the roadmap (new-epic, new-item and set do it too)
```

- `--description` fills in the page's description and its first section (Problem, or What and why).
- `--github`, `--jira` and `--paperclip` record the external copies in `links`, on `new-epic`,
  `new-item` and `set`. `set --pr` records the pull request that delivers an item in `links.github`.
- `set ... done` warns when acceptance criteria are still unticked; the status is set anyway.

`tools/kb check` validates the work tree: IDs match folders and files, statuses are valid,
dependencies exist, closed epics have no open items, planned epics have a plan, and the
roadmap is current. It also warns about drift:

| Warning | Fix |
| --- | --- |
| A `done` item has unticked (`- [ ]`) acceptance criteria | Tick them, or say in the item why one no longer applies |
| Started work (items `in_progress`, `in_review` or `done`; epics `in_progress` or `done`) still has `TODO` placeholders in its description or sections | Fill them in, or delete sections that don't apply. An epic's Retrospective may stay a placeholder until the epic closes |
| A `backlog`, `todo` or `in_review` item's pull request is merged | Set the item `done`, or `in_progress` if more pull requests follow |

Merged pull requests are read from the local git history: GitHub's squash-merge titles
(`[0007-02] Title (#57)`, which may list several items) and merge commits from a
`0007-02-...` branch, plus the pull request in an item's `links.github`. Without git (for
example in the kb-tools Docker image) that check is skipped.

A linked pull request counts as merged only if a merge commit with its number names that item
or its epic, or names no work id at all. Pull request numbers restart when a project moves to a
new repository, so an old `[0003-01] … (#8)` in the history doesn't make a new `#8` look merged.
Link to a pull request in another repository by its full URL; those links are not looked up in
the local history.

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
4. **Close:** when every item is `done` or `cancelled`, check the success measures, record the
   stakeholder's acceptance and the retrospective in `epic.md`, act on the retrospective, and set
   the epic to `done` ([definition of done](#definition-of-done)). `kb check` warns about a done
   epic with no retrospective.

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
