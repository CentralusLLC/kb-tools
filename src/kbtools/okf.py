"""Minimal OKF (Open Knowledge Format) helpers: front matter, page discovery, links."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

RESERVED = {"index.md", "log.md"}
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def parse_front_matter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (front matter or None, body, error)."""
    match = FRONT_MATTER.match(text)
    if not match:
        return None, text, None
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        return None, text[match.end():], f"invalid YAML front matter: {error}".splitlines()[0]
    if not isinstance(data, dict):
        return None, text[match.end():], "front matter is not a mapping"
    return data, text[match.end():], None


def bundle_pages(docs: Path, exclude: tuple[str, ...] = ("sources",)) -> list[Path]:
    """All markdown files of the bundle, skipping excluded top-level directories."""
    pages = []
    for path in sorted(docs.rglob("*.md")):
        relative = path.relative_to(docs)
        if relative.parts and relative.parts[0] in exclude:
            continue
        if any(part.startswith(".") for part in relative.parts):
            continue
        pages.append(path)
    return pages


def is_concept(path: Path) -> bool:
    return path.name not in RESERVED


def is_template(data: dict | None) -> bool:
    return bool(data) and str(data.get("type", "")).strip().lower() == "template"


def verified_entries(data: dict) -> list[dict]:
    value = data.get("verified")
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [entry for entry in value if isinstance(entry, dict)]
    return []


def links(text: str):
    """Yield (is_image, label, target) for markdown links outside fenced code blocks."""
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK.finditer(line):
            yield match.group(1) == "!", match.group(2), match.group(3)
