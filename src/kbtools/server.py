"""MCP server exposing kb commands as tools (streamable HTTP).

Each tool runs the `kb` CLI as a subprocess against a repository the server itself can
see. The server is meant for agents on the Paperclip machine (the Librarian, Chief) that
need the heavy commands (extract, figure); project containers use `tools/kb` instead.

`repo` is either a repository name looked up under KB_REPOS_ROOT (`gameworld` or
`owner/gameworld`) or an absolute path under KB_REPOS_ROOT or one of the allowed roots.
Failures are raised, so MCP clients see them as tool errors (`isError: true`).
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_REPOS_ROOT = "/repos"
TIMEOUT = 1800


@dataclass
class Settings:
    """Server settings from the environment (`kb serve` flags override them)."""

    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    repos_root: Path = Path(DEFAULT_REPOS_ROOT)
    allowed_roots: list[Path] = field(default_factory=list)


def settings(environ: dict[str, str] | None = None) -> Settings:
    env = os.environ if environ is None else environ
    port = env.get("KB_MCP_PORT", "").strip()
    try:
        port_number = int(port) if port else DEFAULT_PORT
    except ValueError:
        raise SystemExit(f"kb serve: KB_MCP_PORT must be a port number, not {port!r}")
    return Settings(
        host=env.get("KB_MCP_HOST", "").strip() or DEFAULT_HOST,
        port=port_number,
        repos_root=Path(env.get("KB_REPOS_ROOT", "").strip() or DEFAULT_REPOS_ROOT),
        allowed_roots=[Path(p) for p in env.get("KB_ALLOWED_ROOTS", "").split(os.pathsep) if p.strip()],
    )


class KbToolError(Exception):
    """A tool failure; FastMCP returns it to the client as a tool error (isError: true)."""


_REPOS_ROOT: list[Path] = [Path(DEFAULT_REPOS_ROOT)]
_ALLOWED: list[Path] = []


def configure(repos_root: Path, allowed_roots: list[Path]) -> None:
    _REPOS_ROOT[:] = [Path(repos_root).resolve()]
    _ALLOWED[:] = [Path(root).resolve() for root in allowed_roots]


def _roots() -> list[Path]:
    return [*_REPOS_ROOT, *(r for r in _ALLOWED if r not in _REPOS_ROOT)]


def visible_repos(limit: int = 50) -> list[str]:
    """Repository names under KB_REPOS_ROOT (`name` or `owner/name`), as agents can pass them."""
    root = _REPOS_ROOT[0]
    if not root.is_dir():
        return []

    def is_repo(path: Path) -> bool:
        return (path / ".git").exists() or (path / "docs").is_dir()

    names = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if is_repo(child):
            names.append(child.name)
        else:
            names += [f"{child.name}/{g.name}" for g in sorted(child.iterdir()) if g.is_dir() and is_repo(g)]
    return names[:limit]


def _where() -> str:
    repos = visible_repos()
    listed = ", ".join(repos) if repos else "none"
    return (f"KB_REPOS_ROOT is {_REPOS_ROOT[0]} (repositories there: {listed}); "
            f"absolute paths must be under {', '.join(str(r) for r in _roots())}")


def resolve_repo(repo: str) -> Path:
    """Map `repo` (a name under KB_REPOS_ROOT, or an absolute path) to a directory, or raise."""
    value = (repo or "").strip()
    if not value:
        raise KbToolError(f"repo is required. {_where()}")
    if Path(value).is_absolute():
        path = Path(value).resolve()
        if not path.is_dir():
            raise KbToolError(f"{value} is not a directory visible to the kb-tools server. {_where()}")
        if not any(path.is_relative_to(root) for root in _roots()):
            raise KbToolError(f"{value} is outside the kb-tools server's roots. {_where()}")
        return path
    name = value.removesuffix(".git").strip("/")
    parts = name.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise KbToolError(f"{value!r} is not a repository name. {_where()}")
    root = _REPOS_ROOT[0]
    candidates = [root / name]
    if len(parts) > 1:
        candidates.append(root / parts[-1])
    elif root.is_dir():
        candidates += sorted(owner / name for owner in root.iterdir() if owner.is_dir() and not owner.name.startswith("."))
    found = list(dict.fromkeys(c.resolve() for c in candidates if c.is_dir()))
    found = [f for f in found if f.is_relative_to(root)]
    if len(found) > 1:
        raise KbToolError(f"{value!r} matches more than one repository: {', '.join(map(str, found))}; "
                          f"pass owner/name or the absolute path")
    if not found:
        raise KbToolError(f"no repository {value!r} under KB_REPOS_ROOT. {_where()}. On the Paperclip "
                          f"machine, check the repository out under KB_REPOS_ROOT; in a project container, "
                          f"use tools/kb instead of the MCP tools")
    return found[0]


def instructions() -> str:
    return f"""\
