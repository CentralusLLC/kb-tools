"""Command line: `kb <command>`. Run `kb --help` for the list."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .common import Repo, find_repo


def _repo(args) -> Repo:
    return find_repo(Path(args.repo) if args.repo else None)


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


def cmd_extract(args) -> int:
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
    from .figure import make_figure

    snippet = make_figure(
        _repo(args), Path(args.image), Path(args.out), crop=args.crop, pad=args.pad, max_width=args.max_width,
        page=Path(args.page) if args.page else None, alt=args.alt, caption=args.caption,
        source_ref=args.source, overwrite=args.overwrite,
    )
    print(snippet)
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

    serve(host=args.host, port=args.port, allowed_roots=[Path(p) for p in args.allowed_root])
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kb", description="Knowledge-base ingestion and trust tools.")
    parser.add_argument("--version", action="version", version=f"kb-tools {__version__}")
    parser.add_argument("--repo", help="repository root (default: found from the current directory)")
    sub = parser.add_subparsers(dest="command", required=True)

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

    p = sub.add_parser("check", help="validate the ingest log, OKF front matter, links, images and diagrams")
    p.add_argument("--strict", action="store_true", help="fail on warnings too")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("report", help="verification level and recency for every page")
    p.add_argument("--format", choices=["md", "csv", "json"], default="md")
    p.add_argument("--max-age", type=int, default=365, help="days after which a verification counts as old")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("serve", help="run the MCP server (streamable HTTP) for agents")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--allowed-root", action="append", default=[], help="directories repos must live under (repeatable)")
    p.set_defaults(func=cmd_serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
