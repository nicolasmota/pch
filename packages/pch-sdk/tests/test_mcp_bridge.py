import json

from pch_sdk.capture_guidance import DURABLE_TRIGGERS, TASK_START_TRIGGERS
from pch_sdk.mcp_bridge import TOOL_NAMES, handle_message, map_tool_result


def test_tools_list_parity():
    reply = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, "http://x", "tok")
    names = [t["name"] for t in reply["result"]["tools"]]
    assert names == TOOL_NAMES
    contract = next(t for t in reply["result"]["tools"] if t["name"] == "get_context_contract")
    assert "as_of" in contract["inputSchema"]["properties"]


def test_revocation_and_unreachable_mapping():
    revoked = map_tool_result(401, {})
    assert "revoked" in revoked["content"][0]["text"].lower()
    assert revoked["isError"] is True
    down = map_tool_result(0, {"detail": "Connection refused"})
    assert (
        "unreachable" in down["content"][0]["text"].lower()
        or "Hub unreachable" in down["content"][0]["text"]
    )


def test_search_round_trip(monkeypatch):
    def fake_call(base, token, name, arguments):
        assert name == "search_personal_context"
        return 200, {"results": [{"id": "mem_1", "statement": "Atlas prefers cited briefs"}]}

    monkeypatch.setattr("pch_sdk.mcp_bridge.call_hub", fake_call)
    reply = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "search_personal_context",
                "arguments": {"query": "Atlas", "purpose": "brief"},
            },
        },
        "http://x",
        "tok",
    )
    payload = json.loads(reply["result"]["content"][0]["text"])
    assert payload["results"][0]["statement"].startswith("Atlas")


def test_situation_and_propose_descriptions_include_when_to_use():
    reply = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, "http://x", "tok")
    tools = {t["name"]: t["description"].lower() for t in reply["result"]["tools"]}
    sit = tools["get_context_contract"]
    prop = tools["propose_memory"]
    assert sit != "get context contract"
    assert prop != "propose memory"
    assert any(token in sit for token in TASK_START_TRIGGERS)
    assert any(token in prop for token in DURABLE_TRIGGERS)
    assert "invent" in sit
    assert "proposal" in prop or "propose" in prop
