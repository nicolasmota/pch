from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime, timedelta

from pch_core.connectors.gmail import GmailConnector
from pch_core.connectors.google_calendar import GoogleCalendarConnector
from pch_core.errors import Busy, Revoked, ValidationFailed
from pch_core.service import Hub

from pch_server.marketplace.catalog import refresh_catalog
from pch_server.sync.google_fetch import fetch_calendar_events, fetch_gmail_messages
from pch_server.sync.oauth import refresh_access_token

log = logging.getLogger(__name__)
_locks: dict[str, asyncio.Lock] = {}
_thread_locks: dict[str, bool] = {}


def _due(connector: dict) -> bool:
    last = (connector.get("last_sync") or {}).get("at")
    cadence = int(connector.get("cadence_minutes") or 15)
    if not last:
        return True
    try:
        then = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except ValueError:
        return True
    return datetime.now(UTC) >= then + timedelta(minutes=cadence)


def run_connector_sync(hub: Hub, connector_id: str) -> dict:
    if _thread_locks.get(connector_id):
        raise Busy("sync in progress")
    _thread_locks[connector_id] = True
    try:
        if getattr(hub.engine.conn, "in_transaction", False):
            hub.engine.conn.commit()
        connector = hub.store.get(connector_id)
        if connector.get("status") != "active":
            raise ValidationFailed("connector is not active")
        if connector.get("kind") == "email" and not _email_ok(connector.get("selection") or {}):
            raise ValidationFailed("email selection must include labels, senders, or a date range")
        try:
            token = refresh_access_token(hub, connector_id)
        except Exception:
            connector["status"] = "reconnect_needed"
            hub.store.put(connector)
            hub.engine.conn.commit()
            raise Revoked("reconnect needed") from None
        if connector.get("kind") == "calendar":
            mapper = GoogleCalendarConnector()
            selection = connector.get("selection") or {}
            items_raw, deleted_ids, cursor, _full = fetch_calendar_events(
                token, selection.get("calendar_ids") or ["primary"], connector.get("sync_cursor")
            )
            mapped = []
            for raw in items_raw:
                item = mapper.map_item(raw, connector)
                if item:
                    mapped.append(item)
            deleted_keys = [mapper.source_key({"id": i}, connector) for i in deleted_ids]
        else:
            mapper = GmailConnector()
            items_raw, cursor = fetch_gmail_messages(
                token, connector.get("selection") or {}, connector.get("sync_cursor")
            )
            mapped = []
            for raw in items_raw:
                item = mapper.map_item(raw, connector)
                if item:
                    mapped.append(item)
            deleted_keys = []
        summary = hub.apply_connector_items(connector_id, mapped, deleted_keys)
        connector = hub.store.get(connector_id)
        connector["sync_cursor"] = cursor
        connector["last_sync"] = summary
        connector["status"] = "active"
        hub.store.put(connector)
        hub.engine.conn.commit()
        return summary
    finally:
        _thread_locks.pop(connector_id, None)


def _email_ok(selection: dict) -> bool:
    return bool(
        selection.get("labels")
        or selection.get("senders")
        or selection.get("after")
        or selection.get("before")
    )


def _plugin_due(plugin: dict) -> bool:
    last = (plugin.get("last_run") or {}).get("at")
    schedule = ((plugin.get("manifest") or {}).get("permissions") or {}).get("schedule") or "manual"
    if schedule == "manual":
        return False
    minutes = 60
    if schedule.endswith("m"):
        minutes = int(schedule[:-1])
    elif schedule.endswith("h"):
        minutes = int(schedule[:-1]) * 60
    if not last:
        return True
    try:
        then = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except ValueError:
        return True
    return datetime.now(UTC) >= then + timedelta(minutes=minutes)


def _catalog_due(hub: Hub) -> bool:
    raw = hub._kv_get("marketplace_catalog")
    if not raw:
        return True
    try:
        fetched = json.loads(raw).get("fetched_at")
        then = datetime.fromisoformat(str(fetched).replace("Z", "+00:00"))
    except Exception:
        return True
    return datetime.now(UTC) >= then + timedelta(hours=12)


async def scheduler_loop(
    hub: Hub, stop: asyncio.Event, *, catalog_refresh: bool = True
) -> None:
    while not stop.is_set():
        try:
            for connector in hub.list_connectors():
                if connector.get("status") != "active":
                    continue
                if connector.get("migrated_to"):
                    continue
                if _due(connector):
                    try:
                        await asyncio.to_thread(run_connector_sync, hub, connector["id"])
                    except Exception:
                        log.exception("scheduled sync failed for %s", connector.get("id"))
            for plugin in hub.list_plugins():
                if plugin.get("state") != "enabled":
                    continue
                if _plugin_due(plugin):
                    try:
                        # Circular: plugins.host -> sync.http -> scheduler
                        from pch_server.plugins.host import run_plugin_sync

                        await asyncio.to_thread(
                            run_plugin_sync, hub, plugin["id"], reason="scheduled"
                        )
                    except Exception:
                        log.exception("scheduled plugin sync failed for %s", plugin.get("id"))
            if catalog_refresh and _catalog_due(hub):
                try:
                    await asyncio.to_thread(refresh_catalog, hub)
                except Exception:
                    log.exception("catalog refresh failed")
        except Exception:
            log.exception("scheduler tick failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=30)
        except TimeoutError:
            continue
