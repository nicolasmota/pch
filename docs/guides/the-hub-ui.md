# The Hub UI

The SPA is a React 19 app served by `pch-server` on loopback. After `GET /v1/bootstrap` succeeds, the sidebar is the map of the product.

Default nav is three verbs: **Home**, **Agents**, **Review**. Everything else is **Advanced** (collapsed) or a deep link. On small screens, **Menu** opens the same navigation.

## Default

| Route | Page | What it is for |
|---|---|---|
| `/` | Home | First-run vault, then the live situation (`GET /v1/situation`) |
| `/connections` | Agents | Pairing, grant presets, recipes, grant list, revoke |
| `/review` | Review | Memory / operational / relation proposals; conflicts and outbound approvals when they exist |

## Advanced

Collapsed until you open it. Simulator appears here only when `PCH_SIM_ENABLED=1` or `pch serve --sim`.

| Route | Page | What it is for |
|---|---|---|
| `/search` | Search | Full-text search, filtered by type / project / classification |
| `/projects` | Projects | Projects, goals, commitments, decisions, operational phase, relations |
| `/memories` | Memories | Memories and preferences: create, supersede, retract |
| `/plugins` | Plugins | Calendar, Gmail, RSS; sideload, consent, enable / pause / sync |
| `/export` | Export | Encrypted PCA |
| `/import` | Import | Stage/apply PCA and vendor batches |
| `/audit` | Audit | Hash-chained event log, including contract issuance |
| `/sim` | Simulator | Dev only. Not a product agent. |

## Deep links (not in the default nav)

| Route | Page | What it is for |
|---|---|---|
| `/access` | Access | Same grant list as Agents; kept for bookmarks |
| `/handoff` | Handoff | `SharedState` put/get (TTL scratch between agents — not operational State) |
| `/conflicts` | Conflicts | Standalone conflict list (also on Review when non-empty) |
| `/approvals` | Approvals | Standalone outbound approvals (also on Review when non-empty) |
| `/marketplace` | Marketplace | Signed catalog install. Route exists; **not** in the default nav. |
| `/connectors` | Connectors | Leftover first-party Google accounts. Day-to-day import is **Plugins**. |

## Mental model while clicking

1. **Home** is the current situation — what is in play, assembled from the vault.
2. **Agents** pairs a runtime and grants a slice.
3. **Review** is where you confirm what an agent proposed.
4. **Advanced** is the rest of the console (projects, memories, import, audit).

If a page is empty, you are probably looking at a grant-scoped assistant view in the API, not the owner UI. The SPA uses the owner token.
