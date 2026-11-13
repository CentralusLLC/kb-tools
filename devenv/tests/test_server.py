"""Unit tests for the devenv manager's pure logic (no Docker needed)."""

import io
import subprocess
import tarfile

import pytest

from kbdevenv import server


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "DATA", tmp_path)
    monkeypatch.setattr(server, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(server, "LOGS", tmp_path / "logs")
    monkeypatch.setattr(server, "PUBKEY", tmp_path / "missing.pub")
    (tmp_path / "logs").mkdir()
    return tmp_path


@pytest.mark.parametrize("key, ok", [
    ("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGf2PmfcIydJTJyyeNL/PIWR8ulqJ3PVr5Lwb0G4h+RK chief@paperclip", True),
    ("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGf2PmfcIydJTJyyeNL/PIWR8ulqJ3PVr5Lwb0G4h+RK", True),
    ("-----BEGIN OPENSSH PRIVATE KEY-----", False),  # kb-scan: allow (test data)
    ("ssh-ed25519 AAAA\ncommand=\"sh\" ssh-ed25519 AAAA", False),
    ('command="sh" ssh-ed25519 AAAA', False),
])
def test_public_key_validation(key, ok):
    assert bool(server.PUBLIC_KEY.match(key)) is ok


def test_public_key_falls_back_to_shared_key(data_dir, monkeypatch):
    with pytest.raises(RuntimeError, match="no public key"):
        server._public_key({})
    shared = data_dir / "shared.pub"
    shared.write_text("ssh-ed25519 AAAA shared\n")
    monkeypatch.setattr(server, "PUBKEY", shared)
    assert server._public_key({}) == "ssh-ed25519 AAAA shared"
    assert server._public_key({"public_key": "ssh-ed25519 BBBB own"}) == "ssh-ed25519 BBBB own"


@pytest.mark.parametrize("given, expected", [
    ("/home/agent/workspace/repo", "/home/agent/workspace/repo"),
    ("workspace/repo", "/home/agent/workspace/repo"),
])
def test_workspace_paths_inside_home(given, expected):
    assert server._find_workspace("p", given) == expected


@pytest.mark.parametrize("given", ["/etc", "/home/agent/../root", "../x", "/home/agentx"])
def test_workspace_paths_outside_home_rejected(given):
    with pytest.raises(RuntimeError, match="inside /home/agent"):
        server._find_workspace("p", given)


def _tar(members: dict[str, bytes], link: tuple[str, str] | None = None) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for name, body in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(body)
            archive.addfile(info, io.BytesIO(body))
        if link:
            info = tarfile.TarInfo(link[0])
            info.type = tarfile.SYMTYPE
            info.linkname = link[1]
            archive.addfile(info)
    return buffer.getvalue()


class FakePopen:
    def __init__(self, payload: bytes):
        self.stdout = io.BytesIO(payload)
        self.returncode = 0

    def communicate(self, timeout=None):
        return b"", b""


def test_export_workspace_copies_files_and_blocks_escaping_links(data_dir, monkeypatch):
    payload = _tar({"./.devcontainer/devcontainer.json": b"{}", "./src/app.py": b"print(1)\n"},
                   link=("./escape", "/etc/passwd"))
    monkeypatch.setattr(server.subprocess, "Popen", lambda *a, **k: FakePopen(payload))
    monkeypatch.setattr(server.subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="abc123\n", stderr=""))
    with pytest.raises(tarfile.TarError):
        server._export_workspace("p", "/home/agent/workspace/repo", data_dir / "logs" / "p.log")

    payload = _tar({"./.devcontainer/devcontainer.json": b"{}", "./src/app.py": b"print(1)\n"})
    monkeypatch.setattr(server.subprocess, "Popen", lambda *a, **k: FakePopen(payload))
    src, origin = server._export_workspace("p", "/home/agent/workspace/repo", data_dir / "logs" / "p.log")
    assert (src / "src" / "app.py").read_text() == "print(1)\n"
    assert origin == "/home/agent/workspace/repo at abc123"


