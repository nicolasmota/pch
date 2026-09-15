# The Hub UI

The SPA is a React 19 app served by `pch-server` on loopback. After `GET /v1/bootstrap` succeeds, the sidebar is the map of the product.

On small screens, **Menu** opens the same navigation.

## Start

| Route | Page | What it is for |
|---|---|---|
| `/` | Home | First-run vault, then the live situation package (`GET /v1/situation`) |
| `/sim` | Simulator | Dev only. Hidden in the nav unless `PCH_SIM_ENABLED=1` or `pch serve --sim`. Not a product agent. |

## Content

| Route | Page | What it is for |
|---|---|---|
| `/projects` | Projects | Projects, goals, commitments, decisions, operational phase, relations |
| `/memories` | Memories | Memories and preferences: create, supersede, retract |
| `/search` | Search | Full-text search, filtered by type / project / classification |

## Governance

| Route | Page | What it is for |
|---|---|---|
| `/review` | Review | Memory proposals from agents — accept or reject |
| `/conflicts` | Conflicts | Conflicting live facts; your resolution wins |
| `/approvals` | Approvals | External `ActionIntent`s waiting on you |
| `/access` | Access | Grants in plain language; revoke |
| `/audit` | Audit | Hash-chained event log, including contract issuance |

## Connections

| Route | Page | What it is for |
|---|---|---|
| `/connections` | Agents | Pairing links, recipes, connection revoke |
| `/plugins` | Plugins | Sideload, consent, enable / pause / sync. Link to Marketplace. |
| `/marketplace` | Marketplace | Signed catalog install. Route exists; **not** in the default nav. |
| `/connectors` | Connectors | Google OAuth, Calendar, Gmail |

## Data

| Route | Page | What it is for |
|---|---|---|
| `/handoff` | Handoff | `SharedState` put/get (TTL scratch between agents — not operational State) |
| `/export` | Export | Encrypted PCA |
| `/import` | Import | Stage/apply PCA and vendor batches |

## Mental model while clicking

1. **Home** is the current situation — what is in play, assembled from the vault.
2. **Projects** hold the operational frame (phase, step, intent).
3. **Memories** and **preferences** are the durable record. Agents propose; you confirm.
4. **Agents** + **Access** bound who may read or propose.
5. **Audit** is the proof of what happened. Marketplace and Simulator stay off the default path.

If a page is empty, you are probably looking at a grant-scoped assistant view in the API, not the owner UI. The SPA uses the owner token.
