# Quickstart Validation: External Connectors

**Feature**: 002-external-connectors — runnable scenarios proving each user story end-to-end.

## Prerequisites

- 001 MVP installed and working: `make install && make serve` (Hub on `http://127.0.0.1:8765`, setup completed, Atlas project + one cited memory present)
- Cursor installed (primary US1 target per clarification)
- For US2/US3: a Google account and network access (or run the mocked suite: `uv run pytest -m connectors`)

## Scenario 1 — Real assistant answers with vault context (US1 / SC-001, SC-002, SC-003)

1. Hub UI → **Connections** → *Create pairing link* → grant preset "Can read a specific project" scoped to Atlas.
2. Pick **Cursor** in the assistant catalog → copy the rendered `mcp.json` snippet ([contract](./contracts/connectors-rest.md)).
3. Paste into `.cursor/mcp.json`, reload MCP servers.
4. In Cursor chat, ask: *"Using my personal context hub, what does my Atlas project prefer?"*
   - **Expected**: answer grounded in the vault memory with citations; total setup time under 10 minutes (SC-001).
5. Ask about personal finance.
   - **Expected**: refusal; Hub **Audit** shows the denial under the connection's identity (SC-002).
6. Hub UI → revoke the connection → repeat step 4.
   - **Expected**: revocation error within seconds (SC-003).

## Scenario 2 — Calendar grounds schedule questions (US2 / SC-004, SC-005)

1. Hub UI → **Connectors** → *Connect Google Calendar* → consent screen shows read-only scope + 15-min cadence → confirm in browser.
2. Wait for first sync (or press *Sync now*).
   - **Expected**: events visible as `event` objects, classification `private`, authority `imported`, provenance pointing at the connector ([data model](./data-model.md)); sync run in Audit.
3. In Cursor (granted): *"What does my week look like?"*
   - **Expected**: answer within 5 minutes of consent, citing synced events (SC-004).
4. Disconnect the connector (keep data).
   - **Expected**: no further syncs; existing events readable, marked no-longer-syncing.

## Scenario 3 — Email stays selective, sensitive, and proposal-gated (US3 / SC-006, SC-008)

1. **Connectors** → *Connect Gmail* → select exactly one label and a date range (empty selection must be rejected).
2. After sync: verify imported messages are `artifact` objects, `kind=email`, classification `sensitive`.
3. In Cursor with a **preset** grant (ceiling `private`): search a topic covered by the imported email.
   - **Expected**: content withheld + redaction notice (SC-006).
4. With a sensitive-ceiling grant: ask Cursor to record a durable claim from an email (e.g., a confirmed date).
   - **Expected**: claim lands in **Review** as a proposal citing the messages — not canonical memory (FR-017).
5. Run the injection suite: `uv run pytest -m forbidden_context -k connector`.
   - **Expected**: all pass — imported payloads never change grants, policy, or actions (SC-008).

## Scenario 4 — Credentials never leave (SC-007)

1. **Export** with a passphrase → inspect the archive.
   - **Expected**: zero `connector_token:*` material; connector account objects contain labels only.
2. `uv run pytest -k "export and connector"` — token-exclusion test passes.

## Automated suites

```bash
uv run pytest -m connectors          # mocked Google transports: consent, sync, dedup, lifecycle
uv run pytest -k mcp_bridge          # stdio conformance per contracts/mcp-bridge.md
uv run pytest -m forbidden_context   # 001 suite + connector-origin fixtures
```

## Validation outcomes (2026-08-21)

| Scenario | Result | Evidence |
|---|---|---|
| 1 — Cursor / MCP recipe | **Automated pass.** Catalog + recipe + bridge mapping (tools/list parity, cited search round-trip, revocation/unreachable errors). Live Cursor paste still needs a running Hub (`make serve`) and the copied `mcp.json`. | `uv run pytest packages/pcl-server/tests/contract/test_assistant_catalog.py packages/pcl-sdk/tests/test_mcp_bridge.py` |
| 2 — Calendar | **Mocked pass.** Consent, sync, dedup, 410 resync, pause/resume/disconnect. Real Google OAuth needs `GOOGLE_OAUTH_CLIENT_ID`. | `uv run pytest -m connectors` |
| 3 — Gmail | **Mocked pass.** Empty selection 422, sensitive import, private-ceiling redaction, claim → review queue, injection suite. | `uv run pytest -m connectors` and `uv run pytest -m forbidden_context -k connector` |
| 4 — Token exclusion | **Pass.** | `uv run pytest packages/pca/tests/test_token_exclusion.py` |

Default pytest: 58 passed, 1 skipped. Frontend production build succeeded.
