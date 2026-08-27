# Quickstart: Situation State and Intent

**Feature**: `specs/007-situation-state-intent/`
Set where the trip stands, prove two agents see it, prove SharedState is not the phase.

Requires `make serve` and the 004 trip seed (or create Project “Europe Trip”).

## 1. Set operational now (owner)

`PATCH /v1/projects/{id}` (owner token):

```json
{
  "operational_phase": "comparing_itineraries",
  "current_step": "rank two remaining itineraries",
  "situation_intent": "choose next itinerary"
}
```

Do **not** only `PUT /v1/state/trip.phase` or MCP `set_shared_state` with key `trip.phase` — that is SharedState (TTL handoff). The seed may already have that key; leave it.

Unknown phase string → 422.

## 2. Two agents, same package

Pair two agents with the same grant. Each calls `get_context_contract`:

```json
{ "purpose": "continue planning the trip" }
```

Expect both payloads:

- `situation.operational_phase` = `comparing_itineraries`
- `situation.situation_intent` = `choose next itinerary`
- `situation.current_step` = `rank two remaining itineraries`
- `situation.status` = `active` (ProjectStatus, not the phase)

If SharedState `trip.phase` exists, it may appear under `state[]` with a TTL; it is not `situation.operational_phase`.

## 3. Hub Projects page

Open **Projects**. The Europe Trip row shows phase, step, and intent as operational fields (badges/inputs), not as memory cards. Edit phase to `choosing_hotel` and save. Next `get_context_contract` uses `choosing_hotel`.

## 4. Agent propose (does not silent-write)

Agent calls MCP `propose_operational_state`:

```json
{
  "target_id": "prj_…",
  "operational_phase": "choosing_hotel",
  "situation_intent": "pick a hotel tonight"
}
```

Live phase stays whatever the owner last PATCHed until Review Queue **Accept**. **Reject** leaves live fields unchanged. This is not `propose_memory`.

## 5. Isolation

Work-scoped agent: `get_context_contract` for a work purpose returns **zero** personal-project `operational_phase` / `situation_intent`. Omission note has category + count, not the personal project title or id.

## 6. Unset still assembles

Clear the three fields (PATCH `null`). Next contract still assembles (E1). `operational_phase` is `null`. No phase invented from trip emails or memories.
