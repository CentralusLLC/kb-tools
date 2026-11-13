"""Command line: `kb <command>`. Run `kb --help` for the list."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .version import full_version
from .common import Repo, find_repo


def _repo(args) -> Repo:
    return find_repo(Path(args.repo) if args.repo else None)


def cmd_scaffold(args) -> int:
    import subprocess

    from .scaffold import POINTER_SNIPPET, scaffold

    if args.repo:
        target = Path(args.repo).resolve()
    else:
        try:
            top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
            target = Path(top.stdout.strip()) if top.returncode == 0 and top.stdout.strip() else Path.cwd()
        except OSError:  # no git in the container: the wrapper starts us at the repository root
            target = Path.cwd()
    if not (target / ".git").exists():
        print(f"note: {target} is not a git repository root; scaffolding there anyway")
    result = scaffold(target, project=args.project, actor=args.by, dry_run=args.dry_run)
    verb = "would create" if args.dry_run else "created"
    for path in result["created"]:
        print(f"{verb} {path}")
    for path in result["skipped"]:
        print(f"exists, kept {path}")
    print(f"{len(result['created'])} {verb.split()[-1]}, {len(result['skipped'])} kept")
    kept_pointers = [p for p in ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md") if p in result["skipped"]]
    if kept_pointers:
        print("\nThese agent files already existed and were not changed: " + ", ".join(kept_pointers))
        print("Add a pointer to the knowledge base in each, for example:\n\n" + POINTER_SNIPPET)
    if not args.dry_run:
        print("Next: fill in the TODOs (start with docs/business/vision.md and docs/architecture/overview.md), "
              "then run `tools/kb check`.")
    return 0


def cmd_init(args) -> int:
    from .intake import init

    created = init(_repo(args))
    print("\n".join(f"created {p}" for p in created) or "already initialised")
    return 0


def cmd_inventory(args) -> int:
    from .intake import inventory

    result = inventory(_repo(args), added_by=args.by, origin=args.origin)
    for key in ("added", "changed", "missing_locally"):
        for name in result[key]:
            print(f"{key}: {name}")
    print(f"{len(result['added'])} added, {len(result['changed'])} changed, "
          f"{len(result['unchanged'])} unchanged, {len(result['missing_locally'])} not present locally")
    return 0


EXTRACT_MISSING = """kb {command}: the extraction libraries are not installed (light install).
Document extraction and figures run on the Paperclip machine: ask the agent that ingests
documents there (for example a Librarian agent) to run kb_{command} through the kb-tools MCP server.
To run it here instead, install everything: tools/kb --install --full ({missing} is missing)."""


def _needs_extract(command: str) -> int:
    """0 when the [extract] dependencies import, otherwise print why and return 2."""
    import importlib

    modules = ("PIL",) if command == "figure" else ("markitdown", "pptx", "openpyxl", "pypdfium2", "PIL")
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError:
            print(EXTRACT_MISSING.format(command=command, missing=module), file=sys.stderr)
            return 2
    return 0


def cmd_extract(args) -> int:
    if code := _needs_extract("extract"):
        return code
    from .extract import extract_source, pending_sources

    repo = _repo(args)
    sources = pending_sources(repo) if args.pending else [_relative_source(repo, s) for s in args.sources]
    if not sources:
        print("nothing to extract")
        return 0
    failed = 0
    for relative in sources:
        result = extract_source(repo, relative, dpi=args.dpi, force=args.force)
        failed += result["status"] == "failed"
        print(json.dumps({"source": relative, **result}, indent=2))
    return 1 if failed else 0


def _relative_source(repo: Repo, value: str) -> str:
    path = Path(value)
    candidates = [path] if path.is_absolute() else [Path.cwd() / path, repo.root / path, repo.sources / path]
    for candidate in candidates:
        if candidate.exists():
            try:
                return candidate.resolve().relative_to(repo.sources.resolve()).as_posix()
            except ValueError:
                raise SystemExit(f"kb: {value} is not inside docs/sources/")
    raise SystemExit(f"kb: {value} not found")


def cmd_log(args) -> int:
    from .intake import update_row

    from . import ingest_log

    repo = _repo(args)
    logged = {row["source"] for row in ingest_log.load(repo.log_path)}
    source = args.source if args.source in logged else _relative_source(repo, args.source)
    row = update_row(
        repo, source,
        status=args.status, by=args.by, origin=args.origin,
        outputs=[o for o in args.outputs.split(";") if o] if args.outputs is not None else None,
        add_outputs=args.add_output, notes=args.notes, rehash=args.rehash,
    )
    print(json.dumps(row, indent=2))
    return 0


def cmd_figure(args) -> int:
    if code := _needs_extract("figure"):
        return code
    from .figure import make_figure

    snippet = make_figure(
        _repo(args), Path(args.image), Path(args.out), crop=args.crop, pad=args.pad, max_width=args.max_width,
        page=Path(args.page) if args.page else None, alt=args.alt, caption=args.caption,
        source_ref=args.source, overwrite=args.overwrite,
    )
    print(snippet)
    return 0


def cmd_work(args) -> int:
    from . import work

    repo = _repo(args)
    if args.work_command == "new-epic":
        folder = work.new_epic(repo, args.title, by=args.by, priority=args.priority, status=args.status)
        print(f"created {repo.rel(folder)}/epic.md and plan.md")
    elif args.work_command == "new-item":
        path = work.new_item(repo, args.epic, args.title, by=args.by, priority=args.priority,
                             status=args.status, depends_on=args.depends_on or [], kind=args.kind)
        print(f"created {repo.rel(path)}")
    elif args.work_command == "set":
        print(f"updated {repo.rel(work.set_status(repo, args.id, args.status))}")
    elif args.work_command == "index":
        print(f"updated {repo.rel(work.write_index(repo))}")
    elif args.work_command == "list":
        print(work.listing(repo, status=args.status, open_only=args.open), end="")
    return 0


def cmd_catalog(args) -> int:
    from . import catalog

    repo = _repo(args)
    if args.write:
        print(f"updated {repo.rel(catalog.write(repo))}")
        return 0
    rows = catalog.select(catalog.records(repo), type_=args.type, section=args.section, tag=args.tag,
                          tier=args.tier, status=args.status, work_status=args.work_status, text=args.text)
    print(catalog.render(rows, args.format), end="")
    return 0


def cmd_check(args) -> int:
    from .check import run_checks

    errors, warnings = run_checks(_repo(args))
    for line in errors:
        print(f"ERROR   {line}")
    for line in warnings:
        print(f"warning {line}")
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors or (args.strict and warnings) else 0


def cmd_report(args) -> int:
    from .report import page_trust, render

    print(render(page_trust(_repo(args), args.max_age), args.format), end="")
    return 0


def cmd_serve(args) -> int:
    from .server import serve

    from .server import settings

    config = settings()
    serve(host=args.host or config.host, port=args.port or config.port, repos_root=config.repos_root,
          allowed_roots=[Path(p) for p in args.allowed_root] or config.allowed_roots)
    return 0


class _Version(argparse.Action):
    """--version, resolved only when asked for (it may call git)."""

    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):
        super().__init__(option_strings, dest=dest, default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        print(f"kb-tools {full_version()}")
        parser.exit()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kb", description="Knowledge-base ingestion and trust tools.")
    parser.add_argument("--version", action=_Version, help="show the version, git ref and commit, and exit")
    parser.add_argument("--repo", help="repository root (default: found from the current directory)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scaffold", help="install the generic knowledge-base layout (docs/, AGENTS.md, tools/kb, ...) without overwriting")
    p.add_argument("--project", required=True, help="project name used in the pages")
    p.add_argument("--by", default=f"kb-tools/{__version__}", help="actor recorded in generated: (default kb-tools/<version>)")
    p.add_argument("--dry-run", action="store_true", help="list what would be created")
    p.set_defaults(func=cmd_scaffold)

    p = sub.add_parser("init", help="scaffold docs/sources (git-ignored), the ingest log and extracted/")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("inventory", help="hash new files in docs/sources and log them as pending")
    p.add_argument("--by", required=True, help="who is logging: human:<name> or <tool>/<version>")
    p.add_argument("--origin", default="", help="where new files came from (URL, paperclip:<issue>, drive path)")
    p.set_defaults(func=cmd_inventory)

    p = sub.add_parser("extract", help="build extraction packages under extracted/")
    p.add_argument("sources", nargs="*", help="files in docs/sources (path or name)")
    p.add_argument("--pending", action="store_true", help="extract every pending source")
    p.add_argument("--dpi", type=int, default=120, help="render resolution (default 120)")
    p.add_argument("--force", action="store_true", help="rebuild existing packages")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("log", help="update a source's ingest-log row")
    p.add_argument("source")
    p.add_argument("--status", help="pending|extracted|reconciled|ingested|partial|skipped|superseded")
    p.add_argument("--by", help="who did it (sets ingested_by for final statuses)")
    p.add_argument("--origin")
    p.add_argument("--outputs", help="replace outputs: 'path;path' relative to the repo root")
    p.add_argument("--add-output", action="append", help="append one output path (repeatable)")
    p.add_argument("--notes")
    p.add_argument("--rehash", action="store_true", help="record the file's current hash")
    p.set_defaults(func=cmd_log)

    p = sub.add_parser("figure", help="crop/resize a render or media image into docs/ and print a Markdown snippet")
    p.add_argument("image", help="render or media file, e.g. extracted/<pkg>/renders/page-004.png")
    p.add_argument("--out", required=True, help="destination inside docs/, e.g. docs/domains/world/assets/map.png")
    p.add_argument("--crop", help="left,top,right,bottom as fractions (from slides.md) or pixels")
    p.add_argument("--pad", type=float, default=0.01, help="margin added around the crop, as a fraction")
    p.add_argument("--max-width", type=int, default=1600)
    p.add_argument("--page", help="the page that will embed the figure (makes the link relative to it)")
    p.add_argument("--alt", default="")
    p.add_argument("--caption", default="")
    p.add_argument("--source", default="", help="citation, e.g. 'docs/sources/deck.pptx, slide 4'")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_figure)

    p = sub.add_parser("work", help="repository-native work tracking: epics, plans and items in docs/work/")
    work_sub = p.add_subparsers(dest="work_command", required=True)
    w = work_sub.add_parser("new-epic", help="create docs/work/epics/NNNN-slug/ with epic.md and plan.md")
    w.add_argument("title")
    w.add_argument("--by", required=True, help="human:<name> or <tool>/<version>")
    w.add_argument("--priority", default="medium", choices=["critical", "high", "medium", "low"])
    w.add_argument("--status", default="proposed", help="proposed|planned|in_progress|done|cancelled")
    w = work_sub.add_parser("new-item", help="create items/NN-slug.md in an epic")
    w.add_argument("epic", help="epic number, e.g. 0007")
    w.add_argument("title")
    w.add_argument("--by", required=True)
    w.add_argument("--priority", default="medium", choices=["critical", "high", "medium", "low"])
    w.add_argument("--status", default="todo", help="backlog|todo|in_progress|in_review|blocked|done|cancelled")
    w.add_argument("--depends-on", action="append", help="item id this depends on (repeatable)")
    w.add_argument("--kind", default="story", choices=["story", "task", "bug", "spike", "chore"])
    w = work_sub.add_parser("set", help="set work_status of an epic or item")
    w.add_argument("id", help="epic id (0007) or item id (0007-02)")
    w.add_argument("status")
    work_sub.add_parser("index", help="regenerate the roadmap in docs/work/index.md")
    w = work_sub.add_parser("list", help="list epics and items")
    w.add_argument("--status")
    w.add_argument("--open", action="store_true", help="only items and epics not done or cancelled")
    p.set_defaults(func=cmd_work)

    p = sub.add_parser("catalog", help="list every page (path, type, description, tags, trust); --write updates docs/catalog.md")
    p.add_argument("--write", action="store_true", help="regenerate docs/catalog.md (unfiltered)")
    p.add_argument("--format", choices=["md", "json", "jsonl"], default="md")
    p.add_argument("--type", help="page type, e.g. 'Work Item'")
    p.add_argument("--section", help="top-level section, e.g. domains")
    p.add_argument("--tag")
    p.add_argument("--tier", choices=["human", "machine", "unverified"])
    p.add_argument("--status", help="draft|stable|deprecated")
    p.add_argument("--work-status")
    p.add_argument("--text", help="words that must all appear in path, title, description or tags")
    p.set_defaults(func=cmd_catalog)

    p = sub.add_parser("check", help="validate the ingest log, OKF front matter, links, images and diagrams")
    p.add_argument("--strict", action="store_true", help="fail on warnings too")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("report", help="verification level and recency for every page")
    p.add_argument("--format", choices=["md", "csv", "json"], default="md")
    p.add_argument("--max-age", type=int, default=365, help="days after which a verification counts as old")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("serve", help="run the MCP server (streamable HTTP) for agents")
    p.add_argument("--host", help="address to listen on (default: $KB_MCP_HOST or 127.0.0.1)")
    p.add_argument("--port", type=int, help="port to listen on (default: $KB_MCP_PORT or 8765)")
    p.add_argument("--allowed-root", action="append", default=[],
                   help="extra directories absolute repo paths may live under (repeatable; default: "
                        "$KB_ALLOWED_ROOTS). Repos under $KB_REPOS_ROOT (default /repos) are always allowed")
    p.set_defaults(func=cmd_serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
