# Contract: Open-Source Readiness Surface

**Feature**: `specs/014-github-oss-readiness/`  
**Surface**: repository files + `scripts/check_secrets.py` + `make check-secrets`. No HTTP. No MCP. No Hub.

Implementer tests live in `packages/pcl-sdk/tests/oss/` and MUST be written first (fail before docs/script satisfy them).

## Required files (presence contract)

| Path | Must contain |
|------|----------------|
| `LICENSE` | MIT text; copyright; permission grant; warranty disclaimer |
| `SECURITY.md` | Supported versions; GitHub private vulnerability reporting; in/out of scope; forbid public exploit dumps and vault dumps |
| `CONTRIBUTING.md` | Prerequisites; `make install`; `make test`; `make lint`; `make check-secrets`; must-not-commit deny-list; loopback-only; imported-is-data; coding agent on this repo is not a Hub client |
| `CODE_OF_CONDUCT.md` | Behavioral standards; enforcement; maintainer contact |
| `.github/ISSUE_TEMPLATE/bug.yml` | Repro fields + explicit secrets warning / required checkbox |
| `.github/PULL_REQUEST_TEMPLATE.md` | Summary; test/lint evidence; no-secrets confirmation |
| `scripts/check_secrets.py` | Deny-list scan of `git ls-files` |
| `.github/workflows/ci.yml` | On PR (and push to main): frontend build as needed, `make lint`, `make test`, `make check-secrets` |

## Secrets checker CLI

```text
uv run python scripts/check_secrets.py
# or
make check-secrets
```

| Result | Exit | Stdout |
|--------|------|--------|
| No tracked deny-list paths | 0 | Optional one-line OK |
| One or more matches | 1 | Each matching path on its own line (or clearly listed) |

### Deny-list (normative)

Must flag tracked paths matching any of:

- `*.db`, `*.db-wal`, `*.db-shm`, `*.pca`, `*.key`
- basename `.env` or `.env.*`
- basename `google_oauth.json`
- path ending with / equal to `.cursor/mcp.json`
- basename matching `pairing_token*` or `*pairing*token*` (case-insensitive)
- path containing `.vault/` as a segment
- path containing `.pch/` or `.pch-sim/` as a segment (Hub data dirs / sim data dirs)

Must **not** flag ordinary source files that merely discuss secrets (e.g. `oauth.py`, test modules under `packages/*/tests/`).

## Package license metadata

Each of these files MUST include PEP 621 `license = "MIT"` (or equivalent table form that renders SPDX MIT):

- `packages/pcl-core/pyproject.toml`
- `packages/pcl-server/pyproject.toml`
- `packages/pcl-sdk/pyproject.toml`
- `packages/pca/pyproject.toml`
- `apps/hub-desktop/pyproject.toml`

## README front-door contract (SC-001)

`README.md` MUST make all of the following discoverable without opening other docs first (links may complete detail):

1. What the Hub is (one or two sentences)
2. Where data lives / local-first (e.g. `~/.pch`, nothing leaves the device by default)
3. How to install **or** run from source (at least one clear path)
4. License is MIT (text or link to `LICENSE`)
5. Links to `CONTRIBUTING.md` and `SECURITY.md` (and CoC)

## Template warning contract (SC-005)

Bug issue template and PR template MUST each include a human-readable warning whose text matches (case-insensitive) at least three of: `vault`, `.env`, `oauth`, `pairing`, `mcp.json` — or an explicit umbrella phrase naming “vault data, tokens, or OAuth client files.”

## Pytest mapping (fail first)

| Test module | Asserts |
|-------------|---------|
| `test_secrets_check.py` | Clean tree → exit 0; temp repo with tracked `.env` → exit 1; tracked `.pch/vault.db` or `.pch-sim/x` → exit 1; deny-list covers contract patterns |
| `test_community_files.py` | Required paths exist; README links; LICENSE starts with MIT markers; templates include secrets warning; pyprojects declare MIT; `ci.yml` exists and references `check-secrets` or `lint`/`test` |

## Out of contract

- Changing GitHub repository visibility
- Implementing VISION.md / ROADMAP.md product features
- New Hub listeners, vault schema, connectors, or plugins
- Auto-pairing the coding agent as a Hub client
