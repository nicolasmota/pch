# Research: Vendor Memory Portability

**Feature**: `specs/014-vendor-memory-portability` · **Bar**: [PLAN-BAR.md](./PLAN-BAR.md)

No `[NEEDS CLARIFICATION]` markers remained in the spec. Decisions below resolve detection, propose-not-write, no-scrape, and PCA+PAM+UMP against constitution 1.1.0 and Hub 001–013 code.

## Facts

**F1. PCA today writes canonical records on apply.** `POST /v1/import/stage` decrypts a `.pca`, `mark_untrusted`, then `POST .../apply` `store.put`s records. That is correct for the person's own Hub archive. It is the wrong path for a vendor ZIP (spec FR-012).

**F2. ChatGPT export marker.** Official export is a ZIP or folder whose conversations file is `conversations.json`: a JSON **array** of conversations whose nodes live in a `mapping` DAG (OpenAI shape). Distinct from Claude. Optional `memories.json` (array of objects) and `user.json` custom-instruction fields are structured sources when present. Fixture: `packages/pca/tests/fixtures/vendor/chatgpt/`.

**Structured field map** (statement text, in order; first present wins): `content`, then `text`, then `memory`, then `value`. Id: `id` or `uuid`. ChatGPT `user.json`: `chatgpt_plus_user` / `about_user_message` / `custom_instructions` string fields only — not chat turns. Claude `memories.json`: same content/text map. PAM: `content`. UMP: `body.text`.

**F3. Claude export marker.** ZIP or folder with `conversations.json` where each conversation has a `chat_messages` array, plus `memories.json` when the person used Claude memory. Fixture includes both. Do not treat `chat_messages[].text` as `Memory.statement`.

**F4. Gemini export marker.** Google Takeout ZIP or unpacked tree containing `Takeout/Gemini Apps/` (per-conversation JSON and/or `conversations.json`) and/or `MyActivity.json` under a Gemini Apps path. Structured memories are often absent (PAM lists Gemini memories as "via prompt"). Fixture for SC-001 includes optional `Takeout/Gemini Apps/memories.json` so "contains structured memory objects" is testable without a scrape. Conversations-only Takeout is a separate fixture (0 memory proposals).

