---
type: Policy
title: Testing
description: "Testing rules for kb-tools: where tests live, what every change needs, how agents run tests, and what never to do to make tests pass."
tags: [process, testing, quality, policy]
status: draft
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Testing

## Current state

Tests are in `tests/` (pytest), with fixtures in `tests/conftest.py` that build real
PowerPoint, Excel, Word and PDF files. They run inside the image, so LibreOffice rendering
is exercised:

```sh
docker build --target test -t kb-tools:test .     # runs the suite during the build
# faster loop against the source tree (the dev stage has git and the test dependencies):
docker build --target dev -t kb-tools:dev .
docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/workspace" kb-tools:dev python -m pytest -q
```

`-u` makes files the tests write in the bind-mounted tree belong to you rather than to
root. Your uid usually has no entry in the image's `/etc/passwd`; the suite and the
`tools/kb` wrapper handle that (the wrapper falls back to `$HOME`), and `-e HOME=/tmp`
gives that user a writable home. On rootless Docker, drop `-u`: root in the container is
already your host user, while `-u` maps to a subordinate uid on the host, so anything the
run writes into the tree would not be yours.

The `test` stage must be able to run the full suite. It adds git (tests create repositories)
and copies `bin/` (the `tools/kb` wrapper the tests run and compare with the scaffold
template's copy); git stays out of `base`, so the runtime image doesn't grow. A test that
needs another tool or file from the repository root needs a matching line in that stage.

A scaffold test checks that a freshly scaffolded repository passes `kb check` with no
errors or warnings, and that the template carries no project-specific words.

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
