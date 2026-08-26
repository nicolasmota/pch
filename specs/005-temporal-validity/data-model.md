# Data Model: Temporal Validity

**Feature**: `specs/005-temporal-validity/` · **Date**: 2026-08-26

Interval fields are stored on existing vault documents (Preference, Memory). Request/response additions live in `packages/pcl-core/src/pcl_core/schema/contract.py`. Field names below are normative for REST and MCP.

## Preference (existing type, extended)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| *(all 001 fields)* | | | `key`, `value`, `rationale`, envelope metadata including `version`, `retention`, `created_at` |
| `valid_from` | str (ISO-8601 UTC) | no | Default: `created_at`. When this statement became true of the person. |
| `valid_until` | str \| null | no | Default: `null` (still current). Exclusive end (`[valid_from, valid_until)`). |
| `never_true` | bool | no | Default: `false`. Set by retract; excluded from current and historical truth. |

**Invariants**:
- If both ends present: `valid_from < valid_until` else validation error (FR-014).
- At most one row per `key` that is current *now* (`never_true` false, not tombstoned, interval contains now). Enforced on `create` and `supersede` (research D4).
- Change of mind does not delete or tombstone the predecessor.
- `retention` and `version` unchanged in meaning.

## Memory (existing type, extended)

Same interval fields and `never_true` as Preference. `tombstone` remains the 001 delete/FTS flag. Retract sets `never_true` **and** tombstones.

Episodic/procedural/summary memories may carry intervals; assembly still only treats them as live context when current at evaluation time. No new `MemoryKind`.

## ContextQuery (extended)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `purpose` | str | yes | Unchanged. |
| `subject_ref` | str \| null | no | Unchanged. |
| `max_items` | int \| null | no | Unchanged. |
| `as_of` | str \| null | no | ISO-8601 UTC instant. `null` → evaluation time = now. Invalid timestamp → 422. |

Requester identity still comes from the connection, not a field.

## ContextContract (unchanged sections; body delta)

No new top-level arrays. `assembled_at` remains the issuance clock (may differ from `as_of`).

**Invariants** (additive to 004):
- Every inlined Preference and Memory is current at evaluation time and `never_true` is false (FR-004).
- Historical Preference/Memory never appear in `preferences` / `memories` / `constraints` / `references` as live context.
- Two current Preferences with the same `key` at evaluation time → `conflicts` entry `preference_key_collision` (no winner).
- Grant filter still applies before temporal filter (historical out-of-scope items are omissions, not "historical in package").

## ContractItem.body (preference / memory)

Include `valid_from` and `valid_until` alongside existing keys (`key`/`value`/`rationale` or `statement`/`kind`). Do not add a `temporal: historical` item to live lists.

## Hub operations (not vault types)

### Supersede

Input: id of a current Preference or Memory + successor body (`value` or `statement`, optional rationale/classification).  
Output: `{ "predecessor": <closed row>, "successor": <new current row> }`.  
Effect: predecessor `valid_until = now`; successor `valid_from = now`, `valid_until = null`, same `key` (preference) or `subject_ref` (memory when present).

### Retract never-true

Input: id.  
Output: the retracted row (`never_true: true`, tombstoned).  
Effect: excluded from current and historical Hub lists and from assembly.

### Set interval

Existing `Hub.patch` may set `valid_from` / `valid_until` with FR-014 validation. Patching `value`/`statement` without `supersede` is an E1 correction of the same object (version bump) and **does not** create a historical truth.

## State transitions

```text
(create preference/memory) ──► current
                                │
              supersede ─────────┼──► predecessor: historical
                                 └──► successor: current

              patch interval ────► still same object; current/historical follows new interval

              retract_never_true ──► never_true + tombstone (not historical truth)

              delete (existing) ──► tombstone; not a change of mind
```

SharedState: no transition in this feature (TTL sweep unchanged).

## Relationships to existing schema

```text
Preference/Memory.valid_*     ── distinct from ──> UniversalMetadata.retention
                              ── distinct from ──> UniversalMetadata.version / object_versions
                              ── distinct from ──> SharedState.expires_at
ContextQuery.as_of            ── evaluation time for ──> assemble_contract
assemble_contract             ── live items ──> current Preference/Memory only
Hub.supersede                 ── writes two objects, one ledger tx
Hub.retract_never_true        ── never_true + tombstone
decide_proposal (accept)      ── may Hub.supersede matching current memory (D7)
Memories.tsx                  ── lists current + historical (not never_true)
PCA export                    ── includes interval fields; historical rows exported
```
