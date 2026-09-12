# Gauntlet bar — Speckit plan pack `specs/014-vendor-memory-portability/`

**Frozen:** 2026-09-10  
**Role:** this file is the critic's only quality bar. Do not move the bar to match the draft. Do not grade the author's intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/014-vendor-memory-portability/plan.md`
- `specs/014-vendor-memory-portability/research.md`
- `specs/014-vendor-memory-portability/data-model.md`
- `specs/014-vendor-memory-portability/contracts/` (all files)
- `specs/014-vendor-memory-portability/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar's existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to the spec**: a later `/speckit-tasks` agent can generate tasks that let a **stranger with a vendor ZIP** enqueue years of prior context as proposals (never live truth), keep chats as untrusted data (never scraped into memory, never instructions), and export a PCA that a PAM reader and a UMP portable-record reader can open without this Hub. Not a chat scraper. Not Personal Intelligence. Not reopening 001 as an epic.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution **1.1.0**, Hub 001–013 code (`propose_memory`, review queue, PCA `packages/pca`, `POST /v1/import/stage` for Hub archives, untrusted artifacts, `ArtifactKind.CONVERSATION`), and this pack. They know: owner cannot call `propose_memory` (actor must not be owner); PCA import writes staged records into the vault on apply; ChatGPT/Claude/Gemini layouts are those PAM documents; PAM v1 requires `memory-store.json`; UMP L0 is `*.ump.json` / `*.ump.md` files, not a Hub-hosted UMP server. They are allergic to: LLM or heuristic harvesting of facts from chat turns; treating vendor ZIP apply like PCA apply; exporting unaccepted proposals as the person's memory; a new network listener or converter-as-a-service; `pcl-core` growing HTTP or plugin-host I/O; shipping only PAM or only UMP when the spec requires both; Copilot/Grok scope creep.

## Blind comparison (use when possible)

- **A** — this 014 plan pack
- **B** — `specs/001-personal-context-hub/` plan pack, especially `contracts/pca-format.md` and the import-quarantine rules: staging, integrity, exclusions, authority never upgraded by import, untrusted artifacts

If they pick B because A is thinner, waves at "parse the ZIP", has no fixture contract per vendor, or cannot name how PAM/UMP projections sit inside PCA without breaking the existing archive contract, **A loses**. Density should match 001's portability slice: numbered research with rejected alternatives, tables in the data model, a contract an implementer can test against fixtures, a quickstart that *is* the demo.

Also contrast, in one sentence each, against:

