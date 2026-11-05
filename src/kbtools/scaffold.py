"""Install the generic knowledge-base layout into a repository (`kb scaffold`).

The template lives in kbtools/template/. Path parts named `dot-<x>` install as `.<x>`
(kept that way so the template's own .gitignore files don't affect this repository).
Placeholders: {{PROJECT}}, {{DATE}}, {{NOW}}, {{ACTOR}}, {{VERSION}}.
Existing files are never overwritten.
"""

from __future__ import annotations

import os
from importlib import resources
from pathlib import Path

from . import __version__
from .common import now_iso, today

TEXT_SUFFIXES = {".md", ".csv", ".txt", ".json", ".yaml", ".yml"}
EXECUTABLE = {"tools/kb"}

POINTER_SNIPPET = """\
## Knowledge base

Read `docs/index.md` and follow `docs/process/agent-workflow.md` before starting any task.
"""


def template_files() -> list[tuple[str, resources.abc.Traversable]]:
    root = resources.files("kbtools") / "template"
    found = []

    def walk(node, parts):
        for child in node.iterdir():
            if child.name == "__pycache__":
                continue
            if child.is_dir():
                walk(child, parts + [child.name])
            else:
                found.append(("/".join(parts + [child.name]), child))

    walk(root, [])
    return sorted(found)


def install_path(template_path: str) -> str:
    return "/".join("." + p[4:] if p.startswith("dot-") else p for p in template_path.split("/"))


def scaffold(target: Path, *, project: str, actor: str, dry_run: bool = False) -> dict[str, list[str]]:
    project = project.replace('"', "'").strip()  # used inside quoted YAML values
    values = {
        "{{PROJECT}}": project,
        "{{DATE}}": today(),
        "{{NOW}}": now_iso(),
        "{{ACTOR}}": actor,
        "{{VERSION}}": __version__,
    }
    result: dict[str, list[str]] = {"created": [], "skipped": []}
    for template_path, node in template_files():
        relative = install_path(template_path)
        destination = target / relative
        if destination.exists():
            result["skipped"].append(relative)
            continue
        result["created"].append(relative)
        if dry_run:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = node.read_bytes()
        if destination.suffix in TEXT_SUFFIXES or destination.name == ".gitignore":
            text = data.decode("utf-8")
            for key, value in values.items():
                text = text.replace(key, value)
            data = text.encode("utf-8")
        destination.write_bytes(data)
        if relative in EXECUTABLE:
            os.chmod(destination, 0o755)
    if not dry_run and "docs/catalog.md" in result["created"]:
        from .catalog import write
        from .common import Repo

        write(Repo(target))
    return result
