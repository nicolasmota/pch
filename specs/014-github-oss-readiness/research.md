# Research: GitHub Open-Source Readiness

**Feature**: `specs/014-github-oss-readiness/` · **Date**: 2026-09-12

No NEEDS CLARIFICATION markers remained in Technical Context. Decisions below resolve design choices against constitution 1.1.0, existing `.gitignore` / `release.yml` / README, GitHub community-health conventions, and `specs/006-dev-loop-automation/` as the repository-tooling density reference.

## D1 — Repository tooling, not a product epic

**Decision**: Treat this feature as **repository tooling** (constitution allowed origin). Deliver only docs, templates, ignore rules, license metadata, a secrets checker, and optional PR CI. Explicitly refuse tasks that implement Context Engine, temporal validity, situation/state/intent, graph, runtime adapters, eval harness productization, or any VISION/ROADMAP epic body.

**Rationale**: Spec FR-011/SC-006 and bar criterion 10. Opening the repo must not become a back door to product scope.

**Alternatives considered**: (a) Spawn under `--roadmap` next epic — rejected: readiness is not an era epic. (b) Bundle “while we’re public, finish E3” — rejected: constitution one-child-spec rule and bar scope hold.

## D2 — MIT license + SPDX on every publishable package

**Decision**: Add root `LICENSE` with the full MIT text, copyright line `Copyright (c) 2026 Personal Context Hub contributors` (or repository owner name if already established). Set `license = "MIT"` (PEP 621) on: `packages/pcl-core`, `packages/pcl-server`, `packages/pcl-sdk`, `packages/pca`, `apps/hub-desktop` pyproject files. Root workspace `pyproject.toml` may set license for documentation consistency even though `package = false`.

**Rationale**: Spec assumption MIT; FR-001/FR-002; cold visitors and package indexes both need an unambiguous grant. Matching SPDX across wheels avoids “root says MIT, wheel says nothing.”

**Alternatives considered**: (a) Apache-2.0 — viable but not the stated default; switching later is a maintainer choice before public flip. (b) License only at root — rejected: FR-002 and packaging hygiene. (c) Unlicense / proprietary “view only” — rejected: user asked to open the code.

## D3 — Machine-checkable secrets deny-list

**Decision**: Normative deny-list patterns (path basename or repo-relative match) for **tracked** files via `git ls-files`:

| Pattern | Meaning |
|---------|---------|
| `*.db`, `*.db-wal`, `*.db-shm` | Vault SQLite / SQLCipher |
| `*.pca` | PCA export blobs if ever dropped in-tree |
| `*.key` | Key material |
| `.env`, `.env.*` | Environment secrets |
| `google_oauth.json` | OAuth client file (any directory) |
| `.cursor/mcp.json` | Editor pairing/connection file |
| `pairing_token*`, `*pairing*token*` | Pairing token material filenames |
| `.vault/` path segments | Local vault dirs |
| `.pch/`, `.pch-sim/` path segments | Hub data dirs (default home vault / sim harness data if ever created under the repo) |

Script: `scripts/check_secrets.py` exits **1** if any tracked path matches, **0** otherwise; prints matching paths on failure. Makefile target `check-secrets`. Pytest covers: clean tree passes; temporary tracked fixture path fails; tracked path under `.pch/` or `.pch-sim/` fails.

**Rationale**: Bar criterion 3; SC-002; constitution II. Prose “don’t commit secrets” without a check fails the bar.

**Alternatives considered**: (a) gitleaks/trufflehog as hard dependency — rejected: heavier; can be suggested later; stdlib+git is enough for path deny-list. (b) Only `.gitignore` — rejected: force-add bypass; SC-002 needs tracked-file scan. (c) Pre-commit hook mandatory — optional later; not required for SC-002.

## D4 — Align `.gitignore` with the deny-list (close gaps)

**Decision**: Keep existing vault/env/oauth/mcp rules. Add any missing patterns from D3 (explicit `pairing_token*`, `.pch/`, `.pch-sim/`, and keep `.cursor/mcp.json`). The secrets checker (D3) and `.gitignore` MUST both cover Hub data dirs — ignore-only is not enough. Do not ignore legitimate test fixtures that only *mention* secrets in source (code files are fine).

**Rationale**: FR-008; bar criterion 4. Ignore rules and the checker must tell the same story.

**Alternatives considered**: (a) Ignore all of `.cursor/` — rejected: project skills under `.cursor/skills/` are intentional repo content. (b) Ignore `specs/**/RUN.json` — rejected: loop state is intentional Speckit artifact.

