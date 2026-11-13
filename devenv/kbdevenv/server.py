"""devenv manager: per-project agent dev containers, exposed as MCP tools.

Runs in the isolated `agentdev` account with that account's rootless Docker socket.
The manager never clones repositories and holds no GitHub credential: Paperclip's SSH
environment syncs the project worktree into the container on every run. So:

  devenv_create   starts a project from the default image plus the agent overlay (sshd, node,
                  claude CLI, `agent` user), authorising the public key the agent supplies
                  (its private half is stored in Paperclip through an approved secret proposal).
  devenv_rebuild  builds the project's `.devcontainer/` from the worktree already synced into
                  the container, adds the overlay, and recreates the container (home kept).

sshd is published on HOST_IP in the configured port range.

Environment:
  DEVENV_TOKEN      required bearer token (set in the Paperclip connection, not given to agents)
  DEVENV_HOST_IP    address to publish sshd on (default 127.0.0.1; set the address the
                    Paperclip server reaches this host on)
  DEVENV_PORTS      port range for dev containers (default 24000-24099)
  DEVENV_DATA       state, logs and build contexts (default /data)
  DEVENV_PUBKEY     fallback public key for projects created without one
                    (default /data/keys/paperclip.pub; optional)
  DEVENV_MEMORY / DEVENV_CPUS / DEVENV_PIDS   container limits (default 8g / 6 / 4096)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import threading
import time
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path

DEFAULT_HOST_IP = "127.0.0.1"
DEFAULT_PORTS = "24000-24099"
DATA = Path(os.environ.get("DEVENV_DATA", "/data"))
HOST_IP = os.environ.get("DEVENV_HOST_IP", "").strip() or DEFAULT_HOST_IP
PORTS = tuple(int(p) for p in (os.environ.get("DEVENV_PORTS", "").strip() or DEFAULT_PORTS).split("-"))
PUBKEY = Path(os.environ.get("DEVENV_PUBKEY", str(DATA / "keys" / "paperclip.pub")))
LIMITS = (os.environ.get("DEVENV_MEMORY", "8g"), os.environ.get("DEVENV_CPUS", "6"), os.environ.get("DEVENV_PIDS", "4096"))
STATE = DATA / "state.json"
LOGS = DATA / "logs"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
PACKAGE = re.compile(r"^[a-z0-9][a-z0-9+.-]{0,80}$")
PUBLIC_KEY = re.compile(r"^(ssh-ed25519|ecdsa-sha2-nistp(256|384|521)|ssh-rsa) [A-Za-z0-9+/]+={0,3}( [^\r\n]{0,200})?$")
HOME = "/home/agent"
# Never copied into a build context: caches and dependency trees the agent creates.
CONTEXT_EXCLUDES = (".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache",
                    ".mypy_cache", ".ruff_cache", ".dart_tool")
SWAP_WAIT = int(os.environ.get("DEVENV_SWAP_WAIT", str(6 * 3600)))  # seconds to wait for agent sessions to end
_lock = threading.RLock()


# ---------------------------------------------------------------- state

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load() -> dict:
    with _lock:
        return json.loads(STATE.read_text()) if STATE.exists() else {"projects": {}}


def _save(state: dict) -> None:
    with _lock:
        DATA.mkdir(parents=True, exist_ok=True)
        tmp = STATE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(STATE)


def _update(project: str, **fields) -> dict:
    with _lock:
        state = _load()
        entry = state["projects"].setdefault(project, {})
        entry.update(fields)
        _save(state)
        return entry


def _run(cmd: list[str], log: Path | None = None, timeout: int = 3600, **kw) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)
    if log:
        with log.open("a") as stream:
            stream.write(f"\n$ {' '.join(cmd)}\n{result.stdout}{result.stderr}")
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:3])} failed: {(result.stderr or result.stdout).strip()[-800:]}")
    return result


def _free_port(state: dict) -> int:
    used = {p.get("port") for p in state["projects"].values()}
    for port in range(PORTS[0], PORTS[1] + 1):
        if port not in used:
            return port
    raise RuntimeError("no free dev-container ports left")


# ---------------------------------------------------------------- build

def _strip_jsonc(text: str) -> str:
    text = re.sub(r"(?m)^\s*//.*$", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r",(\s*[}\]])", r"\1", text)


def _public_key(entry: dict) -> str:
    key = entry.get("public_key", "")
    if not key and PUBKEY.exists():
        key = PUBKEY.read_text().strip()
    if not key:
        raise RuntimeError("no public key for this project; recreate it with devenv_create(public_key=...)")
    return key


def _find_workspace(project: str, workspace: str) -> str:
    """The synced worktree inside the container: the given path, or the single directory under
    the home's workspace that holds .devcontainer/devcontainer.json."""
    container = f"devenv-{project}"
    if workspace:
        path = os.path.normpath(workspace if workspace.startswith("/") else f"{HOME}/{workspace}")
        if path != HOME and not path.startswith(HOME + "/"):
            raise RuntimeError(f"workspace must be inside {HOME}")
        return path
    found = subprocess.run(["docker", "exec", "-u", "agent", container, "find", f"{HOME}/workspace",
                            "-maxdepth", "5", "-path", "*/.devcontainer/devcontainer.json",
                            "-not", "-path", "*/node_modules/*"], capture_output=True, text=True)
    paths = sorted({os.path.dirname(os.path.dirname(p)) for p in found.stdout.split()})
    if len(paths) == 1:
        return paths[0]
    if not paths:
        raise RuntimeError("no .devcontainer/devcontainer.json in the synced workspace; run an agent in "
                           "this environment first, or pass workspace=<the repository root>")
    raise RuntimeError(f"several workspaces found {paths}; pass workspace=<the repository root>")