kb-tools: document ingestion and knowledge-base checks for repositories that keep an
OKF knowledge base in docs/. These MCP tools are for agents on the Paperclip machine (the
agent that ingests documents, e.g. a Librarian, and Chief): they run against checkouts the
server can see. Agents working in a project's dev container use `tools/kb` there instead.
Pass `repo` as a repository name under the server's repos root ({_REPOS_ROOT[0]}), e.g.
`gameworld` or `owner/gameworld`, or as an absolute path under {', '.join(str(r) for r in _roots())}.
A failed call is returned as a tool error. Typical flow: kb_inventory -> kb_extract ->
read extracted/<package>/ (pages.md, slides.md, renders/*.png) and reconcile ->
kb_figure for key graphics -> write pages -> kb_log -> kb_check. Read the repository's
docs/process/ingestion.md for the full method.
"""


def _run(repo: str, *args: str) -> str:
    path = resolve_repo(repo)
    try:
        run = subprocess.run([sys.executable, "-m", "kbtools.cli", "--repo", str(path), *args],
                             capture_output=True, text=True, timeout=TIMEOUT, cwd=path)
    except subprocess.TimeoutExpired:
        raise KbToolError(f"kb {' '.join(args[:2])} timed out after {TIMEOUT}s")
    output = (run.stdout + ("\n" + run.stderr if run.stderr.strip() else "")).strip()
    if run.returncode != 0:
        raise KbToolError(f"kb {' '.join(args[:2])} failed (exit {run.returncode}) in {path}\n{output}")
    return f"exit 0 ({path})\n{output}"


def _run_dir(repo: str, *args: str) -> str:
    """Like _run, but for commands that work before docs/ exists (scaffold)."""
    return _run(repo, *args)


def _options(**values: str) -> list[str]:
    """CLI options for the non-empty values: _options(pr="41") -> ["--pr", "41"]."""
    return [part for key, value in values.items() if value for part in (f"--{key}", value)]


def build_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    from mcp.server.fastmcp import FastMCP
    from mcp.types import ToolAnnotations

    mcp = FastMCP("kb-tools", instructions=instructions(), host=host, port=port)
    # Risk hints for clients that classify tools (Paperclip quarantines destructive tools
    # and gates writes): reads are read-only; writes only add or update files inside the
    # repository's docs/sources log, extracted/ and docs/ assets, never delete user content.
    read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    write = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)

    @mcp.tool(annotations=write)
    def kb_scaffold(repo: str, project: str, by: str = "", dry_run: bool = False) -> str:
        """Install the generic knowledge-base layout (docs/ sections, conventions, process pages,
        AGENTS.md/CLAUDE.md pointers, tools/kb, data/, intake folders) into a repository.
        Never overwrites existing files; use dry_run=true to preview."""
        args = ["scaffold", "--project", project] + (["--by", by] if by else []) + (["--dry-run"] if dry_run else [])
        return _run_dir(repo, *args)

    @mcp.tool(annotations=write)
    def kb_init(repo: str) -> str:
        """Scaffold docs/sources (git-ignored), docs/sources/ingest-log.csv and extracted/ if missing."""
        return _run(repo, "init")

    @mcp.tool(annotations=write)
    def kb_inventory(repo: str, by: str, origin: str = "") -> str:
        """Hash new files in docs/sources and log them as pending. `by` is who is logging,
        e.g. 'paperclip/<agent-name>'; `origin` is where the files came from, e.g. 'paperclip:CEN-12'."""
        return _run(repo, "inventory", "--by", by, "--origin", origin)

    @mcp.tool(annotations=write)
    def kb_extract(repo: str, sources: list[str] | None = None, pending: bool = False,
                   dpi: int = 120, force: bool = False) -> str:
        """Build extraction packages in extracted/<slug>/: text.md, pages.md, slides.md (PowerPoint),
        workbook.json (Excel), renders/page-NNN.png for every page or slide, media/, review.md.
        Pass file names relative to docs/sources, or pending=true for all pending sources."""
        args = ["extract", "--dpi", str(dpi)] + (["--pending"] if pending else list(sources or []))
        return _run(repo, *args, *(["--force"] if force else []))

    @mcp.tool(annotations=write)
    def kb_figure(repo: str, image: str, out: str, crop: str = "", page: str = "", alt: str = "",
                  caption: str = "", source: str = "", max_width: int = 1600, overwrite: bool = False) -> str:
        """Crop/resize a render or media image into docs/ (e.g. docs/<section>/assets/name.png) and return
        a Markdown snippet with alt text, caption, source and an element table to fill in.
        `crop` is 'left,top,right,bottom' as fractions (copy a bbox from slides.md) or pixels."""
        args = ["figure", image, "--out", out, "--max-width", str(max_width), "--alt", alt,
                "--caption", caption, "--source", source]
        if crop:
            args += ["--crop", crop]
        if page:
            args += ["--page", page]
        if overwrite:
            args.append("--overwrite")
        return _run(repo, *args)

    @mcp.tool(annotations=write)
    def kb_log(repo: str, source: str, status: str = "", by: str = "", outputs: str = "",
               add_outputs: list[str] | None = None, notes: str = "", origin: str = "", rehash: bool = False) -> str:
        """Update a source's ingest-log row. status: pending|extracted|reconciled|ingested|partial|skipped|superseded.
        outputs replaces the list ('path;path' relative to the repo root); add_outputs appends."""
        args = ["log", source]
        for flag, value in (("--status", status), ("--by", by), ("--outputs", outputs), ("--notes", notes), ("--origin", origin)):
            if value:
                args += [flag, value]
        for item in add_outputs or []:
            args += ["--add-output", item]
        if rehash:
            args.append("--rehash")
        return _run(repo, *args)

    @mcp.tool(annotations=write)
    def kb_catalog(repo: str, format: str = "md", type: str = "", section: str = "", tag: str = "",
                   tier: str = "", status: str = "", work_status: str = "", text: str = "",
                   write: bool = False) -> str:
        """List knowledge pages (path, type, title, description, tags, status, work_status, trust tier,
        last verification). Filter by type/section/tag/tier/status/work_status or words in `text`.
        format: md (compact, grouped by section) | json | jsonl. Start here to find pages.
        write=true regenerates docs/catalog.md from page front matter instead of listing
        (same as `kb catalog --write`; filters and format are ignored). Use it after adding or
        editing pages rather than editing catalog.md rows by hand."""
        if write:
            return _run(repo, "catalog", "--write")
        args = ["catalog", "--format", format]
        for flag, value in (("--type", type), ("--section", section), ("--tag", tag), ("--tier", tier),
                            ("--status", status), ("--work-status", work_status), ("--text", text)):
            if value:
                args += [flag, value]
        return _run(repo, *args)

    @mcp.tool(annotations=read)
    def kb_work_list(repo: str, status: str = "", open_only: bool = False) -> str:
        """List epics and work items in docs/work/ (id, kind, title, work_status, dependencies, path)."""
        return _run(repo, "work", "list", *(["--status", status] if status else []), *(["--open"] if open_only else []))

    @mcp.tool(annotations=write)
    def kb_work_new_epic(repo: str, title: str, by: str, priority: str = "medium", status: str = "proposed",
                         description: str = "", github: str = "", jira: str = "", paperclip: str = "") -> str:
        """Create docs/work/epics/NNNN-slug/ with epic.md (business need) and plan.md (implementation plan).
        `description` is one sentence on the business need; github, jira and paperclip set its links."""
        args = ["work", "new-epic", title, "--by", by, "--priority", priority, "--status", status]
        return _run(repo, *args, *_options(description=description, github=github, jira=jira, paperclip=paperclip))

    @mcp.tool(annotations=write)
    def kb_work_new_item(repo: str, epic: str, title: str, by: str, kind: str = "story", priority: str = "medium",
                         status: str = "todo", depends_on: list[str] | None = None, description: str = "",
                         github: str = "", jira: str = "", paperclip: str = "") -> str:
        """Create a work item in an epic's items/ folder (ids NNNN-NN). kind: story|task|bug|spike|chore.
        `description` is one sentence on what it delivers; github, jira and paperclip set its links."""
        args = ["work", "new-item", epic, title, "--by", by, "--kind", kind, "--priority", priority, "--status", status]
        for dependency in depends_on or []:
            args += ["--depends-on", dependency]
        return _run(repo, *args, *_options(description=description, github=github, jira=jira, paperclip=paperclip))

    @mcp.tool(annotations=write)
    def kb_work_set(repo: str, id: str, status: str, pr: str = "", github: str = "", jira: str = "",
                    paperclip: str = "") -> str:
        """Set work_status of an epic (proposed|planned|in_progress|done|cancelled) or item
        (backlog|todo|in_progress|in_review|blocked|done|cancelled); regenerates the roadmap.
        `pr` (URL or number) records the delivering pull request in links.github; github, jira and
        paperclip set those links."""
        return _run(repo, "work", "set", id, status, *_options(pr=pr, github=github, jira=jira, paperclip=paperclip))

    @mcp.tool(annotations=read)
    def kb_check(repo: str, strict: bool = False) -> str:
        """Validate the ingest log, OKF front matter, links, images (alt text) and diagram element descriptions."""
        return _run(repo, "check", *(["--strict"] if strict else []))

    @mcp.tool(annotations=read)
    def kb_report(repo: str, format: str = "md", max_age: int = 365) -> str:
        """Verification level (human/machine/unverified), last verification date, age and flags
        (changed-since-verified, stale, verification-old, deprecated) for every page."""
        return _run(repo, "report", "--format", format, "--max-age", str(max_age))

    return mcp


def serve(host: str, port: int, repos_root: Path, allowed_roots: list[Path]) -> None:
    configure(repos_root, allowed_roots)
    build_server(host, port).run(transport="streamable-http")
