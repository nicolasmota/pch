# pcl-sdk

Python client, MCP stdio bridge, plugin kit, demo agent, and repository tooling (Speckit loop, sim, eval) for Personal Context Hub.

```python
from pcl_sdk import Client

c = Client("http://127.0.0.1:8765", token="")
c.pair("<code>")
print(c.call("get_context_contract", purpose="continue planning the trip"))
```

```bash
uv run pcl-sdk mcp-bridge --token "$PCH_TOKEN" --base http://127.0.0.1:8765
uv run pcl-sdk plugin new my.importer
```

Documentation: [Python SDK](../../docs/reference/python-sdk.md) · [MCP tools](../../docs/reference/mcp.md) · [Plugins](../../docs/guides/plugins.md)
