# Adapter authoring

Pair with a one-time link from the Hub, then call MCP tools via `/v1/mcp/tools/{name}`
or the official MCP Streamable HTTP endpoint when enabled.

```python
from pcl_sdk import Client

c = Client("http://127.0.0.1:8765", token="")
c.pair("<code>")
print(c.search("Atlas", purpose="status_update"))
```