## D5 — GitHub templates that refuse vault dumps

**Decision**: Add `.github/ISSUE_TEMPLATE/bug.yml` (YAML form) with environment/repro fields and a required checkbox: “I have not pasted vault exports, `.env`, OAuth client files, pairing tokens, or `.cursor/mcp.json`.” Optional `feature.yml` with the same warning. Add `.github/PULL_REQUEST_TEMPLATE.md` requiring summary, test/lint evidence, and the same no-secrets confirmation. Optional `config.yml` with `blank_issues_enabled: true` but contact link to SECURITY for vulnerabilities.

**Rationale**: FR-006/FR-007/SC-005; bar criterion 6.

**Alternatives considered**: (a) Markdown-only issue templates — acceptable fallback; YAML forms preferred for required checkboxes. (b) No templates — rejected: spec P2.

## D6 — README is the public front door; CONTRIBUTING owns from-source

**Decision**: README structure (edit in place, keep one-command install from 013):

1. One-line product purpose  
2. Local-first / data on device / loopback-only (where data lives: `~/.pch`)  
3. Install (existing `uvx` path)  
4. License badge or “MIT — see LICENSE”  
5. Links: Contributing · Security · Code of Conduct · Vision (optional)  
6. Contributing-from-source section may shrink to a pointer to `CONTRIBUTING.md` to avoid duplication, or keep a short command block plus “details in CONTRIBUTING”

CONTRIBUTING includes: prerequisites (Python 3.14, uv, Node 22+ for UI), `make install` / `make test` / `make lint` / `make check-secrets`, PR expectations, must-not-commit list, loopback-only, imported-is-data, coding-agent-on-this-repo-is-not-a-Hub-client.

**Rationale**: SC-001/SC-003/SC-004; bar criteria 5 and 7.

**Alternatives considered**: (a) Duplicate full setup in README and CONTRIBUTING forever — rejected: drift. (b) Replace README with only contributor docs — rejected: install path is the product surface from 013.

## D7 — SECURITY and CODE_OF_CONDUCT defaults

**Decision**:

- `SECURITY.md`: supported versions = current `main` and latest release tag; report via GitHub Private Vulnerability Reporting / Security Advisories on this repo; do not file public issues with exploit detail before a fix; in scope = Hub software defects; out of scope = requesting another person’s vault contents, social engineering for pairing tokens.
- `CODE_OF_CONDUCT.md`: Contributor Covenant v2.1 plain adaptation; enforcement contact = repository maintainers via GitHub (issues marked conduct or maintainer contact).

**Rationale**: FR-003/FR-005; bar criterion 8; spec assumptions.

**Alternatives considered**: (a) Personal email only — optional additive later. (b) Skip CoC — rejected: FR-005 and public norms.

## D8 — PR CI wraps existing gates only

**Decision**: Add `.github/workflows/ci.yml` on `pull_request` and `push` to `main`: checkout, setup Node 22 + `frontend` build (needed for static embedding tests if any), setup uv, `make lint`, `make test`, `make check-secrets`. No OAuth secrets, no real `~/.pch` cache upload, `HOST=127.0.0.1` if any serve step appears (prefer none). Do not change `release.yml` semantics.

**Rationale**: FR-012; bar criterion 9. Public contributors need a signal beyond “trust me.”

**Alternatives considered**: (a) No PR CI — allowed by bar only if quickstart still proves SC-004 locally; weaker for public. (b) Full e2e Playwright in CI always — keep existing pytest defaults; Playwright stays as today (skip if not installed / existing markers). (c) Require Google OAuth in CI — rejected: constitution / FR-012.

## D9 — Visibility flip is out of band

**Decision**: Document in quickstart and CONTRIBUTING (maintainer note): after SC-001–SC-006 evidence is green, the human owner uses GitHub settings to set visibility public. Agents and CI do not flip visibility.

**Rationale**: Spec assumption; bar criterion 13; cloud agents lack org-admin guarantee and should not surprise the owner.

**Alternatives considered**: (a) `gh repo edit --visibility public` in delivery — rejected: irreversible social action; owner’s call.

## D10 — Complexity: smallest file set

**Decision**: New files listed in plan structure; tests under `packages/pcl-sdk/tests/oss/`; no new Python package; no frontend dependency for hygiene.

**Rationale**: Matches 006’s “smallest testable change” for repo DX without Hub surface.

**Alternatives considered**: (a) New `packages/pcl-oss` — rejected: overhead. (b) Only Markdown, zero tests — rejected: SC-002 / red-before-green.