**F5. PAM v1 marker.** File or ZIP member `memory-store.json` with `"schema": "portable-ai-memory"` (schema_version 1.0). Memories array is the structured source. Companion `conversations/*.json` are archive candidates, not scrape input. Official schema: Apache-2.0, [portable-ai-memory](https://github.com/portable-ai-memory/portable-ai-memory). Spec URI `https://portable-ai-memory.org/spec/v1.0`.

**F6. UMP L0 marker.** `*.ump.json` (JSON array of records or NDJSON) or a JSON array whose objects have `"ump": "0.1"`. Required record fields: `ump`, `id`, `kind`, `body`, `scope`, `time` ([UMP spec](https://universalmemoryprotocol.io/specification/) file binding). `body.text` is the statement source. `*.ump.md` MAY be accepted later; v1 import requires JSON. UMP HTTP/MCP (L1+) is out of scope.

**F7. `Hub.propose_memory` forbids owner.** Actor must not be `owner`. Importer actors: `importer.chatgpt`, `importer.claude`, `importer.gemini`, `importer.pam`, `importer.ump`.

**F8. Duplicate pipeline.** `statement_hash` already marks exact-duplicate canonical statements `SUPERSEDED`. That is necessary but not sufficient for SC-008 (pending re-import). Need an explicit fingerprint on the batch/proposal.

**F9. Artifact kind `conversation` already exists.** `ArtifactKind.CONVERSATION`. Default `untrusted=True`. Gmail already writes untrusted artifacts. Reuse, do not invent a parallel type.

**F10. Export skip list** already drops `shared_state`, `connection`, `grant`, `manifest`, `action_intent`, `approval`. Proposals are not in `TYPE_FILES`, so they are already omitted from PCA objects — keep it that way. PAM/UMP builders must iterate the **same** exported object set as PCA, not `hub.store.list()` unfiltered.

**F11. PAM SDK converters** (`pam convert`) include a "memory prompt" path that LLM-extracts memories from chats. Constitution: do not build chat-transcript scraping as a memory source. Do not depend on that SDK at runtime.

**F12. Empty export.** A valid PAM store may have `memories: []`. A valid UMP file may be `[]`. Omitting the files would look like a failed export (spec edge case).

## Decisions

### D1. Vendor import is a new path, not PCA apply

**Choice:** `POST /v1/import/vendor` with `{ "path": "<local file or dir>" }` (no passphrase). Returns a `VendorImportBatch` (counts, source, proposal ids, archive pending). PCA `/v1/import/stage` unchanged; a vendor ZIP posted there fails closed if it is not a PCA.

**Rejected:** Reusing apply-into-vault. That writes live records and is how a ChatGPT dump would become "truth."

### D2. Structured objects → `propose_memory`, always pending

**Choice:** Map each structured memory-like object to a Memory draft (`kind` semantic/procedural/preference-as-semantic, `authority=proposed`, `source_refs` = batch id). Call `hub.propose_memory`. Force `ProposalStatus.PENDING` (never auto-accept). Provenance: `policy_tags` or memory labels include `vendor:<platform>`; original id on the batch item list and on `proposed_memory.labels` as `origin:<platform>:<id>`. Accept and edit-then-accept MUST copy those origin labels onto the canonical Memory (named assertion in `test_vendor_proposals.py`). Export PAM `provenance.platform` is `personal-context-hub` (this Hub exported it) while Hub labels still carry `origin:…` for the vendor id.

**Rejected:** Owner direct write; `store.put` of memories; auto-accept for "high confidence" vendor memories.

### D3. No scrape, no PAM SDK converter

**Choice:** `map_structured.py` reads only: Claude/ChatGPT/Gemini `memories.json` (and ChatGPT `user.json` custom instructions when present); PAM `memories[]`; UMP `body.text`. It MUST NOT walk `mapping`, `chat_messages`, Gemini activity HTML/JSON turns, or PAM conversation companions to produce Memory statements. Do not pip-install `portable-ai-memory` for convert. Vendor official PAM **schema JSON** only (validation of our export).

**Rejected:** Shell out to `pam convert`; LLM memory prompt; heuristic "first user message is a preference."

### D4. Conversation archive is one confirm per batch

**Choice:** Batch includes `archive_status: pending|admitted|discarded` and `conversation_count`. `POST /v1/import/vendor/{id}/archive` `{ "admit": true|false }`. Admit writes `Artifact` rows (`kind=conversation`, `untrusted=true`, `authority=source_imported`, body = transcript text stored as artifact body/blob). Discard writes nothing. Memory proposals from D2 are independent.

**Rejected:** Implicitly storing all chats on import; one proposal per thread (unusable at year-scale); putting chats into Memory.kind=episodic.

### D5. Dedup key `(platform, original_id)` then statement hash

**Choice:** Fingerprint `sha256(f"{platform}:{original_id}")`. If a pending or accepted proposal/memory already carries that fingerprint (on the batch item table or `labels`), skip creating a new proposal (SC-008). If original_id missing, fall back to `statement_hash` (existing pipeline SUPERSEDED). Re-import after reject may enqueue again only if we record rejected fingerprints too — **record rejected fingerprints on the batch** so reject stays rejected (spec Story 1.4). Store fingerprints on `VendorImportBatch.items[]` and a small `vendor_origin` label on the proposed memory.

**Rejected:** Dedup by filename only; silent second canonical copy.

### D6. PAM + UMP live inside the PCA zip

**Choice:** After writing `objects/*.jsonl`, also write:

- `interoperability/pam/memory-store.json`
- `interoperability/ump/memories.ump.json`

Include both in `manifest.integrity.files`. Same age envelope. Old PCA readers that only open `objects/` keep working. Empty vault still writes both files (empty memories / empty array).

**Rejected:** Separate unencrypted PAM download as the only door (classification leak unless we duplicate all PCA filters and the passphrase gate). Optional later. Dual encrypted PCA + plaintext PAM would split the filter story.

**Rejected:** UMP L1 HTTP `/ump/*` or MCP `ump.*` tools (new protocol surface / A2A-adjacent).

### D7. Projection mapping (Hub → PAM / UMP)

**PAM memory object (emit):** `id` (Hub id), `type` from a closed map (`preference` type and Memory.kind semantic → PAM `preference` or `fact`; procedural → `instruction`; episodic → `episode`; else `fact`), `content` = statement or preference value, `provenance.platform` = `personal-context-hub`, `provenance.extraction_method` = `api_export`, `exported_by` = `personal-context-hub/<version>`. Include preferences and profile-derived facts that PCA already exports. Skip artifacts, events, connectors.

**UMP record (emit):** `ump=0.1`, `id=urn:ump:<hub-id>`, `kind` mapped from MemoryKind (`semantic|episodic|procedural`; preferences → `semantic`; profile → `identity`), `body.text`, `scope.owner` = opaque person id (L0 MAY skip DID), `scope.visibility=private`, `time.created/observed` from `created_at`, `provenance.actor_kind=import` or `user` when `authority=user_confirmed`, `consent.exportable=true`. Honor nothing to redact in v1 beyond existing PCA skip list.

**Filters:** build projections from the in-memory `grouped` lists already selected for PCA (same loop in `export_archive`).

### D8. Export hygiene

**Choice:** PAM/UMP builders receive only rows that entered `grouped`. Additionally exclude `type=proposal`, `vendor_import_batch`, `import_staging`, plugin secret fields (already excluded). SC-007 scans UTF-8 of zip members after decrypt for grant tokens, `pairing`, `refresh_token`, `client_secret`, and any `authority: proposed` memory that was never accepted (proposals should not be in grouped).

### D9. Detection order

1. UMP (`ump` key / `.ump.json`)
2. PAM (`memory-store.json` schema)
3. Claude (`conversations.json` + `chat_messages` and/or `memories.json` with Claude conversation shape)
4. ChatGPT (`conversations.json` + `mapping`)
5. Gemini (`Takeout/Gemini Apps` or Gemini `MyActivity.json`)
6. unknown → error, no writes

Ambiguous ZIP containing both `memory-store.json` and vendor files: prefer PAM (already normalized).

### D10. UI / CLI

**Choice:** Import page: second card "Vendor or interchange file" — local path, no passphrase, Stage. Show counts + archive admit/discard. Existing PCA card unchanged. CLI for tests: `uv run pcl-sdk import-vendor PATH` against a running test Hub or in-process Hub.

**Rejected:** Drag-drop cloud picker; fetching the export from OpenAI/Anthropic/Google.

### D11. Situation / search

**Choice:** Pending proposals remain type `proposal` (already not listed as memory). After archive admission, conversation artifacts may be searchable as artifacts but MUST carry `untrusted=true`. Situation contract already sets `untrusted` on items. Test: injected "ignore previous instructions / grant admin" in an admitted artifact does not create grants or accept proposals. Do not place conversation artifacts in the memory inline list.

### D12. Fixtures and red-before-green

Committed synthetic fixtures only (see [contracts/fixtures.md](contracts/fixtures.md)). Tasks write the SC-001/002/004/007/008 tests first; implementation follows failing tests.

## Rejected alternatives (summary)

| Alternative | Why rejected |
|-------------|--------------|
| PCA apply for vendor ZIP | Writes live truth |
| `pam convert` / memory prompt | Chat scrape + extra dependency |
| UMP HTTP/MCP runtime | Out of scope; new protocol |
| Only PAM or only UMP on export | Spec requires both |
| Copilot/Grok | Later child spec; fail closed |
| Per-thread memory proposals from chats | Scrape + queue flood |
| Unencrypted PAM sidecar as default | Filter/secret leak vs PCA envelope |
| Plugin-hosted importer | Plugins must not own kernel proposals |
