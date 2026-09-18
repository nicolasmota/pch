# Personal Context Hub

Local-first **personal context** for any agent. Assistants connect over **MCP**. Your encrypted vault stays on this device, bound to loopback (`127.0.0.1`). The Hub is not a public server.

> Your agent can change. Your context shouldn’t.

[Getting started](getting-started.md) · [Pair an agent](guides/pair-an-agent.md) · [MCP tools](reference/mcp.md) · [Security](security.md) · [llms.txt](llms.txt)

This site is the product documentation. Source: [github.com/nicolasmota/personal-context-hub](https://github.com/nicolasmota/personal-context-hub). Local planning files (`VISION.md`, `ROADMAP.md`) stay on the maintainer’s machine and are not published.

## Start here

| I want to… | Go to |
|---|---|
| Install and open the Hub in a few minutes | [Getting started](getting-started.md) |
| Understand memory vs context vs situation | [Concepts](concepts.md) |
| Pair Cursor, Hermes, OpenClaw, or Claude | [Pair an agent](guides/pair-an-agent.md) |
| Ask an agent for the situation package | [Situation package](guides/situation-package.md) |
| Import Calendar or Gmail | [Google connectors](guides/google-connectors.md) |

## Guides

- [Pair an agent](guides/pair-an-agent.md) — pairing link, grant, MCP recipe
- [Situation package](guides/situation-package.md) — `get_context_contract`
- [Google connectors](guides/google-connectors.md) — OAuth client, Calendar, Gmail
- [Plugins](guides/plugins.md) — bundled importers, marketplace, authoring
- [Export and import](guides/export-import.md) — Portable Context Archive
- [The Hub UI](guides/the-hub-ui.md) — Home, Agents, Review; Advanced for the rest

## Reference

- [MCP tools](reference/mcp.md)
- [HTTP API](reference/http-api.md)
- [OpenAPI 3.1](openapi.json) — also `GET /openapi.json` and Swagger UI at `/docs` while the Hub is running
- [Data model](reference/data-model.md)
- [Situation package envelope](reference/context-contract.schema.json) — JSON Schema; check a package without the Hub
- [CLI](reference/cli.md)
- [Configuration](reference/configuration.md)
- [Python SDK](reference/python-sdk.md)

## How it is built

- [Architecture](architecture.md) — packages, data flow, trust kernel
- [Developing](develop.md) — from-source loop, tests, Speckit
- [Security](security.md) — encryption, grants, plugins, reporting
- [Contributing](https://github.com/nicolasmota/personal-context-hub/blob/main/CONTRIBUTING.md) — setup, PR expectations, secrets

## What this is not

The Hub is not a chatbot, not a foundation model, and not a vector database product. Agents read a **granted slice** of your record. None of them own it.
