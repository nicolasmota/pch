# Data Model: Runtime Adapters

**Feature**: `specs/009-runtime-adapters/` · **Date**: 2026-08-26

No new vault entity. Pairing, grants, connections, and the situation package are unchanged (002 + E1–E4). This feature adds **catalog rows** and **recipe documents** (ephemeral).

## Catalog entry (existing shape)

| Field | Meaning |
|-------|---------|
| `id` | Stable id: `cursor`, `hermes`, `openclaw`, plus 002’s other ids |
| `name` | Person-visible name |
| `supported` | If false, picker disables and recipe POST 422s |
| `notes` | Short hint (WSL, paste path) |

**Validation**: `hermes` and `openclaw` MUST be present and `supported: true`. `cursor` remains supported. Demo-agent is **not** a catalog id.

## Recipe document (ephemeral POST response)

| Field | Meaning |
|-------|---------|
| `assistant` | Catalog id |
| `format` | `cursor-mcp-json` \| `hermes-yaml` \| `openclaw-json` |
| `instructions` | Plain language: which file, which key, reload |
| `snippet` | Native config fragment (see contracts) |

**Validation**: snippet MUST include stdio `command`/`args` running `pcl-sdk mcp-bridge` and `env.PCH_TOKEN` + `env.PCH_BASE` with host `127.0.0.1`. MUST NOT introduce a second protocol field.

Unknown or unsupported `assistant` → 422. No recipe row is stored in the vault; audit event `connection.recipe_issued` is enough.

## Connection / grant (unchanged)

Pairing codes, tokens, grants, revoke stay 002. Switching runtime = new connection + grant (or reuse). Revoke MUST NOT cascade-delete projects, memories, relations, or operational fields.

## Situation package (unchanged)

`get_context_contract` response is the E1 contract (E2–E4 fields when set). Adapters **consume** it. They do not own it. No runtime-specific projection.

## State transitions

```text
catalog list → person picks hermes|openclaw → POST recipe
  → pending paste (outside Hub)
  → pair + grant (existing)
  → get_context_contract (existing)
revoke connection → subsequent contract calls fail for that token
                 → Hub objects remain
```

No `relation_proposal`-style queue for recipes. The person copies; the Hub does not install into `~/.hermes` or `~/.openclaw` (those trees are the runtime’s, and a coding agent is not a Hub client).
