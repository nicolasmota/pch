from __future__ import annotations

from pcl_core.schema.audit import EventKind
from pcl_core.service import Hub

from pcl_server.plugins.host import isolation_mode
from pcl_server.plugins.package import load_manifest, manifest_to_snapshot
from pcl_server.plugins.paths import bundled_dir

KIND_TO_PLUGIN = {
    "calendar": "pcl.google-calendar",
    "email": "pcl.gmail",
}


def migrate_connectors(hub: Hub) -> list[str]:
    migrated: list[str] = []
    for connector in list(hub.store.list("connector_account")):
        if connector.get("status") == "disconnected":
            continue
        plugin_id = KIND_TO_PLUGIN.get(str(connector.get("kind") or ""))
        if not plugin_id:
            continue
        existing = [
            p
            for p in hub.list_plugins()
            if p.get("plugin_id") == plugin_id or p.get("source_account_id") == connector["id"]
        ]
        if existing:
            continue
        root = bundled_dir(plugin_id)
        if root is None:
            continue
        manifest = manifest_to_snapshot(load_manifest(root / "plugin.toml"))
        token = hub.get_connector_token(connector["id"])
        inst = hub.create_plugin_installation(
            manifest,
            origin="bundled",
            isolation=isolation_mode(),
            installation_id=None,
            selection=connector.get("selection") or {},
            source_account_id=connector["id"],
        )
        inst["package_dir"] = str(root)
        inst["sync_cursor"] = connector.get("sync_cursor")
        inst["last_run"] = connector.get("last_sync")
        hub.store.put(inst)
        if token:
            hub.set_plugin_secret(inst["id"], "oauth", token)
        # Preserve source_key account segment: google:{connector_id}:...
        inst["source_account_id"] = connector["id"]
        hub.store.put(inst)
        if connector.get("status") == "active":
            hub.consent_plugin(inst["id"])
        elif connector.get("status") == "paused":
            hub.consent_plugin(inst["id"])
            hub.set_plugin_state(inst["id"], "paused", "migrated from paused connector")
        connector["status"] = "disconnected"
        connector["migrated_to"] = inst["id"]
        hub.store.put(connector)
        hub.ledger.append(
            EventKind.PLUGIN_LIFECYCLE,
            "owner",
            f"migrated connector {connector['id']} to {plugin_id}",
            [connector["id"], inst["id"]],
        )
        migrated.append(inst["id"])
    hub.engine.conn.commit()
    return migrated
