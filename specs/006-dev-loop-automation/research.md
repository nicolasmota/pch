# Research: Development Loop Automation

**Feature**: `specs/006-dev-loop-automation/` · **Date**: 2026-08-26

No NEEDS CLARIFICATION markers remained in Technical Context. Decisions below resolve design choices against existing Speckit skills, `.specify/workflows/speckit/workflow.yml`, the E2 Gauntlet practice (`PLAN-BAR.md` + independent critics), and `pcl-sdk` as the repo CLI package.

## D1 — Sequencer is a CLI in `pcl-sdk`; the skill is the trigger, not the gate

**Decision**: A Python module `pcl_sdk.devloop` plus `pcl-sdk loop …` owns next-stage, refusals, resume, retry budgets, bar-hash checks, and complete-requires-evidence. A project skill `.cursor/skills/speckit-loop/SKILL.md` (invoked as `/speckit-loop`) is the person's one start instruction: it calls the CLI, then runs the corresponding Speckit/Gauntlet/test stage, then records the result. Pytest hits the CLI/module with no model in the loop.

**Rationale**: FR-001/SC-008 need one start; FR-005/SC-003 need a gate that cannot be skipped by forgetting. A skill-only design is the “document it in AGENTS.md” failure mode the bar names. Putting the machine in `pcl-sdk` keeps `pcl-core` free of I/O, matches package boundaries (CLI lives in the SDK), and gives SC-001…SC-007 deterministic tests.

**Alternatives considered**: (a) Skill-only orchestration — rejected: untestable without an LLM; skipping Gauntlet stays a memory. (b) Extend only `.specify/workflows/speckit/workflow.yml` — rejected: that workflow inserts mandatory human review after spec and plan (spec assumption: no pause on WIN) and has no Gauntlet, resume, or delivery evidence. (c) New package or cloud automation — rejected: extra complexity; FR-017 forbids auto-commit/push; constitution forbids a new public surface.

## D2 — Run record is `RUN.json` in the spec folder

**Decision**: Each loop execution writes `specs/<nnn>-<name>/RUN.json` (schema in `contracts/dev-loop.md`). It holds mode, current stage, completed stages with outcomes, bar hash, critic verdicts, retry counts, stop reason, and delivery evidence. `.specify/feature.json` continues to mean “active spec directory” only; it is not the run record.

**Rationale**: US3 requires inspectable status without asking. Resume (FR-004) needs a pointer next to the artifacts. Putting state in the spec folder makes the feature pack the source of truth; a hidden cache would fail “the person can see”.

**Alternatives considered**: (a) `.specify/runs/<id>.json` — rejected: status is detached from the spec the person is looking at. (b) Git notes / branch name as state — rejected: FR-017, and mid-loop work is often uncommitted. (c) Vault object — rejected: FR-016, coding agent is not a Hub client.

## D3 — Stage graph is explicit; Gauntlet is not optional

**Decision**: Ordered stages: `specify` → `clarify?` → `freeze_bar` → `plan` → `gauntlet` → `tasks` → `analyze` → `implement` → `test` → `delivery` → `converge?` → `complete`. `clarify` runs only when the spec still contains `[NEEDS CLARIFICATION]`. `converge` runs when delivery finds unmet tasks/SCs. `freeze_bar` must record `bar_path` + `bar_sha256` before `plan` is allowed to create/overwrite `plan.md` / `research.md` / `data-model.md` / `contracts/` / `quickstart.md`. `gauntlet` requires two independent WIN verdicts; disagreement or LOSE increments `gauntlet_round` (max 3) and returns the run to `plan` without clearing the bar hash. Design-only mode sets `complete` after `gauntlet` WIN.

**Rationale**: FR-002, FR-006–FR-009, US2. The E2 practice (bar frozen, then pack, then two critics) becomes a state machine instead of a chat request.

**Alternatives considered**: (a) Flag `--skip-gauntlet` — rejected: spec says skipping is a defect. (b) Gauntlet after tasks — rejected: tasks agents must receive a WIN pack; that is the point of the E2 bar. (c) One critic — rejected: US2/assumption of two independent judgments.

## D4 — Start targets: description, epic, folder, or next roadmap epic

