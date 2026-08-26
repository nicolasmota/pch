# Quickstart: Temporal Validity

**Feature**: `specs/005-temporal-validity/`  
Record a dislike, change your mind, prove two agents see only the current like, and still read the old dislike as historical in the Hub.

Requires a running Hub (`make serve`) and an initialized owner session. Reuse the 004 trip seed if present; the reversal below is the E2 demo even without the trip.

## 1. Record the old truth

As owner, create a preference (or use the test helper that seeds one):

- `key` = `food.spicy`
- `value` = `dislike`
- no `valid_until` (current)

Optional: a semantic memory `"I don't like spicy food"` with no end either.

## 2. Change your mind (do not PATCH the value)

`POST /v1/preferences/{id}/supersede` with `{ "value": "like", "rationale": "I now like spicy food" }`.

Expect two objects: predecessor `value=dislike` with `valid_until` set; successor `value=like` with `valid_until` null. Both remain. Do **not** only PATCH `value` on the first id — that is a typo correction, not this demo.

## 3. Two agents, current package only

Pair two agents with the same grant (`profile.read` plus whatever the situation needs). Each calls `get_context_contract`:

```json
{ "purpose": "plan dinner this week" }
```

Expect: live preference `food.spicy` = like, with `valid_from`/`valid_until` in the item body. The dislike MUST NOT appear as a live preference. Both agents agree. Neither searches.

Optional: `{ "purpose": "plan dinner this week", "as_of": "<timestamp before supersede>" }` returns the dislike as live and the like as not yet current.

## 4. Hub still shows history

Open **Memories**. The dislike row is badged **historical** with its interval; the like row is **current**. Version "History" on a single object is still typo versions — it is not this list.

## 5. Isolation (same as 004, plus history)

A work-scoped agent must receive zero personal `food.spicy` items, including the historical dislike, and an omission note without titles or ids.

## Mistake (optional)

`POST /v1/preferences/{id}/retract` on a false statement. It MUST NOT appear as historical on Memories and MUST NOT appear in later contracts.
