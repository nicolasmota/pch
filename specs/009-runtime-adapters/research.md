# Research: Runtime Adapters

**Feature**: `specs/009-runtime-adapters/` · **Date**: 2026-08-26

No NEEDS CLARIFICATION markers remained in the Technical Context. Mapped 2026-08-26: catalog in `packages/pcl-server/src/pcl_server/pairing/catalog.py` (cursor, claude-code, claude-desktop, chatgpt — all emit the same `mcpServers` JSON); REST `GET /v1/catalog/assistants`, `POST /v1/connections/{id}/recipe`; Connections page loads the catalog; `get_context_contract` is the E1 seam. Hermes and OpenClaw are **absent**. Demo-agent is a pytest helper, not a catalog target.

## D1 — Catalog Hermes and OpenClaw; do not invent a protocol

**Decision**: Add `hermes` and `openclaw` to `ASSISTANTS` with `supported: True`. Keep Cursor. Claude Code / Desktop / ChatGPT stay as already-supported 002 entries (not the E5 “two real-use” count; E5’s named targets are Hermes + OpenClaw). Issue recipes through the existing POST. Audit `connection.recipe_issued` unchanged. **No** new MCP tool, **no** A2A object, **no** second `get_context_*`.

**Rationale**: Spec FR-001/FR-003/FR-005. Roadmap: at least two real-use runtimes; candidates Hermes, OpenClaw. Constitution: adapters MAY be added; a new A2A protocol MUST NOT.

**Alternatives considered**: (a) Count demo-agent as the second runtime — rejected: spec edge case; not “uso real.” (b) New `get_openclaw_context` tool — rejected: E1 seam is one contract. (c) HTTP MCP URL on a non-loopback host — rejected: constitution loopback-only. (d) Adapter per model (GPT vs Claude inside OpenClaw) — rejected: roadmap “Não cabe.”

## D2 — Native recipe shapes, same stdio bridge

**Decision**: `render_recipe` returns a **native** snippet per id, plus `format` (`cursor-mcp-json` \| `hermes-yaml` \| `openclaw-json`) and plain-language `instructions`:

| id | Person pastes into | Snippet shape | Bridge |
|----|--------------------|---------------|--------|
| cursor (unchanged) | `.cursor/mcp.json` | `{ "mcpServers": { "personal-context-hub": { command, args, env } } }` | `uv run pcl-sdk mcp-bridge` |
| hermes | `~/.hermes/config.yaml` under `mcp_servers` | `{ "mcp_servers": { "personal-context-hub": { "command", "args", "env" } } }` | same |
| openclaw | `~/.openclaw/openclaw.json` under `mcp.servers` | `{ "mcp": { "servers": { "personal-context-hub": { "command", "args", "env" } } } }` | same |

`env` is always `PCH_TOKEN` + `PCH_BASE=http://127.0.0.1:8765`. Unknown id → 422 (existing).

**Rationale**: FR-002. Hermes docs (2026): top-level `mcp_servers` in `config.yaml` (stdio `command`/`args`/`env`). OpenClaw docs: `mcp.servers` in `openclaw.json`. Forcing Cursor's `mcpServers` envelope would make the recipe lie.

**Alternatives considered**: (a) One JSON `mcpServers` blob for all three — rejected: Hermes will not load it as-is. (b) `hermes mcp add` CLI only, no copy-paste — rejected: Hub must show a person-visible recipe (US3). (c) Remote HTTP MCP — rejected: would imply a reachable server.

## D3 — Two real-use tokens agree on the existing contract

**Decision**: Automated SC-003 pairs two connections labeled as real-use targets (e.g. `hermes` and `openclaw`, or `cursor` and `hermes`), same grant, same purpose `"continue planning the trip"`, both `POST /v1/mcp/tools/get_context_contract`. Assert situation + goals match; phase/relations if seeded. No live Hermes/OpenClaw process in CI.

**Rationale**: Spec assumption: live desktop paste is manual; CI proves the connection surface. E1/E4 already proved two tokens agree; E5 names the **catalog ids** and native recipes, then reuses that seam.

**Alternatives considered**: (a) Spawn Hermes in CI — rejected: not in this repo; flaky; constitution coding-agent ≠ Hub client. (b) Skip SC-003 because E4 exists — rejected: E5 must name Hermes/OpenClaw in the test, not anonymous “one”/“two.”

## D4 — Switch/revoke does not rewrite the vault

**Decision**: SC-004: seed trip; pair A; fetch contract; pair B; B’s contract still names Europe Trip. SC-005: revoke A; `GET /v1/projects` still has the trip; memories/relations/phase unchanged. Revoke already exists (`POST /v1/connections/{id}/revoke`).

**Rationale**: FR-004, constitution “agents are replaceable.”

**Alternatives considered**: (a) Soft-delete projects on last-connection revoke — rejected: Hub objects are the person’s. (b) Require re-setup on switch — rejected: that is the bug E5 exists to prevent.

## D5 — Isolation uses a newly listed runtime name

**Decision**: Forbidden-context test pairs a connection whose catalog recipe id is `hermes` or `openclaw`, work-scoped grant, purpose continues the work roadmap. 0 personal trip titles/ids. Reuse E1 omission rules.

**Rationale**: FR-008, SC-006. A work agent named “hermes” must not leak personal trip because the recipe is new.

**Alternatives considered**: (a) Skip isolation “because E1 already did it” — rejected: bar criterion 7 names this file. (b) Redact with `"withheld"` titles — rejected: E1 forbids it.

## D6 — Connections copies native snippet

**Decision**: Keep catalog-driven picker (already maps `/v1/catalog/assistants`). After generate, copy `snippet` as JSON pretty-print **unless** `format === "hermes-yaml"`, in which case copy a YAML dump of `mcp_servers` (instructions still say merge under `mcp_servers:`). Do not coerce Hermes into `mcpServers`.

**Rationale**: US3. A JSON blob labeled as YAML would fail the “person can paste” bar.

**Alternatives considered**: (a) Always JSON — rejected for Hermes. (b) New Connections page — rejected: same surface.
