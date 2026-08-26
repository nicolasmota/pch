from __future__ import annotations

ASSISTANTS: list[dict] = [
    {
        "id": "cursor",
        "name": "Cursor",
        "supported": True,
        "notes": "Primary validated target",
    },
    {
        "id": "claude-code",
        "name": "Claude Code",
        "supported": True,
        "notes": "",
    },
    {
        "id": "claude-desktop",
        "name": "Claude Desktop",
        "supported": True,
        "notes": "On WSL, run the bridge inside WSL",
    },
    {
        "id": "chatgpt",
        "name": "ChatGPT",
        "supported": True,
        "notes": "Requires MCP connector availability on the user's plan",
    },
]


def list_assistants() -> list[dict]:
    return [dict(item) for item in ASSISTANTS]


def get_assistant(assistant_id: str) -> dict | None:
    for item in ASSISTANTS:
        if item["id"] == assistant_id:
            return dict(item)
    return None


def render_recipe(assistant_id: str, token: str, base_url: str) -> dict:
    entry = get_assistant(assistant_id)
    if not entry:
        return {}
    if not entry["supported"]:
        return {}
    snippet = {
        "mcpServers": {
            "personal-context-hub": {
                "command": "uv",
                "args": ["run", "pcl-sdk", "mcp-bridge"],
                "env": {"PCH_TOKEN": token, "PCH_BASE": base_url},
            }
        }
    }
    instructions = {
        "cursor": "Add this to .cursor/mcp.json, then reload MCP servers.",
        "claude-code": "Add this MCP server in Claude Code settings.",
        "claude-desktop": "Paste into Claude Desktop mcpServers config.",
        "chatgpt": "Add as an MCP connector if your plan supports it.",
    }
    return {
        "assistant": assistant_id,
        "instructions": instructions.get(assistant_id, "Paste this MCP config into the assistant."),
        "snippet": snippet,
    }
