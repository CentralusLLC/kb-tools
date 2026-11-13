"""Repository-native work tracking: epics, implementation plans and work items in docs/work/.

docs/work/
  index.md                      roadmap (generated between kb:work-index markers)
  trackers.yaml                 external trackers this repo mirrors to
  epics/NNNN-slug/
    epic.md                     type: Epic             (id "NNNN")
    plan.md                     type: Implementation Plan
    items/NN-slug.md            type: Work Item        (id "NNNN-NN")

Work state lives in `work_status` (OKF's `status` keeps meaning page maturity).
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import okf
from .common import Repo, atomic_write, now_iso, slugify

EPIC_STATUSES = ("proposed", "planned", "in_progress", "done", "cancelled")
ITEM_STATUSES = ("backlog", "todo", "in_progress", "in_review", "blocked", "done", "cancelled")
PRIORITIES = ("critical", "high", "medium", "low")
ITEM_KINDS = ("story", "task", "bug", "spike", "chore")
CLOSED = {"done", "cancelled"}
INDEX_START, INDEX_END = "<!-- kb:work-index:start -->", "<!-- kb:work-index:end -->"
EPIC_DIR = re.compile(r"^(\d{4})-[a-z0-9-]+$")
ITEM_FILE = re.compile(r"^(\d{2})-[a-z0-9-]+\.md$")
TRACKERS = ("github", "jira", "paperclip")
# Items that can't still be waiting for their pull request once it has merged. in_progress and
# blocked items are left alone: an item can take several pull requests.
STALE_WHEN_MERGED = {"backlog", "todo", "in_review"}
# GitHub's squash-merge title ("[0007-02] Title (#41)", several ids allowed) and merge-commit title.
SQUASH_SUBJECT = re.compile(r"^((?:\[\d{4}-\d{2}\]\s*)*).*\(#(\d+)\)$")
# The branch names an item ("0007-02-...") or only an epic ("0007-...").
MERGE_SUBJECT = re.compile(r"^Merge pull request #(\d+) from \S+?/(?:(\d{4}-\d{2})-|(\d{4})-)")
GITHUB_REPO = re.compile(r"github\.com[:/]([^/\s]+)/([^/\s]+?)(?:\.git)?(?:/pull/\d+/?)?/?$", re.I)
STARTED_ITEM = {"in_progress", "in_review", "done"}
STARTED_EPIC = {"in_progress", "done"}
UNCHECKED = re.compile(r"(?m)^\s*[-*] \[ \]")
PLACEHOLDER = re.compile(r"^\s*(?:>\s*TODO\b|[-*] \[[ xX]\] TODO\b)")
PR_NUMBER = re.compile(r"(?:^#?|/pull/)(\d+)/?$")


@dataclass
class Item:
    path: Path
    data: dict
    number: str

    @property
    def id(self) -> str:
        return str(self.data.get("id", ""))


@dataclass
class Epic:
    path: Path
    number: str
    data: dict
    has_plan: bool
    items: list[Item] = field(default_factory=list)

    @property
    def id(self) -> str:
        return str(self.data.get("id", ""))


def work_dir(repo: Repo) -> Path:
    return repo.docs / "work"


def load(repo: Repo) -> tuple[list[Epic], list[str]]:
    """Read all epics and items. Returns (epics, problems found while reading)."""
    problems: list[str] = []
    epics: list[Epic] = []
    root = work_dir(repo) / "epics"
    if not root.is_dir():
        return epics, problems
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        match = EPIC_DIR.match(folder.name)
        if not match:
            problems.append(f"{repo.rel(folder)}: epic folders are named NNNN-slug")
            continue
        epic_file = folder / "epic.md"
        if not epic_file.is_file():
            problems.append(f"{repo.rel(folder)}: missing epic.md")
            continue
        data, _, error = okf.parse_front_matter(epic_file.read_text(encoding="utf-8"))
        if error or data is None:
            problems.append(f"{repo.rel(epic_file)}: unreadable front matter")
            continue
        epic = Epic(epic_file, match.group(1), data, (folder / "plan.md").is_file())
        items_dir = folder / "items"
        if items_dir.is_dir():
            for item_file in sorted(items_dir.glob("*.md")):
                item_match = ITEM_FILE.match(item_file.name)
                if not item_match:
                    problems.append(f"{repo.rel(item_file)}: item files are named NN-slug.md")
                    continue
                item_data, _, item_error = okf.parse_front_matter(item_file.read_text(encoding="utf-8"))
                if item_error or item_data is None:
                    problems.append(f"{repo.rel(item_file)}: unreadable front matter")
                    continue
                epic.items.append(Item(item_file, item_data, item_match.group(1)))
        epics.append(epic)
    return epics, problems


def validate(repo: Repo) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    epics, problems = load(repo)
    errors += problems
    ids: dict[str, str] = {}
    merged = merged_pull_requests(repo)
    for epic in epics:
        where = repo.rel(epic.path)
        if str(epic.data.get("type", "")).strip() != "Epic":
            errors.append(f"{where}: type must be Epic")
        if epic.id != epic.number:
            errors.append(f"{where}: id {epic.id!r} must be \"{epic.number}\" (quoted) to match its folder")
        status = str(epic.data.get("work_status", ""))
        if status not in EPIC_STATUSES:
            errors.append(f"{where}: work_status must be one of {', '.join(EPIC_STATUSES)}")
        if epic.data.get("priority") and epic.data["priority"] not in PRIORITIES:
            warnings.append(f"{where}: priority should be one of {', '.join(PRIORITIES)}")
        if status in {"planned", "in_progress", "done"} and not epic.has_plan:
            warnings.append(f"{where}: {status} epic has no plan.md")
        if status in STARTED_EPIC:
            for page in (epic.path, epic.path.parent / "plan.md"):
                if page.is_file() and (todo := todo_placeholders(page)):
                    warnings.append(f"{repo.rel(page)}: epic is {status} but still has TODO placeholders ({todo})")
        ids[epic.id] = where
        open_items = []
        for item in epic.items:
            item_where = repo.rel(item.path)
            expected = f"{epic.number}-{item.number}"
            if str(item.data.get("type", "")).strip() != "Work Item":
                errors.append(f"{item_where}: type must be Work Item")
            if item.id != expected:
                errors.append(f"{item_where}: id {item.id!r} must be \"{expected}\" to match its file and epic")
            if str(item.data.get("epic", "")) != epic.number:
                errors.append(f"{item_where}: epic must be \"{epic.number}\"")
            item_status = str(item.data.get("work_status", ""))
            if item_status not in ITEM_STATUSES:
                errors.append(f"{item_where}: work_status must be one of {', '.join(ITEM_STATUSES)}")
            kind = str(item.data.get("kind", ""))
            if not kind:
                warnings.append(f"{item_where}: no kind (one of {', '.join(ITEM_KINDS)})")
            elif kind not in ITEM_KINDS:
                errors.append(f"{item_where}: kind must be one of {', '.join(ITEM_KINDS)}")
            if item.id in ids:
                errors.append(f"{item_where}: duplicate id {item.id}")
            ids[item.id] = item_where
            if item_status not in CLOSED:
                open_items.append(item.id)
            if item_status in STARTED_ITEM and (todo := todo_placeholders(item.path)):
                warnings.append(f"{item_where}: item is {item_status} but still has TODO placeholders ({todo})")
            if item_status == "done" and (unchecked := unchecked_criteria(item.path)):
                warnings.append(f"{item_where}: {_unchecked_message(unchecked)}")
            if merged is not None and item_status in STALE_WHEN_MERGED:
                prs = _merged_for(item, merged)
                if prs:
                    warnings.append(f"{item_where}: pull request {', '.join(prs)} is merged but work_status is "
                                    f"{item_status}; set it done (`kb work set {item.id} done`), or in_progress "
                                    "if more pull requests follow")
            if item_status in {"in_progress", "in_review", "done"} and status in {"proposed"}:
                warnings.append(f"{item_where}: item is {item_status} but its epic is still proposed")
        if status in CLOSED and open_items:
            warnings.append(f"{where}: epic is {status} but items are still open: {', '.join(open_items)}")
        if status == "done" and _retro_missing(epic.path):
            warnings.append(f"{where}: epic is done but its Retrospective section is not filled in")
    for epic in epics:
        for item in epic.items:
            for dependency in item.data.get("depends_on") or []:
                if str(dependency) not in ids:
                    errors.append(f"{repo.rel(item.path)}: depends_on {dependency} does not exist")
    index = work_dir(repo) / "index.md"
    if epics and index.is_file() and index.read_text(encoding="utf-8") != _with_index(index.read_text(encoding="utf-8"), epics, repo):
        warnings.append("docs/work/index.md roadmap is out of date (run `kb work index`)")
    return errors, warnings


@dataclass
class MergedPullRequests:
    """Pull requests merged into the checked-out branch, as read from the git history."""

    by_item: dict[str, set[str]]           # item id named in the merge commit -> {"#N", ...}
    owners: dict[str, list[set[str]]]      # "N" -> the work ids each merge commit for #N names
    repo: str | None                       # "owner/name" of the origin remote, when known


def merged_pull_requests(repo: Repo) -> MergedPullRequests | None:
    """Pull requests merged into the checked-out branch, read from the local git history.

    Returns None when there is no git (the kb-tools runtime image has none) or no repository.
    """
    git_dir = repo.root / ".git"
    if not git_dir.exists() or not shutil.which("git"):
        return None
    try:
        result = subprocess.run(["git", f"--git-dir={git_dir}", "log", "--format=%s"],
                                capture_output=True, text=True, timeout=60)
        remote = subprocess.run(["git", f"--git-dir={git_dir}", "config", "--get", "remote.origin.url"],
                                capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    merged = MergedPullRequests({}, {}, _github_repo(remote.stdout) if remote.returncode == 0 else None)
    for subject in result.stdout.splitlines():
        subject = subject.strip()
        if squash := SQUASH_SUBJECT.match(subject):
            number, idents = squash.group(2), set(re.findall(r"\d{4}-\d{2}", squash.group(1)))
        elif merge := MERGE_SUBJECT.match(subject):
            number, idents = merge.group(1), {merge.group(2) or merge.group(3)}
        else:
            continue
        merged.owners.setdefault(number, []).append(idents)
        for ident in idents:
            if "-" in ident:
                merged.by_item.setdefault(ident, set()).add(f"#{number}")
    return merged


def _github_repo(url: str) -> str | None:
    """"owner/name" from a GitHub remote or pull request URL (https or ssh), else None."""
    match = GITHUB_REPO.search(url.strip())
    return f"{match.group(1)}/{match.group(2)}".lower() if match else None


def _merged_for(item: Item, merged: MergedPullRequests) -> list[str]:
    """Merged pull requests for an item: named in a merge commit, or linked from links.github.

    A linked number counts only when a merge commit for it names this item or its epic, or
    names no work id at all. Pull request numbers restart when a project moves to a new
    repository, so the history can hold an old "(#8)" from another item; a link to another
    repository's pull request (for example the old one) is not looked up in local history.
    """
    found = set(merged.by_item.get(item.id, set()))
    links = item.data.get("links")
    link = str(links.get("github") or "") if isinstance(links, dict) else ""
    linked = PR_NUMBER.search(link)
    link_repo = _github_repo(link)
    other_repo = bool(merged.repo and link_repo and link_repo != merged.repo)
    if linked and not other_repo:
        own = {item.id, item.id.split("-")[0]}
        if any(not idents or idents & own for idents in merged.owners.get(linked.group(1), [])):
            found.add(f"#{linked.group(1)}")
    return sorted(found, key=lambda pr: int(pr[1:]))


def _sections(body: str) -> list[tuple[str, str]]:
    """(heading, text) for each `## ` section; text before the first one has heading ""."""
    parts = re.split(r"(?m)^## +(.+?)[ \t]*$", body)
    return [("", parts[0])] + [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def todo_placeholders(path: Path) -> str:
    """Where a work page still has template placeholders ("description, What and why"), or ""."""
    data, body, _ = okf.parse_front_matter(path.read_text(encoding="utf-8"))
    found = []
    if str((data or {}).get("description", "")).lstrip().startswith("TODO"):
        found.append("description")
    for heading, text in _sections(body):
        # The Retrospective is filled in when an epic closes; the done-epic check covers it.
        if heading == "Retrospective":
            continue
        if any(PLACEHOLDER.match(line) for line in text.splitlines()):
            found.append(heading or "introduction")
    return ", ".join(found)


def unchecked_criteria(path: Path) -> int:
    """Number of unticked `- [ ]` boxes in a work item's Acceptance criteria section."""
    _, body, _ = okf.parse_front_matter(path.read_text(encoding="utf-8"))
    return sum(len(UNCHECKED.findall(text)) for heading, text in _sections(body)
               if heading.lower().startswith("acceptance criteria"))


