"""MCP server exposing kb commands as tools (streamable HTTP).

Each tool runs the `kb` CLI as a subprocess against a repository path that must
live under one of the allowed roots (for Paperclip: the shared /paperclip volume),
so agents in other containers can ingest without LibreOffice or Python packages.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

INSTRUCTIONS = """\
kb-tools: document ingestion and knowledge-base checks for repositories that keep an
OKF knowledge base in docs/. Pass `repo` as the absolute path of the repository checkout
(the same path you see in your workspace). Typical flow: kb_inventory -> kb_extract ->
read extracted/<package>/ (pages.md, slides.md, renders/*.png) and reconcile ->
kb_figure for key graphics -> write pages -> kb_log -> kb_check. Read the repository's
docs/process/ingestion.md for the full method.
"""

_ALLOWED: list[Path] = []
TIMEOUT = 1800


def _run(repo: str, *args: str) -> str:
    path = Path(repo).resolve()
    if not path.is_dir():
        return f"error: {repo} is not a directory visible to the kb-tools server"
    if _ALLOWED and not any(path.is_relative_to(root) for root in _ALLOWED):
        return f"error: {repo} is outside the allowed roots {[str(r) for r in _ALLOWED]}"
    try:
        run = subprocess.run([sys.executable, "-m", "kbtools.cli", "--repo", str(path), *args],
                             capture_output=True, text=True, timeout=TIMEOUT, cwd=path)
    except subprocess.TimeoutExpired:
        return f"error: kb {' '.join(args)} timed out after {TIMEOUT}s"
    output = (run.stdout + ("\n" + run.stderr if run.stderr.strip() else "")).strip()
    return f"exit {run.returncode}\n{output}"


def _run_dir(repo: str, *args: str) -> str:
    """Like _run, but for commands that work before docs/ exists (scaffold)."""
    return _run(repo, *args)


def build_server(host: str = "0.0.0.0", port: int = 8765):
    from mcp.server.fastmcp import FastMCP
    from mcp.types import ToolAnnotations

    mcp = FastMCP("kb-tools", instructions=INSTRUCTIONS, host=host, port=port)
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

    @mcp.tool(annotations=read)
    def kb_work_list(repo: str, status: str = "", open_only: bool = False) -> str:
        """List epics and work items in docs/work/ (id, kind, title, work_status, dependencies, path)."""
        return _run(repo, "work", "list", *(["--status", status] if status else []), *(["--open"] if open_only else []))

    @mcp.tool(annotations=write)
    def kb_work_new_epic(repo: str, title: str, by: str, priority: str = "medium", status: str = "proposed") -> str:
        """Create docs/work/epics/NNNN-slug/ with epic.md (business need) and plan.md (implementation plan)."""
        return _run(repo, "work", "new-epic", title, "--by", by, "--priority", priority, "--status", status)

    @mcp.tool(annotations=write)
    def kb_work_new_item(repo: str, epic: str, title: str, by: str, priority: str = "medium",
                         status: str = "todo", depends_on: list[str] | None = None) -> str:
        """Create a work item (story/task) file in an epic's items/ folder; ids are NNNN-NN."""
        args = ["work", "new-item", epic, title, "--by", by, "--priority", priority, "--status", status]
        for dependency in depends_on or []:
            args += ["--depends-on", dependency]
        return _run(repo, *args)

    @mcp.tool(annotations=write)
    def kb_work_set(repo: str, id: str, status: str) -> str:
        """Set work_status of an epic (proposed|planned|in_progress|done|cancelled) or item
        (backlog|todo|in_progress|in_review|blocked|done|cancelled); regenerates the roadmap."""
        return _run(repo, "work", "set", id, status)

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


def serve(host: str, port: int, allowed_roots: list[Path]) -> None:
    _ALLOWED[:] = [root.resolve() for root in allowed_roots]
    build_server(host, port).run(transport="streamable-http")
