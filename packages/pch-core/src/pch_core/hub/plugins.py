from __future__ import annotations

import json

from pch_core.errors import NotFound, ValidationFailed
from pch_core.hub.const import OWNER
from pch_core.ids import new_id
from pch_core.schema.audit import EventKind
from pch_core.timeutil import now_iso


class PluginsMixin:
    def _plugin_secret_key(self, installation_id: str, name: str) -> str:
        return f"plugin_secret:{installation_id}:{name}"

    def _plugin_state_key(self, installation_id: str, name: str) -> str:
        return f"plugin_state:{installation_id}:{name}"

    def set_plugin_secret(self, installation_id: str, name: str, value: str) -> None:
        self._kv_set(self._plugin_secret_key(installation_id, name), value)

    def get_plugin_secret(self, installation_id: str, name: str) -> str | None:
        return self._kv_get(self._plugin_secret_key(installation_id, name))

    def delete_plugin_secrets(self, installation_id: str) -> None:
        prefix = f"plugin_secret:{installation_id}:"
        for key in list(self.kv_keys()):
            if key.startswith(prefix) or key.startswith(f"plugin_state:{installation_id}:"):
                self.engine.conn.execute("DELETE FROM kv WHERE k = ?", (key,))
        self.engine.conn.commit()

    def set_plugin_state_value(self, installation_id: str, name: str, value: str) -> None:
        self._kv_set(self._plugin_state_key(installation_id, name), value)

    def get_plugin_state_value(self, installation_id: str, name: str) -> str | None:
        return self._kv_get(self._plugin_state_key(installation_id, name))

    def list_plugins(self) -> list[dict]:
        return [p for p in self.store.list("plugin") if p.get("state") != "removed"]

    def get_plugin(self, installation_id: str) -> dict:
        payload = self.store.get(installation_id)
        if payload.get("type") != "plugin":
            raise NotFound(installation_id)
        return payload

    def create_plugin_installation(
        self,
        manifest: dict,
        *,
        origin: str = "bundled",
        package_sha256: str = "",
        isolation: str = "reduced",
        installation_id: str | None = None,
        selection: dict | None = None,
        source_account_id: str | None = None,
    ) -> dict:
        body = {
            "plugin_id": manifest["id"],
            "plugin_version": manifest["version"],
            "manifest": manifest,
            "origin": origin,
            "package_sha256": package_sha256,
            "state": "installed",
            "state_reason": "",
            "grant_id": None,
            "isolation": isolation,
            "last_run": None,
            "selection": selection or {},
            "sync_cursor": None,
            "source_account_id": source_account_id,
            "classification": "private",
        }
        if installation_id:
            body["id"] = installation_id
        stored = self.create("plugin", body)
        self.ledger.append(
            EventKind.PLUGIN_INSTALL,
            OWNER,
            f"installed {manifest['id']}",
            [stored["id"]],
            extra={"origin": origin, "version": manifest["version"]},
        )
        return stored

    def consent_plugin(self, installation_id: str, *, schedule: str | None = None) -> dict:
        inst = self.get_plugin(installation_id)
        if inst.get("state") in {"removed"}:
            raise ValidationFailed("plugin is removed")
        manifest = inst["manifest"]
        permissions = manifest.get("permissions") or {}
        grant = self.create_grant(
            f"plugin:{installation_id}",
            None,
            [],
            {
                "produces": json.dumps(permissions.get("produces") or []),
                "hosts": ",".join(permissions.get("hosts") or []),
                "schedule": schedule or permissions.get("schedule") or "manual",
                "approved_manifest_version": manifest.get("version", ""),
            },
            "sensitive",
        )
        inst["grant_id"] = grant["id"]
        inst["state"] = "enabled"
        inst["state_reason"] = ""
        if schedule:
            inst.setdefault("manifest", {}).setdefault("permissions", {})["schedule"] = schedule
        stored = self.store.put(inst)
        self.ledger.append(
            EventKind.PLUGIN_CONSENT,
            OWNER,
            f"consented {inst.get('plugin_id')}",
            [installation_id, grant["id"]],
        )
        self.engine.conn.commit()
        return stored

    def set_plugin_state(self, installation_id: str, state: str, reason: str = "") -> dict:
        inst = self.get_plugin(installation_id)
        inst["state"] = state
        inst["state_reason"] = reason
        stored = self.store.put(inst)
        self.ledger.append(
            EventKind.PLUGIN_LIFECYCLE,
            OWNER,
            f"plugin {state}",
            [installation_id],
            extra={"reason": reason},
        )
        self.engine.conn.commit()
        return stored

    def apply_plugin_items(
        self,
        installation_id: str,
        items: list[dict],
        deleted_keys: list[str] | None = None,
    ) -> dict:
        created = updated = tombstoned = 0
        with self.engine.tx():
            for item in items:
                item.setdefault("id", new_id(str(item.get("type") or "artifact")))
                item.setdefault("space_id", "personal")
                item.setdefault("owner", self.person_id())
                item.setdefault("labels", [])
                item.setdefault("created_at", now_iso())
                item.setdefault("updated_at", now_iso())
                item.setdefault("confidence", 1.0)
                item.setdefault("retention", {"mode": "until_revoked"})
                item.setdefault("policy_tags", [])
                item.setdefault("version", 1)
                item.setdefault("source_refs", [])
                if f"plugin:{installation_id}" not in item["source_refs"]:
                    item["source_refs"] = [*item["source_refs"], f"plugin:{installation_id}"]
                item.setdefault("authority", "source_imported")
                _, action = self._upsert_by_source_key(item)
                if action == "created":
                    created += 1
                else:
                    updated += 1
            for key in deleted_keys or []:
                existing = self.store.get_by_source_key(key)
                if existing and f"plugin:{installation_id}" in (existing.get("source_refs") or []):
                    self.store.tombstone(existing["id"])
                    tombstoned += 1
            inst = self.store.get(installation_id)
            last_run = {
                "at": now_iso(),
                "outcome": "ok",
                "created": created,
                "updated": updated,
                "tombstoned": tombstoned,
            }
            inst["last_run"] = last_run
            self.store.put(inst)
            self.ledger.append(
                EventKind.PLUGIN_SYNC,
                f"plugin:{installation_id}",
                f"sync {inst.get('plugin_id')} ok",
                [installation_id],
                extra=last_run,
            )
        return last_run

    def remove_plugin(self, installation_id: str, *, purge_data: bool = False) -> dict:
        inst = self.get_plugin(installation_id)
        with self.engine.tx():
            if inst.get("grant_id"):
                try:
                    self.revoke_grant(inst["grant_id"])
                except NotFound:
                    pass
            self.delete_plugin_secrets(installation_id)
            if purge_data:
                marker = f"plugin:{installation_id}"
                for row in self.store.list():
                    if marker in (row.get("source_refs") or []):
                        self.store.tombstone(row["id"])
            inst["state"] = "removed"
            stored = self.store.tombstone(installation_id)
            self.ledger.append(
                EventKind.PLUGIN_LIFECYCLE,
                OWNER,
                "plugin removed",
                [installation_id],
                extra={"purge_data": purge_data},
            )
        return stored

    def record_plugin_denied(self, installation_id: str, detail: str) -> None:
        self.ledger.append(
            EventKind.PLUGIN_DENIED,
            f"plugin:{installation_id}",
            detail,
            [installation_id],
        )
