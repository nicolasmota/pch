# Data Model: Light Graph

**Feature**: `specs/008-light-graph/` · **Date**: 2026-08-26

Field semantics here are normative. Wire shapes live in [contracts/relations.md](contracts/relations.md).

## RelationType (enum, not a vault type)

| Value | Meaning | Non-example |
|-------|---------|-------------|
| `owned_by` | Directed ownership/accountability link | Goal `project_id` (membership FK) |
| `depends_on` | Near end cannot proceed without far end | E3 phase `waiting_for_approval` |
| `blocked_by` | Far end is blocking the near end | ActionIntent (approval to act) |
| `related_to` | Weak typed association | Project `stakeholders` string list |

## Relation (vault type `relation`)

| Field | Type | Notes |
|-------|------|-------|
| `from_id` | str | Existing vault object id |
| `to_id` | str | Existing vault object id; must differ from `from_id` |
| `relation_type` | RelationType | Closed set of four |
| `status` | `live` \| `removed` | Remove is a status change (or tombstone); not presented as live |

**Invariants**:

- Self-link forbidden.
- Duplicate live (from, to, type) forbidden (409).
- Opposite direction is a different relation.
- Does not create a Memory. SharedState TTL does not clear it.
- FKs are not rewritten when a Relation is created.

## RelationRef (ephemeral, on ContextContract)

| Field | Type | Notes |
|-------|------|-------|
| `id` | str | Relation object id |
| `relation_type` | str | |
| `from` | ItemRef | id, type, summary |
| `to` | ItemRef | id, type, summary |

Included only when both ends ALLOW. Sorted by (`relation_type`, `id`) for determinism.

## RelationProposal (vault type `relation_proposal`)

| Field | Type | Notes |
|-------|------|-------|
| `from_id` | str | |
| `to_id` | str | |
| `relation_type` | str | |
| `status` | ProposalStatus | pending / accepted / rejected |
| `submitted_by` | str | |

Accept → create live Relation. Reject → no live row.

## ContextContract (extended)

Existing fields unchanged (including E3 SituationRef). Additive:

| Field | Type | Notes |
|-------|------|-------|
| `relations` | list[RelationRef] | Required key; empty list when none |

## Not this feature

| Object | Why it is not E4 |
|--------|------------------|
| Goal/Memory `project_id` | Membership FK. Named non-example. |
| Project `stakeholders` | String list. Named non-example. |
| E3 operational fields | Phase/intent, not graph. |
| MemoryKind.relationship | Durable memory about a relationship, not an edge. |
| Graph database / A2A / social graph | Out of scope. |
