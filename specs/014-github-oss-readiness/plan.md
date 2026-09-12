# Implementation Plan: GitHub Open-Source Readiness

**Branch**: `014-github-oss-readiness` | **Date**: 2026-09-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-github-oss-readiness/spec.md`

## Summary

Prepare this repository so the maintainer can flip GitHub visibility to **public** without a privacy incident or a confusing front door. Deliverables are repository tooling only: root **MIT** `LICENSE`, matching license metadata on workspace packages, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, GitHub issue/PR templates, tightened `.gitignore`, README sections that answer the four cold-visitor questions and link community docs, a **machine-checkable** secrets hygiene script (`scripts/check_secrets.py` + `make check-secrets`) with pytest coverage, and a PR CI workflow that runs existing `make lint`, `make test`, and `make check-secrets` gates. No Hub runtime, vault, connector, or VISION/ROADMAP product work. Switching the GitHub private→public toggle remains a manual maintainer action.

## Technical Context

**Language/Version**: Python 3.14 (uv workspace) for the secrets checker + pytest; Markdown/YAML for community health and GitHub templates; existing Makefile targets

**Primary Dependencies**: stdlib only for `scripts/check_secrets.py` (subprocess/`git ls-files`); existing `make test` / `make lint`; GitHub Actions (`actions/checkout`, `setup-uv`, `setup-node`) mirroring `release.yml` patterns

**Storage**: None. No vault tables. Artifacts are repo files only (`.github/`, root docs, `scripts/`, package `pyproject.toml` license fields)

**Testing**: pytest under `packages/pcl-sdk/tests/oss/` (or `scripts/` covered via sdk tests that invoke the script). SC-002 secrets check MUST fail red before ignore/docs satisfy it when a deny-list path is staged in a fixture. Delivery also records SC-001/SC-003/SC-005 checklist evidence.

**Target Platform**: Local repo checkout (Linux/WSL2/macOS/Windows contributors). Fully offline for the secrets check (`git ls-files` only). CI on `ubuntu-latest` for PRs.

**Project Type**: Repository tooling (docs + scripts + CI). Not a Hub feature surface.

**Performance Goals**: `make check-secrets` completes in under 5 seconds on this tree size.

**Constraints**: Constitution **1.1.0**; loopback/Hub unchanged; `pcl-core` untouched; coding agent is not a Hub client; no commit of vault DBs / `.env` / OAuth / pairing tokens / `.cursor/mcp.json`; no VISION/ROADMAP implementation; visibility flip is out of agent authority

**Scale/Scope**: One root license; five workspace `pyproject.toml` license fields (+ root workspace if applicable); four community docs; bug (+ optional feature) issue templates; one PR template; one secrets script; one optional `ci.yml`; README edits only for public front door — not a product redesign

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` **v1.1.0**. Gates:

| Gate | Status | Evidence |
|------|--------|----------|
| I. Person owns context; coding agent is not a Hub client | PASS | No pairing, no vault writes, no MCP; CONTRIBUTING restates coding-agent-is-not-client (D7) |
| II. Local-first, loopback-only; secrets not committed | PASS | Deny-list + `.gitignore` + SECURITY/CONTRIBUTING warnings; no new listener (D3, D8, FR-008/FR-010) |
| III. Least privilege / least context | PASS | No grant/assembly change |
| IV. Provenance / explicit control | PASS | Docs only; maintainer flips visibility manually (D9) |
| V. Imported content is data | PASS | CONTRIBUTING restates; templates forbid pasting imports/vault exports (D5) |
| `pcl-core` free of I/O from this feature | PASS | No `pcl-core` edits; script lives in `scripts/` + tests in `pcl-sdk` |
| Spec-not-vision; closed 001–003 | PASS | Repository tooling origin; no epic reopen; forbids VISION/ROADMAP implement (D1) |
| No Personal Intelligence / Personal Agency | PASS | Hygiene only |
| Tests fail before satisfying implementation | PASS | Secrets-check tests + contract name red-before-green for SC-002 |
| No new cloud dependency for core Hub | PASS | CI only runs test/lint; no OAuth vault in CI (D8) |

**Post-design re-check (Phase 1)**: PASS — community files and secrets checker are repo artifacts; Complexity Tracking empty; visibility flip documented as out-of-band.

## Project Structure

### Documentation (this feature)

```text
specs/014-github-oss-readiness/
├── plan.md                 # This file
├── research.md             # Phase 0
├── data-model.md           # Phase 1
├── quickstart.md           # Phase 1 — public-flip rehearsal
├── contracts/
│   └── oss-readiness.md    # File presence + secrets check + template warnings
├── PLAN-BAR.md             # Frozen before this pack (Gauntlet)
└── tasks.md                # Phase 2 (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
LICENSE                                 # NEW: MIT text
SECURITY.md                             # NEW
CONTRIBUTING.md                         # NEW
CODE_OF_CONDUCT.md                      # NEW
README.md                               # EDIT: four cold-visitor answers + community links
.gitignore                              # EDIT: align with full deny-list (incl. .pch/, .pch-sim/, pairing_token*)
scripts/check_secrets.py                # NEW: fail if deny-list paths are tracked (incl. Hub data dirs)
Makefile                                # EDIT: check-secrets target
.github/
├── ISSUE_TEMPLATE/
│   ├── bug.yml                         # NEW (or .md)
│   └── config.yml                      # NEW: disable blank issues optional
├── PULL_REQUEST_TEMPLATE.md            # NEW
└── workflows/
    ├── release.yml                     # UNCHANGED behavior
    └── ci.yml                          # NEW: PR → make lint && make test
packages/*/pyproject.toml               # EDIT: license = "MIT" (all workspace members)
apps/hub-desktop/pyproject.toml         # EDIT: license = "MIT"
packages/pcl-sdk/tests/oss/
├── test_secrets_check.py               # NEW: SC-002 (fail first)
└── test_community_files.py             # NEW: SC-003 / template warning presence (fail first)
```

**Structure Decision**: Keep automation in `scripts/` + Makefile (same pattern as `scripts/check_release.py`). Tests live in `pcl-sdk` so `make test` picks them up via existing `testpaths`. No `pcl-core`, `pcl-server` runtime, or `frontend` product changes.

## Success criteria → tests / delivery checks

| SC | Check (must fail first where automated) |
|----|----------------------------------------|
| SC-001 | Delivery checklist: four README questions answered (manual timed walk in quickstart) |
| SC-002 | `packages/pcl-sdk/tests/oss/test_secrets_check.py` + `make check-secrets` exit 0 on clean tree; fixture with tracked `.env` fails |
| SC-003 | `test_community_files.py::test_required_docs_exist` + README link assertions |
| SC-004 | Delivery: follow CONTRIBUTING → `make test` and `make lint` (evidence via `loop evidence`) |
| SC-005 | `test_community_files.py::test_templates_warn_against_secrets` |
| SC-006 | Delivery: diff scope review — no VISION/ROADMAP product implementation; no Hub runtime feature files |

## Complexity Tracking

> Empty — no constitution exceptions required.
