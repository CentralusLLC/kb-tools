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
from dataclasses import dataclass, field
from pathlib import Path

from . import okf
from .common import Repo, atomic_write, now_iso, slugify

EPIC_STATUSES = ("proposed", "planned", "in_progress", "done", "cancelled")
ITEM_STATUSES = ("backlog", "todo", "in_progress", "in_review", "blocked", "done", "cancelled")
PRIORITIES = ("critical", "high", "medium", "low")
CLOSED = {"done", "cancelled"}
INDEX_START, INDEX_END = "<!-- kb:work-index:start -->", "<!-- kb:work-index:end -->"
EPIC_DIR = re.compile(r"^(\d{4})-[a-z0-9-]+$")
ITEM_FILE = re.compile(r"^(\d{2})-[a-z0-9-]+\.md$")


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
            if item.id in ids:
                errors.append(f"{item_where}: duplicate id {item.id}")
            ids[item.id] = item_where
            if item_status not in CLOSED:
                open_items.append(item.id)
            if item_status in {"in_progress", "in_review", "done"} and status in {"proposed"}:
                warnings.append(f"{item_where}: item is {item_status} but its epic is still proposed")
        if status in CLOSED and open_items:
            warnings.append(f"{where}: epic is {status} but items are still open: {', '.join(open_items)}")
    for epic in epics:
        for item in epic.items:
            for dependency in item.data.get("depends_on") or []:
                if str(dependency) not in ids:
                    errors.append(f"{repo.rel(item.path)}: depends_on {dependency} does not exist")
    index = work_dir(repo) / "index.md"
    if epics and index.is_file() and index.read_text(encoding="utf-8") != _with_index(index.read_text(encoding="utf-8"), epics, repo):
        warnings.append("docs/work/index.md roadmap is out of date (run `kb work index`)")
    return errors, warnings


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
    for epic in epics:
        entries = [("epic", epic.id, epic.data, epic.path)] + [("item", i.id, i.data, i.path) for i in epic.items]
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


def new_epic(repo: Repo, title: str, *, by: str, priority: str = "medium", status: str = "proposed") -> Path:
    if status not in EPIC_STATUSES:
        raise SystemExit(f"kb: status must be one of {', '.join(EPIC_STATUSES)}")
    epics, _ = load(repo)
    number = f"{max((int(e.number) for e in epics), default=0) + 1:04d}"
    folder = work_dir(repo) / "epics" / f"{number}-{slugify(title)[:48].strip('-')}"
    folder.mkdir(parents=True)
    stamp = [("generated", f"\n  by: {by}\n  at: {now_iso()}")]
    epic = _front([
        ("type", "Epic"), ("id", f'"{number}"'), ("title", _quote(title)),
        ("description", _quote(f"TODO: one sentence on the business need behind {title}.")),
        ("tags", "[epic]"), ("status", "draft"), ("work_status", status), ("priority", priority),
        ("owner", '""'), ("target", '""'),
        ("links", "\n  github: \"\"\n  jira: \"\"\n  paperclip: \"\""), *stamp,
    ]) + f"""
# Epic {number}: {title}

## Problem / business need

> TODO: Who has the problem, what it costs them, and why now.

## Outcome and success measures

> TODO: What is true when this epic is done, and how we will know (measurable where possible).

## Scope

> TODO: What is included.

## Non-goals

> TODO: What is deliberately excluded.

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
             status: str = "todo", depends_on: list[str] | None = None) -> Path:
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
        ("description", _quote(f"TODO: one sentence on what {ident} delivers.")),
        ("tags", "[work-item]"), ("status", "draft"), ("work_status", status), ("priority", priority),
        ("depends_on", depends), ("links", "\n  github: \"\"\n  jira: \"\"\n  paperclip: \"\""),
        ("generated", f"\n  by: {by}\n  at: {now_iso()}"),
    ]) + f"""
# {ident}: {title}

Part of [epic {epic.number}](../epic.md) ([plan](../plan.md)).

## What and why

> TODO: The change, and the user or business value it delivers.

## Acceptance criteria

- [ ] TODO

## Notes

> TODO: Design notes, constraints, links. Record decisions that outlive this item as ADRs.
"""
    atomic_write(path, text)
    _refresh(repo)
    return path


def _refresh(repo: Repo) -> None:
    from .catalog import refresh_if_present

    write_index(repo)
    refresh_if_present(repo)


def set_status(repo: Repo, ident: str, status: str) -> Path:
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
                atomic_write(path, updated)
                _refresh(repo)
                return path
    raise SystemExit(f"kb: no epic or item with id {ident}")

