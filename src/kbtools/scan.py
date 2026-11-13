"""Scan a repository's tracked files for secrets and deployment-specific values.

`kb check` runs this so a public repository does not pick up secrets, private addresses or
internal names again. The built-in rules are generic. Values that are specific to one
organisation (host names, people, project names) must not be written into the repository
that is being protected, so they come from a deny list outside it: the file named by
`KB_SCAN_DENYLIST`, one case-insensitive regular expression per line, `#` for comments.

Findings report the file, line and rule, never the matched text, so check output can be
shared. A line containing `kb-scan: allow` is skipped (for deliberate test data).
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .common import Repo

ALLOW_MARKER = "kb-scan: allow"
DENYLIST_ENV = "KB_SCAN_DENYLIST"
MAX_BYTES = 1024 * 1024
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
# Untracked runtime folders that hold deployment values by design and are never committed:
# Paperclip writes its per-run MCP config into .paperclip-runtime/ in every agent workspace.
RUNTIME_DIRS = {".paperclip-runtime"}


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    error: bool

    @property
    def advice(self) -> str:
        if self.name.startswith("deny-list"):
            return f"matches {DENYLIST_ENV}; use a placeholder or a setting"
        if self.error:
            return "remove it and rotate it; secrets belong in a secret store"
        return "use a placeholder or a setting"


def _rule(name: str, pattern: str, error: bool, flags: int = 0) -> Rule:
    return Rule(name, re.compile(pattern, flags), error)


# Secrets are errors; addresses that are usually deployment-specific are warnings, because a
# project may document an example network on purpose.
BUILTIN_RULES = (
    _rule("private key", r"-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----", True),
    _rule("GitHub token", r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b", True),
    _rule("AWS access key id", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", True),
    _rule("Slack token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b", True),
    _rule("API key (sk-...)", r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,}\b", True),
    _rule("private IPv4 address",
          r"(?<![\d.])(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}(?![\d.])", False),
    _rule("carrier-grade NAT / tailnet IPv4 address",
          r"(?<![\d.])100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}(?![\d.])", False),
    _rule("tailnet host name", r"\b[a-z0-9-]+\.[a-z0-9-]+\.ts\.net\b", False, re.IGNORECASE),
)


def load_denylist(path: Path) -> tuple[list[Rule], list[str]]:
    """Read deny-list rules; return them and any problems (without echoing the patterns)."""
    rules: list[Rule] = []
    problems: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return rules, [f"{DENYLIST_ENV}: cannot read the deny list ({exc.strerror or exc})"]
    for number, line in enumerate(lines, 1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        try:
            rules.append(Rule(f"deny-list entry {number}", re.compile(text, re.IGNORECASE), True))
        except re.error as exc:
            problems.append(f"{DENYLIST_ENV}: line {number} is not a valid regular expression ({exc})")
    return rules, problems


def tracked_files(repo: Repo) -> list[Path]:
    """Files git tracks plus untracked, not ignored ones (so a value is caught before it is
    committed); untracked files in runtime folders such as .paperclip-runtime/ are skipped, but
    a tracked file there is still scanned. A directory walk outside git."""
    def ls_files(*args: str) -> set[str]:
        result = subprocess.run(["git", "-C", str(repo.root), "ls-files", "-z", *args],
                                capture_output=True, check=True)
        return {n for n in result.stdout.decode("utf-8", "replace").split("\0") if n}

    try:
        tracked = ls_files("--cached")
        untracked = {n for n in ls_files("--others", "--exclude-standard")
                     if n.split("/", 1)[0] not in RUNTIME_DIRS}
        return [repo.root / n for n in sorted(tracked | untracked) if (repo.root / n).is_file()]
    except (OSError, subprocess.CalledProcessError):
        pass
    found = []
    for directory, subdirs, files in os.walk(repo.root):
        subdirs[:] = sorted(d for d in subdirs if d not in SKIP_DIRS | RUNTIME_DIRS)
        here = Path(directory)
        if here == repo.sources or repo.sources in here.parents:
            continue
        found += [here / f for f in sorted(files)]
    return found


def _text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def scan(repo: Repo, denylist: Path | None = None) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) naming file, line and rule for each finding."""
    errors: list[str] = []
    warnings: list[str] = []
    rules = list(BUILTIN_RULES)
    if denylist is None and os.environ.get(DENYLIST_ENV):
        denylist = Path(os.environ[DENYLIST_ENV]).expanduser()
    if denylist is not None:
        extra, problems = load_denylist(denylist)
        rules += extra
        errors += problems
    skip = denylist.resolve() if denylist is not None else None
    for path in tracked_files(repo):
        if skip is not None and path.resolve() == skip:
            continue
        text = _text(path)
        if text is None:
            continue
        relative = path.relative_to(repo.root).as_posix()
        for number, line in enumerate(text.splitlines(), 1):
            if ALLOW_MARKER in line:
                continue
            for rule in rules:
                if rule.pattern.search(line):
                    (errors if rule.error else warnings).append(f"{relative}:{number}: {rule.name} ({rule.advice})")
    return errors, warnings
