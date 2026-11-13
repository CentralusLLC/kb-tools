"""The installed kb-tools version, with the git ref and commit it was built from.

`kb --version` prints `kb-tools 0.1.0+<ref>.<sha>` so installs from different branches or
commits can be told apart. The ref and commit come from pip's install record
(`direct_url.json`, PEP 610) for `pip install git+...@<ref>` installs, or from git when
running from a source checkout. Image builds without either show the bare version.
"""

from __future__ import annotations

import json
import re
import subprocess
from importlib import metadata
from pathlib import Path

from . import __version__

# Where `tools/kb --install` gets kb-tools from when nothing else says: the public
# repository. Scaffolded projects record it in tools/kb.conf, where a fork can change it.
UPSTREAM_SOURCE = "git+https://github.com/CentralusLLC/kb-tools"


def _label(ref: str, sha: str) -> str:
    ref = re.sub(r"[^A-Za-z0-9.]+", "-", ref).strip("-.")
    parts = [p for p in (ref, sha[:7]) if p]
    return "+" + ".".join(parts) if parts else ""


def _from_install_record() -> tuple[str, str] | None:
    try:
        raw = metadata.distribution("kb-tools").read_text("direct_url.json")
    except metadata.PackageNotFoundError:
        return None
    if not raw:
        return None
    try:
        vcs = json.loads(raw).get("vcs_info") or {}
    except ValueError:
        return None
    if not vcs.get("commit_id"):
        return None
    return vcs.get("requested_revision", ""), vcs["commit_id"]


def install_source() -> str:
    """The pip source this kb-tools was installed from (`git+<url>`), or the public repository."""
    try:
        raw = metadata.distribution("kb-tools").read_text("direct_url.json")
        data = json.loads(raw) if raw else {}
    except (metadata.PackageNotFoundError, ValueError):
        data = {}
    url = data.get("url", "")
    if (data.get("vcs_info") or {}).get("vcs") == "git" and url and "@" not in url.split("://", 1)[-1]:
        return "git+" + url
    return UPSTREAM_SOURCE


def _from_git(source: Path) -> tuple[str, str] | None:
    def git(*args: str) -> str:
        run = subprocess.run(["git", "-C", str(source), *args], capture_output=True, text=True, timeout=5)
        return run.stdout.strip() if run.returncode == 0 else ""

    try:
        if not git("rev-parse", "--show-toplevel"):
            return None
        sha = git("rev-parse", "HEAD")
        ref = git("rev-parse", "--abbrev-ref", "HEAD")
    except (OSError, subprocess.SubprocessError):
        return None
    return ("" if ref == "HEAD" else ref), sha


def full_version() -> str:
    """`0.1.0+<ref>.<sha>` when the ref or commit is known, otherwise `0.1.0`."""
    here = Path(__file__).resolve().parent
    found = None
    if "site-packages" in here.parts or "dist-packages" in here.parts:
        found = _from_install_record()
    else:
        found = _from_git(here)
    return __version__ + (_label(*found) if found else "")
