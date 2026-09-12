# Data Model: GitHub Open-Source Readiness

**Feature**: `specs/014-github-oss-readiness/` · **Date**: 2026-09-12

No vault types. Entities are repository files and check results. Names below are normative for the secrets checker and community-health contract.

## CommunityHealthDoc

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `path` | str | yes | Repo-relative path |
| `kind` | str | yes | `license` \| `security` \| `contributing` \| `conduct` |
| `min_sections` | list[str] | yes | Headings or named content blocks that must appear |

### Required instances

| kind | path | min_sections |
|------|------|--------------|
| `license` | `LICENSE` | MIT permission grant; copyright line; warranty disclaimer |
| `security` | `SECURITY.md` | Supported versions; reporting channel; in/out of scope; no public exploit dump |
| `contributing` | `CONTRIBUTING.md` | Prerequisites; setup; test; lint; check-secrets; PR expectations; must-not-commit; loopback/local-first; imported-is-data; coding-agent-not-client |
| `conduct` | `CODE_OF_CONDUCT.md` | Standards; enforcement; contact |

**Invariants**:
- README links to each of `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` by path or conventional GitHub name.
- Package manifests that build wheels declare SPDX `MIT` matching `LICENSE`.

## ContributionTemplate

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `path` | str | yes | Under `.github/` |
| `kind` | str | yes | `bug_issue` \| `feature_issue` \| `pull_request` |
| `secrets_warning` | bool | yes | Must be `true` — explicit warning or required checkbox |

### Required instances

| kind | path | secrets_warning text must mention |
|------|------|-----------------------------------|
| `bug_issue` | `.github/ISSUE_TEMPLATE/bug.yml` | vault / `.env` / OAuth / pairing / `mcp.json` |
| `pull_request` | `.github/PULL_REQUEST_TEMPLATE.md` | same deny categories + test/lint evidence prompt |

Optional: `.github/ISSUE_TEMPLATE/feature.yml`, `.github/ISSUE_TEMPLATE/config.yml`.

## SecretsDenyPattern

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | str | yes | Stable id, e.g. `env_file` |
| `match` | str | yes | Glob or rule implemented by `check_secrets.py` |
| `gitignore_rule` | str | yes | Corresponding `.gitignore` entry |

### Normative set (D3)

| id | match (tracked paths) | gitignore_rule |
|----|----------------------|----------------|
| `vault_db` | `*.db` | `*.db` |
| `vault_wal` | `*.db-wal` | `*.db-wal` |
| `vault_shm` | `*.db-shm` | `*.db-shm` |
| `pca_export` | `*.pca` | `*.pca` |
| `key_file` | `*.key` | `*.key` |
| `env_file` | `.env` or basename `.env.*` | `.env`, `.env.*` |
| `google_oauth` | basename `google_oauth.json` | `google_oauth.json` |
| `cursor_mcp` | `.cursor/mcp.json` (path suffix) | `.cursor/mcp.json` |
| `pairing_token` | basename matches `pairing_token*` or `*pairing*token*` | `pairing_token*`, `*pairing*token*` |
| `vault_dir` | path contains `/.vault/` or starts `.vault/` | `.vault/` |
| `hub_data` | path contains `/.pch/` or starts `.pch/` (segment) | `.pch/` |
| `hub_sim_data` | path contains `/.pch-sim/` or starts `.pch-sim/` | `.pch-sim/` |

## SecretsCheckResult

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `ok` | bool | yes | `true` iff zero matches |
| `matches` | list[str] | yes | Tracked paths that hit a deny pattern |
| `exit_code` | int | yes | `0` if ok else `1` |

**Invariants**:
- `make check-secrets` and `scripts/check_secrets.py` produce the same pass/fail semantics.
- SC-002 delivery requires `ok=true` on the default branch tree.

## PackageLicenseMetadata

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `pyproject_path` | str | yes | Workspace member path |
| `license_spdx` | str | yes | Must equal `MIT` |

Required members: `packages/pcl-core/pyproject.toml`, `packages/pcl-server/pyproject.toml`, `packages/pcl-sdk/pyproject.toml`, `packages/pca/pyproject.toml`, `apps/hub-desktop/pyproject.toml`.

## ReadinessChecklist (delivery only)

| SC | Evidence artifact |
|----|-------------------|
| SC-001 | Quickstart timed README walk notes |
| SC-002 | `make check-secrets` exit 0 + pytest oss secrets tests |
| SC-003 | `test_community_files` + README links |
| SC-004 | `make test` / `make lint` per CONTRIBUTING |
| SC-005 | Template warning tests |
| SC-006 | Diff scope attestation (no VISION/ROADMAP product implement) |
