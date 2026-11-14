---
type: Work Item
id: "0010-17"
epic: "0010"
title: "Dockerfile test stage runs the full suite (git and bin/)"
description: "The Dockerfile test stage installs git and copies bin/, so docker build --target test runs the whole suite green; the runtime image is unchanged."
tags: [work-item]
status: draft
kind: bug
work_status: in_review
priority: high
depends_on: []
links: 
  github: "https://github.com/CentralusLLC/kb-tools/pull/4"
  jira: ""
  paperclip: "CEN-54"
generated: 
  by: claude-code/opus-5.5
  at: 2026-11-13T22:44:42Z
---

# 0010-17: Dockerfile test stage runs the full suite (git and bin/)

Part of [epic 0010](../epic.md) ([plan](../plan.md)).

## What and why

The sidecar rebuild from `main` 59a7906 (CEN-12) stopped at `docker build --target test`:
3 failed, 64 passed, 1 skipped, 15 errors. The code was fine; the test stage could not run
the newer tests:

- `test` is built `FROM base`, which has no git (only the `dev` stage installs it).
  `tests/test_kb_wrapper.py` and `tests/test_scan.py` create git repositories.
- The stage never copied `bin/`, so `/opt/kb-tools/bin/kb` was missing for
  `tests/test_kb_wrapper.py` and the `tools/kb` comparisons in `tests/test_deployment.py`
  and `tests/test_kb.py`.

The runtime image was not affected: it ships the wrapper as
`src/kbtools/template/tools/kb`, identical to `bin/kb`.

## Acceptance criteria

- [x] `docker build --target test` runs the full suite with no failures or errors
- [x] git is installed only in the `test` stage; `base` and `runtime` are unchanged
- [x] The tests need no git identity in a clean container (`HOME=/tmp`, no gitconfig)
- [x] `docs/process/testing.md` says what the test stage must provide
- [x] The suite passes for a uid with no `/etc/passwd` entry (`docker run -u`, CI), and the
      `tools/kb` wrapper falls back to `$HOME` there without printing errors
- [x] `docs/process/testing.md` says when to use `-u` and why to drop it on rootless Docker

## Notes

- Reproduced without Docker (none in the dev container) in the kb-tools dev environment
  (Debian bookworm, Python 3.12, LibreOffice): a clean copy of the build context
  (`pyproject.toml`, `README.md`, `src`, `tests`, and `bin` for the fixed case), a fresh venv
  with `.[extract,server]` then `.[dev]` installed as in the Dockerfile, an empty `HOME`
  and `env -i`. Without git on `PATH` and without `bin/`: 3 failed, 64 passed, 1 skipped,
  15 errors (the same as the failed build). With both: 83 passed.
- No test commits, so no git identity is needed.
- Review follow-up (CEN-54): with `docker run -u "$(id -u):$(id -g)" -e HOME=/tmp` the
  suite had 1 failure, a `KeyError` from `pwd.getpwuid` in
  `test_default_home_is_the_password_database_home_not_HOME`. Only the test crashed. The
  wrapper already fell back to `$HOME`, but it looked the user up by name (`id -un`), which
  printed `cannot find name for user ID` on stderr. It now looks up the uid
  (`getent passwd "$(id -u)"`). The test expects `$HOME` when the uid has no entry, and a
  new test stubs `id` and `getent` to cover the fallback.