**Decision**: `pcl-sdk loop start` accepts exactly one of: `--desc` (new specify), `--epic E2` (read `docs/ROADMAP.md` epic block, specify if no spec path, else resume that folder), `--dir specs/005-temporal-validity` (resume), `--roadmap` (next era epic that is not `complete` in its RUN.json / has no spec). `--mode full|design-only`. Empty start is an error. `--dir docs/VISION.md` / `docs/ROADMAP.md` or a request to implement those files as the feature is `refused` (`reason=not_a_feature`). `--epic` values that resolve to `specs/001-*` / `002-*` / `003-*` as a new epic are `refused` (`reason=closed_chapter`).

**Rationale**: FR-001, FR-015, SC-007. `--roadmap` is how “avance no roadmap até finalizar” is a loop of one-epic-at-a-time runs, not one run that implements the roadmap document.

**Alternatives considered**: (a) One run that implements E3–E6 in a single RUN.json — rejected: constitution and roadmap say one child spec at a time; FR-015 forbids treating the roadmap as a feature. (b) Auto-specify every remaining epic in parallel — rejected: shared Hub code, shared constitution; sequential is the product rule.

## D5 — Agent executes Speckit; CLI does not embed the LLM

**Decision**: The loop CLI never calls a model. After `loop next` returns `{"stage":"plan","command":"speckit-plan"}`, the skill runs `/speckit-plan` (and for `gauntlet`, dispatches two fresh-context critics that read only the bar + pack on disk). Then `loop record` writes the outcome. Tests fake `record` without running Speckit.

**Rationale**: Replacing Speckit is out of scope. Deterministic tests cannot spawn a coding agent. The skill is the adapter to Cursor (and Hermes, which already discovers `speckit-*` skills).

**Alternatives considered**: (a) Shell out to `cursor agent` from Python — rejected: non-deterministic, extra runtime, hard to test, not local-first in CI. (b) Duplicate specify/plan in Python — rejected: second specification method.

## D6 — Delivery evidence and TDD gate are fields, not vibes

**Decision**: Stage `test` records `{command, exit_code, summary, recorded_at}`. Stage `delivery` records constitution-gate checklist results, `sc_results` (each SC id → pass/fail/missing), and `red_before_green` (true only if the run recorded a failing test for that SC before a passing one). `complete` is a derived status: allowed only if mode is design-only and gauntlet WIN, or mode is full and test exit_code is 0 and every spec SC is pass and `unmet_items` is empty. Missing `red_before_green` for a code SC fails delivery (FR-013) even if final tests are green.

**Rationale**: SC-004, SC-005, US4, constitution “tests fail before the implementation that satisfies them.”

**Alternatives considered**: (a) Trust implementer’s “tasks marked [x]” — rejected: US4. (b) Require git diff as evidence — rejected: FR-017, uncommitted is valid.

## D7 — Pause vs continue is encoded as `blocked_on_person`

**Decision**: Outcomes: `pass`, `fail`, `blocked_on_person`. `blocked_on_person` is set for remaining `[NEEDS CLARIFICATION]`, constitution-exception requests, or exhausted-budget fail the person must redirect. Successful stages auto-advance (`loop next` is called by the skill without asking). `loop stop` sets `stop_reason=person_stop`. `loop start --dir` on an existing RUN.json resumes unless `--redo <stage>`.

**Rationale**: FR-010, FR-011, US3.

**Alternatives considered**: Gate options from stock Speckit workflow (`approve/reject` after every plan) — rejected: spec default is no pause on WIN.

## D8 — Complexity: one CLI module, one skill, no Hub surface

**Decision**: Files: `packages/pcl-sdk/src/pcl_sdk/devloop/` (pure stage machine + JSON IO to the spec dir), `__main__.py` subparser `loop`, tests under `packages/pcl-sdk/tests/devloop/`, skill under `.cursor/skills/speckit-loop/`, AGENTS.md one-line start. No REST, no MCP tool, no frontend page, no `pcl-core` change.

**Rationale**: Smallest change that is testable. Status is `pcl-sdk loop status` (US3) plus the RUN.json the person can open. A Hub UI would violate FR-016 and reopen product surface for DX.

**Alternatives considered**: Audit-page status in the Hub — rejected: would pair the coding agent as a client. Makefile-only targets — rejected: resume/verdicts need structured state.
