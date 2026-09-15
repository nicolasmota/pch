from __future__ import annotations

from pathlib import Path

from pch_core.service import Hub
from pch_server.plugins.host import isolation_mode


def write_plugin(root: Path, plugin_id: str, sync_src: str, hosts: list[str], produces: list[dict]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "src").mkdir(exist_ok=True)
    hosts_toml = ", ".join(f'"{h}"' for h in hosts)
    produce_blocks = "\n".join(
        f'[[permissions.produces]]\ntype = "{p["type"]}"\n'
        + (f'kind = "{p["kind"]}"\n' if p.get("kind") else "")
        + f'classification = "{p.get("classification", "personal")}"\n'
        for p in produces
    )
    (root / "plugin.toml").write_text(
        f"""[plugin]
id = "{plugin_id}"
name = "{plugin_id}"
description = "test"
version = "0.1.0"
publisher = "test"
api_version = 1
entry = "sync:main"

[permissions]
secrets = true
schedule = "manual"
hosts = [{hosts_toml}]

{produce_blocks}
""",
        encoding="utf-8",
    )
    (root / "src" / "sync.py").write_text(sync_src, encoding="utf-8")
    return root


def install_and_enable(hub: Hub, root: Path, plugin_id: str) -> dict:
    from pch_server.plugins.package import load_manifest, manifest_to_snapshot

    snap = manifest_to_snapshot(load_manifest(root / "plugin.toml"))
    inst = hub.create_plugin_installation(snap, origin="sideload", isolation=isolation_mode())
    inst["package_dir"] = str(root)
    hub.store.put(inst)
    hub.consent_plugin(inst["id"])
    return hub.get_plugin(inst["id"])
