from __future__ import annotations

from pch_core.errors import ValidationFailed
from pch_core.hub.const import OWNER
from pch_core.schema.audit import EventKind
from pch_core.timeutil import now_iso


def _email_selection_ok(selection: dict) -> bool:
    return bool(
        selection.get("labels")
        or selection.get("senders")
        or selection.get("after")
        or selection.get("before")
    )


class ConnectorsMixin:
    def _token_kv_key(self, connector_id: str) -> str:
        return f"connector_token:{connector_id}"

    def set_connector_token(self, connector_id: str, token_blob: str) -> None:
        self._kv_set(self._token_kv_key(connector_id), token_blob)

    def get_connector_token(self, connector_id: str) -> str | None:
        return self._kv_get(self._token_kv_key(connector_id))

    def delete_connector_token(self, connector_id: str) -> None:
        self.engine.conn.execute("DELETE FROM kv WHERE k = ?", (self._token_kv_key(connector_id),))
        self.engine.conn.commit()

    def kv_keys(self) -> list[str]:
        return [r["k"] for r in self.engine.conn.execute("SELECT k FROM kv").fetchall()]

    def create_connector(self, provider: str, kind: str, selection: dict | None = None) -> dict:
        cadence = 15 if kind == "calendar" else 60
        body = {
            "provider": provider,
            "kind": kind,
            "status": "pending_consent",
            "selection": selection or {},
            "cadence_minutes": cadence,
            "classification": "private",
            "account_label": "",
        }
        stored = self.create("connector_account", body)
        return stored

    def list_connectors(self) -> list[dict]:
        return [c for c in self.store.list("connector_account") if c.get("status") != "disconnected"]

    def patch_connector(self, connector_id: str, body: dict, if_match: int | None = None) -> dict:
        if body.get("kind") == "email" or self.store.get(connector_id).get("kind") == "email":
            selection = body.get("selection")
            if selection is not None and not _email_selection_ok(selection):
                raise ValidationFailed("email selection must include labels, senders, or a date range")
        return self.patch(connector_id, body, if_match)

    def upsert_by_source_key(self, payload: dict) -> tuple[dict, str]:
        with self.engine.tx():
            return self._upsert_by_source_key(payload)

    def _upsert_by_source_key(self, payload: dict) -> tuple[dict, str]:
        key = payload.get("source_key")
        if not key:
            raise ValidationFailed("source_key required")
        existing = self.store.get_by_source_key(key, include_deleted=True)
        if existing:
            payload["id"] = existing["id"]
            payload["version"] = int(existing.get("version", 1)) + 1
            payload["created_at"] = existing.get("created_at")
            return self.store.put(payload), "updated"
        return self.store.put(payload, new=True), "created"

    def tombstone_source_key(self, source_key: str) -> dict | None:
        existing = self.store.get_by_source_key(source_key)
        if not existing:
            return None
        with self.engine.tx():
            return self.store.tombstone(existing["id"])

    def apply_connector_items(
        self, connector_id: str, items: list[dict], deleted_keys: list[str] | None = None
    ) -> dict:
        created = updated = tombstoned = 0
        with self.engine.tx():
            for item in items:
                _, action = self._upsert_by_source_key(item)
                if action == "created":
                    created += 1
                else:
                    updated += 1
            for key in deleted_keys or []:
                existing = self.store.get_by_source_key(key)
                if existing:
                    self.store.tombstone(existing["id"])
                    tombstoned += 1
            connector = self.store.get(connector_id)
            last_sync = {
                "at": now_iso(),
                "outcome": "ok",
                "created": created,
                "updated": updated,
                "tombstoned": tombstoned,
            }
            connector["last_sync"] = last_sync
            self.store.put(connector)
            self.ledger.append(
                EventKind.CONNECTOR_SYNC,
                OWNER,
                f"sync {connector.get('kind')} {last_sync['outcome']}",
                [connector_id],
                extra=last_sync,
            )
        return last_sync

    def disconnect_connector(self, connector_id: str, *, purge: bool = False) -> dict:
        connector = self.store.get(connector_id)
        with self.engine.tx():
            connector["status"] = "disconnected"
            self.store.put(connector)
            self.delete_connector_token(connector_id)
            if purge:
                prefix = f"google:{connector_id}:"
                for row in self.store.list_by_source_prefix(prefix):
                    self.store.tombstone(row["id"])
            stored = self.store.tombstone(connector_id)
            self.ledger.append(
                EventKind.CONNECTOR_DISCONNECTED,
                OWNER,
                "connector disconnected",
                [connector_id],
                extra={"purge": purge},
            )
        return stored

    def recipe_issued(self, connection_id: str, assistant: str) -> None:
        self.ledger.append(
            EventKind.CONNECTION_RECIPE_ISSUED,
            OWNER,
            f"recipe issued for {assistant}",
            [connection_id],
        )
