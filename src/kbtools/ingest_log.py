"""Read and write docs/sources/ingest-log.csv."""

from __future__ import annotations

import csv
import io
from pathlib import Path

from .common import atomic_write

COLUMNS = [
    "source",
    "sha256",
    "added_at",
    "added_by",
    "origin",
    "status",
    "extraction",
    "ingested_at",
    "ingested_by",
    "outputs",
    "notes",
]
STATUSES = ("pending", "extracted", "reconciled", "ingested", "partial", "skipped", "superseded")
DONE_STATUSES = {"ingested", "partial", "skipped", "superseded"}


def load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return [{column: (row.get(column) or "").strip() for column in COLUMNS} for row in reader]


def header_problems(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path} does not exist (run `kb init`)"]
    with path.open(newline="", encoding="utf-8") as stream:
        header = next(csv.reader(stream), [])
    missing = [c for c in COLUMNS if c not in header]
    extra = [c for c in header if c not in COLUMNS]
    problems = []
    if missing:
        problems.append(f"ingest log is missing columns {missing} (any kb write upgrades it)")
    if extra:
        problems.append(f"ingest log has unknown columns {extra}")
    return problems


def save(path: Path, rows: list[dict[str, str]]) -> None:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in sorted(rows, key=lambda r: r["source"]):
        writer.writerow({column: row.get(column, "") for column in COLUMNS})
    atomic_write(path, buffer.getvalue())


def by_source(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["source"]: row for row in rows}


def split_outputs(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]
