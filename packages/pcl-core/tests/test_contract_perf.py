import time

import pytest
from pcl_core.service import OWNER
from pcl_core.testing.trip_seed import seed_trip


@pytest.mark.perf
def test_contract_assembly_under_two_seconds(hub):
    seed = seed_trip(hub)
    pid = seed["project"]["id"]
    for i in range(2000):
        hub.create(
            "memory",
            {"statement": f"background fact {i} unrelated to cooking", "kind": "semantic"},
        )
        if i < 50:
            hub.create(
                "memory",
                {"statement": f"travel packing item {i} for the Europe trip", "kind": "semantic", "project_id": pid},
            )
    t0 = time.perf_counter()
    contract = hub.get_context_contract(OWNER, "continue planning the trip")
    elapsed = time.perf_counter() - t0
    assert contract["situation"]["project_id"] == pid
    assert elapsed < 2.0
