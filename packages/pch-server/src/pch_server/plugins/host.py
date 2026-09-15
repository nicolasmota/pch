from __future__ import annotations

import os
import select
import subprocess
import sys
import time
from pathlib import Path

from pch_core.errors import Busy, ConsentRequired, ValidationFailed
from pch_core.schema.audit import EventKind
from pch_core.service import Hub
from pch_core.timeutil import now_iso

from pch_server.plugins.enforcement import RunGuard
from pch_server.plugins.protocol import API_VERSION, ProtocolError, decode_line, dispatch, encode
from pch_server.plugins.sandbox import isolation_mode, sandbox_available, wrap_plugin_command

DEFAULT_TIMEOUT = 600
_running: dict[str, bool] = {}

__all__ = [
    "isolation_mode",
    "plugin_child_env",
    "run_plugin_sync",
    "sandbox_available",
    "wrap_plugin_command",
]


def _refresh_oauth_if_present(hub: Hub, installation_id: str) -> None:
    raw = hub.get_plugin_secret(installation_id, "oauth")
    if not raw:
        return
    from pch_server.sync.oauth import refresh_access_token

    # refresh_access_token reads connector_token; mirror into that key for the call
    hub.set_connector_token(installation_id, raw)
    try:
        refresh_access_token(hub, installation_id)
        updated = hub.get_connector_token(installation_id)
        if updated:
            hub.set_plugin_secret(installation_id, "oauth", updated)
    except Exception:
        pass


def run_plugin_sync(hub: Hub, installation_id: str, *, reason: str = "manual", timeout: int = DEFAULT_TIMEOUT) -> dict:
    if _running.get(installation_id):
        raise Busy("sync in progress")
    _running[installation_id] = True
    try:
        inst = hub.get_plugin(installation_id)
        if inst.get("state") != "enabled":
            raise ConsentRequired("plugin is not enabled")
        if int((inst.get("manifest") or {}).get("api_version") or 1) != API_VERSION:
            hub.set_plugin_state(installation_id, "needs_update", "api_version unsupported")
            raise ValidationFailed("api_version unsupported")
        root = Path(inst.get("package_dir") or "")
        if not root.is_dir():
            raise ValidationFailed("plugin package missing")
        guard = RunGuard(hub, inst)
        _refresh_oauth_if_present(hub, installation_id)
        proc = _spawn(root, inst)
        try:
            _write(proc, {"jsonrpc": "2.0", "id": 0, "method": "plugin.run", "params": {
                "run_id": installation_id,
                "reason": reason,
                "api_version": API_VERSION,
                "account_id": inst.get("source_account_id") or installation_id,
                "selection": inst.get("selection") or {},
            }})
            deadline = time.time() + timeout
            summary = {"created": 0, "updated": 0, "tombstoned": 0}
            while time.time() < deadline:
                line = _readline(proc, deadline)
                if line is None:
                    if time.time() >= deadline:
                        proc.kill()
                        raise ValidationFailed("plugin run timed out")
                    if proc.poll() is not None:
                        err = ""
                        if proc.stderr is not None:
                            err = proc.stderr.read() or ""
                        raise ValidationFailed(f"plugin exited without plugin.done: {err[-800:]}")
                    continue
                message = decode_line(line)
                method = message.get("method")
                if method == "plugin.done":
                    reported = (message.get("params") or {}).get("summary") or {}
                    summary = {
                        "created": guard.created or int(reported.get("created") or 0),
                        "updated": guard.updated or int(reported.get("updated") or 0),
                        "tombstoned": guard.tombstoned or int(reported.get("tombstoned") or 0),
                    }
                    break
                if method and str(method).startswith("hub."):
                    try:
                        result = dispatch(hub, guard, str(method), message.get("params") or {})
                        _write(proc, {"jsonrpc": "2.0", "id": message.get("id"), "result": result})
                    except ProtocolError as exc:
                        _write(proc, {
                            "jsonrpc": "2.0",
                            "id": message.get("id"),
                            "error": {"code": exc.code, "message": exc.message},
                        })
                        if exc.code == -32001 and guard.denials >= 3:
                            raise ValidationFailed(exc.message) from exc
            else:
                proc.kill()
                raise ValidationFailed("plugin run timed out")
            last_run = {
                "at": now_iso(),
                "outcome": "ok",
                "created": summary["created"],
                "updated": summary["updated"],
                "tombstoned": summary["tombstoned"],
            }
            inst = hub.get_plugin(installation_id)
            inst["last_run"] = last_run
            hub.store.put(inst)
            hub.engine.conn.commit()
            return last_run
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=5)
    except Exception as exc:
        try:
            inst = hub.get_plugin(installation_id)
            inst["last_run"] = {
                "at": now_iso(),
                "outcome": "error",
                "created": 0,
                "updated": 0,
                "tombstoned": 0,
                "error": str(exc),
            }
            hub.store.put(inst)
            hub.ledger.append(
                EventKind.PLUGIN_SYNC,
                f"plugin:{installation_id}",
                f"sync failed: {exc}",
                [installation_id],
                extra=inst["last_run"],
            )
            hub.engine.conn.commit()
        except Exception:
            pass
        raise
    finally:
        _running.pop(installation_id, None)


def plugin_child_env(root: Path, inst: dict) -> dict[str, str]:
    env = dict(os.environ)
    env["PCH_PLUGIN_SRC"] = str(root / "src")
    env["PCH_PLUGIN_ENTRY"] = str((inst.get("manifest") or {}).get("entry") or "sync:main")
    return env


def _spawn(root: Path, inst: dict) -> subprocess.Popen:
    env = plugin_child_env(root, inst)
    cmd = [sys.executable, "-c", "from pch_sdk.plugin_runtime import serve; serve()"]
    cmd, env = wrap_plugin_command(
        cmd,
        root=root,
        isolation=str(inst.get("isolation") or "reduced"),
        env=env,
    )
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1,
    )


def _write(proc: subprocess.Popen, message: dict) -> None:
    assert proc.stdin is not None
    proc.stdin.write(encode(message).decode())
    proc.stdin.flush()


def _readline(proc: subprocess.Popen, deadline: float) -> str | None:
    assert proc.stdout is not None
    remaining = deadline - time.time()
    if remaining <= 0:
        return None
    ready, _, _ = select.select([proc.stdout], [], [], remaining)
    if not ready:
        return None
    line = proc.stdout.readline()
    if not line:
        return None
    return line.strip()
