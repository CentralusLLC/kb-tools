"""The tools/kb wrapper (bin/kb): Docker first, then a local install it can create."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

WRAPPER = Path(__file__).resolve().parents[1] / "bin" / "kb"


def stub(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(0o755)
    return path


@pytest.fixture
def env(tmp_path: Path) -> dict:
    """A git repository with a docs/ subdir, fake tools on PATH and an empty KB_TOOLS_HOME."""
    project = tmp_path / "project"
    (project / "docs").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    fakes = tmp_path / "fakes"
    fakes.mkdir()
    environ = {k: v for k, v in os.environ.items() if not k.startswith("KB_TOOLS_")}
    environ["PATH"] = f"{fakes}:{environ['PATH']}"
    environ["KB_TOOLS_HOME"] = str(tmp_path / "kbhome")
    return {"project": project, "fakes": fakes, "log": tmp_path / "calls.log", "env": environ, "tmp": tmp_path}


def run(env: dict, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["sh", str(WRAPPER), *args], cwd=cwd or env["project"] / "docs", env=env["env"], capture_output=True, text=True
    )


def fake_docker(env: dict, has_image: bool) -> None:
    inspect = "exit 0" if has_image else "exit 1"
    stub(env["fakes"] / "docker", f'[ "$1" = image ] && {inspect}\necho "docker $*" >> {env["log"]}\n')


def fake_local_install(env: dict) -> None:
    stub(Path(env["env"]["KB_TOOLS_HOME"]) / "bin" / "kb", f'echo "local $* in $(pwd)" >> {env["log"]}\n')


def test_uses_docker_when_it_has_the_image(env):
    fake_docker(env, has_image=True)
    fake_local_install(env)
    result = run(env, "check")
    assert result.returncode == 0, result.stderr
    call = env["log"].read_text()
    assert call.startswith("docker run") and "--network none" in call and call.rstrip().endswith("kb-tools:latest check")
    assert "-w /work/docs" in call


def test_falls_back_to_the_local_install_without_the_image(env):
    fake_docker(env, has_image=False)
    fake_local_install(env)
    result = run(env, "check", "--strict")
    assert result.returncode == 0, result.stderr
    assert env["log"].read_text().strip() == f"local check --strict in {env['project'] / 'docs'}"


def test_explains_both_options_when_nothing_is_installed(env):
    fake_docker(env, has_image=False)
    result = run(env, "check")
    assert result.returncode == 1
    assert "docker build" in result.stderr and "tools/kb --install" in result.stderr
    assert env["env"]["KB_TOOLS_HOME"] in result.stderr


def fake_python(env: dict) -> None:
    # python3 -m venv --clear DIR -> DIR/bin/pip (records its args) and DIR/bin/kb.
    stub(
        env["fakes"] / "python3",
        f'echo "python3 $*" >> {env["log"]}\n'
        'dir="$4"; mkdir -p "$dir/bin"\n'
        f'printf \'#!/bin/sh\\necho "pip $*" >> {env["log"]}\\n\' > "$dir/bin/pip"\n'
        f'printf \'#!/bin/sh\\necho "kb $*" >> {env["log"]}\\n\' > "$dir/bin/kb"\n'
        'chmod +x "$dir/bin/pip" "$dir/bin/kb"\n',
    )


@pytest.mark.parametrize(("args", "ref_env", "ref"), [((), None, "main"), (("v0.2.0",), None, "v0.2.0"), ((), "dev", "dev")])
def test_install_creates_a_light_venv_at_the_ref(env, args, ref_env, ref):
    fake_python(env)
    env["env"]["KB_TOOLS_SOURCE"] = "git+https://example.invalid/kb-tools"
    if ref_env:
        env["env"]["KB_TOOLS_REF"] = ref_env
    result = run(env, "--install", *args)
    assert result.returncode == 0, result.stderr
    home = env["env"]["KB_TOOLS_HOME"]
    calls = env["log"].read_text().splitlines()
    assert calls[0] == f"python3 -m venv --clear {home}"
    # Light by default (board, CEN-12, 2026-11-12): no [extract] libraries in project containers.
    assert calls[1].startswith("pip install") and calls[1].endswith(f" git+https://example.invalid/kb-tools@{ref}")
    assert "[extract]" not in calls[1] and "--no-deps" not in calls[1]
    assert calls[2] == "kb --version"


@pytest.mark.parametrize("how", ["flag", "env"])
def test_full_install_adds_the_extract_extra(env, how):
    fake_python(env)
    env["env"]["KB_TOOLS_SOURCE"] = "git+https://example.invalid/kb-tools"
    if how == "env":
        env["env"]["KB_TOOLS_EXTRAS"] = "extract"
        result = run(env, "--install", "dev")
    else:
        result = run(env, "--install", "--full", "dev")
    assert result.returncode == 0, result.stderr
    pip = env["log"].read_text().splitlines()[1]
    assert pip.endswith("kb-tools[extract] @ git+https://example.invalid/kb-tools@dev")


def test_install_reads_the_source_and_ref_from_the_project_conf(env):
    fake_python(env)
    tools = env["project"] / "tools"
    tools.mkdir()
    (tools / "kb.conf").write_text("# comment\nsource=git+https://example.invalid/upstream/kb-tools\nref=v0.2.0\n")
    result = run(env, "--install")
    assert result.returncode == 0, result.stderr
    assert env["log"].read_text().splitlines()[1].endswith(" git+https://example.invalid/upstream/kb-tools@v0.2.0")
    conf = (Path(env["env"]["KB_TOOLS_HOME"]) / "install.conf").read_text()
    assert "source=git+https://example.invalid/upstream/kb-tools\n" in conf and "ref=v0.2.0\n" in conf
    env["env"]["KB_TOOLS_SOURCE"] = "git+https://example.invalid/fork/kb-tools"  # the environment wins
    assert run(env, "--install", "dev").returncode == 0
    assert env["log"].read_text().splitlines()[-2].endswith(" git+https://example.invalid/fork/kb-tools@dev")


@pytest.mark.parametrize("conf", [None, "source=git+https://github.com/<owner>/kb-tools\n"])
def test_install_without_a_source_explains_where_to_set_it(env, conf):
    if conf:
        (env["project"] / "tools").mkdir()
        (env["project"] / "tools" / "kb.conf").write_text(conf)
    result = run(env, "--install")
    assert result.returncode == 2
    assert "tools/kb.conf" in result.stderr and "KB_TOOLS_SOURCE" in result.stderr


def test_install_reuses_the_recorded_source(env):
    fake_python(env)
    env["env"]["KB_TOOLS_SOURCE"] = "git+https://example.invalid/fork/kb-tools"
    assert run(env, "--install", "dev").returncode == 0
    del env["env"]["KB_TOOLS_SOURCE"]
    env["log"].unlink()
    result = run(env, "--install", "dev")
    assert result.returncode == 0, result.stderr
    assert env["log"].read_text().splitlines()[1].endswith(" git+https://example.invalid/fork/kb-tools@dev")


def test_default_home_is_the_password_database_home_not_HOME(env):
    import pwd

    del env["env"]["KB_TOOLS_HOME"]
    env["env"]["HOME"] = str(env["tmp"] / "per-run-home")
    fake_docker(env, has_image=False)
    result = run(env, "check")
    assert result.returncode == 1
    assert f"{pwd.getpwuid(os.getuid()).pw_dir}/.kb-tools" in result.stderr
