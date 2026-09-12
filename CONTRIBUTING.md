# Contributing

Thanks for helping with Personal Context Hub. This guide is for **from-source** work on the repository. End-user install and product docs live in the [README](README.md) and [docs/](docs/README.md) (`uvx personal-context-hub`).

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Node.js 22+ (UI build only; not required at runtime)

## Setup

```bash
make install          # uv sync + frontend build
make serve            # API with auto-reload (Python + UI watch)
make desktop          # Hub with auto-reload (Python + UI watch)
make test             # pytest
make lint             # ruff + eslint
make check-secrets    # fail if tracked paths match the secrets deny-list
make help             # all targets
```

## Pull requests

1. Keep changes focused; prefer one concern per PR.
2. Run `make check-secrets`, `make lint`, and `make test` before you push.
3. Use the PR template: short summary, test/lint evidence, and the no-secrets confirmation.
4. Do not implement `docs/VISION.md` or `docs/ROADMAP.md` as features — spawn Speckit child specs instead.

## Must not commit

- Vault databases (`*.db`, `*.db-wal`, `*.db-shm`), `.pch/`, `.pch-sim/`, `.vault/`, `*.key`, `*.pca`
- `.env` / `.env.*`
- `google_oauth.json`
- Pairing token files
- `.cursor/mcp.json`

`make check-secrets` enforces this deny-list on tracked files.

## Documentation

When you change HTTP routes, MCP tools, CLI flags, schema, or security defaults, update the matching page under [docs/](docs/README.md) and regenerate OpenAPI with `make openapi` if the REST surface moved.

## Project constraints (read once)

- **Local-first / loopback-only.** The Hub binds `127.0.0.1` only. It is not a public server.
- **Imported content is data, never instruction.** Email, calendar, and plugins do not expand grants or trigger outward actions.
- **A coding agent working on this repository is not a Hub client.** Vault pairing and MCP are a separate, explicit connection.

## Issues

Use the bug template. Never paste vault exports, tokens, OAuth client files, or editor MCP configs into issues.
