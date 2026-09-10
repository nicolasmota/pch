# Quickstart: One-Command Install

**Feature**: `specs/013-one-command-install/` | **Date**: 2026-09-07

This is the stranger's screen. It starts on a machine that has never seen the repository. Run it
on a fresh VM or container per OS; the release matrix automates §2–§4 and §7.

## 0. Prerequisite (the only one)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Nothing else: no Python, no Node, no Docker, no API key, no account.

## 1. The one command (SC-001, SC-002)

```bash
uvx personal-context-hub
```

Start a timer at Enter. Expected, in order:

1. uv fetches Python 3.14 (if absent) and the five wheels.
2. One line: `Installed for offline use. Next time run: pch` — the Hub then restarts itself
   inside the installed copy (about a second; same terminal).
3. A native window (macOS, Windows) or your browser (bare Linux) opens on `http://127.0.0.1:8765/`
   showing the **guided setup** — the full UI, not JSON.
4. The setup screen states where your key lives: `system keychain` or `a private file in ~/.pch`.
5. `ls ~/.pch` shows `vault.db` and empty `blobs/` (plus `vault.key` if no keychain). No `_sim/`.

Stop the timer at step 3. Record it as SC-001 evidence (< 5 minutes). Confirm you were never
asked for a key, an account, or a password for elevation.

Complete setup with a name. Create project **Atlas**, one goal, one memory. Search `Atlas`.

## 2. Doctor (FR-003, FR-005, FR-014)

```bash
pch doctor
```

Expected: `encrypted: true`, `key_storage: keychain|file`, `ui_bundled: true`, `pinned: true`,
`pinned_interpreter: <uv tool dir>/personal-context-hub/bin/python` (or `...\Scripts\python.exe`),
`loopback_only: true`, `native_window: native|browser`, exit code 0. Also:
`curl -s http://127.0.0.1:8765/v1/sim/runs` → `404` with `simulation disabled…`.

## 3. Offline (SC-003, SC-007)

Disconnect the network (airplane mode, or unplug). Then:

```bash
pch
```

Expected: the running Hub is reused (or restarts) with no error about the network. Read Atlas, edit
the memory, search again, open the project brief. Request the situation package for Atlas from the
UI or from a paired assistant later in §5. Reconnect afterwards.

## 4. Loopback refusal (FR-006)

```bash
pch serve --host 0.0.0.0
```

Expected: exit code 2 and `The Hub is not a public server; it binds loopback only.`

## 5. Pair from anywhere (SC-004)

```bash
cd /tmp
```

In the Hub: Connections → New pairing link → pick **Hermes** → Generate recipe → copy. Inspect the
snippet: `command` is an absolute path ending in `.../personal-context-hub/bin/python` (or
`\Scripts\python.exe`), `args` is `["-m", "pcl_sdk", "mcp-bridge"]`, `PCH_BASE` shows the port the
Hub is actually on. There is no `uv run` anywhere.

Paste into `~/.hermes/config.yaml` under `mcp_servers`, reload MCP in Hermes, grant the connection
the Atlas preset. Ask Hermes for the current situation on Atlas. Repeat for **Cursor** from Cursor
Settings → MCP (user level), still with `/tmp` as the shell's cwd.

Expected: both assistants list the Hub tools and return the Atlas situation package; both
connections show as active in Connections.

## 6. Upgrade keeps everything (SC-005)

Only meaningful with two releases. With release N installed and Atlas populated:

```bash
uv tool upgrade personal-context-hub     # or: pch upgrade
pch doctor                               # version shows N+1
pch
```

Expected: Atlas, its goal, memory, version history, the two connections, and the audit log are all
present; recipes issued under N still connect (same interpreter path). The automated equivalent is
`test_upgrade_preserves_vault.py` on the fixture vault.

## 7. Uninstall never deletes the vault (SC-006)

```bash
pch uninstall
```

Expected: `Removed the Hub program. Your data is untouched at ~/.pch (…)`. Verify `~/.pch/vault.db`
still exists. Then reinstall with `uvx personal-context-hub`: Atlas is back (FR-013, same vault).

Optional, destructive:

```bash
pch uninstall --purge-data
# prompt: Type DELETE to remove ~/.pch and the keychain entry:
```

Type anything other than `DELETE` → exit 1, data untouched. Type `DELETE` → `~/.pch` is gone.

## 8. README check (SC-008)

Open `README.md`. Hand it to someone who has not seen the project; ask them to point at the
command to run. Expected: under 30 seconds, `uvx personal-context-hub`, and the Install section
fits on one screen. Automated floor: `test_readme_install_section.py`.

## Automated run (repo)

```bash
make test                                  # all new tests in contracts/install.md §11
uv run pytest apps/hub-desktop/tests packages/pcl-server/tests/contract packages/pcl-server/tests/integration -q
make release                               # maintainer: frontend build → uv build → check_release → publish
```

Release matrix (`.github/workflows/release.yml`) runs §1's install from `dist/`, §2, a headless
`pch smoke` under `UV_OFFLINE=1`, and §7's default uninstall on ubuntu, macOS, and Windows before
anything is published.