- PCA import as shipped (`/v1/import/stage` then apply into canonical tables) — that path is for the person's own Hub archive, not vendor files; a plan that dumps ChatGPT into apply **fails**
- Official PAM SDK converters that LLM-extract memories from chats ("memory prompt") — that is chat-transcript scraping; a plan that shells out to it or reimplements the prompt **fails**
- A Hub-hosted UMP HTTP/MCP runtime (L1+) — out of scope; file projections only; inventing a memory protocol **fails**

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **Three vendor layouts + two interchange files** — Research names the on-disk markers that distinguish ChatGPT, Claude, Gemini Takeout, PAM `memory-store.json`, and UMP portable records, and names the fixture files tests will use. "Detect ZIP" without per-source markers **fails**. Copilot/Grok as required work **fails** scope.
2. **Proposals, not truth** — Structured memory-like objects enqueue via the existing memory-proposal path (non-owner actor). 0 canonical memories before accept. Named test per SC-001. A plan that `store.put`s memories on import **fails**.
3. **Actor and authority** — Pack names the importer actor(s) (not `owner`), that `authority` stays `proposed` until accept/edit-then-accept, and that accept must not erase vendor provenance. Owner-as-importer **fails**.
4. **No scrape** — Explicit rejected alternative: no LLM, no "memory prompt", no heuristic fact harvest from chat turns. Named test (SC-002) that a fixture full of chats and zero structured memories yields 0 memory proposals from those chats. Any extractor that reads `chat_messages` / mapping trees into `Memory.statement` **fails**.
5. **Conversation archive is a separate confirm** — One batch admission (admit untrusted artifacts vs discard). Not implicit with proposal enqueue. Declining still leaves Story 1 proposals. Named test.
6. **Imported is data** — Conversation artifacts `untrusted=true`; instruction payloads cannot expand grants, auto-accept, or fire actions. Named `forbidden_context` / untrusted test. "We'll wrap JSON" without a grant-unchanged assertion **fails**.
7. **Dedup** — Re-import of the same fixture does not create a second live copy of pending or accepted items (SC-008). Pack names the identity key (vendor + original id / content hash). "Skip duplicates" with no key **fails**.
8. **PCA still PCA** — Existing archive contract remains: age envelope, integrity hashes, exclusions (secrets, grants, pairing, SharedState), filters, lineage. Hub PCA still uses stage/apply, not the vendor-proposal path. Named regression (SC-006).
9. **PCA speaks PAM and UMP** — The same export includes a PAM v1 memory-store projection **and** a UMP L0 portable-record projection of the same filter-respecting exported objects. Paths inside the archive are named. Empty vault → valid empty projections, not missing files. Only-PAM or only-UMP **fails**.
10. **Foreign readers** — Pack names how SC-005 is proven without this Hub: validate PAM projection against the published PAM v1 memory-store schema (vendored or fetched-at-dev, not a runtime network call); validate UMP records against the published UMP portable-record shape. "Looks like JSON" **fails**.
11. **Export hygiene** — Unaccepted proposals, credentials, grants, pairing, plugin secrets absent from PCA, PAM, and UMP (SC-007). Filters apply identically to all three (SC-004). Named scans.
12. **Surface** — Person can choose a local vendor/PAM/UMP file without a PCA passphrase. Unrecognized layout fails closed with a plain-language error. Loopback only. Offline once the file is on disk. No vendor API calls. Named UI or CLI path, not "add an endpoint someday".
13. **Package boundaries** — Detection and mapping live where PCA already lives (`packages/pca` depending on `pcl-core` only). `pcl-core` gains no network, plugin-host, or server imports. HTTP remains loopback in `pcl-server`. Constitution Check table cites **1.1.0** with evidence per gate. Missing table **fails**.
14. **Success criteria → tests** — SC-001…SC-008 each map to a named test file or named delivery check. Tests fail before satisfying code (`red_before_green`). SC-001, SC-002, SC-004, SC-007, SC-008 are deterministic automated tests. Fixture exports are synthetic and committed (no person's real vault, no live vendor download in CI).
15. **Quickstart is the empty-vault demo** — Clean Hub → import Claude (or ChatGPT) fixture ZIP → see pending proposals, zero live memories → accept one → search finds it → decline or admit conversation archive as untrusted → export → PAM and UMP projections validate. A quickstart that starts with filling a profile form, or that applies a vendor ZIP through PCA staging, **fails**.
16. **Scope held** — No chat scraper, no UMP server, no PAM-as-database, no Copilot/Grok, no Personal Intelligence/Agency, no new listener, no pairing the implementing agent. Complexity Tracking is empty unless a real constitution exception is justified and marked `blocked_on_person`.

## What "good" means here (inspectable)

Not: a plugin that "ingests ChatGPT"; wrapping PCA apply; shelling out to `pam convert`; an essay about portability.

Yes: named detect → map structured objects to `propose_memory` → separate untrusted archive confirm → PCA zip that a PAM schema validator and a UMP record validator accept, with fixtures and tests named before code.

## What the critic inspects

The five artifact paths listed above, as they actually are. Counts, quotes, named files, named fixtures, named tests. Never a changelog. Never a summary written by a builder.

## Verdict format (mandatory)

```text
VERDICT: WIN | LOSE
Would hand to speckit-tasks: yes | no
Blind vs 001 plan pack (portability slice): A wins | B wins
Biggest gap: <one sentence>
Failing criteria: <ids>
Evidence: <quotes / file-level notes>
Do not rewrite the pack. Do not propose a new bar.
```
