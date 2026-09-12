from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from pcl_core.schema.metadata import UniversalMetadata

PLUGIN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,63}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+([.-][a-zA-Z0-9.]+)?$")
SCHEDULE_RE = re.compile(r"^(manual|\d+m|\d+h)$")
ALLOWED_PRODUCE_TYPES = frozenset({"event", "artifact", "note"})
ALLOWED_CLASSIFICATIONS = frozenset({"public", "personal", "private", "sensitive"})
HOST_RE = re.compile(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$|^[A-Za-z0-9.-]+$")


class PluginState(StrEnum):
    INSTALLED = "installed"
    ENABLED = "enabled"
    PAUSED = "paused"
    DISABLED = "disabled"
    NEEDS_UPDATE = "needs_update"
    REMOVED = "removed"


class PluginOrigin(StrEnum):
    BUNDLED = "bundled"
    MARKETPLACE = "marketplace"
    SIDELOAD = "sideload"


class Isolation(StrEnum):
    SANDBOXED = "sandboxed"
    REDUCED = "reduced"


class ProducesPermission(BaseModel):
    type: str
    kind: str | None = None
    classification: str = "private"

    @field_validator("type")
    @classmethod
    def _type_ok(cls, value: str) -> str:
        if value not in ALLOWED_PRODUCE_TYPES:
            raise ValueError(f"unsupported produce type {value}")
        return value

    @field_validator("classification")
    @classmethod
    def _class_ok(cls, value: str) -> str:
        if value not in ALLOWED_CLASSIFICATIONS:
            raise ValueError(f"unsupported classification {value}")
        return value


class PluginPermissions(BaseModel):
    secrets: bool = False
    schedule: str = "manual"
    hosts: list[str] = Field(default_factory=list)
    produces: list[ProducesPermission] = Field(default_factory=list)

    @field_validator("schedule")
    @classmethod
    def _schedule_ok(cls, value: str) -> str:
        if not SCHEDULE_RE.match(value):
            raise ValueError("schedule must be manual, Nm, or Nh")
        if value.endswith("m") and int(value[:-1]) < 5:
            raise ValueError("schedule must be at least 5m")
        return value

    @field_validator("hosts")
    @classmethod
    def _hosts_ok(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for host in value:
            if "/" in host or ":" in host or "*" in host or host.startswith("http"):
                raise ValueError(f"hosts must be bare hostnames: {host}")
            if not HOST_RE.match(host):
                raise ValueError(f"invalid host {host}")
            cleaned.append(host.lower())
        return cleaned


class PluginManifest(BaseModel):
    id: str
    name: str
    description: str
    version: str
    publisher: str
    api_version: int = 1
    entry: str
    permissions: PluginPermissions = Field(default_factory=PluginPermissions)

    @field_validator("id")
    @classmethod
    def _id_ok(cls, value: str) -> str:
        if not PLUGIN_ID_RE.match(value):
            raise ValueError("plugin id must be a 3-64 char slug")
        return value

    @field_validator("version")
    @classmethod
    def _version_ok(cls, value: str) -> str:
        if not SEMVER_RE.match(value):
            raise ValueError("version must be semver")
        return value

    @classmethod
    def from_toml_dict(cls, raw: dict) -> PluginManifest:
        plugin = dict(raw.get("plugin") or raw)
        nested = dict(raw.get("permissions") or {})
        produces = list(nested.get("produces") or [])
        return cls(
            id=str(plugin.get("id") or ""),
            name=str(plugin.get("name") or ""),
            description=str(plugin.get("description") or ""),
            version=str(plugin.get("version") or ""),
            publisher=str(plugin.get("publisher") or ""),
            api_version=int(plugin.get("api_version") or 1),
            entry=str(plugin.get("entry") or "sync:main"),
            permissions=PluginPermissions(
                secrets=bool(nested.get("secrets", False)),
                schedule=str(nested.get("schedule") or "manual"),
                hosts=list(nested.get("hosts") or []),
                produces=[ProducesPermission.model_validate(item) for item in produces],
            ),
        )


class PluginInstallation(UniversalMetadata):
    plugin_id: str
    plugin_version: str
    manifest: dict = Field(default_factory=dict)
    origin: PluginOrigin = PluginOrigin.BUNDLED
    package_sha256: str = ""
    state: PluginState = PluginState.INSTALLED
    state_reason: str = ""
    grant_id: str | None = None
    isolation: Isolation = Isolation.REDUCED
    last_run: dict | None = None
    selection: dict = Field(default_factory=dict)
    sync_cursor: str | None = None
    source_account_id: str | None = None
