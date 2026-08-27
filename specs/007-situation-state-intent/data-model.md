# Data Model: Situation State and Intent

**Feature**: `specs/007-situation-state-intent/` · **Date**: 2026-08-26

Field semantics here are normative for persistence and assembly. Wire shapes live in [contracts/operational-state.md](contracts/operational-state.md).

## OperationalPhase (enum, not a vault type)

| Value | Roadmap example | Notes |
|-------|-----------------|-------|
| `planning` | Planning | Kickoff; not ProjectStatus `active` |
| `comparing_itineraries` | Comparing itineraries | SC-001 / quickstart value |
| `waiting_for_approval` | Waiting for approval | Not ActionIntent; the person is waiting, not approving an outbound act |
| `choosing_hotel` | Choosing hotel | |
| `other` | unnamed | Require `current_step` in UI copy; schema does not require it |

## Project (extended)

Existing vault type `project`. No new type.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| *(existing)* | | | `title`, `status` (`ProjectStatus`: `active\|paused\|done\|archived`), `charter`, `stakeholders` |
| `operational_phase` | OperationalPhase \| null | no | Default `null`. Not ProjectStatus. Not SharedState. |
| `current_step` | str \| null | no | Max 200. Finer grain than phase. |
| `situation_intent` | str \| null | no | Max 200. Not ActionIntent, not `Goal.title`. |

**Invariants**:

- Setting these fields does not create a Memory.
- SharedState TTL does not clear them.
- PATCH of these fields bumps object version as any other `Hub.patch`.
- `status` and `operational_phase` may be set independently (e.g. `status=active` + `operational_phase=comparing_itineraries`).

## Goal (extended)

Existing vault type `goal`. Same three optional fields, same max lengths, same null default.

**Overlay rule** (assembly): when `ContextQuery.subject_ref` is this Goal’s id, `current_step` and `situation_intent` overlay Project values if the Goal fields are non-null. `operational_phase` overlays if the Goal phase is non-null; otherwise Project phase is used. When `subject_ref` is the Project (or omitted and the Project is selected), Goal fields are ignored.

## SituationRef (extended)

Ephemeral. Not a vault object. Built in `pcl_core/retrieval/contract.py`.

| Field | Type | Notes |
|-------|------|-------|
| `project_id` | str | Unchanged (anchor project id even when subject is a Goal) |
| `title` | str | Unchanged (project title) |
| `status` | str | **ProjectStatus**, not operational phase |
| `operational_phase` | str \| null | Copied; `null` if unset |
| `current_step` | str \| null | Copied / overlaid |
| `situation_intent` | str \| null | Copied / overlaid |

`candidates[]` uses the same shape. Candidate refs for an ambiguous purpose copy fields from each candidate Project (still in-scope only).

## OperationalProposal (vault type `operational_proposal`)

New vault object, same persistence as `MemoryProposal` (not a SQLite table). Exported from `pcl_core/schema/proposal.py`.

| Field | Type | Notes |
|-------|------|-------|
| `id` | str | Assigned on create |
| `type` | literal `operational_proposal` | Discriminator vs memory proposals |
| `target_id` | str | Project or Goal id |
| `operational_phase` | str \| null | Proposed |
| `current_step` | str \| null | Proposed |
| `situation_intent` | str \| null | Proposed |
| `status` | ProposalStatus | `pending` / `accepted` / `rejected` (reuse existing enum) |
| `submitted_by` | str | Connection actor |
| `created_at` | str | ISO-8601 |

**Accept**: `Hub.patch(target_id, {fields that were non-null on the proposal})`; proposal status → `accepted`.
**Reject**: proposal status → `rejected`; live Project/Goal unchanged.
**Supersede**: a newer pending proposal for the same `target_id` does not auto-supersede; owner resolves each. (Keep v1 simple; no silent drop.)

## Not this feature

| Object | Why it is not E3 |
|--------|------------------|
| SharedState (`key`, `ttl_seconds`, `expires_at`) | TTL handoff. Seed key `trip.phase` remains. Lives in contract `state[]`. |
| ActionIntent | Approval to act externally. Unchanged tools: `request_approval`, `propose_action`, `check_action_status`. |
| ProjectStatus / GoalStatus | Object lifecycle. `situation.status` stays ProjectStatus. |
| Memory | Durable information. Operational now is not a memory kind. |
