# Data Model: Vendor Memory Portability

**Feature**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Decisions**: [research.md](research.md)

Existing 001 entities (`Memory`, `MemoryProposal`, `Artifact`, `ImportStaging`, PCA records) are unchanged in meaning. This feature adds one durable batch type and projection documents that are **not** vault entities.

## VendorImportBatch

One recognized file or folder. Prefix `vib_`. `type = vendor_import_batch`.

| Field | Type | Notes |
|-------|------|--------|
| `id` | `vib_…` | ULID |
| `source` | `chatgpt \| claude \| gemini \| pam \| ump` | From detect |
| `path_basename` | string | Filename only; no need to store full path after enqueue |
| `status` | `enqueued \| complete` | Complete after archive decided (or no conversations) |
| `archive_status` | `none \| pending \| admitted \| discarded` | `none` if conversation_count = 0 |
| `memory_item_count` | int | Structured objects seen |
| `conversation_count` | int | Threads found, not yet artifacts until admitted |
| `proposal_ids` | string[] | `prop_…` created this batch |
| `skipped_fingerprints` | string[] | Already pending/accepted/rejected |
| `items` | VendorOriginItem[] | Fingerprints + original ids |
| `injection_guard` | bool | Always true: import did not execute content |
| universal metadata | | `authority=source_imported`, classification `private` |

### VendorOriginItem

| Field | Type | Notes |
|-------|------|--------|
| `fingerprint` | sha256 hex | `sha256("{source}:{original_id}")` or statement hash fallback |
| `original_id` | string | Vendor/PAM/UMP id |
| `proposal_id` | string \| null | Null if skipped |
| `statement_preview` | string | Truncated, for UI summary |

**Validation:** `source` exhaustive. `archive_status=pending` iff `conversation_count > 0` and not yet decided. Declining archive does not delete `proposal_ids`.

**State:**

```text
detect → enqueue proposals (pending) → archive pending?
         ├─ no conversations → status=complete
         └─ POST archive admit → untrusted conversation artifacts, complete
            POST archive discard → no artifacts, complete
```

## MemoryProposal (existing, import usage)

Importer `submitted_by` ∈ {`importer.chatgpt`, `importer.claude`, `importer.gemini`, `importer.pam`, `importer.ump`}.

`proposed_memory.authority` = `proposed`.

`proposed_memory.labels` includes `origin:{source}:{original_id}`.

`status` is **always** `pending` on create from vendor import (never `auto_accepted`).

Accept / reject remain existing owner endpoints. Reject records the fingerprint as skipped for future imports (store on the batch and/or a `vendor_origin_decision` label on the rejected proposal row).

## Artifact (existing, archive admission)

| Field | Import value |
|-------|----------------|
| `kind` | `conversation` |
| `untrusted` | `true` |
| `authority` | `source_imported` |
| `title` | vendor thread title or id |
| `body` / blob | transcript text as **data** |
| `source_refs` | `[batch id]` |

Not a Memory. Not an instruction. Not in the situation memory inline list.

## PCA projections (files, not rows)

Produced at export from the same in-memory object groups as `objects/*.jsonl`.

### PAM memory-store.json

Root: `schema=portable-ai-memory`, `schema_version=1.0`, `exported_by=personal-context-hub/<pca_version>`, `export_type=full`, `memories[]`, `relations=[]`, `conversations_index=[]`, `integrity` per PAM spec (hash of memories). Each memory: `id`, `type`, `content`, `provenance.platform=personal-context-hub`, `provenance.extraction_method=api_export`.

Hub types → PAM `type`: preference → `preference`; Memory.kind procedural → `instruction`; episodic → `episode`; else `fact`. Profile statements → `identity` if PAM allows, else `fact`.

### memories.ump.json

JSON array of UMP 0.1 records: `ump`, `id` (`urn:ump:{hub_id}`), `kind`, `body.text`, `scope` (`owner` opaque person id, `visibility=private`), `time`, `provenance`. Hub MemoryKind → UMP kind: semantic/preference → `semantic`; episodic → `episodic`; procedural → `procedural`; profile → `identity`.

## Relationships

```text
Vendor file ──detect──► VendorImportBatch
                           │
                           ├─► MemoryProposal[] (pending) ──accept──► Memory (canonical)
                           │                         └──reject──► never canonical + fingerprint skipped
                           └─► archive admit ──► Artifact(conversation, untrusted)
                               archive discard ─► no artifacts

Hub canonical objects ──export──► PCA zip
                                    ├─ objects/*.jsonl  (existing)
                                    ├─ interoperability/pam/memory-store.json
                                    └─ interoperability/ump/memories.ump.json
```

## Audit

| Kind | When |
|------|------|
| `import.vendor_enqueued` | Batch + proposals written |
| `import.archive_decided` | Admit or discard |
| `export.created` | Existing; extra lists pam/ump member hashes |

Same transaction as the corresponding `store.put`s (constitution IV).
