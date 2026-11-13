"""Deployment settings (0010-13): MCP server settings and repo lookup, tool errors,
--version, the light install and sources that are not present locally."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from kbtools import server, version
from kbtools.check import run_checks
from kbtools.cli import build_parser
from kbtools.common import Repo, sha256
from kbtools.intake import inventory, update_row
from kbtools.scaffold import scaffold

SRC = str(Path(server.__file__).resolve().parents[1])


@pytest.fixture
def cli_path(monkeypatch):
    """The MCP tools run the CLI in a subprocess; make it import this source tree."""
    monkeypatch.setenv("PYTHONPATH", SRC + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else ""))


@pytest.fixture
def repos(tmp_path):
    """A repos root with `gameworld` at the top level and `acme/shop` one level down."""
    root = tmp_path / "repos"
    for name in ("gameworld", "acme/shop"):
        scaffold(root / name, project=name, actor="t")
        (root / name / ".git").mkdir()
    (root / "not-a-repo").mkdir()
    server.configure(root, [])
    yield root
    server.configure(Path(server.DEFAULT_REPOS_ROOT), [])


# ---------------------------------------------------------------- settings

def test_server_settings_defaults_are_neutral():
    config = server.settings({})
    assert config.host == "127.0.0.1" and config.port == 8765
    assert config.repos_root == Path("/repos") and config.allowed_roots == []


def test_server_settings_from_environment():
    config = server.settings({"KB_MCP_HOST": "0.0.0.0", "KB_MCP_PORT": "9000", "KB_REPOS_ROOT": "/srv/checkouts",
                              "KB_ALLOWED_ROOTS": f"/a{os.pathsep}/b"})
    assert (config.host, config.port, config.repos_root) == ("0.0.0.0", 9000, Path("/srv/checkouts"))
    assert config.allowed_roots == [Path("/a"), Path("/b")]
    with pytest.raises(SystemExit, match="KB_MCP_PORT"):
        server.settings({"KB_MCP_PORT": "http"})


def test_serve_flags_override_environment(monkeypatch):
    seen = {}
    monkeypatch.setattr(server, "serve", lambda **kwargs: seen.update(kwargs))
    monkeypatch.setenv("KB_MCP_HOST", "10.0.0.1")
    monkeypatch.setenv("KB_MCP_PORT", "9001")
    monkeypatch.setenv("KB_REPOS_ROOT", "/checkouts")
    args = build_parser().parse_args(["serve"])
    args.func(args)
    assert seen == {"host": "10.0.0.1", "port": 9001, "repos_root": Path("/checkouts"), "allowed_roots": []}
    args = build_parser().parse_args(["serve", "--host", "127.0.0.2", "--port", "8000", "--allowed-root", "/x"])
    args.func(args)
    assert (seen["host"], seen["port"], seen["allowed_roots"]) == ("127.0.0.2", 8000, [Path("/x")])


# ---------------------------------------------------------------- repo lookup

def test_repo_names_resolve_under_the_repos_root(repos):
    assert server.resolve_repo("gameworld") == (repos / "gameworld").resolve()
    assert server.resolve_repo("someowner/gameworld") == (repos / "gameworld").resolve()
    assert server.resolve_repo("acme/shop") == (repos / "acme/shop").resolve()
    assert server.resolve_repo("shop") == (repos / "acme/shop").resolve()
    assert server.resolve_repo("shop.git") == (repos / "acme/shop").resolve()
    assert server.resolve_repo(str(repos / "gameworld")) == (repos / "gameworld").resolve()
    assert server.visible_repos() == ["acme/shop", "gameworld"]


@pytest.mark.parametrize("bad", ["missing", "../outside", "", "acme/../../etc"])
def test_unknown_repos_explain_what_the_server_can_see(repos, bad):
    with pytest.raises(server.KbToolError) as raised:
        server.resolve_repo(bad)
    message = str(raised.value)
    assert f"KB_REPOS_ROOT is {repos.resolve()}" in message and "acme/shop, gameworld" in message


def test_absolute_paths_must_be_under_a_root(repos, tmp_path):
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    with pytest.raises(server.KbToolError, match="outside the kb-tools server's roots"):
        server.resolve_repo(str(outside))
    server.configure(repos, [tmp_path / "elsewhere"])
    assert server.resolve_repo(str(outside)) == outside.resolve()


def test_instructions_name_the_roots_and_who_the_tools_are_for(repos):
    text = server.instructions()
    assert str(repos.resolve()) in text and "tools/kb" in text and "Paperclip machine" in text
    assert "same path you see in your workspace" not in text


def _call(tool: str, arguments: dict):
    from mcp.shared.memory import create_connected_server_and_client_session

    async def go():
        async with create_connected_server_and_client_session(server.build_server()._mcp_server) as client:
            return await client.call_tool(tool, arguments)

    result = asyncio.run(go())
    return result.isError, "".join(getattr(block, "text", "") for block in result.content)


def test_mcp_tools_take_repo_names_and_report_errors_as_tool_errors(repos, cli_path):
    is_error, text = _call("kb_work_list", {"repo": "gameworld"})
    assert not is_error and text.startswith("exit 0")

    is_error, text = _call("kb_work_list", {"repo": "nowhere"})
    assert is_error and "no repository 'nowhere'" in text and "gameworld" in text

    (repos / "gameworld" / "docs" / "broken.md").write_text("no front matter\n")
    is_error, text = _call("kb_check", {"repo": "gameworld"})
    assert is_error and "exit 1" in text and "broken.md" in text


# ---------------------------------------------------------------- version

def test_version_label_from_ref_and_commit():
    assert version._label("dev", "3061f26abcdef") == "+dev.3061f26"
    assert version._label("0010-13/settings", "abc1234ffff") == "+0010-13-settings.abc1234"
    assert version._label("", "abc1234ffff") == "+abc1234"
    assert version._label("", "") == ""


def test_version_reads_pip_install_record(monkeypatch):
    class Dist:
        def read_text(self, name):
            assert name == "direct_url.json"
            return json.dumps({"url": "https://example.invalid/kb-tools",
                               "vcs_info": {"vcs": "git", "requested_revision": "dev", "commit_id": "3061f26" + "0" * 33}})

    monkeypatch.setattr(version.metadata, "distribution", lambda name: Dist())
    assert version._from_install_record() == ("dev", "3061f26" + "0" * 33)


def test_cli_version_includes_ref_and_commit(capsys, monkeypatch):
    monkeypatch.setattr("kbtools.cli.full_version", lambda: "0.1.0+dev.3061f26")
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--version"])
    assert capsys.readouterr().out.strip() == "kb-tools 0.1.0+dev.3061f26"


# ---------------------------------------------------------------- light install

BLOCK_EXTRACT = """
import sys
from importlib.abc import MetaPathFinder
class Block(MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name.split('.')[0] in {'markitdown', 'pptx', 'openpyxl', 'pypdfium2', 'PIL'}:
            raise ModuleNotFoundError(name)
        return None
sys.meta_path.insert(0, Block())
from kbtools.cli import main
sys.exit(main(sys.argv[1:]))
"""


def _light(repo: Path, *args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": SRC}
    return subprocess.run([sys.executable, "-c", BLOCK_EXTRACT, "--repo", str(repo), *args],
                          capture_output=True, text=True, cwd=repo, env=env)


def test_light_commands_run_without_the_extraction_libraries(tmp_path):
    scaffold(tmp_path, project="Shop", actor="t")
    (tmp_path / ".git").mkdir()
    (tmp_path / "docs" / "sources" / "brief.txt").write_text("hello")
    for args in (["inventory", "--by", "t"], ["log", "brief.txt", "--status", "skipped", "--by", "t"],
                 ["work", "new-epic", "Reporting", "--by", "t"], ["work", "list"], ["catalog", "--write"],
                 ["catalog"], ["report"], ["check"]):
        result = _light(tmp_path, *args)
        assert result.returncode == 0, (args, result.stdout, result.stderr)


@pytest.mark.parametrize("args", [["extract", "--pending"], ["figure", "x.png", "--out", "docs/x.png"]])
def test_heavy_commands_explain_the_light_install(tmp_path, args):
    scaffold(tmp_path, project="Shop", actor="t")
    result = _light(tmp_path, *args)
    assert result.returncode == 2
    assert "MCP server" in result.stderr and "tools/kb --install --full" in result.stderr


# ---------------------------------------------------------------- sources not present locally

def test_check_is_clean_when_an_ingested_original_is_not_present(repo):
    """Originals never go into git, so a project container has an empty docs/sources/."""
    original = repo.sources / "orig.pdf"
    original.write_bytes(b"%PDF original")
    inventory(repo, added_by="t")
    (repo.docs / "page.md").write_text("---\ntype: Guide\ntitle: Page\ndescription: d\n---\n\n# Page\n")
    update_row(repo, "orig.pdf", status="ingested", by="t", outputs=["docs/page.md"])
    assert run_checks(repo) == ([], [])

    original.unlink()  # a fresh clone elsewhere
    assert run_checks(repo) == ([], [])

    original.write_bytes(b"%PDF edited")  # present but different still warns
    assert sha256(original) != ""
    errors, warnings = run_checks(repo)
    assert errors == [] and any("hash mismatch" in w for w in warnings)


def test_check_still_reports_missing_outputs_when_the_original_is_absent(repo):
    (repo.sources / "orig.pdf").write_bytes(b"%PDF")
    inventory(repo, added_by="t")
    update_row(repo, "orig.pdf", status="ingested", by="t", outputs=["docs/gone.md"])
    (repo.sources / "orig.pdf").unlink()
    errors, _ = run_checks(Repo(repo.root))
    assert any("output docs/gone.md does not exist" in e for e in errors)


# ---------------------------------------------------------------- kb-tools source for projects

def test_scaffold_records_where_to_install_kb_tools_from(tmp_path, monkeypatch):
    monkeypatch.setattr("kbtools.scaffold.install_source", lambda: "git+https://example.invalid/fork/kb-tools")
    scaffold(tmp_path, project="Shop", actor="t")
    conf = (tmp_path / "tools" / "kb.conf").read_text()
    assert "source=git+https://example.invalid/fork/kb-tools\n" in conf and "ref=main\n" in conf


def test_install_source_prefers_the_git_install_record(monkeypatch):
    def record(data):
        class Dist:
            def read_text(self, name):
                return json.dumps(data)
        monkeypatch.setattr(version.metadata, "distribution", lambda name: Dist())

    record({"url": "https://example.invalid/fork/kb-tools", "vcs_info": {"vcs": "git", "commit_id": "abc"}})
    assert version.install_source() == "git+https://example.invalid/fork/kb-tools"
    record({"url": "https://user:token@example.invalid/kb-tools", "vcs_info": {"vcs": "git", "commit_id": "abc"}})
    assert version.install_source() == version.UPSTREAM_SOURCE  # never copy credentials into a project
    record({"url": "file:///opt/kb-tools", "dir_info": {}})
    assert version.install_source() == version.UPSTREAM_SOURCE
