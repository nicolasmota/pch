# Feature Specification: Hub Plugin Framework & Marketplace

**Feature Branch**: `003-hub-plugin-marketplace`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "quais proximos passos de evolução para ter um hub melhor, um framework melhor pensando em que ele possua plugins e criar um marketplace para plugins"

## Clarifications

### Session 2026-08-21

- Q: What plugin types must the framework support in v1 — import-only plugins, or also plugins that act outward on the owner's behalf? → A: Import-only in v1. Plugins may write only to the vault; outward actions (sending email, creating events, exporting) and UI extensions are out of scope for v1.
- Q: Must plugin permissions be technically enforced (isolated runtime, mediated access), or is process-level enforcement (curation/review plus runtime policy checks) enough? → A: Technical enforcement. Plugin code runs isolated from the kernel and can reach vault data and the network only through a Hub-mediated interface; undeclared access is technically impossible, for first-party and third-party plugins alike.
- Q: Who can publish to the v1 marketplace — first-party only, or third-party developers too? → A: Third-party developers can be listed after submission and manual curator review; self-service publishing remains out of scope for v1.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extend My Hub With Plugins (Priority: P1)

A person opens the Hub's new Plugins page and sees every optional import capability of their Hub — connectors (Google Calendar, Gmail) and future data sources — presented as installable plugins. They can install, enable, pause, disable, and remove a plugin without touching code or restarting the Hub. Before a plugin activates, the Hub shows in plain language what the plugin can do (which object types it reads or writes, which external services it contacts, what runs in the background), and nothing runs until the user confirms. Disabling a plugin stops all of its activity immediately; removing it offers to keep or delete the data it created, with clear provenance either way.

**Why this priority**: This is the structural step everything else depends on. Today connectors are hard-wired into the Hub's core; each new source or capability grows the trusted kernel. A plugin boundary turns the Hub from a fixed app into a platform while *shrinking* what must be trusted: the kernel keeps vault, policy, grants, and audit; everything else becomes a permissioned guest. Without this boundary there is nothing for a marketplace to distribute.

**Independent Test**: Can be fully tested with the built-in capabilities alone — repackage the existing Google Calendar and Gmail connectors as the first two plugins, then verify: fresh Hub shows them as available-but-inactive; enabling one prompts for its declared permissions; syncing works exactly as before; disabling stops scheduled syncs immediately; removing with "delete data" purges imported objects; audit timeline attributes every plugin action to that plugin's identity.

**Acceptance Scenarios**:

1. **Given** an installed Hub with no plugins active, **When** the user opens the Plugins page, **Then** they see the bundled plugins (calendar, email) as available, each with a plain-language description of what it will be able to do once enabled, and nothing has run yet.
2. **Given** a plugin being enabled, **When** the Hub shows the consent screen, **Then** it lists the plugin's declared permissions (object types touched, external hosts contacted, background schedules) and the plugin only activates after explicit confirmation.
3. **Given** an active plugin, **When** it attempts an action outside its declared permissions (e.g., reading object types it never declared), **Then** the action is denied, the denial is recorded in the audit timeline under the plugin's identity, and the plugin is flagged on the Plugins page.
4. **Given** an active plugin with scheduled background work, **When** the user disables it, **Then** no further background work runs, and existing data created by the plugin remains readable and marked with the plugin as its source.
5. **Given** a disabled plugin, **When** the user removes it and chooses "also delete its data", **Then** all objects the plugin created are tombstoned and the removal is recorded in the audit timeline.
6. **Given** the existing calendar and email connectors migrated to plugins, **When** a user who had them configured upgrades the Hub, **Then** their connections, sync state, and imported data continue working without reconfiguration.

---

### User Story 2 - Build a Plugin Without Touching the Core (Priority: P2)

