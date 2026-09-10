<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0 (MINOR: material expansion of workflow guidance,
  new package boundaries, era status; no principle removed or redefined)
- Modified principles: none renamed. Wording unchanged for I–V.
- Modified sections:
  - Product Boundaries: added era status (E1–E6 spawned as specs 004–010),
    horizon promotion rule, simulation/eval harnesses are not a product agent
    runtime, runtime portability rule (Hermes/OpenClaw via existing bridge).
  - Development Workflow: added allowed feature origins (epic, child spec,
    repository tooling) replacing "MUST spawn from a roadmap epic"; added
    Gauntlet gate (frozen bar, two fresh-context critics, delivery evidence,
    red-before-green, blocked_on_person on constitution exception); clarified
    `pcl-core` I/O rule (no network, plugin-host, or server/SDK imports; local
    encrypted vault persistence is core's job); extended package map with
    `packages/pca` and `apps/hub-desktop`; repo tooling lives in `pcl-sdk`;
    Speckit artifacts are repository files, never vault objects; coding-agent
    runtime defaults (Cursor default, Hermes alongside).
  - Governance: Constitution Check MUST cite the version checked; loop
    deliveries count as compliance reviews.
- Added sections: none (heading hierarchy retained)
- Removed sections: none
- Migration: all loop runs 006–012 are `complete`; no in-flight spec requires a
  Constitution Check re-run. Next spec MUST check against 1.1.0.
- Follow-up TODOs: none
-->

# Personal Context Hub Constitution

## Core Principles

### I. Person Owns the Context
The person is the sole owner of personal context. No agent, runtime, model,
plugin, or connector MAY own that context or treat Hub objects as product
memory. Agents are replaceable: disconnecting or switching a runtime MUST NOT
delete history or require the person to re-enter canonical facts. Canonical
objects live in the person's vault. A coding agent working on this repository
is not a Hub client; vault pairing and MCP are a separate connection.

**Rationale**: The product solves an ownership problem, not a retrieval
problem. Continuity across agents is the reason the Hub exists.

### II. Local-First, Loopback-Only
Read, edit, and search MUST work entirely offline. Vault data MUST be encrypted
at rest on the person's device (default `~/.pch`). Network listeners MUST bind
loopback only (`127.0.0.1`). The Hub MUST NOT be a public server, MUST NOT
require a cloud account, and MUST NOT depend on a remote service for core
operation. Secrets, vault databases, OAuth client files, pairing tokens, and
`.cursor/mcp.json` MUST NOT be committed.

**Rationale**: Privacy and availability are the install story. A reachable
non-loopback surface would make the Hub a public server.

### III. Least Privilege, Least Context
An agent receives only what its grant and stated purpose allow — never the
whole vault. Access decisions MUST be evaluated by Hub policy rules outside
any model's reasoning. Grants MUST be shown in plain language before confirm,
MUST be revocable, and revocation MUST take effect on subsequent requests.
Context assembly MUST return the smallest sufficient set for the situation and
MUST name withheld categories without revealing withheld content.

**Rationale**: Trust is scoped, revocable access. More context is not better
context; leakage of irrelevant or unauthorized items is a defect.

### IV. Provenance, Authority, and Explicit Control
Every durable object MUST carry provenance (source, time, authority). Agents
MUST propose durable memories; they MUST NOT write them as canonical. User
confirmation MUST beat agent inference. A person's correction MUST take effect
in all subsequent retrieval; superseded content MUST NOT be presented as live.
Conflicts MUST be surfaced, not silently discarded. Consequential reads,
writes, proposals, approvals, grant changes, and export/import MUST be
recorded in an append-only audit in the same transaction as the write.

**Rationale**: Source is not truth. Without provenance and human control the
vault cannot be trusted as the person's record.

### V. Imported Content Is Data, Never Instruction
Email, calendar, plugin output, and other imported artifacts MUST be treated
as untrusted data. They MUST NOT expand grants, alter policy, trigger actions,
or be interpreted as instructions to the Hub or to an agent. Plugins in v1
MUST be import-only: they write to the vault only through kernel capabilities
and MUST NOT act outward (send, create external events, export, or extend the
Hub UI). Plugin permission enforcement MUST be technical isolation, not
curation or review.

**Rationale**: Imported content is a prompt-injection surface. Curation reduces
risk; it is never the enforcement mechanism.

## Product Boundaries

Memory, context, and situation are distinct. Memory is persisted information.
Context is the relevant slice for a situation. Situation is the operational
frame (project, goal, state, intent) in which an agent is acting now. Features
MUST NOT collapse these into a single "memory" store or treat embeddings as
the product.

Context is temporal: facts and preferences change; history MUST NOT disappear.
Representing "what is live now" versus "what was true" is required of the
Context Engine era; silent overwrite of history is forbidden.

The Hub is model-agnostic. MCP is the first integration surface. Runtime
adapters MAY be added; a new agent-to-agent protocol MUST NOT be invented.
Every real-use runtime (Cursor, Hermes, OpenClaw, or a later one) MUST consume
the same situation package through the existing Hub bridge; recipe text MAY
differ per runtime, the package MUST NOT. Recipes and capture guidance target
the person's runtime, not only this repository. The Hub MUST NOT ship a
foundation model, a vector database as the product, or its own agent runtime
for real users. Simulation, evaluation, and development harnesses that
exercise the Hub are test tooling, not a product agent: they MUST be labeled
as such in the data they write, MUST run under real grants and policy, and
MUST NOT act outward.

Vocabulary collisions that MUST NOT be "fixed" by rename:

- Hub `SharedState` is a TTL handoff object, not operational project State.
- Hub `ActionIntent` is an approval for an external action, not situation Intent.
- `MemoryKind.procedural` is not a Skill object.

Do not build until this constitution is amended: autonomous Personal Agency;
Personal Intelligence (pattern inference across the person); universal ingest
of "everything the person has done"; a mandatory graph database; standing
pre-authorization of high-stakes external actions; chat-transcript scraping as
a memory source.

Era status: the six era epics E1–E6 are spawned as `specs/004` through
`specs/010`. The era closes only when the roadmap exit criterion is met — the
right context, to the right agent, for the right situation, at the right time,
under the person's control — as shown by the evaluation harness, not by spec
count. Promoting a horizon item (Skills primitive, Personal Intelligence,
Personal Agency, A2A, Context Debt, Anticipatory AI) into the queue requires a
roadmap revision and an amendment to this constitution, in that order.

Product thesis lives in `docs/VISION.md`. Operational epics live in
`docs/ROADMAP.md`. Neither file is a Speckit feature. Cross-cutting
properties — identity, privacy, provenance, policy, user ownership,
interoperability — MUST accompany every layer.

## Development Workflow

Feature work follows specify → plan → tasks → implement under
`specs/<nnn>-<name>/`, and every spec MUST be independently testable.
`/speckit-implement` MUST NOT be run against the vision or roadmap documents.
Closed chapters (001 Hub, 002 connectors, 003 plugins) MUST NOT be reopened as
epics; evolve them only via a child spec.

A spec MUST have exactly one of these origins, named in its Input:

- a roadmap epic (E1–E6) from `docs/ROADMAP.md`;
- a child spec of a closed chapter or of a delivered spec, scoped to one gap;
- repository tooling (development loop, simulation, evaluation harness) that
  adds no Personal Intelligence or Personal Agency surface.

A spec MUST NOT implement a horizon item. The loop sequencer MUST refuse a
start whose source is not a feature (`not_a_feature`) or reopens a closed
chapter (`closed_chapter`).

`/speckit-loop` (`uv run pcl-sdk loop`) is the default driver for new feature
work; the person issues one start and the loop does not ask stage by stage.
The Gauntlet gate inside it is mandatory:

- A quality bar (`PLAN-BAR.md` or `SPEC-BAR.md`) MUST be frozen before the
  pack it judges is written. The bar MUST NOT be edited to match a draft; a
  LOSE revises the pack.
- Two independent critics with fresh context MUST judge; they read only the
  frozen bar and the pack files on disk, never a builder recap. Critics in
  disagreement is not a WIN.
- Delivery MUST map each success criterion to executed checks with recorded
  evidence, including that the test failed before the satisfying code
  (`red_before_green`). No stage MAY report complete without evidence.
- The loop MUST pause `blocked_on_person` when a product choice, a failed
  gate, or a constitution exception needs a human decision. It MUST NOT grant
  a constitution exception itself. It MUST NOT commit unless the person asked.

Package boundaries:

- `packages/pcl-core` — vault, schema, policy, context assembly. Owns local
  encrypted vault persistence. MUST NOT perform network I/O, host plugins,
  serve HTTP, or import `pcl-server`, `pcl-sdk`, or plugin code.
- `packages/pcl-server` — loopback HTTP, plugin host, connectors, pairing.
- `packages/pcl-sdk` — CLI, MCP stdio bridge, plugin kit, and repository
  tooling (dev-loop sequencer, simulation and evaluation harnesses).
- `packages/pca` — Portable Context Archive export/import; depends on
  `pcl-core` only.
- `plugins/` — bundled import plugins.
- `frontend/` — React UI, built into `pcl-server` static assets.
- `apps/hub-desktop` — pywebview shell around the loopback server.

Speckit artifacts (`spec.md`, `plan.md`, bars, `RUN.json`, evidence) are
repository files. They MUST NOT be written to the vault, and the coding agent
running them MUST NOT pair as a Hub client to do its work.

Every `plan.md` MUST include a Constitution Check that cites the constitution
version checked and maps these principles to concrete gates (loopback, grant
isolation, provenance, import-as-data, package I/O, spec-not-vision, no
Personal Intelligence/Agency). Absolute success criteria (forbidden-context
blocks, audit completeness, export round-trip) MUST have deterministic
automated tests. New grant or assembly behavior MUST add or extend
`forbidden_context` coverage. Tests for a success criterion MUST fail before
the implementation that is supposed to satisfy it is written.

Complexity MUST be justified in the plan. New listeners, cloud dependencies,
vector indexes, policy engines outside `pcl-core`, network or plugin-host I/O
in `pcl-core`, or kernel I/O in plugins require an explicit constitution
exception in that plan, decided by the person.

Python 3.14 via `uv` is the runtime. Node.js is build-time for the UI only.
Cursor is the default Speckit integration; Hermes is installed alongside it and
discovers the same skills globally. The default MUST NOT be switched unless
the person asks.

## Governance

This constitution supersedes informal practice, README convenience, and
agent habit. Where a spec or plan conflicts with a principle here, the
constitution wins until it is amended.

Amendments MUST be made by updating this file, bumping the version
per the rules below, setting **Last Amended** to the change date, and recording
a Sync Impact Report at the top of the file. A migration note is required when
an amendment invalidates an in-flight spec or plan (re-run Constitution Check).

Versioning:

- **MAJOR**: removal or incompatible redefinition of a principle or gate.
- **MINOR**: new principle or section, or material expansion of guidance.
- **PATCH**: clarification, wording, or non-semantic refinement.

Compliance review: every pull request or loop delivery that changes grants,
policy, plugins, network bind, vault I/O, runtime recipes, or MCP surface MUST
state which principles were checked. `/speckit-plan` Constitution Check is the
design-time gate; Gauntlet critics and `delivery-validate` are the process
gate; `forbidden_context` and audit tests are the runtime gate.

Runtime development guidance for coding agents is `AGENTS.md`. Product
sequencing remains `docs/ROADMAP.md`. This file is the enforceable subset.

**Version**: 1.1.0 | **Ratified**: 2026-08-26 | **Last Amended**: 2026-09-07
