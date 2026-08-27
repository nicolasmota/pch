# Research: Assistant Capture Guidance

**Feature**: `specs/012-assistant-capture-guidance/` · **Date**: 2026-08-27

No NEEDS CLARIFICATION markers in Technical Context. Mapped 2026-08-27: `mcp_bridge._mcp_tools` sets `"description": name.replace("_", " ")`; Cursor recipe instructions in `pairing/catalog.py` are `"Add this to .cursor/mcp.json, then reload MCP servers."`; Hermes/OpenClaw recipes already target user home config. `AGENTS.md` line: coding agent is not a Hub client. Simulator 011 isolated vault is unrelated.

## D1 — Static when-to-use on existing tools, not a new tool

**Decision**: Replace bare-name descriptions for `get_context_contract` and `propose_memory` with the shared constants in `pcl_sdk.capture_guidance`. Other tools MAY get a one-line “not a capture operation” so they are not mistaken for the loop. **No** new MCP tool. **No** `get_capture_policy` resource required for v1 (`tools/list` is enough).

**Rationale**: Spec FR-001/FR-002/SC-002. Constitution: MCP is the first surface; do not invent A2A. A stranger assistant only sees `tools/list`.

**Alternatives considered**: (a) New `capture_hints` tool the model must call first — rejected: extra hop; they already do not call existing tools. (b) Live model in CI to prove “would call” — rejected: flaky; SC-003 is a deterministic fixture that consumes the same constants. (c) Fine-tune / Hub-owned model — rejected: constitution.

## D2 — Cursor attach is user-level; snippet shape unchanged

**Decision**: Keep snippet `{ "mcpServers": { "personal-context-hub": { command, args, env } } }`. Change **instructions** to: add the server in Cursor **Settings → MCP** (user / global on this machine) so every window can use it; project `.cursor/mcp.json` is an optional extra, **not** the only supported path. Hermes/OpenClaw instructions already name `~/.hermes/config.yaml` and `~/.openclaw/openclaw.json` — keep them; add the same `runtime_rule` block.

**Rationale**: Spec FR-004/SC-001/SC-004. Cursor user MCP is how “other window” works without a second paste. Hub still does not write those files (FR-007).

**Alternatives considered**: (a) Auto-write `~/.cursor/mcp.json` — rejected: FR-007, constitution secrets/mcp.json not committed, coding agent not a client. (b) Leave project-only as the documented path — rejected: that is the bug. (c) Second Hub port for sim vs everyday — rejected: out of scope (011 isolation stays).

## D3 — One `runtime_rule` string shared with recipes

**Decision**: `capture_guidance.RUNTIME_RULE` is a short plain-language block (task-start read, durable-fact propose, empty honesty, propose-not-canonical, do not propose code chatter or demo fiction as the person’s life). `render_recipe` adds `runtime_rule` to the recipe JSON for every supported assistant. Connections copies it as text. SC-005: character/word count stays pasteable in under 2 minutes (cap ~400 words).

**Rationale**: Spec FR-005/FR-006/US3. Tool descriptions can be truncated by runtimes; the rule is the spare tire.

**Alternatives considered**: (a) Rule only in docs/VISION — rejected: not person-visible at pairing. (b) Different rule per runtime — rejected: same capture loop; only paste location differs. (c) Require the person to write their own rule — rejected: that is form-filling.

## D4 — Three-turn eval is a fixture, not a product LLM

**Decision**: `EXPECTED_THREE_TURN` in `capture_guidance.py`: turn 1 (task start, empty vault) → call `get_context_contract` with purpose from the line; turns 2–3 (durable facts) → `propose_memory` each; after calls, Hub state has 0 canonical memories until owner accept. Test drives REST MCP tools with a paired token against a temp Hub (same pattern as 002 contract tests). A tiny `follow_capture_guidance(transcript, tools_list)` helper uses the **same** trigger phrases as the descriptions (not a neural net). Fail if descriptions drift off the helper.

**Rationale**: SC-003 measurable without CI depending on Cursor. Bar: deterministic automated test.

**Alternatives considered**: (a) Call a cloud model — rejected: cost, flaky, not local-first. (b) Only string-contains tests — rejected: bar wants the loop (request + two proposals + not canonical). (c) Reuse 011 lived-stretch — rejected: that writes as owner into sim space; this spec is assistant propose.

## D5 — No config writes, no scraper, no new listener

**Decision**: Tests assert `render_recipe` / recipe POST never creates files under `~/.cursor`, `~/.hermes`, or `~/.openclaw`. No new FastAPI bind. No job that tails editor transcripts. Scheduler stays unrelated.

**Rationale**: FR-007/FR-009/SC-006. Constitution II and “coding agent is not a Hub client.”

**Alternatives considered**: (a) File watcher on Cursor logs — rejected: new surveillance surface, not loopback-product. (b) Plugin that reads chat — rejected: plugins are import-only and still would be extraction.

## D6 — This repository stays not a Hub client

**Decision**: Do not weaken `AGENTS.md` / constitution sentence. SC-007 reads the file. Optional personal override is the person’s Cursor user rule, not a Hub default. Capture guidance in tool text still says do not propose implementation chatter as the person’s life — that applies in other repos too.

**Rationale**: Spec FR-008/SC-007. Dogfood in the pcl window remains an explicit person choice.

**Alternatives considered**: (a) Delete the AGENTS.md line so this chat captures — rejected: pollutes vault with spec/plan text. (b) Hub detects “pcl repo” and disables tools — rejected: grant is enough; wrong layer.
