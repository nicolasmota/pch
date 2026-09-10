# Gauntlet bar — Speckit plan pack `specs/013-one-command-install/`

**Frozen:** 2026-09-07  
**Role:** this file is the critic's only quality bar. Do not move the bar to match the draft. Do not grade the author's intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/013-one-command-install/plan.md`
- `specs/013-one-command-install/research.md`
- `specs/013-one-command-install/data-model.md`
- `specs/013-one-command-install/contracts/` (all files)
- `specs/013-one-command-install/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar's existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to the spec**: a later `/speckit-tasks` agent can generate tasks that let a **stranger on a clean machine** paste one command, reach the guided setup with the full UI, pair an assistant from any directory, upgrade without losing the vault, and uninstall without the vault being deleted — with no API key, no account, no build step, no repository checkout, and nothing but loopback after the first fetch.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution 1.1.0, Hub 001–012 code, and this pack. They know the current facts: the built UI is git-ignored under `pcl-server/static/`, so nothing installed outside the checkout has an interface; the pairing catalog emits `uv run pcl-sdk mcp-bridge`, which only works inside the repo; the desktop shell already re-attaches to a running Hub, hunts a free port, and falls back to the browser; the vault key already falls back to a `0600` file when the OS keychain is missing; `pch.spec` is an empty PyInstaller skeleton. They are allergic to: a plan that says "publish to PyPI" with no release step that actually embeds the UI; recipes that still point at the repo; a new network listener or telemetry; plaintext or non-loopback defaults sneaking in through packaging; a "one command" that is really three; upgrade with no migration story; uninstall that touches `~/.pch`.

## Blind comparison (use when possible)

- **A** — this 013 plan pack
- **B** — `specs/006-dev-loop-automation/` plan pack as the named reference for repository-tooling work: numbered research with rejected alternatives, a data model with tables, a contract an implementer can test, a quickstart that is the demo, and a Constitution Check table with evidence per gate

If they pick B because A is thinner, hand-waves the release mechanics, or lists platforms without saying how each is verified, **A loses**. Density should match 006.

Also contrast, in one sentence each, against:

- The current README path (clone → `uv sync` → `npm ci && npm run build` → `make serve`) — that is the bug, not the design
- OpenMemory-style install (Docker + Postgres + Qdrant + `OPENAI_API_KEY`) — a plan that adds any daemon, database service, or key **fails** the thesis
- A native `.dmg`/`.msi`/AppImage installer — explicitly the next spec; a plan that quietly makes it this one **loses scope**

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **One command, literally** — The pack names the exact command a stranger pastes and the single prerequisite (with its own one-line install). A sequence disguised as one command, or a prerequisite that itself needs a build, **fails**.
2. **UI ships inside the release** — The pack states, with a named build/release step and a named location in the distributed artifact, how the built interface gets into what the person installs, given that `static/` is git-ignored. "The wheel includes static files" with no step that produces them **fails**. A test that opens `/` on a packaged install and asserts the SPA, not a 404 or JSON, is named.
3. **No key, no account, no build, no checkout** — Research shows each of the four is absent from the install and first run, and names the test or check that proves it. Calendar/Gmail credentials are correctly excluded as optional connectors.
4. **Offline after first fetch** — A named test runs the 001/004 read-edit-search-assemble scenarios against a packaged install with network disabled (or with an allow-list that admits only loopback) and passes. "Works offline" as a sentence **fails**.
5. **Protections survive packaging** — Constitution Check table cites **1.1.0** and shows: vault encrypted by default (the `plain=True` path in `create_app(hub=None)` is not reachable from the packaged entry point), loopback-only bind with refusal of any other host (named test), no telemetry, no new listener, `pcl-core` still free of network/plugin-host I/O. Any gate without evidence **fails**.
6. **Recipes from anywhere** — The pack names the catalog change: recipes emit commands that exist after the install (not `uv run … ` inside the repo), for Cursor, Hermes, and OpenClaw equally, and reflect the actual port. A named test asserts no recipe contains a repo-relative command. Cursor-only **fails**.
7. **Reuse, port, browser** — The pack states that existing `choose_port` / health re-attach / browser fallback are preserved by the packaged entry point and names the test. Re-implementing them differently, or dropping any, **fails**.
8. **Upgrade preserves 100%** — A named upgrade path (old release → new release on the same data dir) with schema migration ordering (migrate before serving) and a test that compares object, version, grant, connection, and audit counts and content hashes before/after. "Data is preserved" without a test **fails**.
9. **Uninstall never deletes the vault by default** — Named uninstall step; named test proving `~/.pch` (and key file if present) untouched; data-removal only behind a separate explicit confirmation; output names the data location. Silent deletion, or no uninstall story, **fails**.
10. **Existing vault reused** — Packaged Hub on a machine with a source-install `~/.pch` opens that vault; no second vault, no migration prompt. Named test.
11. **Three OSes, honestly** — Research states per OS (macOS, Linux, Windows native) how the install is verified in delivery (real run, container, or CI matrix), what the native-window story is, and where the browser fallback is expected. Listing three names with one test **fails**. Windows-via-WSL as the only Windows path **fails**.
12. **README is the product surface** — The pack includes the README install section as it will read (one command, one prerequisite, upgrade, uninstall) and moves contributor setup elsewhere; SC-008 (one screen, 30 seconds) has a check.
13. **No install-time side effects** — Install and first launch write nothing to the vault, pair nothing, send nothing. Named assertion. The coding agent implementing this is still not a Hub client.
14. **Success criteria → tests** — SC-001…SC-008 each map to a named test file or a named delivery check. Tests are written first and must fail before the satisfying code exists (`red_before_green`). SC-004 (recipes connect from a non-repo directory) and SC-005 (upgrade hash equality) are deterministic automated tests. SC-001 and SC-008 may be timed manual checks recorded as delivery evidence.
15. **Quickstart is the stranger's screen** — Quickstart starts on a clean machine (or container) with only the prerequisite, pastes the command, reaches setup, creates a project, disconnects the network, restarts, searches, generates a Hermes recipe from `/tmp`, connects. A quickstart that begins with `git clone` **fails**.
16. **Scope held** — No native installer, no login autostart, no cloud sync, no new daemon, no Personal Intelligence. Complexity Tracking is empty unless a real constitution exception is justified and marked for the person's decision.

## What "good" means here (inspectable)

Not: a `pyproject` tweak and a sentence about PyPI; a plan that still needs Node on the person's machine; "cross-platform" as an adjective.

Yes: the shortest release path that puts the built UI inside the distributed artifact, makes recipes point at installed commands, proves upgrade and uninstall on a real data directory, and leaves every protection exactly where 001–012 put it.

## What the critic inspects

The five artifact paths listed above, as they actually are. Counts, quotes, named files, named commands, named tests. Never a changelog. Never a summary written by a builder.

## Verdict format (mandatory)

```text
VERDICT: WIN | LOSE
Would hand to speckit-tasks: yes | no
Blind vs 006 plan pack: A wins | B wins
Biggest gap: <one sentence>
Failing criteria: <ids>
Evidence: <quotes / file-level notes>
Do not rewrite the pack. Do not propose a new bar.
```
