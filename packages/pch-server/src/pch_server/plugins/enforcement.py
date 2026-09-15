from __future__ import annotations

from urllib.parse import urlparse

from pch_core.errors import PolicyDenied, ValidationFailed
from pch_core.policy.plugin import check_host, check_produce, manifest_from_snapshot
from pch_core.schema.plugin import PluginManifest
from pch_core.service import Hub

MAX_ITEM_BYTES = 256 * 1024
MAX_ITEMS = 100
MAX_STATE_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 10 * 1024 * 1024
DENIAL_ABORT = 3


class RunGuard:
    def __init__(self, hub: Hub, installation: dict) -> None:
        self.hub = hub
        self.installation = installation
        self.manifest: PluginManifest = manifest_from_snapshot(installation["manifest"])
        self.denials = 0
        self.created = 0
        self.updated = 0
        self.tombstoned = 0

    def deny(self, detail: str) -> None:
        self.denials += 1
        self.hub.record_plugin_denied(self.installation["id"], detail)
        if self.denials >= DENIAL_ABORT:
            raise PolicyDenied(f"aborted after {self.denials} denials: {detail}")
        raise PolicyDenied(detail)

    def check_upsert(self, items: list[dict]) -> list[dict]:
        if len(items) > MAX_ITEMS:
            raise ValidationFailed(f"at most {MAX_ITEMS} items per call")
        cleaned: list[dict] = []
        for item in items:
            raw = str(item).encode("utf-8", errors="replace")
            if len(raw) > MAX_ITEM_BYTES:
                raise ValidationFailed("item exceeds 256KB")
            type_ = str(item.get("type") or "")
            kind = item.get("kind")
            classification = str(item.get("classification") or "private")
            if not item.get("source_key"):
                raise ValidationFailed("source_key required")
            try:
                check_produce(self.manifest, type_, kind if isinstance(kind, str) else None, classification)
            except PolicyDenied as exc:
                self.deny(str(exc.detail if hasattr(exc, "detail") else exc))
            item["authority"] = "source_imported"
            cleaned.append(item)
        return cleaned

    def check_fetch_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            self.deny("https only")
        host = (parsed.hostname or "").lower()
        try:
            check_host(self.manifest, host)
        except PolicyDenied as exc:
            self.deny(str(exc.detail if hasattr(exc, "detail") else exc))
        return host

    def check_secrets(self) -> None:
        if not self.manifest.permissions.secrets:
            self.deny("secrets not declared")

    def check_state_size(self, value: str) -> None:
        if len(value.encode()) > MAX_STATE_BYTES:
            raise ValidationFailed("state value exceeds 64KB")
