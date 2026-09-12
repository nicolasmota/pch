# Quickstart: GitHub Open-Source Readiness

**Feature**: `specs/014-github-oss-readiness/`  
Public-flip **rehearsal**. Does not flip GitHub visibility. Does not pair a Hub client.

From the repo root, with the workspace installed (`uv sync` / `make install` as needed for tests).

## 0. Baseline (expect gaps before implement)

```bash
test -f LICENSE || echo "missing LICENSE"
test -f SECURITY.md || echo "missing SECURITY"
test -f CONTRIBUTING.md || echo "missing CONTRIBUTING"
test -f CODE_OF_CONDUCT.md || echo "missing CODE_OF_CONDUCT"
ls .github/ISSUE_TEMPLATE 2>/dev/null || echo "missing issue templates"
ls .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null || echo "missing PR template"
```

After the secrets script exists:

```bash
make check-secrets
# Before ignore/docs are fixed, a deliberately staged deny-list file in a test fixture must fail red
# (including a path under .pch/ or .pch-sim/).
```

## 1. Red before green (SC-002)

```bash
uv run pytest packages/pcl-sdk/tests/oss/test_secrets_check.py -v
```

Expect: tests written first **fail** until `scripts/check_secrets.py` exists and `.gitignore` aligns. Then they pass on the clean tree.

## 2. Community files + templates (SC-003, SC-005)

```bash
uv run pytest packages/pcl-sdk/tests/oss/test_community_files.py -v
```

Expect: required docs present; README links; bug + PR templates warn against secrets; package `license = "MIT"`.

## 3. Cold-visitor README walk (SC-001)

Open `README.md` only. Time yourself (target under five minutes). Write answers:

1. What is this?
2. Where does my data live?
3. How do I install or run from source?
4. What is the license?

All four must be answerable. Confirm links to Contributing and Security.

## 4. Contributor path (SC-004)

Follow `CONTRIBUTING.md` only:

```bash
make install   # if not already
make check-secrets
make lint
make test
```

Expect: all exit 0 on a clean machine that meets prerequisites.

## 5. PR CI present (FR-012)

Open `.github/workflows/ci.yml`. Confirm it runs lint, test, and secrets check without OAuth secrets or a real personal vault.

## 6. Scope attestation (SC-006)

```bash
git diff main --stat
```

Confirm the diff is hygiene/docs/CI/scripts/metadata only — no Context Engine / situation / graph / VISION implement.

## 7. Maintainer-only: flip visibility

When SC-001…SC-006 evidence is recorded:

1. Review GitHub → Settings → Danger Zone / General → Change repository visibility → **Public**.
2. Enable Private Vulnerability Reporting if not already on.
3. Do **not** automate this step from the coding agent.

## Done when

- `make check-secrets` → 0  
- `make lint` && `make test` → 0  
- OSS pytest module green  
- README four questions answered  
- Human ready to flip visibility  
