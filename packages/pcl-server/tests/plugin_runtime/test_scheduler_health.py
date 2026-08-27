import asyncio
import time
from unittest.mock import MagicMock

from pcl_server.sync.scheduler import scheduler_loop


async def test_scheduler_plugin_sync_does_not_block_event_loop(monkeypatch):
    hub = MagicMock()
    hub.list_connectors.return_value = []
    hub.list_plugins.return_value = [
        {
            "id": "plug_1",
            "state": "enabled",
            "last_run": None,
            "manifest": {"permissions": {"schedule": "15m"}},
        }
    ]
    hub._kv_get.return_value = '{"fetched_at": "2099-01-01T00:00:00+00:00"}'

    def slow_sync(*_a, **_k):
        time.sleep(0.4)

    monkeypatch.setattr("pcl_server.plugins.host.run_plugin_sync", slow_sync)

    stop = asyncio.Event()
    task = asyncio.create_task(scheduler_loop(hub, stop))
    started = time.monotonic()
    await asyncio.sleep(0.05)
    elapsed = time.monotonic() - started
    stop.set()
    await asyncio.wait_for(task, timeout=2)
    assert elapsed < 0.2, f"event loop blocked for {elapsed:.3f}s during plugin sync"
