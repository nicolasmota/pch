# Quickstart: empty vault, vendor file, export that others can read

This is the demo. It does not start with a profile form. It does not `POST /v1/import/stage` on a vendor ZIP.

Use a throwaway vault (pytest tmp dir or a fresh `PCH_DATA` in tests). Do not import into the implementer's real `~/.pch`.

## 1. Clean Hub

Start the Hub against an empty encrypted vault (existing test client / `create_app` with tmp `data_dir`). Confirm search for a fixture statement returns nothing.

## 2. Import Claude fixture (no passphrase)

Path: `packages/pca/tests/fixtures/vendor/claude/` (or the zip of that folder).

```text
POST /v1/import/vendor  { "path": "<fixture>" }
```

Expect: `source=claude`, `enqueued` equals `memories.json` length, `archive_status=pending`, **zero** rows with `type=memory`.

`GET /v1/memories/proposals?status=pending` lists those statements. Review UI would show them.

## 3. Chats are not memories

The Claude `conversations.json` contains an instruction-like user turn. Expect **no** proposal whose `statement` is that turn. `GET` grants: unchanged from empty-vault defaults.

## 4. Accept one

`POST /v1/memories/proposals/{id}/accept`

Search finds that one statement. Other imported statements still absent from canonical memory.

## 5. Archive

Discard: `POST /v1/import/vendor/{id}/archive { "admit": false }` → `type=artifact` count still 0.

(On a second clean run) Admit: `admit: true` → conversation artifacts exist, each `untrusted=true`. Situation package for a generic purpose does not treat artifact body as a grant or as live memory.

## 6. PAM / UMP files

`POST /v1/import/vendor` on `fixtures/vendor/pam/` and `fixtures/vendor/ump/` similarly enqueues proposals, not canonical rows.

Unrecognized `fixtures/vendor/unknown/` returns 400, vault unchanged.

## 7. Export speaks PAM and UMP

With the one accepted memory (and optionally a preference created only if a test needs a second object — prefer using only the accepted import):

```text
POST /v1/export  { "passphrase": "secret", "filters": {} }
```

Decrypt the `.pca` with the existing age/test helper. Zip contains:

- `objects/memories.jsonl` (the accepted memory)
- `interoperability/pam/memory-store.json` — validates against vendored PAM schema; `exported_by` starts with `personal-context-hub/`
- `interoperability/ump/memories.ump.json` — array with `ump=0.1` and matching statement

Pending proposals and grants are absent from all three.

Re-import the `.pca` through **`/v1/import/stage`**, not `/v1/import/vendor`. Round-trip of Hub objects still holds (existing contract test).

## 8. Re-import vendor fixture

`POST /v1/import/vendor` again on the same Claude folder. Expect `skipped >= 1` for the already accepted item; no second canonical copy (SC-008).
