# Contract: Vendor / interchange import

**Consumers**: Hub UI Import page, `pcl-sdk import-vendor`, pytest.  
**Producer**: `packages/pca` detect+map; `pcl-server` portability router.

All routes bind loopback only. Owner session required. No passphrase (these files are not age-encrypted PCA).

## Detect

Input: filesystem path (file or directory). ZIP is opened read-only in memory; no write except vault via Hub APIs below.

| Detected `source` | Markers (all must be documented in tests) |
|-------------------|-------------------------------------------|
| `ump` | `.ump.json` or JSON array of objects with `"ump"` |
| `pam` | `memory-store.json` with `schema` = `portable-ai-memory` |
| `claude` | `conversations.json` items have `chat_messages` and/or sibling `memories.json` with Claude conversation shape |
| `chatgpt` | `conversations.json` items have `mapping` |
| `gemini` | `Takeout/Gemini Apps/` or Gemini `MyActivity.json` |
| _error_ | none of the above — HTTP 400, vault unchanged |

If PAM and vendor files coexist, `source=pam`.

## `POST /v1/import/vendor`

Body: `{ "path": "/abs/or/relative" }`

Effects:

1. Detect. Unknown → 400, no writes.
2. Map **structured** memory-like objects only (see research D3). Each → `hub.propose_memory` with actor `importer.{source}`, `authority=proposed`, status pending.
3. Do not create Memory rows.
4. Do not create conversation Artifacts yet.
5. Persist `VendorImportBatch` with counts, `proposal_ids`, fingerprints skipped, `archive_status`.
6. Audit `import.vendor_enqueued` in the same transaction.

Response 200:

```json
{
  "id": "vib_…",
  "source": "claude",
  "memory_item_count": 12,
  "conversation_count": 40,
  "enqueued": 12,
  "skipped": 0,
  "archive_status": "pending",
  "proposal_ids": ["prop_…"]
}
```

A conversations-only file: `enqueued=0`, `archive_status=pending` if threads exist.

## `GET /v1/import/vendor/{batch_id}`

Returns the batch. 404 if missing.

## `POST /v1/import/vendor/{batch_id}/archive`

Body: `{ "admit": true }` or `{ "admit": false }`

- `true`: write `Artifact` conversations, `untrusted=true`, `authority=source_imported`. Set `archive_status=admitted`.
- `false`: no artifacts. `archive_status=discarded`.
- Idempotent if already decided: 409 or 200 no-op with current status (pick 409 in tests for double admit).
- Audit `import.archive_decided` in the same transaction.
- Does not accept or reject memory proposals.

## Non-goals on this contract

- Must not call OpenAI/Anthropic/Google.
- Must not run models.
- Must not apply PCA staging.
- Must not change grants.

## Errors

| Case | Status | Vault |
|------|--------|--------|
| Path missing | 400 | unchanged |
| Unrecognized layout | 400 | unchanged |
| Truncated ZIP | 400 | unchanged |
| PCA file posted here | 400 (tell person to use Stage archive) | unchanged |
| Vendor ZIP posted to `/v1/import/stage` | 400 (not a PCA) | unchanged |