An independent developer wants their service (say, a note-taking app or a fitness tracker) to feed a user's Hub. They read a short plugin guide, scaffold a plugin from a template, and declare in a manifest what the plugin needs: which object types it produces, which external services it talks to, how often it syncs. They develop and test it against a local Hub in a developer mode that shows permission checks, audit entries, and imported objects live. Validation tooling tells them before publishing whether the plugin violates any platform rule (undeclared access, missing provenance, oversized payloads). At no point do they need to read or modify the Hub's source code.

**Why this priority**: A plugin framework without third-party authors is just refactoring. The developer experience decides whether an ecosystem forms. It comes after P1 because the extension surface must exist and be proven by the first-party plugins before outside developers are invited onto it.

**Independent Test**: A developer who has never seen the Hub codebase follows only the plugin guide to build a "read-only RSS feed importer" plugin; it imports items as artifacts with correct provenance and classification, passes the validation tool on first packaging, installs on a clean Hub from its package file, and cannot read any vault data beyond what its manifest declared.

**Acceptance Scenarios**:

1. **Given** the plugin developer kit, **When** a developer scaffolds a new plugin, **Then** they get a working skeleton with a manifest, a sync entry point, and a runnable example against a local Hub, without cloning the Hub repository.
2. **Given** a plugin manifest, **When** the developer declares produced object types, external hosts, and sync cadence, **Then** the Hub enforces exactly those declarations at runtime — anything undeclared is denied by default.
3. **Given** a finished plugin, **When** the developer runs the validation tool, **Then** it reports rule violations (undeclared access, missing source provenance, classification omissions) with actionable messages, and a passing plugin produces an installable package.
4. **Given** a plugin package file, **When** a user installs it manually (side-load), **Then** the Hub shows the same consent screen as for bundled plugins, including a clear "unverified developer" notice.
5. **Given** a plugin that crashes or hangs during sync, **When** the failure occurs, **Then** the Hub stays responsive, the plugin is marked as failing on the Plugins page, and other plugins are unaffected.

---

### User Story 3 - Discover and Install Plugins From a Marketplace (Priority: P3)

A person opens the Marketplace tab inside their Hub and browses a catalog of plugins: connectors and importers for new data sources. Each listing shows what the plugin does, exactly which permissions it will request, its publisher, its verification status, and community signals (installs, rating). Installing is one click followed by the standard consent screen. Updates are offered — never forced — with a diff of any permission changes, and a plugin pulled from the marketplace for being malicious can be remotely flagged so affected users are warned on their next Hub session.

**Why this priority**: The marketplace is the growth engine, but it is only safe and useful after the plugin boundary (P1) and the authoring pipeline (P2) exist. Shipping it earlier would distribute unsandboxed code.

**Independent Test**: With a marketplace populated by at least the two first-party plugins and one third-party example, a non-technical user finds a plugin by searching, installs it in one click plus consent, uses it, receives an update that adds a permission (and must re-consent to that specific addition), and sees a warning when a test plugin is flagged as withdrawn.

**Acceptance Scenarios**:

1. **Given** the Marketplace tab, **When** the user searches or browses by category, **Then** each listing shows description, publisher, verification badge, requested permissions, and rating before any install action.
2. **Given** a chosen listing, **When** the user clicks install, **Then** the plugin package is fetched, its integrity verified against the marketplace's published fingerprint, and the standard consent screen shown — a tampered or mismatched package never activates.
3. **Given** an installed marketplace plugin with an available update, **When** the update changes requested permissions, **Then** the user sees exactly what was added or removed and must approve additions before the new version activates.
4. **Given** a plugin withdrawn from the marketplace for malicious behavior, **When** an affected user's Hub next checks the catalog, **Then** the user is warned, the plugin is paused pending their decision, and their imported data remains intact.
5. **Given** a Hub with no internet access, **When** the user opens the Marketplace tab, **Then** browsing gracefully degrades (cached catalog or clear offline notice) and all installed plugins keep working locally.

---

### Edge Cases

