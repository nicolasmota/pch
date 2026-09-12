# Contract: PCA interoperability members (PAM + UMP)

**Extends**: [001 pca-format.md](../../001-personal-context-hub/contracts/pca-format.md) without breaking it.

## Zip layout (additive)

Existing members unchanged. New members, included in `manifest.integrity.files`:

```text
interoperability/pam/memory-store.json
interoperability/ump/memories.ump.json
```

Empty vault: both files still present (`memories: []` / `[]`).

## Population rule

Let `S` be the set of records written to `objects/*.jsonl` except `versions.jsonl` (same filters, same skip list as today's exporter).

- PAM `memories[]` contains one object per member of `S` that is a `memory`, `preference`, or `profile`/`person` fact.
- UMP array contains one record per the same subset.
- Ids in PAM/UMP MUST match Hub ids (PAM `id`, UMP `id` = `urn:ump:{hub_id}`).
- If `id ∈ S` is a memory/preference/profile, it appears in both projections. If `id ∉ S`, it appears in neither (SC-004).
- `proposal`, `vendor_import_batch`, `import_staging`, `grant`, `connection`, secrets: not in `S` (SC-007).

Artifacts and calendar events stay PCA-only in v1 (not PAM memories, not UMP records) so conversation archives do not re-enter interchange as "the person's memory."

## PAM memory-store.json

Must validate against vendored `packages/pca/schemas/pam/portable-ai-memory.schema.json` (official PAM v1, Apache-2.0 copy).

Minimum root fields: `schema`, `schema_version` (`1.0`), `exported_by` (`personal-context-hub/<version>`), `export_date`, `memories`, `integrity`.

Each memory: `content` is the Hub statement (or preference value as text); `provenance.platform` is `personal-context-hub`; `provenance.extraction_method` is `api_export`.

A process that is **not** this Hub (jsonschema + the vendored file) MUST accept the document (SC-005).

## memories.ump.json

JSON array (not NDJSON in v1). Each element:

| Field | Rule |
|-------|------|
| `ump` | `"0.1"` |
| `id` | `urn:ump:{hub_id}` |
| `kind` | `semantic` \| `episodic` \| `procedural` \| `identity` |
| `body.text` | Hub statement |
| `scope.owner` | Hub person id (opaque string allowed at L0) |
| `scope.visibility` | `private` |
| `time.created` | Hub `created_at` |

A reader that only checks those keys (not this Hub) MUST accept the file (SC-005).

No UMP HTTP or MCP in this contract.

## PCA import

`POST /v1/import/stage` continues to read `objects/*.jsonl` only. It MAY ignore `interoperability/**`. It MUST still verify every `integrity.files` hash, including the new members, so tampering with PAM/UMP is detected even if those files are unused on apply.

Applying PCA still MUST NOT upgrade authority to `user_confirmed`.
