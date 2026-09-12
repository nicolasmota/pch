# Gauntlet bar — Speckit plan pack `specs/014-github-oss-readiness/`

**Frozen:** 2026-09-12  
**Role:** this file is the critic's only quality bar. Do not move the bar to match the draft. Do not grade the author's intent or the conversation that produced the files.

**Artifact under test (the pack, not a summary):**

- `specs/014-github-oss-readiness/plan.md`
- `specs/014-github-oss-readiness/research.md`
- `specs/014-github-oss-readiness/data-model.md`
- `specs/014-github-oss-readiness/contracts/` (all files)
- `specs/014-github-oss-readiness/quickstart.md`

The critic MUST read those files as they are on disk. Ignore `spec.md` except to check the pack does not contradict it. Ignore this bar's existence in the pack. Do not read agent transcripts, do not accept a builder recap, do not invent missing files.

The bar is **implementable and honest to the spec**: a later `/speckit-tasks` agent can generate tasks that make this repository **safe and clear to flip public on GitHub** — license, security, contributing, conduct, issue/PR templates, tightened ignore rules, README that answers four cold-visitor questions, a runnable secrets hygiene check with zero tracked deny-list hits, and optional PR CI that only wraps existing test/lint — **without** implementing VISION/ROADMAP product features or changing Hub runtime behavior.

## Who the reader is

A coding agent about to run `/speckit-tasks` then `/speckit-implement`. They have constitution **1.1.0**, Hub 001–013 code, and this pack. They know today's gaps: no root `LICENSE`, no `SECURITY.md` / `CONTRIBUTING.md` / `CODE_OF_CONDUCT.md`, no issue/PR templates, only `.github/workflows/release.yml`, README mixes install and contribute without community links, package manifests lack a license field. They are allergic to: rewriting the product thesis; "add some docs" without a secrets check; templates that invite vault dumps; CI that needs a real vault, cloud account, or non-loopback bind; quietly implementing E1–E6 features under an open-source excuse; treating this coding agent as a Hub client.

## Blind comparison (use when possible)

- **A** — this 014 plan pack
- **B** — `specs/006-dev-loop-automation/` plan pack as the named reference for **repository tooling**: numbered research with rejected alternatives, a data model with tables, a contract an implementer can test, a quickstart that *is* the demo, and a Constitution Check table with evidence per gate

If they pick B because A is thinner, hand-waves the secrets deny-list, or lists community files without saying what each must contain and how delivery proves it, **A loses**. Density should match 006.

Also contrast, in one sentence each, against:

- The current tree (private repo, release-only workflow, no LICENSE/community health) — that is the bug, not the design
- A "just make it public" checklist with no deny-list verification — a plan that ships docs but no SC-002 check **fails**
- A product epic disguised as hygiene (Context Engine, new connector, Personal Agency) — scope leak **loses**

If a tasks agent cannot tell this plan apart from those three after Summary + first research decisions, it **loses**.

## Pass / fail criteria (all must pass to WIN)

1. **License is real** — Pack names the root license file, the SPDX identifier (MIT per spec assumption), and every workspace package manifest field that must declare the same license. "Add a LICENSE someday" **fails**.
2. **Four community health docs** — Pack names exact paths for `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and root `LICENSE`, plus the minimum sections each must contain (reporting channel; setup/test/lint/must-not-commit; conduct + enforcement contact; license text). Missing any **fails**.
3. **Secrets deny-list is machine-checkable** — Pack lists the deny-list patterns from the spec/constitution (vault DBs + sidecars, `.env` / `.env.*`, `google_oauth.json`, pairing-token material, `.cursor/mcp.json`, Hub data dirs) and names the script or documented command that fails if any are tracked. A prose-only "be careful" **fails**.
4. **`.gitignore` matches the deny-list** — Research or plan maps each deny-list pattern to an ignore rule; gaps are closed. Ignore rules without the check in (3) still **fail** criterion 3.
5. **README answers SC-001** — Pack includes the README outline (or exact section structure) that answers: what it is, where data lives, install / from-source, license — and links to contributing + security. A README that only says `make install` **fails**.
6. **Templates warn against secrets** — Issue and PR templates are named with paths under `.github/`; each contains an explicit warning not to paste vault data, tokens, or OAuth client files. Templates that ask for "logs" without that warning **fail**.
7. **Contributing is the from-source path** — CONTRIBUTING names prerequisites, `make install` / test / lint (or documented equivalents), PR expectations, loopback-only / local-first / imported-is-data, and that a coding agent on this repo is not a Hub client by default.
8. **Security scope is Hub software, not strangers' vaults** — SECURITY states private reporting (GitHub advisory flow), in-scope = Hub software defects, out-of-scope = demanding someone else's vault contents in public issues.
9. **Optional PR CI is gates-only** — If added, pack names the workflow file and that it runs only existing documented test and/or lint; no cloud account, no real `~/.pch`, no non-loopback bind. A CI that "boots the Hub against production OAuth" **fails**. Absence of PR CI is allowed only if quickstart/delivery still proves SC-004 via local commands — and the pack says so explicitly.
10. **No product scope leak** — Constitution Check cites **1.1.0**. Pack forbids implementing VISION/ROADMAP features, new listeners, Personal Agency/Intelligence, vault format changes, or connector behavior changes. Any plan task that edits Context Engine / situation / graph code for this feature **fails**.
11. **Success criteria → checks** — SC-001…SC-006 each map to a named test, script, or delivery checklist item. SC-002 MUST be an automated secrets hygiene check that fails red before ignore/docs are fixed. `red_before_green` applies to that check and to any new CI workflow assertions.
12. **Quickstart is the public-flip rehearsal** — Quickstart starts from a clean clone mindset: run secrets check (expect fail or pass per stage), add community files, re-run check (zero hits), walk README four questions, open templates, run `make test` and `make lint` per CONTRIBUTING. A quickstart that begins by implementing a roadmap epic **fails**.
13. **Visibility flip stays manual** — Pack states that switching GitHub from private to public is a maintainer action outside automated implement; deliverables stop at readiness. A plan that requires the agent to change org visibility settings **fails** (out of agent authority / not the feature).
14. **Shareable to tasks** — Density matches 006: numbered research with rejected alternatives, tables in the data model, a contract an implementer can test (community file presence + secrets check + template warnings), Constitution Check with evidence columns. A bullet list of slogans with no contract **fails**.

## What "good" means here (inspectable)

Not: a vague "add open-source docs"; a LICENSE without package metadata; templates that collect personal context; CI that needs secrets.

Yes: the smallest repository-tooling change that lets the maintainer flip visibility knowing SC-001–SC-006 are evidenced, with constitution 1.1.0 protections restated for contributors and zero tracked deny-list files.

## What the critic inspects

The five artifact paths listed above, as they actually are. Counts, quotes, named files, named commands, named checks. Never a changelog. Never a summary written by a builder.

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
