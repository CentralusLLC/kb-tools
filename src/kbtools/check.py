"""Consistency checks for a knowledge-base repository. Errors fail; warnings inform."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from . import ingest_log, okf
from .common import Repo, sha256

ELEMENT_DESCRIPTION = re.compile(r"^\s*(\||[-*] |\d+\. )")


def _check_log(repo: Repo, errors: list[str], warnings: list[str]) -> None:
    for problem in ingest_log.header_problems(repo.log_path):
        warnings.append(problem)
    rows = ingest_log.load(repo.log_path)
    seen = set()
    for row in rows:
        name = row["source"]
        where = f"ingest-log {name!r}"
        if not name:
            errors.append("ingest-log has a row without a source")
            continue
        if name in seen:
            errors.append(f"{where}: duplicate row")
        seen.add(name)
        if row["status"] not in ingest_log.STATUSES:
            errors.append(f"{where}: unknown status {row['status']!r}")
        path = repo.sources / name
        if path.is_file():
            if row["sha256"] and sha256(path) != row["sha256"]:
                warnings.append(f"{where}: file changed since it was logged (hash mismatch); re-ingest or log a new version")
        if row["status"] in {"ingested", "partial"}:
            if not row["outputs"]:
                warnings.append(f"{where}: {row['status']} but no outputs recorded")
            if not row["ingested_at"]:
                warnings.append(f"{where}: {row['status']} but no ingested_at")
        for output in ingest_log.split_outputs(row["outputs"]):
            if not (repo.root / output).exists():
                errors.append(f"{where}: output {output} does not exist")
    for path in repo.sources.rglob("*") if repo.sources.exists() else []:
        relative = path.relative_to(repo.sources).as_posix()
        if path.is_file() and relative not in seen and path.name not in {"index.md", "ingest-log.csv", ".gitignore", ".DS_Store", ".gitkeep"} \
                and not any(p.startswith(".") for p in Path(relative).parts):
            warnings.append(f"source {relative} is not in the ingest log (run `kb inventory`)")


def _check_page(repo: Repo, path: Path, errors: list[str], warnings: list[str]) -> None:
    relative = repo.rel(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    data, body, error = okf.parse_front_matter(text)
    if okf.is_concept(path):
        if error:
            errors.append(f"{relative}: {error}")
        elif data is None:
            errors.append(f"{relative}: missing front matter (OKF requires `type`)")
        elif not str(data.get("type", "")).strip():
            errors.append(f"{relative}: front matter has no `type`")
        else:
            for entry in okf.verified_entries(data):
                if not entry.get("by") or not entry.get("at"):
                    errors.append(f"{relative}: each `verified` entry needs `by` and `at`")
    elif data is not None and not (path.name == "index.md" and path.parent == repo.docs):
        warnings.append(f"{relative}: reserved file should not have front matter")
    if okf.is_template(data):
        return
    for is_image, label, target in okf.links(body):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        target_path = unquote(target.split("#", 1)[0])
        if not target_path:
            continue
        resolved = (repo.root / target_path.lstrip("/")) if target_path.startswith("/") else (path.parent / target_path)
        if target_path.startswith("/"):
            resolved = repo.docs / target_path.lstrip("/")
        if not resolved.exists():
            (errors if is_image else warnings).append(f"{relative}: broken {'image' if is_image else 'link'} {target}")
        if is_image and not label.strip():
            warnings.append(f"{relative}: image {target} has no alt text")
    lines = body.splitlines()
    in_mermaid = False
    for number, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```mermaid"):
            in_mermaid = True
            continue
        if in_mermaid and stripped.startswith("```"):
            in_mermaid = False
            following = []
            for later in lines[number + 1:]:
                if later.startswith("#"):
                    break
                following.append(later)
            if not any(ELEMENT_DESCRIPTION.match(x) for x in following):
                warnings.append(f"{relative}: Mermaid diagram (line ~{number + 1}) has no element list or table after it")


def run_checks(repo: Repo) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if repo.sources.exists() or repo.log_path.exists():
        _check_log(repo, errors, warnings)
    if not (repo.docs / "index.md").exists():
        warnings.append("docs/index.md is missing")
    for page in okf.bundle_pages(repo.docs):
        _check_page(repo, page, errors, warnings)
    return errors, warnings
