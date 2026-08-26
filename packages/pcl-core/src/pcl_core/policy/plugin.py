from __future__ import annotations

from pcl_core.errors import PolicyDenied
from pcl_core.policy.evaluator import CLASS_RANK
from pcl_core.schema.plugin import PluginManifest


def manifest_from_snapshot(snapshot: dict) -> PluginManifest:
    if "plugin" in snapshot or "permissions" in snapshot:
        return PluginManifest.from_toml_dict(snapshot)
    return PluginManifest.model_validate(snapshot)


def check_produce(manifest: PluginManifest, type_: str, kind: str | None, classification: str) -> None:
    for item in manifest.permissions.produces:
        if item.type != type_:
            continue
        if item.kind and kind and item.kind != kind:
            continue
        ceiling = CLASS_RANK.get(item.classification, 2)
        actual = CLASS_RANK.get(classification, 1)
        if actual > ceiling:
            raise PolicyDenied(f"classification {classification} exceeds {item.classification}")
        return
    raise PolicyDenied(f"undeclared produce type {type_}" + (f"/{kind}" if kind else ""))


def check_host(manifest: PluginManifest, host: str) -> None:
    allowed = {h.lower() for h in manifest.permissions.hosts}
    if host.lower() not in allowed:
        raise PolicyDenied(f"undeclared host {host}")


def permission_diff(old: PluginManifest, new: PluginManifest) -> dict[str, list[str]]:
    added: list[str] = []
    removed: list[str] = []
    old_types = {(p.type, p.kind or "") for p in old.permissions.produces}
    new_types = {(p.type, p.kind or "") for p in new.permissions.produces}
    for item in sorted(new_types - old_types):
        added.append(f"produce:{item[0]}" + (f":{item[1]}" if item[1] else ""))
    for item in sorted(old_types - new_types):
        removed.append(f"produce:{item[0]}" + (f":{item[1]}" if item[1] else ""))
    old_hosts = set(old.permissions.hosts)
    new_hosts = set(new.permissions.hosts)
    added.extend(f"host:{h}" for h in sorted(new_hosts - old_hosts))
    removed.extend(f"host:{h}" for h in sorted(old_hosts - new_hosts))
    if new.permissions.secrets and not old.permissions.secrets:
        added.append("secrets")
    if old.permissions.secrets and not new.permissions.secrets:
        removed.append("secrets")
    return {"added": added, "removed": removed}
