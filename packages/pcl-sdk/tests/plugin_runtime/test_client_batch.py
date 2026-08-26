from pcl_sdk.plugin_runtime import MAX_ITEMS_PER_CALL, HubClient


def test_items_upsert_batches_over_limit():
    client = HubClient()
    calls: list[tuple[str, dict]] = []

    def fake_call(method: str, params: dict | None = None) -> dict:
        calls.append((method, params or {}))
        return {"ok": True, "summary": {"created": len((params or {}).get("items") or [])}}

    client._call = fake_call  # type: ignore[method-assign]
    items = [{"source_key": f"k{i}"} for i in range(250)]
    client.items_upsert(items)
    assert len(calls) == 3
    assert all(method == "hub.items.upsert" for method, _ in calls)
    assert [len(params["items"]) for _, params in calls] == [100, 100, 50]
    assert MAX_ITEMS_PER_CALL == 100


def test_items_upsert_empty_is_noop():
    client = HubClient()
    calls: list[tuple[str, dict]] = []

    def fake_call(method: str, params: dict | None = None) -> dict:
        calls.append((method, params or {}))
        return {"ok": True}

    client._call = fake_call  # type: ignore[method-assign]
    client.items_upsert([])
    assert calls == []


def test_items_tombstone_batches_over_limit():
    client = HubClient()
    calls: list[tuple[str, dict]] = []

    def fake_call(method: str, params: dict | None = None) -> dict:
        calls.append((method, params or {}))
        return {"ok": True}

    client._call = fake_call  # type: ignore[method-assign]
    client.items_tombstone([f"k{i}" for i in range(101)])
    assert [len(params["source_keys"]) for _, params in calls] == [100, 1]
