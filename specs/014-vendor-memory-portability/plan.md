# Implementation Plan: Vendor Memory Portability

**Branch**: `014-vendor-memory-portability` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-vendor-memory-portability/spec.md`

## Summary

A person points the Hub at a ChatGPT, Claude, or Gemini export (or a PAM v1 / UMP L0 file). Detection uses on-disk markers (research F2–F6). Structured memory-like objects become **pending memory proposals** via `Hub.propose_memory` under actors `importer.*` — never `store.put` of canonical memory, never owner-as-importer (D1, D2). Conversation transcripts are **not** scraped into statements (D3); they wait on a separate archive-admission confirm and land only as `untrusted` `ArtifactKind.CONVERSATION` (D4). Re-import uses `(platform, original_id)` fingerprints so pending/accepted items are not duplicated (D5). PCA export keeps the existing age+zip contract and adds hashed members `interoperability/pam/memory-store.json` and `interoperability/ump/memories.ump.json` covering the same filter-respecting exported objects, omitting secrets and unaccepted proposals (D6–D8). Mapping lives in `packages/pca` (`pcl-core` only). REST stays loopback in `pcl-server`. Fixtures are synthetic and committed. Tests for SC-001, SC-002, SC-004, SC-007, SC-008 are written first and fail before satisfying code.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace); TypeScript/React build-time only for Import/Export UI

**Primary Dependencies**: existing `pca`, `pcl-core` (`propose_memory`, `Artifact`, audit ledger), `pcl-server` FastAPI, vendored PAM v1 JSON Schema (Apache-2.0 copy under `packages/pca/schemas/pam/`). No runtime `portable-ai-memory` SDK (D3). No UMP server.

**Storage**: existing SQLCipher vault. New durable type `vendor_import_batch` (`vib_…`). Conversation blobs in existing artifact blob store. No new database engine.

**Testing**: pytest; jsonschema against vendored PAM schema; structural UMP L0 checks; existing PCA round-trip tests remain green. Fixtures under `packages/pca/tests/fixtures/vendor/`. `red_before_green`.

**Target Platform**: local Hub (loopback). Offline once the file is on disk.

**Project Type**: child spec of 001 portability + proposal queue; library (`pca`) + loopback HTTP + Import/Export UI

**Performance Goals**: representative fixture (hundreds of structured memories, thousands of chat turns stored only if admitted) enqueues without marking anything canonical; Gemini Takeout parse must not hang the event loop — report a clear limit/error rather than partial canonical writes

**Constraints**: constitution 1.1.0 — propose-don't-write; imported is data; no chat-transcript scraping as a memory source; no new listener; `pcl-core` no network/plugin-host/server imports; coding agent not a Hub client; 001–003 not reopened as epics

**Scale/Scope**: ChatGPT, Claude, Gemini, PAM v1, UMP L0 file binding. Not Copilot/Grok/Perplexity. Not UMP L1+ HTTP/MCP. Not LLM converters.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` **v1.1.0** (ratified 2026-08-26, amended 2026-09-07). Gates:

| Gate | Status | Evidence |
|------|--------|----------|
| I. Person owns context; coding agent is not a Hub client | PASS | Import writes proposals the person reviews; implementer never pairs or writes `~/.pch`. Fixtures are synthetic (contract `fixtures.md`) |
| II. Local-first, loopback-only; encrypted at rest | PASS | File on disk only; no vendor HTTP. Existing `/v1/*` loopback. PCA still age-encrypted. No new bind |
| III. Least privilege / least context | PASS | Unaccepted proposals are not live memory in search/situation (`FR-015`, test `test_vendor_import_not_in_situation.py`). Untrusted artifacts labeled |
| IV. Provenance / explicit control | PASS | `propose_memory` + review queue; vendor provenance + fingerprint; audit `import.vendor_enqueued` / `import.archive_decided` / existing `export.created` in the same tx as the write |
| V. Imported content is data, never instruction | PASS | D3/D4; SC-002 fixture with grant/auto-accept payloads; `forbidden_context` extension; conversations never become Memory via scrape |
| Chat-transcript scraping as a memory source | PASS (in scope by exclusion) | Constitution forbids it until amended. This spec **does not scrape**. Structured files only. Rejected: `pam convert` memory-prompt path (research D3) |
| Universal ingest / Personal Intelligence / Agency | PASS | Three vendors + two interchange files, not "everything the person has done" |
| `pcl-core` free of network/plugin-host I/O | PASS | Parsers in `packages/pca`; core only gains schema/id/event kinds + `propose_memory` usage from server/pca |
| Allowed feature origin | PASS | Child spec of closed chapter 001 (PCA, proposals, untrusted import). Not a horizon item. 001–003 not reopened as epics |
| Package boundaries | PASS | `pca` depends on `pcl-core` only; REST in `pcl-server`; UI in `frontend/` |
| Speckit artifacts are repo files | PASS | Specs under `specs/014-…`; nothing written to the vault |
| Tests fail before satisfying implementation | PASS | SC table in research D12; tasks create failing tests first |
| No new listener / cloud / vector DB / UMP runtime | PASS | File import/export only |
| Secrets not committed | PASS | Fixtures contain no real tokens; export scan SC-007 |

