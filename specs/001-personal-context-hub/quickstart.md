# Quickstart: Validating the Personal Context Hub (MVP)

Runnable end-to-end validation scenarios proving the feature works. Contracts: [rest-api.md](./contracts/rest-api.md), [mcp-server.md](./contracts/mcp-server.md), [pca-format.md](./contracts/pca-format.md). Entities: [data-model.md](./data-model.md).

## Prerequisites

- Python 3.14 + [uv](https://docs.astral.sh/uv/) installed; Node 22+ (build-time only, for the UI bundle)
- Playwright browsers for E2E: `uv run playwright install`

## Setup

```bash
uv sync                                   # install the workspace (all packages)
(cd frontend && npm ci && npm run build)  # build UI assets into packages/pcl-server/src/pcl_server/static/
uv run hub-desktop --dev                  # launch the Hub (dev mode: visible logs, temp vault opt-in)
```

Dev-mode conveniences: `uv run pcl-server --headless` runs the service without the pywebview window (REST on `http://127.0.0.1:<port>/v1`, OpenAPI at `/v1/openapi.json`); `uv run pcl-sdk demo-agent` starts a scriptable reference MCP client used by the scenarios below.

## Automated suites

```bash
uv run pytest                                     # unit + integration (policy, memory pipeline, vault, PCA)
uv run pytest packages/pcl-server/tests/contract  # Schemathesis vs OpenAPI + MCP conformance tests
uv run pytest -m forbidden_context                # seeded forbidden-context suite (SC-003: must be 100% blocked)
uv run pytest frontend/tests --e2e                # Playwright: six user-story journeys on the built app
```

## Manual validation scenarios

Each scenario maps to a spec user story; all are also automated in the E2E suite.

### 1. Create and manage context (US1)
Install/launch → guided setup creates the `personal` space → create project "Atlas" with a goal, a commitment, a decision, and two memories → search "Atlas" → edit one memory.
**Expected**: results show citations + classification; the edit is immediate, versioned (view "history"), and survives an app restart with networking disabled (offline check, FR-003).

### 2. Connect an agent with scoped access (US2)
Settings → Connections → "Add agent" → mint one-time link → run `uv run pcl-sdk demo-agent --pair <link>` → grant preset "Can read project Atlas".
**Expected**: agent's `search_personal_context` about Atlas returns cited context; a query about anything else returns empty results + redaction notice; the Hub's access page describes the grant in plain language.

### 3. Continuity across two agents (US3)
Pair a **second** demo agent instance (independent credential) with the same preset → ask both for `pcl://projects/<atlas_id>/brief`.
**Expected**: both receive consistent briefs with identical citations (SC-002). Revoke agent #1 → its next call fails with `revoked` within seconds (SC-004); agent #2 unaffected.

### 4. Memory proposal review (US4)
From agent: `propose_memory` (a) a normal preference with evidence, (b) one flagged `financial`, (c) one contradicting a user-confirmed memory.
**Expected**: (a) appears in the review queue (or auto-accepts per policy, with notification); (b) always requires explicit confirmation (FR-015); (c) opens a Conflict — the user-confirmed value is never silently overwritten (FR-007). Accept (a) and verify its provenance links back to the evidence.

### 5. Approval-gated action + audit (US5)
From agent: `propose_action` (kind `send_message`, human summary) → approve in the Hub → agent polls `check_action_status`, reports `executed`. Submit a second intent and decline it; replay the first intent's idempotency key.
**Expected**: nothing executes before approval; the declined intent never executes; the replay returns the same intent id (FR-020); the audit timeline shows request → approval → execution as one chained sequence, and `GET /v1/events/verify` passes.

### 6. Export / import round trip (US6)
Export the space (passphrase) → verify the file opens with generic `age` + `unzip` tooling → on a **clean vault** (fresh dev profile), stage the import, resolve nothing (no conflicts expected), apply.
**Expected**: staging view lists all objects first (FR-025); after apply, typed objects, version lineage, and policy labels match the source vault (SC-007 comparison script: `uv run pca verify-roundtrip <src-profile> <dst-profile>`).

## Performance checks

```bash
uv run pytest -m perf   # seeds 100k memories/artifact refs, asserts:
                        #   common searches < 1 s (SC-009)
                        #   manifest creation p95 < 500 ms
```

## Done criteria

All automated suites green, the six manual scenarios pass, and the forbidden-context and audit-verification checks report 100% (SC-003, SC-005).
