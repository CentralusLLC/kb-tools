"""Work-tracking checks and options from epic 0013 (gameworld feedback findings 7-13)."""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from kbtools import okf, work
from kbtools.check import run_checks
from kbtools.cli import main
from kbtools.common import Repo
from kbtools.scaffold import scaffold

needs_git = pytest.mark.skipif(not shutil.which("git"), reason="git not installed")


def _project(tmp_path: Path, *, git: bool = False) -> Repo:
    if git:
        subprocess.run(["git", "init", "-q", "-b", "dev", str(tmp_path)], check=True)
    else:
        (tmp_path / ".git").mkdir()
    scaffold(tmp_path, project="Acme", actor="t")
    return Repo(tmp_path)


def _commit(repo: Repo, subject: str) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}
    subprocess.run(["git", "-C", str(repo.root), "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo.root), "commit", "-q", "--allow-empty", "-m", subject], check=True, env=env)


def _fill_in(path: Path) -> Path:
    """Replace the template's placeholders, as an author would, and tick the criteria."""
    text = path.read_text()
    text = re.sub(r'(?m)^description: "TODO[^\n]*$', 'description: "Filled in."', text)
    text = re.sub(r"(?m)^> TODO[^\n]*\n(?:> [^\n]*\n)*", "Filled in.\n", text)
    path.write_text(text.replace("- [ ] TODO", "- [x] It works"))
    return path


def _item(repo: Repo, epic: str, title: str, **options) -> Path:
    return _fill_in(work.new_item(repo, epic, title, by="t", **options))


def _links(path: Path) -> dict:
    data, _, _ = okf.parse_front_matter(path.read_text())
    return data["links"]


# ------------------------------------------------------------------ 0013-01


def test_set_records_pull_request_and_tracker_links(tmp_path, capsys):
    repo = _project(tmp_path)
    work.new_epic(repo, "Onboarding", by="t")
    item = _item(repo, "0001", "Signup form")

    assert main(["--repo", str(tmp_path), "work", "set", "0001-01", "in_review",
                 "--pr", "https://github.com/acme/shop/pull/41", "--paperclip", "PRJ-23"]) == 0
    assert _links(item) == {"github": "https://github.com/acme/shop/pull/41", "jira": "", "paperclip": "PRJ-23"}
    assert "work_status: in_review" in item.read_text()

    main(["--repo", str(tmp_path), "work", "set", "0001-01", "done", "--pr", "42", "--jira", "PRJ-118"])
    assert _links(item) == {"github": "#42", "jira": "PRJ-118", "paperclip": "PRJ-23"}
    main(["--repo", str(tmp_path), "work", "set", "0001", "planned", "--github", "#7"])
    assert _links(repo.docs / "work" / "epics" / "0001-onboarding" / "epic.md")["github"] == "#7"

    with pytest.raises(SystemExit, match="pull request URL or number"):
        main(["--repo", str(tmp_path), "work", "set", "0001-01", "done", "--pr", "soon"])
    errors, warnings = run_checks(repo)
    assert errors == [] and warnings == [], errors + warnings


def test_set_links_adds_missing_keys_and_inline_links():
    block = '---\ntitle: "x"\nlinks:\n  jira: ""\ngenerated:\n  by: t\n---\n\n# x\n'
    updated = work.set_links(block, {"github": "#3", "jira": "PRJ-1"})
    data, body, _ = okf.parse_front_matter(updated)
    assert data["links"] == {"jira": "PRJ-1", "github": "#3"} and data["generated"] == {"by": "t"}
    assert body == "\n# x\n"

    inline = '---\ntitle: "x"\nlinks: {paperclip: PRJ-2}\n---\nbody\n'
    data, body, _ = okf.parse_front_matter(work.set_links(inline, {"github": "#3"}))
    assert data["links"] == {"paperclip": "PRJ-2", "github": "#3"} and body == "body\n"

    data, _, _ = okf.parse_front_matter(work.set_links('---\ntitle: "x"\n---\n', {"github": "#3"}))
    assert data["links"] == {"github": "#3"}


@needs_git
def test_check_warns_about_open_items_whose_pull_request_merged(tmp_path):
    repo = _project(tmp_path, git=True)
    epic = work.new_epic(repo, "Onboarding", by="t", status="in_progress")
    _fill_in(epic / "epic.md"), _fill_in(epic / "plan.md")
    for title in ("Signup form", "Email verification", "Password reset", "Profile", "Avatar"):
        _item(repo, "0001", title)
    work.set_status(repo, "0001-01", "in_review")
    work.set_status(repo, "0001-02", "in_review")
    work.set_status(repo, "0001-03", "in_progress")  # more pull requests may follow: not flagged
    work.set_status(repo, "0001-05", "in_review", links={"github": "https://github.com/acme/shop/pull/12"})
    _commit(repo, "Scaffold")
    _commit(repo, "[0001-01] Signup form")  # a branch commit, not a merge
    errors, warnings = run_checks(repo)
    assert errors == [] and warnings == [], warnings

    _commit(repo, "[0001-01] Signup form (#8)")                          # squash merge
    _commit(repo, "Merge pull request #9 from acme/0001-02-email-verification")  # merge commit
    _commit(repo, "[0001-03][0001-04] Reset and profile (#10)")          # one pull request, two items
    _commit(repo, "Unrelated fix (#12)")                                 # merged pull request linked from 0001-05
    _, warnings = run_checks(repo)
    stale = sorted(w.split(":", 1)[0].rsplit("/", 1)[1][:2] + w.split("pull request ", 1)[1].split(" ", 1)[0]
                   for w in warnings if "is merged but work_status" in w)
    assert stale == ["01#8", "02#9", "04#10", "05#12"], warnings
    assert any("set it done (`kb work set 0001-01 done`)" in w for w in warnings)

    work.set_status(repo, "0001-01", "done")
    _, warnings = run_checks(repo)
    assert not any("0001-01" in w or "01-signup-form" in w for w in warnings), warnings


@needs_git
def test_old_pull_request_numbers_do_not_count_as_merges_of_new_ones(tmp_path):
    """Numbers restart when a project moves repository (kb-tools' own history: old #1 and #8)."""
    repo = _project(tmp_path, git=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin",
                    "git@github.com:acme/shop.git"], check=True)
    work.new_epic(repo, "Onboarding", by="t", status="in_progress")
    work.new_epic(repo, "Billing", by="t", status="in_progress")
    for path in (repo.docs / "work" / "epics").glob("*/*.md"):
        _fill_in(path)
    _item(repo, "0001", "Signup form")
    _item(repo, "0002", "Invoices")
    _item(repo, "0002", "Refunds")
    work.set_status(repo, "0002-01", "in_review", links={"github": "#1"})   # new repo's open #1
    work.set_status(repo, "0002-02", "in_review", links={"github": "#8"})   # new repo's open #8
    work.set_status(repo, "0001-01", "in_review", links={"github": "https://github.com/acme/shop-old/pull/9"})
    _commit(repo, "Merge pull request #1 from acme/0001-onboarding")       # old repo, epic branch
    _commit(repo, "[0001-02] Login (#8)")                                  # old repo, another item
    _commit(repo, "Unrelated fix (#9)")                                    # old repo, no work id
    _, warnings = run_checks(repo)
    assert not any("is merged but work_status" in w for w in warnings), warnings
    assert work._github_repo("https://github.com/Acme/Shop/pull/3") == "acme/shop"

    _commit(repo, "[0002-01] Invoices (#1)")                               # new #1 merges
    _commit(repo, "Merge pull request #8 from acme/0002-refunds")          # new #8, epic branch
    _, warnings = run_checks(repo)
    stale = sorted(w.split("pull request ", 1)[1].split(" ", 1)[0] + w.split("kb work set ", 1)[1][:7]
                   for w in warnings if "is merged but work_status" in w)
    assert stale == ["#10002-01", "#80002-02"], warnings


def test_merged_check_is_skipped_without_git(tmp_path, monkeypatch):
    repo = _project(tmp_path)  # .git is an empty folder: not a repository
    assert work.merged_pull_requests(repo) is None
    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert work.merged_pull_requests(repo) is None


def test_mcp_work_set_records_links(tmp_path, monkeypatch):
    from kbtools import server

    src = str(Path(server.__file__).resolve().parents[1])  # the tool runs the CLI in a subprocess
    monkeypatch.setenv("PYTHONPATH", src + (":" + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else ""))
    repo = _project(tmp_path)
    work.new_epic(repo, "Onboarding", by="t")
    item = work.new_item(repo, "0001", "Signup form", by="t")
    server.configure(tmp_path.parent, [])
    mcp = server.build_server()
    result = asyncio.run(mcp.call_tool("kb_work_set", {"repo": str(tmp_path), "id": "0001-01", "status": "done",
                                                       "pr": "41", "paperclip": "PRJ-23"}))
    content = result[0] if isinstance(result, tuple) else result
    assert "".join(getattr(block, "text", "") for block in content).startswith("exit 0")
    assert _links(item) == {"github": "#41", "jira": "", "paperclip": "PRJ-23"}


# ------------------------------------------------------------------ 0013-02


def test_done_with_unchecked_criteria_is_reported(tmp_path, capsys):
    repo = _project(tmp_path)
    work.new_epic(repo, "Onboarding", by="t")
    item = _item(repo, "0001", "Signup form")
    item.write_text(item.read_text().replace("- [x] It works", "- [x] It works\n- [ ] It is fast\n- [ ] It is pretty")
                    + "\n## Follow-ups\n\n- [ ] Not a criterion: ignored\n")

    assert main(["--repo", str(tmp_path), "work", "set", "0001-01", "done"]) == 0
    captured = capsys.readouterr()
    assert "work_status: done" in item.read_text()  # set anyway
    assert "warning docs/work/epics/0001-onboarding/items/01-signup-form.md: done but 2 acceptance criteria are not ticked" in captured.err
    _, warnings = run_checks(repo)
    assert [w for w in warnings if "not ticked" in w] == [
        "docs/work/epics/0001-onboarding/items/01-signup-form.md: done but 2 acceptance criteria are not ticked "
        "(- [ ]); tick them, or say in the item why they no longer apply"]

    main(["--repo", str(tmp_path), "work", "set", "0001-01", "in_review"])
    assert capsys.readouterr().err == ""  # only done items must have every box ticked
    assert not any("not ticked" in w for w in run_checks(repo)[1])


# ------------------------------------------------------------------ 0013-03


def test_new_item_and_epic_take_description_and_links(tmp_path):
    repo = _project(tmp_path)
    assert main(["--repo", str(tmp_path), "work", "new-epic", "Onboarding", "--by", "t",
                 "--description", "New users can't sign up on their own.", "--paperclip", "PRJ-1"]) == 0
    epic = repo.docs / "work" / "epics" / "0001-onboarding" / "epic.md"
    data, body, _ = okf.parse_front_matter(epic.read_text())
    assert data["description"] == "New users can't sign up on their own."
    assert data["links"] == {"github": "", "jira": "", "paperclip": "PRJ-1"}
    assert "## Problem / business need\n\nNew users can't sign up on their own.\n" in body

    main(["--repo", str(tmp_path), "work", "new-item", "0001", "Signup form", "--by", "t", "--kind", "task",
          "--description", 'A "signup" form that creates an account.', "--github", "#4", "--jira", "PRJ-9"])
    item = repo.docs / "work" / "epics" / "0001-onboarding" / "items" / "01-signup-form.md"
    data, body, _ = okf.parse_front_matter(item.read_text())
    assert data["description"] == 'A "signup" form that creates an account.'
    assert data["links"] == {"github": "#4", "jira": "PRJ-9", "paperclip": ""}
    assert '## What and why\n\nA "signup" form that creates an account.\n' in body
    assert work.todo_placeholders(item) == "Acceptance criteria, Notes"

    # Without the options the placeholders stay, as before.
    plain = work.new_item(repo, "0001", "Email", by="t")
    assert work.todo_placeholders(plain) == "description, What and why, Acceptance criteria, Notes"
    errors, warnings = run_checks(repo)
    assert errors == [] and warnings == [], errors + warnings  # nothing has started yet


def test_todo_placeholders_on_started_work_are_reported(tmp_path):
    repo = _project(tmp_path)
    folder = work.new_epic(repo, "Onboarding", by="t", status="planned")
    item = work.new_item(repo, "0001", "Signup form", by="t")
    for status in ("backlog", "todo", "blocked", "cancelled"):
        work.set_status(repo, "0001-01", status)
        assert not any("TODO" in w for w in run_checks(repo)[1]), status

    for status in ("in_progress", "in_review", "done"):
        work.set_status(repo, "0001-01", status)
        assert [w for w in run_checks(repo)[1] if "TODO" in w] == [
            f"docs/work/epics/0001-onboarding/items/01-signup-form.md: item is {status} but still has TODO "
            "placeholders (description, What and why, Acceptance criteria, Notes)"]
    _fill_in(item)
    assert not any("TODO" in w for w in run_checks(repo)[1])

    work.set_status(repo, "0001", "in_progress")
    todo = [w for w in run_checks(repo)[1] if "TODO" in w]
    assert todo == [
        "docs/work/epics/0001-onboarding/epic.md: epic is in_progress but still has TODO placeholders "
        "(description, Problem / business need, Outcome and success measures, Scope, Non-goals, Acceptance)",
        "docs/work/epics/0001-onboarding/plan.md: epic is in_progress but still has TODO placeholders "
        "(Approach, Design, Risks and open questions, Verification)"], todo
    retrospective = (folder / "epic.md").read_text().split("## Retrospective", 1)[1]
    _fill_in(folder / "epic.md"), _fill_in(folder / "plan.md")
    epic_text = (folder / "epic.md").read_text()
    (folder / "epic.md").write_text(epic_text.split("## Retrospective", 1)[0] + "## Retrospective" + retrospective)
    assert not any("TODO" in w for w in run_checks(repo)[1])  # the Retrospective waits for closing


def test_mcp_new_item_takes_description_and_links(tmp_path, monkeypatch):
    from kbtools import server

    src = str(Path(server.__file__).resolve().parents[1])
    monkeypatch.setenv("PYTHONPATH", src + (":" + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else ""))
    repo = _project(tmp_path)
    server.configure(tmp_path.parent, [])
    mcp = server.build_server()
    for tool, arguments in (("kb_work_new_epic", {"title": "Onboarding", "description": "Sign up alone."}),
                            ("kb_work_new_item", {"epic": "0001", "title": "Signup form", "description": "A form.",
                                                  "paperclip": "PRJ-2"})):
        result = asyncio.run(mcp.call_tool(tool, {"repo": str(tmp_path), "by": "t", **arguments}))
        content = result[0] if isinstance(result, tuple) else result
        assert "".join(getattr(block, "text", "") for block in content).startswith("exit 0")
    item = repo.docs / "work" / "epics" / "0001-onboarding" / "items" / "01-signup-form.md"
    data, _, _ = okf.parse_front_matter(item.read_text())
    assert data["description"] == "A form." and data["links"]["paperclip"] == "PRJ-2"
