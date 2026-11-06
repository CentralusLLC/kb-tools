---
type: Process
title: Knowledge base maintenance
description: How this knowledge base is updated and verified, and how it relates to agent memory (for example Hindsight in Paperclip).
tags: [knowledge-base, okf, agent-memory, process]
status: draft
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Knowledge base maintenance

## Roles of the knowledge base and agent memory

| | Knowledge base (`docs/`) | Agent memory (for example Hindsight in Paperclip) |
| --- | --- | --- |
| Holds | Curated facts, rules and decisions, with sources | Working context: comments, preferences, lessons, dead ends |
| Written by | People and agents, through pull requests | Agents, automatically and with `hindsight_retain` |
| Verified | Optionally, by people or a second agent; level and age are tracked | No |
| Portable | Yes, it travels with the repository | No, it stays in the agent platform |
| When they conflict | Wins | Loses; flag the conflict |

See [Agent workflow](agent-workflow.md#precedence) for the full precedence order.

## Making a change

1. Find the page that already covers the topic. Prefer editing it to creating a new one.
2. For a new page, copy a template from `references/templates/`, place it in the right
   section, and link it from that section's `index.md`.
3. Set `generated` to yourself and the current time, and add `sources` for every claim
   that came from somewhere. Set `status` to `stable` when the page is complete, or
   `draft` while it is not ([conventions](../conventions.md#page-front-matter)).
4. Add one line to [log.md](../log.md), run `tools/kb catalog --write`
   (MCP: `kb_catalog` with `write=true`), then `tools/kb check`.
   Give every page a precise `description` and tags; the catalog is how agents find it.
5. Open a pull request. Merging does not wait for anyone to verify the pages.

## Verifying pages (optional)

Verification is never a gate. It records that someone checked a page, and it is what
agents use to decide how far to trust it ([Verification and trust](../conventions.md#verification-and-trust)).

- **People** verify what they care about, when they care: add
  `{by: human:<name>, at: <now>, note: <what you checked>}` to `verified`.
- **Agents** may verify another agent's or run's page after checking it against its
  sources: add `{by: <tool>/<version>, at: <now>, note: ...}`. They never verify their own pages.
- `tools/kb report` lists every page's level, last verification and age, plus flags for
  pages that changed after verification, pages past `stale_after`, and old verifications.
  Use it to pick what is worth checking next: important pages that are unverified, old,
  or changed-since-verified.

## Promoting memory into the knowledge base

Agents with a memory service build up working memory. Durable knowledge should end up
here:

1. Periodically, or when a topic comes up repeatedly, an agent recalls from memory
   what has been learned about a topic that is missing from the knowledge base or
   contradicts it.
2. The agent drafts or edits pages as `status: draft`, citing the originating issues
   or comments in `sources`.
3. The changes go through a normal pull request. Promoted pages start unverified;
   people or a second agent can verify them later.
4. Remove secrets, personal data and customer details before promoting. The repository
   may be shared more widely than the memory service.

## Keeping memory consistent with the knowledge base

- Agents read the knowledge base directly from the repository. Do not copy whole pages
  into agent memory. A copy goes stale and competes with the original in recall.
- To make recall point here, store short pointers in memory, for example
  "Deploy policy: see `docs/process/operations.md`".
- When a page changes, the agent making the change recalls related memories and removes
  or marks those that the change supersedes.
- Pages with `stale_after` set are reviewed when the date passes. Check recent memory
  for drift before re-verifying them.

> TODO: If agents use a memory service, decide whether they share one memory bank
> for this project or keep per-agent banks.