- What happens when a plugin requests permissions that overlap the owner's most sensitive data (e.g., all sensitive artifacts)? The consent screen escalates the warning, and such grants can be time-boxed or scoped rather than all-or-nothing.
- What happens when two plugins declare the same source (e.g., two Google Calendar plugins)? Both may install; each keeps its own identity, source keys, and provenance, so their objects never collide or overwrite each other.
- What happens when the Hub is upgraded and a plugin targets an older extension API? The plugin is paused with a "needs update" state instead of running against a changed surface; data remains readable.
- What happens when a plugin is abandoned by its publisher? The marketplace marks stale listings; the plugin keeps working locally, and the user is informed it no longer receives updates.
- What happens when a plugin tries to exfiltrate vault content to an undeclared host? The egress attempt is blocked by default (undeclared hosts are unreachable), recorded in the audit timeline, and surfaces as a security flag on the plugin.
- What happens to prompt-injection payloads inside plugin-imported content? Same rule as connectors today: imported content is data, never instructions — it cannot alter grants, trigger actions, or change policy.
- What happens when a marketplace listing's publisher account is compromised? Package integrity pins and permission-diff re-consent limit blast radius; the kill-switch flag reaches affected Hubs on next catalog check.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Hub MUST define a stable plugin boundary such that optional import capabilities (connectors, importers) run as plugins with their own identity, distinct from the trusted kernel (vault, policy, grants, audit, UI shell). In v1, plugins are import-only: they may write only to the vault and MUST NOT perform outward actions (sending messages, creating external events, exporting data) or extend the Hub UI.
- **FR-002**: Every plugin MUST declare, in a machine-readable manifest, the object types it reads/writes, the external hosts it contacts, and any background schedule; the Hub MUST deny anything undeclared by default at runtime.
- **FR-002a**: Permission enforcement MUST be technical, not review-based: plugin code runs isolated from the trusted kernel and can reach vault data and the network only through a Hub-mediated interface. This applies equally to first-party, third-party, and side-loaded plugins — curation reduces risk but is never the enforcement mechanism.
- **FR-003**: A plugin MUST NOT run any code or contact any network host before the user has seen its declared permissions in plain language and explicitly confirmed activation.
- **FR-004**: Users MUST be able to enable, pause, disable, and remove any plugin from the Hub UI; disable/pause MUST take effect immediately for background work.
- **FR-005**: On plugin removal, the user MUST choose whether data created by that plugin is kept (with provenance intact) or deleted; either choice MUST be recorded in the audit timeline.
- **FR-006**: Every object a plugin creates MUST carry the plugin's identity in its provenance (source references) and an appropriate classification, exactly as connector-imported objects do today.
- **FR-007**: Every plugin action that touches the vault or is denied by policy MUST appear in the audit timeline attributed to the plugin's identity.
- **FR-008**: A failing plugin (crash, hang, repeated errors) MUST NOT degrade the Hub or other plugins; the failure MUST be visible on the Plugins page.
- **FR-009**: The existing Google Calendar and Gmail connectors MUST be repackaged as the first two plugins with no loss of user data, connections, or sync state on upgrade.
- **FR-010**: The platform MUST provide a plugin developer kit: a scaffold template, a manifest schema, a local development mode against a real Hub, and a validation tool that rejects rule violations before packaging.
- **FR-011**: Plugins MUST be installable from a package file (side-load) with the same consent flow as bundled plugins, plus an explicit unverified-source warning.
- **FR-012**: The plugin extension surface MUST be versioned; a plugin targeting an incompatible version MUST be paused with a clear "needs update" state rather than run.
- **FR-013**: The Hub MUST offer a Marketplace view listing available plugins with description, publisher, verification status, requested permissions, and community signals, browsable before any install.
- **FR-014**: Marketplace installs MUST verify package integrity against the catalog's published fingerprint; a mismatched package MUST never activate.
- **FR-015**: Plugin updates MUST be user-approved; updates that add permissions MUST show the difference and require re-consent for the additions specifically.
- **FR-016**: The marketplace MUST support withdrawing a malicious plugin such that affected Hubs warn the user and pause the plugin on their next catalog check, without touching the user's data.
- **FR-017**: All installed plugins MUST keep working offline; marketplace browsing MUST degrade gracefully without internet access.
- **FR-018**: Content imported by plugins MUST be treated as data only — it MUST NOT be able to alter grants, trigger actions, or change policy (same prompt-injection rule as connectors today).
- **FR-019**: The marketplace MUST accept third-party plugin submissions and list them only after manual curator review and approval; approved third-party listings carry the publisher's verification status. Self-service (unreviewed) publishing is out of scope for v1.

