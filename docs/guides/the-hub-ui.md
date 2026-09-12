# The Hub UI

The SPA is a React 19 app served by `pcl-server` on loopback. After `GET /v1/bootstrap` succeeds, the sidebar is the map of the product.

On small screens, **Menu** opens the same navigation.

## Start

| Route | Page | What it is for |
|---|---|---|
| `/` | Home / Setup | First-run vault, encryption status, owner identity |
| `/sim` | Simulator | Development simulator (enabled on `make serve` / `pch serve --sim`). Not a product agent. |

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
| `/plugins` | Plugins | Sideload, consent, enable / pause / sync |
| `/marketplace` | Marketplace | Signed catalog install |
| `/connectors` | Connectors | Google OAuth, Calendar, Gmail |

## Data

| Route | Page | What it is for |
|---|---|---|
| `/handoff` | Handoff | `SharedState` put/get (TTL scratch between agents — not operational State) |
| `/export` | Export | Encrypted PCA |
| `/import` | Import | Stage/apply PCA and vendor batches |

## Mental model while clicking

1. **Projects** hold the situation (phase, step, intent).
2. **Memories** and **preferences** are the durable record. Agents propose; you confirm.
3. **Agents** + **Access** bound who may read or propose.
4. **Audit** is the proof of what happened.

If a page is empty, you are probably looking at a grant-scoped assistant view in the API, not the owner UI. The SPA uses the owner token.
