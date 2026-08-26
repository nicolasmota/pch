# Contract: Portable Context Archive (PCA) v0

**Consumers**: the Hub's export/import flows (`packages/pca`), third-party tools, and the user directly — the archive MUST be readable without any running Hub or product account (FR-023).
**Producer**: `POST /v1/export`. **Consumer**: `POST /v1/import/stage`.

## Outer container

A single file: `<name>.pca` = an **age**-encrypted (passphrase recipient, scrypt work factor per age spec) **zip** archive. Decrypting with any standard age implementation yields the zip; no proprietary tooling required.

```text
archive.zip
├── manifest.json          # REQUIRED — see below
├── schemas/               # JSON Schema (draft 2020-12) for every record type,
│   └── {type}.schema.json #   exported from the Pydantic models at export time
├── objects/
│   ├── projects.jsonl     # one canonical-JSON record per line, current version
│   ├── goals.jsonl
│   ├── commitments.jsonl
│   ├── decisions.jsonl
│   ├── preferences.jsonl
│   ├── memories.jsonl
│   ├── artifacts.jsonl    # metadata records; content in artifacts/ when stored
│   ├── profile.jsonl
│   └── versions.jsonl     # full prior versions of exported objects (lineage)
├── events.jsonl           # audit lineage for exported objects (hash chain fields included)
└── artifacts/
    └── {content_hash}     # artifact blobs, decrypted for portability (already inside
                           #   the age envelope); named by sha256 of content
```

## `manifest.json`

```json
{
  "pca_version": "0.1.0",
  "created_at": "2026-08-21T20:00:00Z",
  "generator": {"name": "personal-context-hub", "version": "…"},
  "space": {"id": "personal", "kind": "personal"},
  "filters": {"projects": ["prj_…"], "from": null, "to": null, "classification_max": "sensitive"},
  "counts": {"memories": 1204, "projects": 8, "events": 15321, "artifacts": 77},
  "integrity": {
    "algorithm": "sha256",
    "files": {"objects/memories.jsonl": "…", "events.jsonl": "…"}
  },
  "schema_migration": {"notes_url_or_file": "schemas/", "min_reader_version": "0.1.0"}
}
```

## Record rules

- Records are **canonical JSON** (sorted keys, UTF-8, no insignificant whitespace) so integrity hashes are reproducible.
- Every record carries the full universal metadata envelope from [data-model.md](../data-model.md) — including `authority`, `classification`, `source_refs`, `confidence`, `version` (FR-024: provenance, ownership, classification always included).
- `versions.jsonl` preserves prior versions so "why does the system believe this" survives the round trip (SC-007: lineage preserved).
- **Excluded always**: pairing credentials, grant tokens, OS keychain material, third-party secrets (FR-024), SharedState (ephemeral by definition), FTS/derived indexes (rebuildable).
- Selective export (FR-023): `filters` in the manifest records exactly what subset was requested; records outside the filter MUST NOT appear.

## Import contract (quarantine staging — FR-025)

1. Reader verifies age decryption, then every `integrity.files` hash; any mismatch aborts with a report (nothing touches the vault).
2. All records land in an `ImportStaging` area, never directly in canonical tables.
3. ID reconciliation is by ULID: unknown id → candidate `create`; known id with equal content-hash → `skip`; known id with different content → **conflict**, resolved per item by the user as `merge | replace | keep_separate` (keep_separate re-ids the incoming record and links `imported_from`).
4. Imported records keep their original `authority` — an imported `agent_inferred` memory never becomes `user_confirmed` by import (FR-025), and imported artifacts remain `untrusted` (FR-026).
5. Applying a staging area emits `import.applied` audit events referencing the archive's `manifest` hash.

## Conformance tests (normative)

1. **Round trip** (SC-007): export a populated space → import into a clean vault → 100% of typed objects, version lineage, and policy labels equal by canonical-JSON comparison (modulo re-ids chosen in `keep_separate`).
2. Archive opens with a generic age CLI + unzip — no Hub involved; `schemas/` validates every record line.
3. Tampering with any byte of `objects/*.jsonl` is detected at stage time via `integrity.files`.
4. Export with a project filter contains zero records outside that project.
5. No credential, token, or SharedState record appears in any archive (scan by schema).
6. Import of an archive containing a conflicting `user_confirmed` memory never auto-overwrites — a conflict is always surfaced.