### Key Entities

- **Plugin**: An installable, permissioned extension with its own identity; has a lifecycle (available → enabled → paused/disabled → removed) and a version.
- **Plugin Manifest**: The plugin's declaration of intent — produced/consumed object types, external hosts, background schedule, required extension-surface version, publisher identity.
- **Plugin Grant**: The user's confirmation of a manifest's permissions; revocable; scoped to the plugin's identity; the runtime source of truth for what the plugin may do.
- **Plugin Package**: The distributable artifact of a plugin version, with an integrity fingerprint that installation verifies.
- **Marketplace Listing**: A catalog entry tying a publisher, a plugin, its versions, verification status, requested permissions, and community signals; can be withdrawn (kill-switch).
- **Publisher**: The accountable author of one or more plugins; carries a verification status shown before install.
- **Installation Record**: The local record linking an installed plugin version, its grant, its data (via provenance), and its audit trail on one Hub.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both existing connectors run as plugins with zero data loss and zero reconfiguration for existing users after upgrade (verified by upgrade test on a populated vault).
- **SC-002**: A user can install, consent to, and start using a plugin in under 3 minutes, and can fully disable one in under 30 seconds, from the Hub UI alone.
- **SC-003**: 100% of plugin vault writes carry plugin provenance, and 100% of policy denials for plugins appear in the audit timeline attributed to the correct plugin (verified by automated audit test).
- **SC-004**: A developer outside the core team builds and packages a working read-only importer plugin using only the developer kit and guide, without reading Hub source code, in under one day.
- **SC-005**: A plugin attempting undeclared vault access or undeclared network egress is blocked in 100% of attempts in the adversarial test suite.
- **SC-006**: A tampered plugin package (fingerprint mismatch) is rejected in 100% of install attempts.
- **SC-007**: A withdrawn (kill-switched) plugin is paused with a user-facing warning on the next catalog check in 100% of affected test Hubs, with imported data intact.
- **SC-008**: A Hub with plugins installed remains fully functional offline: reading data, search, and local plugin features all work with no internet (verified by offline test run).

## Assumptions

- The Hub's existing trust mechanics (grants, classification ceilings, audit ledger, proposal queue) are reused as the enforcement layer for plugins; plugins get *less* default trust than today's built-in connectors, never more.
- The first marketplace iteration is a curated, first-party-hosted catalog (static index with signed listings) that accepts third-party submissions via manual curator review; open self-service publishing and monetization (paid plugins, revenue share) are out of scope for this feature.
- Plugin ratings/installs counts may launch as placeholder or minimal signals; full community review infrastructure is out of scope.
- The plugin runtime targets the same local-first, single-device deployment as the current Hub; multi-device plugin sync is out of scope.
- Plugins that act outward on the owner's behalf (send email, create events, export data) and plugins that extend the Hub UI are out of scope for v1; the plugin boundary should not preclude adding them later behind the existing proposal/approval queue.
- The two bundled Google connectors are the reference migration and ship as verified first-party plugins; the RSS importer (or equivalent) serves as the third-party developer-experience proof.
- Marketplace listings and kill-switch checks piggyback on periodic catalog fetches; no push infrastructure is assumed.
