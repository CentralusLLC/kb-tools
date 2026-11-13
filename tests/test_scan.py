"""The secret and internal-reference scan that `kb check` runs (0010-11)."""

from __future__ import annotations

import shutil
import subprocess

import pytest

from kbtools.check import run_checks
from kbtools.common import Repo
from kbtools.scan import DENYLIST_ENV, scan

# Built at run time so this file does not itself contain anything the scan flags.
FAKE_SECRETS = {
    "private key": "-----BEGIN " + "RSA PRIVATE KEY-----",
    "GitHub token": "gh" + "p_" + "a1B2" * 9,
    "AWS access key id": "AK" + "IA" + "ABCDEFGHIJKLMNOP",
    "Slack token": "xo" + "xb-" + "1234567890-abcdef",
    "API key (sk-...)": "s" + "k-ant-" + "x" * 40,
}


@pytest.fixture(autouse=True)
def _no_denylist(monkeypatch):
    monkeypatch.delenv(DENYLIST_ENV, raising=False)


@pytest.mark.parametrize("rule, value", FAKE_SECRETS.items())
def test_secrets_are_errors_without_echoing_the_value(repo, rule, value):
    (repo.root / "config.py").write_text(f"x = 1\nTOKEN = '{value}'\n")
    errors, _ = scan(repo)
    assert errors == [f"config.py:2: {rule} (remove it and rotate it; secrets belong in a secret store)"]
    assert value not in errors[0]


@pytest.mark.parametrize("text, flagged", [
    ("host 10.1" + ".2.3", True),
    ("host 172.20" + ".0.5:8080", True),
    ("host 192.168" + ".1.10", True),
    ("tailnet 100.101" + ".102.103", True),
    ("url https://box.example" + ".ts.net:8443/", True),
    ("doc address 192.0.2.1 and 127.0.0.1", False),
    ("version 1.10.2.3.4 and 0.0.0.0", False),
    ("public 8.8.8.8 or 100.200.1.1", False),
])
def test_deployment_addresses_are_warnings(repo, text, flagged):
    (repo.docs / "net.md").write_text(text + "\n")
    errors, warnings = scan(repo)
    assert errors == []
    assert bool([w for w in warnings if w.startswith("docs/net.md:1:")]) is flagged


def test_allow_marker_skips_a_line(repo):
    value = FAKE_SECRETS["private key"]
    (repo.root / "t.py").write_text(f"KEY = '{value}'  # kb-scan: allow (test data)\n")
    assert scan(repo) == ([], [])


def test_denylist_from_the_environment(repo, tmp_path, monkeypatch):
    deny = tmp_path / "outside" / "deny.txt"
    deny.parent.mkdir()
    deny.write_text("# internal names\n\nsecret-host\n\\bprojectx\\b\n")
    monkeypatch.setenv(DENYLIST_ENV, str(deny))
    (repo.docs / "page.md").write_text("Deployed on Secret-Host.\nProjectX notes\nprojectxy is fine\n")
    errors, _ = scan(repo)
    assert [e.split(" (")[0] for e in errors] == ["docs/page.md:1: deny-list entry 3",
                                                 "docs/page.md:2: deny-list entry 4"]
    assert not any("secret-host" in e.lower() or "projectx" in e.lower() for e in errors)


def test_denylist_problems_are_reported(repo, tmp_path, monkeypatch):
    deny = tmp_path / "deny.txt"
    deny.write_text("ok\n(unclosed\n")
    monkeypatch.setenv(DENYLIST_ENV, str(deny))
    errors, _ = scan(repo)
    assert any("line 2 is not a valid regular expression" in e for e in errors)
    assert "(unclosed" not in " ".join(errors)
    monkeypatch.setenv(DENYLIST_ENV, str(tmp_path / "missing.txt"))
    errors, _ = scan(repo)
    assert any("cannot read the deny list" in e for e in errors)


def test_outside_git_sources_and_virtualenvs_are_skipped(repo):
    value = FAKE_SECRETS["GitHub token"]
    (repo.sources / "original.txt").write_text(value)
    (repo.root / ".venv" / "lib").mkdir(parents=True)
    (repo.root / ".venv" / "lib" / "x.py").write_text(value)
    (repo.root / "image.bin").write_bytes(b"\0\1" + value.encode())
    assert scan(repo)[0] == []


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_in_git_ignored_files_are_skipped(repo):
    subprocess.run(["git", "init", "-q", str(repo.root)], check=True)
    value = FAKE_SECRETS["GitHub token"]
    (repo.root / ".gitignore").write_text(".env\n")
    (repo.root / ".env").write_text(f"TOKEN={value}\n")
    (repo.root / "app.cfg").write_text(f"TOKEN={value}\n")
    errors, _ = scan(repo)
    assert [e.split(":")[0] for e in errors] == ["app.cfg"]


def test_kb_check_runs_the_scan(repo):
    (repo.docs / "setup.md").write_text("---\ntype: Guide\n---\n# Setup\n\nManager at 10.9" + ".8.7:9000.\n")
    _, warnings = run_checks(Repo(repo.root))
    assert "docs/setup.md:6: private IPv4 address (use a placeholder or a setting)" in warnings


def test_untracked_files_are_scanned_but_not_paperclip_runtime(tmp_path):
    """Untracked, not ignored files are scanned (caught before a commit); Paperclip's per-run
    .paperclip-runtime/ folder is not (gameworld feedback 18)."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n# Test\n')
    address = "10.1" + ".2.3"
    (tmp_path / "notes.md").write_text(f"host {address}\n")
    runtime = tmp_path / ".paperclip-runtime" / "mcp"
    runtime.mkdir(parents=True)
    (runtime / "config.json").write_text(f'{{"url": "http://{address}:9000"}}\n')
    _, warnings = scan(Repo(tmp_path))
    assert [w.split(":")[0] for w in warnings] == ["notes.md"]


def test_tracked_file_in_paperclip_runtime_is_still_scanned(tmp_path):
    """Only untracked files in .paperclip-runtime/ are skipped: a file committed there by
    mistake is still flagged."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n# Test\n')
    address = "10.1" + ".2.3"
    runtime = tmp_path / ".paperclip-runtime" / "mcp"
    runtime.mkdir(parents=True)
    (runtime / "committed.json").write_text(f'{{"url": "http://{address}:9000"}}\n')
    (runtime / "local.json").write_text(f'{{"url": "http://{address}:9000"}}\n')
    subprocess.run(["git", "-C", str(tmp_path), "add", "-f", ".paperclip-runtime/mcp/committed.json"],
                   check=True)
    _, warnings = scan(Repo(tmp_path))
    assert [w.split(":")[0] for w in warnings] == [".paperclip-runtime/mcp/committed.json"]
