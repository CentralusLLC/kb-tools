"""Intake commands: init (scaffold), inventory (hash and log sources), log (update a row)."""

from __future__ import annotations

from pathlib import Path

from . import ingest_log
from .common import SOURCE_HOUSEKEEPING, Repo, atomic_write, sha256, today

SOURCES_GITIGNORE = """\
# Source files are working material: keep them out of git.
# The ingest log records each file's hash and origin so it can be re-fetched.
*
!.gitignore
!index.md
!ingest-log.csv
"""

EXTRACTED_GITIGNORE = """\
# Extraction packages (text, renders, media) are reproducible working output.
# Curated figures are copied into docs/ with `kb figure`.
*
!.gitignore
"""

SOURCES_INDEX = """\
# Sources

Inbox for raw source files waiting to be ingested. Files here are ignored by git;
`ingest-log.csv` tracks each one (hash, origin, status, outputs). See the
project's ingestion process page for the workflow.
"""


def init(repo: Repo) -> list[str]:
    """Create the intake scaffolding if missing. Returns the paths created or upgraded."""
    created = []
    files = {
        repo.sources / ".gitignore": SOURCES_GITIGNORE,
        repo.sources / "index.md": SOURCES_INDEX,
        repo.extracted / ".gitignore": EXTRACTED_GITIGNORE,
    }
    for path, content in files.items():
        if not path.exists():
            atomic_write(path, content)
            created.append(repo.rel(path))
    if not repo.log_path.exists() or ingest_log.header_problems(repo.log_path):
        rows = ingest_log.load(repo.log_path)
        ingest_log.save(repo.log_path, rows)
        created.append(repo.rel(repo.log_path))
    return created


def source_files(repo: Repo) -> list[Path]:
    if not repo.sources.exists():
        return []
    files = []
    for path in sorted(repo.sources.rglob("*")):
        relative = path.relative_to(repo.sources)
        if not path.is_file() or any(p.startswith(".") for p in relative.parts):
            continue
        if len(relative.parts) == 1 and relative.name in SOURCE_HOUSEKEEPING:
            continue
        files.append(path)
    return files


def inventory(repo: Repo, *, added_by: str, origin: str = "") -> dict[str, list[str]]:
    """Log new source files as pending and report changed or locally missing ones."""
    rows = ingest_log.load(repo.log_path)
    index = ingest_log.by_source(rows)
    result = {"added": [], "changed": [], "missing_locally": [], "unchanged": []}
    present = set()
    for path in source_files(repo):
        relative = path.relative_to(repo.sources).as_posix()
        present.add(relative)
        digest = sha256(path)
        row = index.get(relative)
        if row is None:
            rows.append(
                {
                    "source": relative,
                    "sha256": digest,
                    "added_at": today(),
                    "added_by": added_by,
                    "origin": origin,
                    "status": "pending",
                }
            )
            result["added"].append(relative)
        elif row["sha256"] != digest:
            result["changed"].append(relative)
        else:
            result["unchanged"].append(relative)
    for relative in index:
        if relative not in present and index[relative]["status"] != "superseded":
            result["missing_locally"].append(relative)
    ingest_log.save(repo.log_path, rows)
    return result


def update_row(
    repo: Repo,
    source: str,
    *,
    status: str | None = None,
    by: str | None = None,
    origin: str | None = None,
    outputs: list[str] | None = None,
    add_outputs: list[str] | None = None,
    notes: str | None = None,
    rehash: bool = False,
) -> dict[str, str]:
    rows = ingest_log.load(repo.log_path)
    index = ingest_log.by_source(rows)
    if source not in index:
        raise SystemExit(f"kb: {source!r} is not in the ingest log (run `kb inventory` first)")
    row = index[source]
    if status:
        if status not in ingest_log.STATUSES:
            raise SystemExit(f"kb: status must be one of {', '.join(ingest_log.STATUSES)}")
        row["status"] = status
        if status in ingest_log.DONE_STATUSES:
            row["ingested_at"] = today()
            if by:
                row["ingested_by"] = by
    if origin is not None:
        row["origin"] = origin
    if outputs is not None:
        row["outputs"] = ";".join(outputs)
    if add_outputs:
        current = ingest_log.split_outputs(row["outputs"])
        row["outputs"] = ";".join(current + [o for o in add_outputs if o not in current])
    if notes is not None:
        row["notes"] = notes
    if rehash:
        path = repo.sources / source
        if not path.exists():
            raise SystemExit(f"kb: cannot rehash, {path} is not present")
        row["sha256"] = sha256(path)
    ingest_log.save(repo.log_path, rows)
    return row
