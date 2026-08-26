# Quickstart: Context Engine

**Feature**: `specs/004-context-engine/`  
Seed a trip vault, pair two agents, request a Context Contract, drop London, inspect Audit.

Requires a running Hub (`make serve`) and an initialized owner session.

## 1. Seed the trip

As owner, create the VISION demo objects (or use the test helper `seed_trip`):

- Project **Europe Trip** — 10-day travel for two, Amsterdam vs London
- Goal: plan the trip
- Preference `travel.budget` = budget-sensitive
- Memories: two travelers; Amsterdam live; London a candidate
- Decision: destination shortlist (both cities)
- Shared state `trip.phase` = comparing itineraries

## 2. Pair two agents with the same grant

1. Create two pairing links (Connections).
2. Pair each agent; grant `project.read`, `commitment.read`, `memory.retrieve`, `profile.read` scoped to the Europe Trip project.

## 3. Request context

Each agent calls MCP tool `get_context_contract`:

```json
{ "purpose": "continue planning the trip" }
```

HTTP equivalent: `POST /v1/mcp/tools/get_context_contract` with the connection bearer token.

Expect one contract: live goal, budget preference, traveler/Amsterdam memories, shortlist decision, citations on every item. Neither agent searches.

## 4. Drop London

As owner, create a Decision titled **Dropped London**, `chosen_option` = Amsterdam, `alternatives` = [London].

Call `get_context_contract` again with the same purpose. The new contract includes that decision; Amsterdam is the live choice.

## 5. Inspect Audit

Open **Audit**. Filter or scan for `context.contract` events. Each issuance shows agent, purpose, item refs, omission categories, and timestamp. `GET /v1/events?kind=context.contract` returns the same `extra` payload.

## Isolation check (optional)

Create a Work project and a second grant scoped only to it. A work agent requesting `"schedule around my travel"` must receive zero trip items and an omission note without titles or ids.