**Post-design re-check (Phase 1)**: PASS — contracts add `/v1/import/vendor` (stage + archive decide) and PCA zip members under `interoperability/`; no non-loopback surface; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/014-vendor-memory-portability/
├── PLAN-BAR.md          # Frozen before this pack (Gauntlet)
├── plan.md              # This file
├── research.md          # Phase 0 — facts F1–F12, decisions D1–D12
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1 — empty-vault demo
├── contracts/
│   ├── vendor-import.md
│   ├── pca-pam-ump.md
│   └── fixtures.md
└── tasks.md             # Phase 2 — not created by /speckit-plan
```

### Source Code (repository root)

```text
packages/pca/src/pca/
├── export.py                 # existing PCA zip; add PAM/UMP members + integrity hashes
├── import_.py                # existing PCA open; unchanged path
├── vendor/
│   ├── detect.py             # layout markers → chatgpt|claude|gemini|pam|ump|unknown
│   ├── map_structured.py     # structured objects → Memory draft dicts (no chat scrape)
│   ├── conversations.py      # list conversation stubs for archive admission (not Memory)
│   ├── pam_project.py        # Hub objects → memory-store.json
│   ├── ump_project.py        # Hub objects → memories.ump.json
│   └── validate.py           # PAM schema + UMP L0 shape
├── schemas/pam/              # vendored official PAM v1 JSON Schema (Apache-2.0)
└── tests/
    ├── fixtures/vendor/      # synthetic ChatGPT, Claude, Gemini, PAM, UMP, injection
    ├── test_detect.py
    ├── test_vendor_proposals.py
    ├── test_no_scrape.py
    ├── test_archive_admission.py
    ├── test_dedup.py
    ├── test_pam_ump_export.py
    └── test_export_hygiene.py

packages/pcl-core/src/pcl_core/
├── ids.py                    # vendor_import_batch → vib
├── schema/metadata.py        # EntityType.VENDOR_IMPORT_BATCH
├── schema/portability.py     # VendorImportBatch model
├── schema/audit.py           # IMPORT_VENDOR_ENQUEUED, IMPORT_ARCHIVE_DECIDED
└── service.py                # enqueue_vendor_batch / decide_archive (or thin wrappers)

packages/pcl-server/src/pcl_server/rest/routers/portability.py
    POST /v1/import/vendor
    POST /v1/import/vendor/{batch_id}/archive
    GET  /v1/import/vendor/{batch_id}

packages/pcl-sdk/src/pcl_sdk/   # optional `import-vendor` CLI for tests

frontend/src/pages/Import.tsx   # vendor file path (no passphrase) + archive admit/discard
frontend/src/pages/Export.tsx   # copy unchanged except success text may mention PAM/UMP inside PCA
```

**Structure Decision**: extend `packages/pca` (already the PCA I/O package depending only on `pcl-core`) rather than a plugin. Plugins are import-only guests and must not own kernel proposal semantics. Vendor import is kernel portability, same family as PCA.

## Complexity Tracking

> Empty — no constitution exception. Chat-transcript scraping is **not** in this feature.

## Success criteria → tests

| SC | Named test / check |
|----|--------------------|
| SC-001 | `packages/pca/tests/test_vendor_proposals.py` — ChatGPT, Claude, Gemini fixtures with structured memories → 100% pending proposals, 0 canonical memories |
| SC-002 | `packages/pca/tests/test_no_scrape.py` + `packages/pcl-core/tests/test_vendor_injection.py` — chats with instruction payloads; 0 scrape proposals; grants/proposal statuses unchanged |
| SC-003 | `packages/pcl-server/tests/contract/test_vendor_import_flow.py` — import → review list → accept one → search hits; no hand-built profile |
| SC-004 | `packages/pca/tests/test_pam_ump_export.py` — filtered export object ids identical across PCA objects, PAM memories, UMP records |
| SC-005 | same file — vendored PAM schema validates `memory-store.json`; UMP L0 required keys on every record; empty vault still writes both files |
| SC-006 | existing `packages/pcl-server/tests/contract/test_export_import.py` stays green (PCA round-trip) |
| SC-007 | `packages/pca/tests/test_export_hygiene.py` — scan PCA/PAM/UMP for secrets, grants, pairing, unaccepted proposals |
| SC-008 | `packages/pca/tests/test_dedup.py` — second import of same fixture does not create a second live copy |
