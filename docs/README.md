# Documentation

Personal Context Hub is a **local-first context layer** you own. Agents connect over MCP. Your vault stays on this device, encrypted, bound to loopback.

> Your agent can change. Your context shouldn’t.

This tree is the product documentation. When GitHub Pages is enabled it is served at [nicolasmota.github.io/personal-context-hub](https://nicolasmota.github.io/personal-context-hub/). Agents should start at [llms.txt](llms.txt). Local planning files (`VISION.md`, `ROADMAP.md`) stay on the maintainer’s machine and are not published.

---

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
- [Contributing](../CONTRIBUTING.md) — setup, PR expectations, secrets

## What this is not

The Hub is not a chatbot, not a foundation model, and not a vector database product. Agents read a **granted slice** of your record. None of them own it.
