# pch-sdk

Python client, MCP stdio bridge, plugin kit, and demo agent for Personal Context Hub.

```python
from pch_sdk import Client

c = Client("http://127.0.0.1:8765", token="")
c.pair("<code>")
print(c.call("get_context_contract", purpose="continue planning the trip"))
```

```bash
uv run pch-sdk mcp-bridge --token "$PCH_TOKEN" --base http://127.0.0.1:8765
uv run pch-sdk plugin new my.importer
```

Documentation: [Python SDK](../../docs/reference/python-sdk.md) · [MCP tools](../../docs/reference/mcp.md) · [Plugins](../../docs/guides/plugins.md)
