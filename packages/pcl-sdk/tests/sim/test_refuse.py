from __future__ import annotations

from pcl_sdk.sim import compile_persona, dump_ticks

FORBIDDEN = frozenset(
    {"propose_action", "apply_connector_items", "create_connector"}
)


def test_no_outbound_actions() -> None:
    ticks = dump_ticks("lived-stretch")
    actions = {t["action"] for t in ticks}
    assert actions.isdisjoint(FORBIDDEN)
    persona = compile_persona("lived-stretch")
    assert all(t["action"] not in FORBIDDEN for t in persona)
