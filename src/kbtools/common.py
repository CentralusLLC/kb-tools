"""Shared helpers: repository layout, hashing, slugs, atomic writes, time."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

SOURCES_DIR = Path("docs/sources")
EXTRACTED_DIR = Path("extracted")
DOCS_DIR = Path("docs")
LOG_NAME = "ingest-log.csv"
# Files in docs/sources that belong to the intake machinery, not sources.
SOURCE_HOUSEKEEPING = {"index.md", LOG_NAME, ".gitignore", ".DS_Store", ".gitkeep"}


@dataclass(frozen=True)
class Repo:
    root: Path

    @property
    def docs(self) -> Path:
        return self.root / DOCS_DIR

    @property
    def sources(self) -> Path:
        return self.root / SOURCES_DIR

    @property
    def extracted(self) -> Path:
        return self.root / EXTRACTED_DIR

    @property
    def log_path(self) -> Path:
        return self.sources / LOG_NAME

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root.resolve()).as_posix()


def find_repo(start: Path | None = None) -> Repo:
    """Walk up from `start` to the directory holding docs/ (plus .git or docs/index.md)."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / DOCS_DIR).is_dir() and (
            (candidate / ".git").exists() or (candidate / DOCS_DIR / "index.md").exists()
        ):
            return Repo(candidate)
    raise SystemExit(f"kb: no knowledge-base repository (docs/ plus .git or docs/index.md) at or above {here}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(text: str) -> str:
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "source"


def source_slug(relative_source: str) -> str:
    """Stable extraction-package name for a path relative to docs/sources (extension kept)."""
    return slugify(relative_source.replace("/", "--"))


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def today() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_datetime(value) -> datetime | None:
    """Parse OKF/YAML timestamps (datetime, date, or ISO string) into aware UTC datetimes."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
