# Quickstart: Light Graph

**Feature**: `specs/008-light-graph/`
Record how the trip hangs together, prove two agents see it, prove FKs are not the graph.

Requires `make serve`, the trip project (E1 seed or create “Europe Trip”), a second project “Visa renewal”, and the person record from setup.

## 1. Record typed links (owner)

`POST /v1/relations`:

```json
{
  "from_id": "prj_trip",
  "to_id": "prj_visa",
  "relation_type": "depends_on"
}
```

```json
{
  "from_id": "prj_visa",
  "to_id": "per_…",
  "relation_type": "blocked_by"
}
```

Do **not** expect Goal `project_id` to show up as `owned_by`. Do **not** POST only a stakeholder string.

Self-link or unknown type → 422. Duplicate triple → 409.

## 2. Two agents, same package

Pair two agents with the same grant. Each calls `get_context_contract`:

```json
{ "purpose": "continue planning the trip" }
```

Expect both payloads:

- a `depends_on` from Europe Trip to Visa renewal
- a one-hop `blocked_by` from Visa renewal to the person
- `relations` is an array on the existing contract (no second tool)
- `situation.operational_phase` still behaves as in E3 if set

## 3. Hub Projects page

Open **Projects**. The Europe Trip card lists `depends_on → Visa renewal`. Remove it. Next `get_context_contract` has no that `depends_on`.

## 4. Agent propose (does not silent-write)

Agent calls MCP `propose_relation` with `related_to`. Live `relations` unchanged until Review Queue **Accept**. **Reject** leaves the live set unchanged.

## 5. Isolation

Work-scoped agent: zero personal relation types, endpoint ids, or titles. Omission notes: category + count only.

## 6. Unset still assembles

Delete all live relations. Next contract still assembles (E1/E3). `relations` is `[]`. Nothing invented from trip emails or “blocked by legal” memories.
