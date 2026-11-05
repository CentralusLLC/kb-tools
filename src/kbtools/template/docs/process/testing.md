---
type: Policy
title: Testing
description: "Testing rules for {{PROJECT}}: where tests live, what every change needs, how agents run tests, and what never to do to make tests pass."
tags: [process, testing, quality, policy]
status: draft
generated:
  by: {{ACTOR}}
  at: {{NOW}}
---

# Testing

## Where tests live

Tests sit next to the code they test, in the project's chosen layout
([Development](development.md#repository-layout)):

```
One app:                         Several apps:
src/          code               apps/<app>/src/      each app's code
tests/        its tests          apps/<app>/tests/    each app's tests
                                 packages/<pkg>/      shared code (with its own tests/)
                                 tests/               cross-app: end-to-end, contract, smoke
```

> TODO: Confirm or change this layout with an [ADR](../architecture/decisions/index.md),
> and list each app's test command in [Local development](../environments/local.md).

## Kinds of tests

| Kind | Checks | Runs |
| --- | --- | --- |
| Unit | One function or module, no network or real services | Every commit |
| Integration | Modules working together with real dependencies (database, queues) | Every pull request |
| End-to-end | A user journey through the running system | Before release |
| Smoke | The deployed system is up and its core path works | After every deployment |

> TODO: Frameworks and tools per app.

## Rules

- **Every change that alters behaviour comes with tests** that fail without it and pass with it.
  Bug fixes start with a test that reproduces the bug.
- **Acceptance criteria are tested.** Each work item's acceptance criteria map to tests, or say
  how they were checked by hand.
- **Run the tests before opening a pull request**, in the [dev environment](../environments/dev-environment.md),
  and report the result: the command, pass or fail, and anything skipped. Never claim tests pass
  without running them.
- **Never weaken tests to make them pass.** Don't delete, skip or loosen assertions, raise
  timeouts, or mock away the code under test without saying why in the pull request.
- **Tests are deterministic.** Seed randomness, freeze time, and don't depend on test order
  or on the network unless the test is explicitly an integration or end-to-end test.
- **Test data is synthetic.** No real personal, customer or production data in fixtures
  (see [Security](security.md)).
- **A failing test on the default branch is fixed or reverted first,** before other work merges.

## Continuous integration

> TODO: Which checks run on each pull request (tests, linters, `tools/kb check`) and which must pass to merge.

## Coverage and quality targets

> TODO: Coverage expectations and any performance or accessibility checks.