def _unchecked_message(count: int) -> str:
    return (f"done but {count} acceptance criteri{'on is' if count == 1 else 'a are'} not ticked (- [ ]); "
            "tick them, or say in the item why they no longer apply")


def status_warnings(path: Path, status: str) -> list[str]:
    """Warnings to show after `kb work set` (the status is set regardless)."""
    if status == "done" and (unchecked := unchecked_criteria(path)):
        return [_unchecked_message(unchecked)]
    return []


def _retro_missing(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "## Retrospective" not in text:
        return True
    section = text.split("## Retrospective", 1)[1].split("\n## ", 1)[0]
    return "TODO" in section


# ---------------------------------------------------------------- rendering

def _links(data: dict) -> str:
    links = data.get("links") or {}
    return ", ".join(f"{k}: {v}" for k, v in links.items() if v) if isinstance(links, dict) else ""


def roadmap(epics: list[Epic], repo: Repo) -> str:
    if not epics:
        return "_No epics yet. Create one with `tools/kb work new-epic \"Title\"`._"
    lines = ["| Epic | Title | Status | Priority | Items done | Links |", "| --- | --- | --- | --- | --- | --- |"]
    for epic in epics:
        rel = epic.path.relative_to(work_dir(repo)).as_posix()
        done = sum(1 for i in epic.items if str(i.data.get("work_status")) == "done")
        live = sum(1 for i in epic.items if str(i.data.get("work_status")) != "cancelled")
        lines.append(f"| [{epic.number}]({rel}) | {epic.data.get('title', '')} | {epic.data.get('work_status', '')} | "
                     f"{epic.data.get('priority', '')} | {done}/{live} | {_links(epic.data)} |")
    return "\n".join(lines)


def _with_index(text: str, epics: list[Epic], repo: Repo) -> str:
    block = f"{INDEX_START}\n{roadmap(epics, repo)}\n{INDEX_END}"
    if INDEX_START in text and INDEX_END in text:
        before, rest = text.split(INDEX_START, 1)
        _, after = rest.split(INDEX_END, 1)
        return before + block + after
    return text.rstrip() + "\n\n## Roadmap\n\n" + block + "\n"


def write_index(repo: Repo) -> Path:
    epics, _ = load(repo)
    index = work_dir(repo) / "index.md"
    text = index.read_text(encoding="utf-8") if index.exists() else "# Work\n"
    atomic_write(index, _with_index(text, epics, repo))
    return index


def listing(repo: Repo, status: str | None = None, open_only: bool = False) -> str:
    epics, _ = load(repo)
    rows = ["| ID | Kind | Title | Status | Depends on | Path |", "| --- | --- | --- | --- | --- | --- |"]
    # Kind is "epic" for epics and the item's kind (story, bug, spike, ...) for items.
    for epic in epics:
        entries = [("epic", epic.id, epic.data, epic.path)] + \
            [(str(i.data.get("kind", "item")), i.id, i.data, i.path) for i in epic.items]
        for kind, ident, data, path in entries:
            current = str(data.get("work_status", ""))
            if status and current != status:
                continue
            if open_only and current in CLOSED:
                continue
            depends = ", ".join(str(d) for d in data.get("depends_on") or [])
            rows.append(f"| {ident} | {kind} | {data.get('title', '')} | {current} | {depends} | {repo.rel(path)} |")
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------------- creation

def _front(fields: list[tuple[str, str]]) -> str:
    return "---\n" + "\n".join(f"{k}: {v}" for k, v in fields) + "\n---\n"


def _quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _check_links(links: dict[str, str] | None) -> dict[str, str]:
    links = {key: value for key, value in (links or {}).items() if value}
    if set(links) - set(TRACKERS):
        raise SystemExit(f"kb: links must be one of {', '.join(TRACKERS)}")
    return links


def _links_block(links: dict[str, str]) -> str:
    return "".join(f"\n  {key}: {_quote(links.get(key, ''))}" for key in TRACKERS)


def new_epic(repo: Repo, title: str, *, by: str, priority: str = "medium", status: str = "proposed",
             description: str = "", links: dict[str, str] | None = None) -> Path:
    if status not in EPIC_STATUSES:
        raise SystemExit(f"kb: status must be one of {', '.join(EPIC_STATUSES)}")
    links = _check_links(links)
    problem = description or "> TODO: Who has the problem, what it costs them, and why now."
    epics, _ = load(repo)
    number = f"{max((int(e.number) for e in epics), default=0) + 1:04d}"
    folder = work_dir(repo) / "epics" / f"{number}-{slugify(title)[:48].strip('-')}"
    folder.mkdir(parents=True)
    stamp = [("generated", f"\n  by: {by}\n  at: {now_iso()}")]
    epic = _front([
        ("type", "Epic"), ("id", f'"{number}"'), ("title", _quote(title)),
        ("description", _quote(description or f"TODO: one sentence on the business need behind {title}.")),
        ("tags", "[epic]"), ("status", "draft"), ("work_status", status), ("priority", priority),
        ("owner", '""'), ("target", '""'),
        ("links", _links_block(links)), *stamp,
    ]) + f"""
# Epic {number}: {title}

## Problem / business need

{problem}

## Outcome and success measures

> TODO: What is true when this epic is done, and how we will know (measurable where possible).

## Scope

> TODO: What is included.

## Non-goals

> TODO: What is deliberately excluded.

## Acceptance

> TODO: Who accepts the outcome (see stakeholders in project management), and how
> (demo, review of success measures). Record the acceptance here when the epic closes.

## Retrospective

> TODO (fill in when the epic closes): what worked, what didn't, and actions. Each action
> becomes a work item, a change to a process page, or an ADR.

## Related

- Plan: [plan.md](plan.md)
- Items: see [the roadmap](../../index.md) or `tools/kb work list`
"""
    plan = _front([
        ("type", "Implementation Plan"), ("epic", f'"{number}"'), ("title", _quote(f"Plan: {title}")),
        ("description", _quote(f"How epic {number} will be delivered: approach, design, risks and sequencing of its items.")),
        ("tags", "[plan]"), ("status", "draft"), *stamp,
    ]) + f"""
# Plan: {title}

## Approach

> TODO: The chosen approach in a few paragraphs, and the alternatives considered.

## Design

> TODO: Components, data and interfaces touched. Add a diagram with node and edge tables
> where relationships matter (`references/templates/diagram.md`).

## Items and sequencing

Items live in [items/](items/), one file each. Create them with
`tools/kb work new-item {number} "Title"`. Summarise the order and dependencies here.

## Risks and open questions

> TODO: Risks, unknowns, and decisions that need an ADR.

## Verification

> TODO: How the outcome will be tested and demonstrated.
"""
    atomic_write(folder / "epic.md", epic)
    atomic_write(folder / "plan.md", plan)
    _refresh(repo)
    return folder


def new_item(repo: Repo, epic_id: str, title: str, *, by: str, priority: str = "medium",
             status: str = "todo", depends_on: list[str] | None = None, kind: str = "story",
             description: str = "", links: dict[str, str] | None = None) -> Path:
    links = _check_links(links)
    if kind not in ITEM_KINDS:
        raise SystemExit(f"kb: kind must be one of {', '.join(ITEM_KINDS)}")
    if status not in ITEM_STATUSES:
        raise SystemExit(f"kb: status must be one of {', '.join(ITEM_STATUSES)}")
    epics, _ = load(repo)
    epic = next((e for e in epics if e.number == epic_id.zfill(4)), None)
    if epic is None:
        raise SystemExit(f"kb: epic {epic_id} not found under docs/work/epics/")
    number = f"{max((int(i.number) for i in epic.items), default=0) + 1:02d}"
    ident = f"{epic.number}-{number}"
    path = epic.path.parent / "items" / f"{number}-{slugify(title)[:48].strip('-')}.md"
    depends = "[" + ", ".join(f'"{d}"' for d in depends_on or []) + "]"
    text = _front([
        ("type", "Work Item"), ("id", f'"{ident}"'), ("epic", f'"{epic.number}"'), ("title", _quote(title)),
        ("description", _quote(description or f"TODO: one sentence on what {ident} delivers.")),
        ("tags", "[work-item]"), ("status", "draft"), ("kind", kind), ("work_status", status), ("priority", priority),
        ("depends_on", depends), ("links", _links_block(links)),
        ("generated", f"\n  by: {by}\n  at: {now_iso()}"),
    ]) + f"""
# {ident}: {title}

Part of [epic {epic.number}](../epic.md) ([plan](../plan.md)).

## What and why

> TODO: @@WHAT@@

## Acceptance criteria

- [ ] @@ACCEPT@@

## Notes

> TODO: Design notes, constraints, links. Record decisions that outlive this item as ADRs.
"""
    guidance = {
        "story": ("The change, and the user or business value it delivers.", "TODO"),
        "task": ("The work, and why it is needed.", "TODO"),
        "bug": ("What happens, what should happen, and how to reproduce it.",
                "A test reproduces the bug and now passes"),
        "spike": ("The question to answer, and the time box.",
                  "Question answered in a research page or ADR (link it here)"),
        "chore": ("The maintenance work, and why now.", "TODO"),
    }[kind]
    what = description or f"> TODO: {guidance[0]}"
    text = text.replace("> TODO: @@WHAT@@", what).replace("@@ACCEPT@@", guidance[1])
    atomic_write(path, text)
    _refresh(repo)
    return path


def _refresh(repo: Repo) -> None:
    from .catalog import refresh_if_present

    write_index(repo)
    refresh_if_present(repo)


def pr_link(value: str) -> str:
    """Normalise a pull request given as a URL, "#N" or "N" for links.github."""
    value = value.strip()
    if value.isdigit():
        return f"#{value}"
    if not PR_NUMBER.search(value):
        raise SystemExit(f"kb: --pr must be a pull request URL or number, not {value!r}")
    return value


def set_links(text: str, links: dict[str, str]) -> str:
    """Set entries of the front matter's `links` mapping, keeping the rest of the page as it is."""
    match = okf.FRONT_MATTER.match(text)
    if not match:
        raise SystemExit("kb: page has no front matter")
    lines = match.group(1).split("\n")
    start = next((i for i, line in enumerate(lines) if re.match(r"links:\s*(#.*)?$", line)), None)
    if start is None:
        # No block-style links: keep any inline values, and write a block at the end.
        data, _, _ = okf.parse_front_matter(text)
        existing = (data or {}).get("links")
        merged = {**(existing if isinstance(existing, dict) else {}), **links}
        lines = [line for line in lines if not line.startswith("links:")]
        lines += ["links:"] + [f"  {key}: {_quote(str(value))}" for key, value in merged.items()]
    else:
        end = start + 1
        while end < len(lines) and lines[end][:1] in {" ", "\t"}:
            end += 1
        for key, value in links.items():
            for i in range(start + 1, end):
                if re.match(rf"\s+{re.escape(key)}:", lines[i]):
                    indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                    lines[i] = f"{indent}{key}: {_quote(value)}"
                    break
            else:
                lines.insert(end, f"  {key}: {_quote(value)}")
                end += 1
    return "---\n" + "\n".join(lines) + "\n---\n" + text[match.end():]


def set_status(repo: Repo, ident: str, status: str, links: dict[str, str] | None = None) -> Path:
    """Set work_status (and any tracker links given) of an epic or item."""
    links = _check_links(links)
    epics, _ = load(repo)
    for epic in epics:
        candidates = [(epic.id, epic.path, EPIC_STATUSES)] + [(i.id, i.path, ITEM_STATUSES) for i in epic.items]
        for candidate_id, path, allowed in candidates:
            if candidate_id == ident:
                if status not in allowed:
                    raise SystemExit(f"kb: status must be one of {', '.join(allowed)}")
                text = path.read_text(encoding="utf-8")
                updated, count = re.subn(r"(?m)^work_status:.*$", f"work_status: {status}", text, count=1)
                if not count:
                    raise SystemExit(f"kb: {repo.rel(path)} has no work_status line")
                if links:
                    updated = set_links(updated, links)
                atomic_write(path, updated)
                _refresh(repo)
                return path
    raise SystemExit(f"kb: no epic or item with id {ident}")
