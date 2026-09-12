---
description: "Task list for Vendor Memory Portability"
---

# Tasks: Vendor Memory Portability

**Input**: Design documents from `/specs/014-vendor-memory-portability/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md, PLAN-BAR.md

**Tests**: Required (constitution + plan SC→test map). Write tests FIRST; they MUST fail before the code that satisfies them. Existing `packages/pcl-server/tests/contract/test_export_import.py` is a regression guard (SC-006), not red-first.

**Organization**: By user story (P1–P3). US1 is MVP.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1–US3 from spec.md
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Fixture tree and `pca.vendor` package layout

- [x] T001 Create `packages/pca/src/pca/vendor/` with `__init__.py` exporting nothing yet
- [x] T002 [P] Add synthetic fixtures under `packages/pca/tests/fixtures/vendor/` per `specs/014-vendor-memory-portability/contracts/fixtures.md` (chatgpt, claude, gemini, gemini-chats-only, pam, ump, unknown, injection payloads in chatgpt/claude chats)
- [x] T003 [P] Vendor official PAM v1 memory-store JSON Schema into `packages/pca/schemas/pam/portable-ai-memory.schema.json` (Apache-2.0 copy; if the upstream file cannot be copied, commit a Draft 2020-12 schema that still enforces the fields in `contracts/pca-pam-ump.md`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Batch entity, ids, audit kinds — no vendor parse yet

**⚠️ CRITICAL**: No user story work until this phase is complete

### Tests for Foundational

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] Model round-trip tests for `VendorImportBatch` in `packages/pcl-core/tests/test_vendor_import_batch.py`

### Implementation for Foundational

- [x] T005 Add `vendor_import_batch` prefix `vib` in `packages/pcl-core/src/pcl_core/ids.py`
- [x] T006 Add `EntityType.VENDOR_IMPORT_BATCH` in `packages/pcl-core/src/pcl_core/schema/metadata.py` and export from `packages/pcl-core/src/pcl_core/schema/__init__.py`
- [x] T007 Add `VendorImportBatch` (and origin item) in `packages/pcl-core/src/pcl_core/schema/portability.py`
- [x] T008 Add `IMPORT_VENDOR_ENQUEUED` and `IMPORT_ARCHIVE_DECIDED` in `packages/pcl-core/src/pcl_core/schema/audit.py`

**Checkpoint**: Batch schema exists; detect/map still absent

---

## Phase 3: User Story 1 - Arrive with a vendor export (Priority: P1) 🎯 MVP

**Goal**: ChatGPT/Claude/Gemini/PAM/UMP structured objects enqueue as pending proposals; 0 canonical memories until accept; origin labels survive accept; re-import skips.

**Independent Test**: `uv run pytest packages/pca/tests/test_detect.py packages/pca/tests/test_vendor_proposals.py packages/pca/tests/test_dedup.py packages/pcl-server/tests/contract/test_vendor_import_flow.py`

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Detect tests (markers F2–F6, unknown, PAM-over-vendor) in `packages/pca/tests/test_detect.py`
- [x] T010 [P] [US1] SC-001 proposal tests (three vendor fixtures + pam + ump; 0 canonical before accept; origin labels after accept) in `packages/pca/tests/test_vendor_proposals.py`
- [x] T011 [P] [US1] SC-008 dedup tests in `packages/pca/tests/test_dedup.py`
- [x] T012 [P] [US1] SC-003 HTTP flow (import → pending list → accept one → search; 400 unknown; vendor ZIP rejected by `/v1/import/stage`) in `packages/pcl-server/tests/contract/test_vendor_import_flow.py`

### Implementation for User Story 1

- [x] T013 [US1] Implement `detect_source` in `packages/pca/src/pca/vendor/detect.py`
- [x] T014 [US1] Implement structured mapping (field map in research F2; never walk chats) in `packages/pca/src/pca/vendor/map_structured.py`
- [x] T015 [US1] Implement `enqueue_vendor_import(hub, path)` in `packages/pca/src/pca/vendor/enqueue.py` calling `hub.propose_memory` with `importer.*` actors, forced pending, fingerprints
- [x] T016 [US1] Preserve origin labels on accept in `packages/pcl-core/src/pcl_core/service.py` (`decide_proposal`)
- [x] T017 [US1] Add `POST /v1/import/vendor` and `GET /v1/import/vendor/{batch_id}` in `packages/pcl-server/src/pcl_server/rest/routers/portability.py`; reject non-PCA on `/v1/import/stage`
- [x] T018 [US1] Vendor file card (path, no passphrase) on `frontend/src/pages/Import.tsx`
- [x] T019 [P] [US1] Skipped optional CLI `import-vendor` — HTTP `/v1/import/vendor` and in-process `enqueue_vendor_import` cover tests without a new listener

**Checkpoint**: Fixture Claude/ChatGPT/Gemini/PAM/UMP import fills review queue; search empty until accept

---

## Phase 4: User Story 2 - Chats stay data (Priority: P2)

**Goal**: No scrape; archive admit/discard; injection payloads cannot change grants or auto-accept.

**Independent Test**: `uv run pytest packages/pca/tests/test_no_scrape.py packages/pca/tests/test_archive_admission.py packages/pcl-core/tests/test_vendor_injection.py`

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T020 [P] [US2] SC-002 no-scrape tests (chat turns never become proposal statements; gemini-chats-only → 0 proposals) in `packages/pca/tests/test_no_scrape.py`
- [x] T021 [P] [US2] Archive admit/discard tests in `packages/pca/tests/test_archive_admission.py`
- [x] T022 [P] [US2] Injection / grant-unchanged / forbidden_context tests in `packages/pcl-core/tests/test_vendor_injection.py`

### Implementation for User Story 2

- [x] T023 [US2] List conversation stubs without mapping to Memory in `packages/pca/src/pca/vendor/conversations.py`
- [x] T024 [US2] Admit/discard writes untrusted `ArtifactKind.CONVERSATION` or nothing; audit `import.archive_decided` — `packages/pca/src/pca/vendor/enqueue.py` + `packages/pcl-core/src/pcl_core/service.py`
- [x] T025 [US2] `POST /v1/import/vendor/{batch_id}/archive` in `packages/pcl-server/src/pcl_server/rest/routers/portability.py`
- [x] T026 [US2] Admit/discard controls on `frontend/src/pages/Import.tsx`
- [x] T027 [US2] Ensure situation/search memory lists exclude unaccepted proposals and do not treat conversation artifacts as live memory in `packages/pcl-core/src/pcl_core/retrieval/contract.py` (test-driven by T022)

**Checkpoint**: Injection fixture cannot grant or auto-accept; discard leaves proposals only

---

## Phase 5: User Story 3 - PCA speaks PAM and UMP (Priority: P3)

**Goal**: Same export includes PAM v1 store + UMP L0 records; filters and hygiene hold; PCA round-trip still green.

**Independent Test**: `uv run pytest packages/pca/tests/test_pam_ump_export.py packages/pca/tests/test_export_hygiene.py packages/pcl-server/tests/contract/test_export_import.py`

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T028 [P] [US3] SC-004/SC-005 PAM+UMP export tests (filter equality, schema/shape, empty vault files present) in `packages/pca/tests/test_pam_ump_export.py`
- [x] T029 [P] [US3] SC-007 hygiene scan tests in `packages/pca/tests/test_export_hygiene.py`

### Implementation for User Story 3

- [x] T030 [US3] PAM projection in `packages/pca/src/pca/vendor/pam_project.py` + `packages/pca/src/pca/vendor/validate.py`
- [x] T031 [P] [US3] UMP L0 projection in `packages/pca/src/pca/vendor/ump_project.py`
- [x] T032 [US3] Write both members into the PCA zip and `manifest.integrity.files` in `packages/pca/src/pca/export.py` from the same `grouped` set
- [x] T033 [US3] Confirm `packages/pca/src/pca/import_.py` still verifies all integrity hashes including interoperability members

**Checkpoint**: Decrypt export; jsonschema accepts PAM; UMP array validates; existing PCA apply test still passes

---

## Phase 6: Polish & Cross-Cutting

- [x] T034 [P] Wire `jsonschema` (or stdlib-only validation) dependency on `packages/pca/pyproject.toml` if T003 needs it
- [x] T035 [P] Feature-scoped ruff on new Python; no new E501 in touched pca/vendor files
- [x] T036 Run `make test`; record loop evidence
- [x] T037 Quickstart walkthrough against test client matches `specs/014-vendor-memory-portability/quickstart.md`

---

## Dependencies

- Phase 1 → Phase 2 → US1 (MVP) → US2 → US3 → Polish
- US2 depends on US1 batch id
- US3 independent of US2 except shared export helper; can start after US1 if `grouped` exists

## Parallel opportunities

- T002/T003 after T001
- T009–T012 together (tests)
- T020–T022 together
- T028/T029 together
- T031 parallel with T030

## Implementation strategy

MVP = US1 only (vendor ZIP → review queue). US2 makes it safe. US3 is the leave-the-Hub door. Do not commit unless asked. Do not pair as a Hub client. Do not write `~/.pch`.