def test_build_rejects_context_outside_repository(data_dir, monkeypatch):
    src = data_dir / "src" / "p"
    (src / ".devcontainer").mkdir(parents=True)
    (src / ".devcontainer" / "devcontainer.json").write_text('{"build": {"dockerfile": "Dockerfile", "context": "../.."}}')
    monkeypatch.setattr(server, "_export_workspace", lambda *a: (src, "repo at abc"))
    monkeypatch.setattr(server, "_run", lambda *a, **k: None)
    with pytest.raises(RuntimeError, match="outside the repository"):
        server._build("p", {"public_key": "ssh-ed25519 AAAA"}, data_dir / "logs" / "p.log", "repo")


def test_build_default_image_writes_project_key(data_dir, monkeypatch):
    commands, keys = [], []

    def fake_run(cmd, *a, **k):
        commands.append(cmd)
        if "--build-arg" in cmd:
            keys.append((server.Path(cmd[-1]) / "authorized_keys").read_text())

    monkeypatch.setattr(server, "_run", fake_run)
    built = server._build("p", {"public_key": "ssh-ed25519 AAAA own"}, data_dir / "logs" / "p.log", None)
    assert built == "default image"
    assert keys == ["ssh-ed25519 AAAA own\n"]
    assert commands[0][:4] == ["docker", "build", "-t", "devenv-p-base:latest"]


# ---------------------------------------------------------------- settings (0010-13)

def _settings_with(env: dict) -> dict:
    """Import the manager in a fresh interpreter with only `env` set, and read its settings."""
    import json
    import os
    import sys
    from pathlib import Path

    clean = {k: v for k, v in os.environ.items() if not k.startswith("DEVENV_")}
    code = ("import json; from kbdevenv import server as s; "
            "print(json.dumps({'host_ip': s.HOST_IP, 'ports': list(s.PORTS), 'data': str(s.DATA), "
            "'limits': list(s.LIMITS), 'swap_wait': s.SWAP_WAIT, 'listen': vars(s.parse_args([]))}))")
    root = str(Path(server.__file__).resolve().parents[1])
    out = subprocess.run([sys.executable, "-c", code], env={**clean, **env, "PYTHONPATH": root},
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def test_settings_defaults_are_neutral():
    got = _settings_with({})
    assert got["host_ip"] == "127.0.0.1" and got["ports"] == [24000, 24099]
    assert got["data"] == "/data" and got["limits"] == ["8g", "6", "4096"] and got["swap_wait"] == 21600
    assert got["listen"] == {"host": "127.0.0.1", "port": 8780}


def test_settings_from_environment():
    got = _settings_with({"DEVENV_HOST_IP": "192.0.2.10", "DEVENV_PORTS": "30000-30009", "DEVENV_DATA": "/srv/devenv",
                          "DEVENV_MEMORY": "4g", "DEVENV_CPUS": "2", "DEVENV_PIDS": "512", "DEVENV_SWAP_WAIT": "60"})
    assert got["host_ip"] == "192.0.2.10" and got["ports"] == [30000, 30009] and got["data"] == "/srv/devenv"
    assert got["limits"] == ["4g", "2", "512"] and got["swap_wait"] == 60


def test_published_ssh_uses_the_configured_host_ip(monkeypatch):
    monkeypatch.setattr(server, "HOST_IP", "192.0.2.10")
    settings = server._paperclip_settings({"project": "demo", "port": 24001})
    assert settings["host"] == "192.0.2.10"


def test_compose_takes_every_deployment_value_from_the_environment():
    import re
    from pathlib import Path

    devenv = Path(server.__file__).resolve().parents[1]
    compose = (devenv / "compose.yaml").read_text()
    assert not re.search(r"\b(?:10|172|192|100)\.\d+\.\d+\.\d+", compose), "no literal IPs in compose.yaml"
    for name in ("DEVENV_TOKEN", "DEVENV_HOST_IP", "DEVENV_MANAGER_PORT", "DEVENV_PORTS"):
        assert "${" + name in compose, name
    example = (devenv / ".env.example").read_text()
    used = set(re.findall(r"\$\{(DEVENV_[A-Z_]+)", compose))
    assert used <= set(re.findall(r"^(DEVENV_[A-Z_]+)=", example, re.M)), "every compose variable is in .env.example"
