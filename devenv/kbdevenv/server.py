"""devenv manager: per-project agent dev containers, exposed as MCP tools.

Runs in the isolated `agentdev` account with that account's rootless Docker socket.
For each project it clones the repository, builds the project's dev image from
`.devcontainer/` (or a default image), adds the agent overlay (sshd, node, claude CLI,
`agent` user), and runs it with sshd published on HOST_IP in the configured port range,
for Paperclip's SSH execution environment.

Environment:
  DEVENV_TOKEN      required bearer token (set in the Paperclip connection, not given to agents)
  DEVENV_HOST_IP    address to publish sshd on (default <host-ip>)
  DEVENV_PORTS      port range for dev containers (default <port-range>)
  DEVENV_DATA       state and clones (default /data)
  DEVENV_PUBKEY     path of the public key Paperclip uses (default /data/keys/paperclip.pub)
  GITHUB_TOKEN      optional, for private repositories
  DEVENV_MEMORY / DEVENV_CPUS / DEVENV_PIDS   container limits (default 8g / 6 / 4096)
"""

from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path

DATA = Path(os.environ.get("DEVENV_DATA", "/data"))
HOST_IP = os.environ.get("DEVENV_HOST_IP", "<host-ip>")
PORTS = tuple(int(p) for p in os.environ.get("DEVENV_PORTS", "<port-range>").split("-"))
PUBKEY = Path(os.environ.get("DEVENV_PUBKEY", str(DATA / "keys" / "paperclip.pub")))
LIMITS = (os.environ.get("DEVENV_MEMORY", "8g"), os.environ.get("DEVENV_CPUS", "6"), os.environ.get("DEVENV_PIDS", "4096"))
STATE = DATA / "state.json"
LOGS = DATA / "logs"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
PACKAGE = re.compile(r"^[a-z0-9][a-z0-9+.-]{0,80}$")
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


def _clone(project: str, repo_url: str, ref: str, log: Path) -> Path:
    src = DATA / "src" / project
    if src.exists():
        shutil.rmtree(src)
    src.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git"]
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token and repo_url.startswith("https://github.com/"):
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        cmd += ["-c", f"http.extraHeader=Authorization: Basic {basic}"]
    cmd += ["clone", "--depth", "1"] + (["--branch", ref] if ref else []) + [repo_url, str(src)]
    _run(cmd, log, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    return src


def _build(project: str, entry: dict, log: Path) -> str:
    src = _clone(project, entry["repo_url"], entry.get("ref", ""), log)
    base_tag = f"devenv-{project}-base:latest"
    config_path = src / ".devcontainer" / "devcontainer.json"
    source = "default"
    if config_path.exists():
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
            cmd = ["docker", "build", "-t", base_tag, "-f", str(dockerfile)]
            if build.get("target"):
                cmd += ["--target", build["target"]]
            for key, value in (build.get("args") or {}).items():
                cmd += ["--build-arg", f"{key}={value}"]
            _run(cmd + [str(context)], log)
            source = f"devcontainer build {dockerfile.relative_to(src)}"
    if source == "default":
        default = resources.files("kbdevenv") / "default"
        with resources.as_file(default) as folder:
            _run(["docker", "build", "-t", base_tag, str(folder)], log)
    with tempfile.TemporaryDirectory() as tmp, resources.as_file(resources.files("kbdevenv") / "overlay") as overlay:
        context = Path(tmp)
        for name in ("Dockerfile", "sshd_config", "entrypoint.sh"):
            shutil.copy(overlay / name, context / name)
        shutil.copy(PUBKEY, context / "authorized_keys")
        tag = f"devenv-{project}:latest"
        _run(["docker", "build", "-t", tag, "--build-arg", f"BASE={base_tag}",
              "--build-arg", f"EXTRA_PACKAGES={' '.join(entry.get('extra_packages', []))}", str(context)], log)
    commit = _run(["git", "-C", str(src), "rev-parse", "--short", "HEAD"]).stdout.strip()
    return f"{source} at {commit}"


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


def _provision(project: str, rebuild_only: bool = False) -> None:
    log = LOGS / f"{project}.log"
    LOGS.mkdir(parents=True, exist_ok=True)
    log.write_text(f"{_now()} provisioning {project}\n")
    entry = _load()["projects"][project]
    _update(project, status="building", error="", updated_at=_now())
    try:
        built_from = _build(project, entry, log)
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
        "privateKey": "use the company secret DEVENV_SSH_KEY",
        "knownHosts": entry.get("known_hosts", "(available once running)"),
        "strictHostKeyChecking": True,
    }


# ---------------------------------------------------------------- MCP

def build_server(host: str, port: int):
    from mcp.server.fastmcp import FastMCP
    from mcp.types import ToolAnnotations

    mcp = FastMCP("devenv", host=host, port=port, instructions=(
        "Dev environments for agents: one container per project, built from the project's "
        ".devcontainer/ (or a default image) plus sshd, node and the claude CLI. Create one with "
        "devenv_create, poll devenv_status until running, then give the owner the Paperclip SSH "
        "environment settings it returns (registering environments needs an instance admin). "
        "System packages: devenv_install (approval required). Project dependencies (uv, npm) "
        "need no tool: install them inside the environment."))
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
        return json.dumps({k: {f: v.get(f) for f in ("status", "port", "repo_url", "built_from", "updated_at")}
                           for k, v in state.items()}, indent=2)

    @mcp.tool(annotations=write)
    def devenv_create(project: str, repo_url: str, ref: str = "") -> str:
        """Create a dev environment for a project: clone repo_url (https), build its .devcontainer
        (or the default image) with the agent overlay, and start it. Runs in the background;
        poll devenv_status. Requires approval."""
        name = check_name(project)
        if not repo_url.startswith("https://"):
            return "error: repo_url must be an https URL"
        with _lock:
            state = _load()
            if name in state["projects"]:
                return f"{name} already exists (status {state['projects'][name].get('status')}); use devenv_rebuild"
            state["projects"][name] = {"repo_url": repo_url, "ref": ref, "port": _free_port(state),
                                       "extra_packages": [], "created_at": _now(), "status": "queued"}
            _save(state)
        threading.Thread(target=_provision, args=(name,), daemon=True).start()
        return f"building {name} on port {state['projects'][name]['port']}; poll devenv_status(project=\"{name}\")"

    @mcp.tool(annotations=write)
    def devenv_rebuild(project: str, ref: str = "") -> str:
        """Rebuild a project's dev environment from the repository's current .devcontainer (default
        branch unless ref is given) and recreate the container; the home volume (caches, logins) is kept."""
        name = check_name(project)
        if name not in _load()["projects"]:
            return f"no dev environment for {name}"
        if ref:
            _update(name, ref=ref)
        threading.Thread(target=_provision, args=(name,), daemon=True).start()
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


def main() -> None:
    import argparse

    import uvicorn
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse

    parser = argparse.ArgumentParser(prog="devenv-manager")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8780)
    args = parser.parse_args()
    token = os.environ.get("DEVENV_TOKEN", "").strip()
    if len(token) < 24:
        raise SystemExit("DEVENV_TOKEN (at least 24 characters) is required")
    if not PUBKEY.exists():
        raise SystemExit(f"{PUBKEY} is missing (the public half of Paperclip's DEVENV_SSH_KEY)")

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