def _export_workspace(project: str, workspace: str, log: Path) -> tuple[Path, str]:
    """Copy the synced worktree out of the container into a fresh build context.
    Extraction uses tarfile's data filter, so links cannot escape the context."""
    container = f"devenv-{project}"
    path = _find_workspace(project, workspace)
    src = DATA / "src" / project
    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True)
    excludes = [f"--exclude=./{name}" if name == ".git" else f"--exclude={name}" for name in CONTEXT_EXCLUDES]
    proc = subprocess.Popen(["docker", "exec", "-u", "agent", container, "tar", "-C", path, *excludes, "-cf", "-", "."],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with tarfile.open(fileobj=proc.stdout, mode="r|") as archive:
        archive.extractall(src, filter="data")
    _, stderr = proc.communicate(timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(f"copying {path} out of {container} failed: {stderr.decode()[-800:]}")
    commit = subprocess.run(["docker", "exec", "-u", "agent", container, "git", "-C", path, "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    with log.open("a") as stream:
        stream.write(f"\nbuild context: {container}:{path} at {commit or 'unknown commit'}\n")
    return src, f"{path} at {commit or 'unknown commit'}"


def _build(project: str, entry: dict, log: Path, workspace: str | None) -> str:
    """Build devenv-<project>:latest. workspace None means the default image (first start);
    otherwise the project's .devcontainer from the synced worktree."""
    src, origin = (None, "") if workspace is None else _export_workspace(project, workspace, log)
    base_tag = f"devenv-{project}-base:latest"
    source = "default image"
    config_path = src / ".devcontainer" / "devcontainer.json" if src else None
    if config_path and config_path.exists():
        config = json.loads(_strip_jsonc(config_path.read_text()))
        if config.get("image"):
            _run(["docker", "pull", config["image"]], log)
            _run(["docker", "tag", config["image"], base_tag], log)
            source = f"devcontainer image {config['image']}"
        elif config.get("build") or config.get("dockerFile"):
            build = config.get("build") or {"dockerfile": config["dockerFile"]}
            folder = config_path.parent
            dockerfile = (folder / build.get("dockerfile", "Dockerfile")).resolve()
            context = (folder / build.get("context", ".")).resolve()
            for target in (dockerfile, context):
                if target != src and src not in target.parents:
                    raise RuntimeError(f"{target} is outside the repository")
            cmd = ["docker", "build", "-t", base_tag, "-f", str(dockerfile)]
            if build.get("target"):
                cmd += ["--target", build["target"]]
            for key, value in (build.get("args") or {}).items():
                cmd += ["--build-arg", f"{key}={value}"]
            _run(cmd + [str(context)], log)
            source = f"devcontainer build {dockerfile.relative_to(src)}"
    if source == "default image":
        default = resources.files("kbdevenv") / "default"
        with resources.as_file(default) as folder:
            _run(["docker", "build", "-t", base_tag, str(folder)], log)
    with tempfile.TemporaryDirectory() as tmp, resources.as_file(resources.files("kbdevenv") / "overlay") as overlay:
        context = Path(tmp)
        for name in ("Dockerfile", "sshd_config", "entrypoint.sh"):
            shutil.copy(overlay / name, context / name)
        (context / "authorized_keys").write_text(_public_key(entry) + "\n")
        tag = f"devenv-{project}:latest"
        _run(["docker", "build", "-t", tag, "--build-arg", f"BASE={base_tag}",
              "--build-arg", f"EXTRA_PACKAGES={' '.join(entry.get('extra_packages', []))}", str(context)], log)
    return f"{source} from {origin}" if origin else source


def _start(project: str, entry: dict, log: Path) -> None:
    name = f"devenv-{project}"
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    memory, cpus, pids = LIMITS
    _run(["docker", "run", "-d", "--name", name, "--restart", "unless-stopped",
          "--hostname", name, "-p", f"{HOST_IP}:{entry['port']}:22",
          "-v", f"{name}-home:/home/agent", "-v", f"{name}-hostkeys:/etc/devenv/hostkeys",
          "--memory", memory, "--cpus", cpus, "--pids-limit", pids,
          "--label", "devenv.project=" + project, f"devenv-{project}:latest"], log)
    for _ in range(30):
        result = subprocess.run(["docker", "exec", name, "cat", "/etc/devenv/hostkeys/ssh_host_ed25519_key.pub"],
                                capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            key = " ".join(result.stdout.split()[:2])
            _update(project, known_hosts=f"[{HOST_IP}]:{entry['port']} {key}")
            return
        time.sleep(1)
    raise RuntimeError("sshd host key did not appear")


def _agent_busy(project: str) -> bool:
    """True while any process runs as `agent` in the container (an SSH session or agent run)."""
    result = subprocess.run(["docker", "exec", f"devenv-{project}", "pgrep", "-u", "agent"], capture_output=True)
    return result.returncode == 0


def _wait_idle(project: str, log: Path) -> None:
    """Recreating the container ends every session in it, including the agent that asked for the
    rebuild, so wait until no agent process is left (bounded by SWAP_WAIT)."""
    deadline = time.monotonic() + SWAP_WAIT
    if _agent_busy(project):
        _update(project, status="waiting for agent sessions to end")
        with log.open("a") as stream:
            stream.write(f"{_now()} image built; waiting for agent sessions to end before swapping\n")
    while _agent_busy(project):
        if time.monotonic() > deadline:
            raise RuntimeError("agent sessions did not end; image built but container not swapped, "
                               "run devenv_rebuild again when the environment is idle")
        time.sleep(15)


def _provision(project: str, workspace: str | None = None) -> None:
    log = LOGS / f"{project}.log"
    LOGS.mkdir(parents=True, exist_ok=True)
    log.write_text(f"{_now()} provisioning {project}\n")
    entry = _load()["projects"][project]
    _update(project, status="building", error="", updated_at=_now())
    try:
        built_from = _build(project, entry, log, workspace)
        _wait_idle(project, log)
        _update(project, status="starting", built_from=built_from)
        _start(project, _load()["projects"][project], log)
        _update(project, status="running", updated_at=_now())
    except Exception as error:  # report failures through status, never crash the server
        _update(project, status="failed", error=str(error)[-1500:], updated_at=_now())


def _paperclip_settings(entry: dict) -> dict:
    return {
        "driver": "ssh",
        "host": HOST_IP,
        "port": entry.get("port"),
        "username": "agent",
        "remoteWorkspacePath": "/home/agent/workspace",
        "remoteCwd": "/home/agent/workspace",
        "privateKey": entry.get("private_key_secret") or "the company secret holding this project's private key",
        "knownHosts": entry.get("known_hosts", "(available once running)"),
        "strictHostKeyChecking": True,
    }


# ---------------------------------------------------------------- MCP

def build_server(host: str, port: int):
    from mcp.server.fastmcp import FastMCP
    from mcp.types import ToolAnnotations

    mcp = FastMCP("devenv", host=host, port=port, instructions=(
        "Dev environments for agents: one container per project with sshd, node and the claude CLI, "
        "used through a Paperclip SSH environment (Paperclip syncs the worktree in on every run). "
        "Setup: generate an ed25519 key pair, submit the private key as a Paperclip secret proposal, "
        "call devenv_create with the public key and the secret's name, poll devenv_status, then give "
        "the owner the SSH environment settings it returns. After the first run has synced the "
        "repository, devenv_rebuild builds the project's .devcontainer. System packages: prefer a "
        "pull request to .devcontainer, then devenv_rebuild; devenv_install for urgent needs. "
        "Project dependencies (uv, pip, npm) need no tool: install them inside the environment. "
        "Never print or log private keys."))
    read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    write = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True)
    destructive = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False)

    def check_name(project: str) -> str:
        project = project.strip().lower()
        if not NAME.match(project):
            raise ValueError("project must be lowercase letters, digits and hyphens (max 41)")
        return project

    @mcp.tool(annotations=read)
    def devenv_status(project: str = "") -> str:
        """Status of one project's dev environment (or all): build state, port, error, and the
        Paperclip SSH environment settings once running. Tail of the build log on failure."""
        state = _load()["projects"]
        if project:
            name = check_name(project)
            if name not in state:
                return f"no dev environment for {name}"
            entry = state[name]
            out = {**entry, "paperclip_environment": _paperclip_settings(entry)}
            log = LOGS / f"{name}.log"
            if entry.get("status") == "failed" and log.exists():
                out["log_tail"] = log.read_text()[-3000:]
            return json.dumps(out, indent=2)
        return json.dumps({k: {f: v.get(f) for f in ("status", "port", "built_from", "updated_at")}
                           for k, v in state.items()}, indent=2)

    @mcp.tool(annotations=write)
    def devenv_create(project: str, public_key: str, private_key_secret: str = "") -> str:
        """Create a dev environment for a project from the default image plus the agent overlay,
        authorising public_key (an OpenSSH public key line) for the `agent` user. private_key_secret
        is the name of the Paperclip secret holding the private half (recorded for the settings).
        Runs in the background; poll devenv_status. After the first agent run has synced the
        repository, call devenv_rebuild to switch to the project's .devcontainer. Requires approval."""
        name = check_name(project)
        public_key = " ".join(public_key.split())
        if not PUBLIC_KEY.match(public_key):
            return "error: public_key must be one OpenSSH public key line (ssh-ed25519 ... recommended)"
        with _lock:
            state = _load()
            if name in state["projects"]:
                return f"{name} already exists (status {state['projects'][name].get('status')}); use devenv_rebuild"
            state["projects"][name] = {"public_key": public_key, "private_key_secret": private_key_secret.strip(),
                                       "port": _free_port(state), "extra_packages": [],
                                       "created_at": _now(), "status": "queued"}
            _save(state)
        threading.Thread(target=_provision, args=(name, None), daemon=True).start()
        return f"building {name} on port {state['projects'][name]['port']}; poll devenv_status(project=\"{name}\")"

    @mcp.tool(annotations=write)
    def devenv_rebuild(project: str, workspace: str = "", default_image: bool = False) -> str:
        """Rebuild a project's dev environment from the .devcontainer in the worktree Paperclip has
        synced into it (workspace: the repository root inside the container, found automatically
        when there is only one). The files are used as they are now, uncommitted changes included.
        The container is recreated only once no agent session is running in it (so a run that
        asks for a rebuild finishes first); the home volume is kept. default_image=True rebuilds
        from the default image instead (recovery from a broken .devcontainer). Requires approval."""
        name = check_name(project)
        if name not in _load()["projects"]:
            return f"no dev environment for {name}"
        target = None if default_image else workspace.strip()
        if target is not None:
            try:
                _find_workspace(name, target)  # fail fast with a useful message
            except Exception as error:
                return f"error: {error}"
        threading.Thread(target=_provision, args=(name, target), daemon=True).start()
        return f"rebuilding {name}; poll devenv_status(project=\"{name}\")"

    @mcp.tool(annotations=write)
    def devenv_install(project: str, packages: list[str], reason: str) -> str:
        """Install Debian system packages into a running dev environment (requires approval).
        They are also added to every future rebuild. Also propose them in the repository's
        .devcontainer so the environment stays reproducible. Project dependencies (uv, pip,
        npm) do not need this tool."""
        name = check_name(project)
        entry = _load()["projects"].get(name)
        if not entry:
            return f"no dev environment for {name}"
        bad = [p for p in packages if not PACKAGE.match(p)]
        if bad or not packages:
            return f"error: invalid package names {bad or packages}"
        log = LOGS / f"{name}.log"
        try:
            _run(["docker", "exec", "-u", "root", f"devenv-{name}", "sh", "-c",
                  "apt-get update -q && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "
                  + " ".join(packages)], log, timeout=1800)
        except Exception as error:
            return f"error: {error}"
        extra = sorted(set(entry.get("extra_packages", [])) | set(packages))
        history = entry.get("install_history", []) + [{"at": _now(), "packages": packages, "reason": reason}]
        _update(name, extra_packages=extra, install_history=history)
        return (f"installed {', '.join(packages)} in {name}. Persisted for rebuilds. Add them to the project's "
                ".devcontainer (in a pull request) so people get them too.")

    @mcp.tool(annotations=write)
    def devenv_stop(project: str) -> str:
        """Stop a project's dev environment container (keeps image and volumes)."""
        name = check_name(project)
        subprocess.run(["docker", "stop", f"devenv-{name}"], capture_output=True)
        _update(name, status="stopped", updated_at=_now())
        return f"stopped {name}"

    @mcp.tool(annotations=destructive)
    def devenv_delete(project: str, delete_home: bool = False) -> str:
        """Delete a project's dev environment: container and images; with delete_home also its
        home volume (caches, agent logins). Destructive; for archived projects."""
        name = check_name(project)
        for cmd in (["docker", "rm", "-f", f"devenv-{name}"],
                    ["docker", "rmi", f"devenv-{name}:latest", f"devenv-{name}-base:latest"]):
            subprocess.run(cmd, capture_output=True)
        subprocess.run(["docker", "volume", "rm", f"devenv-{name}-hostkeys"], capture_output=True)
        if delete_home:
            subprocess.run(["docker", "volume", "rm", f"devenv-{name}-home"], capture_output=True)
        with _lock:
            state = _load()
            state["projects"].pop(name, None)
            _save(state)
        return f"deleted {name}" + (" and its home volume" if delete_home else "")

    return mcp


def parse_args(argv: list[str] | None = None):
    """Where the manager listens inside its container. The address and port published on
    the host come from DEVENV_HOST_IP and DEVENV_MANAGER_PORT in compose.yaml."""
    import argparse

    parser = argparse.ArgumentParser(prog="devenv-manager")
    parser.add_argument("--host", default="127.0.0.1", help="listen address (the image passes 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8780)
    return parser.parse_args(argv)


def main() -> None:
    import uvicorn
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse

    args = parse_args()
    token = os.environ.get("DEVENV_TOKEN", "").strip()
    if len(token) < 24:
        raise SystemExit("DEVENV_TOKEN (at least 24 characters) is required")

    class BearerAuth(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            if request.url.path == "/health":
                return JSONResponse({"status": "ok"})
            if request.headers.get("authorization", "") != f"Bearer {token}":
                return JSONResponse({"error": "unauthorized"}, status_code=401)
            return await call_next(request)

    app = build_server(args.host, args.port).streamable_http_app()
    app.add_middleware(BearerAuth)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
