# Feature Specification: GitHub Open-Source Readiness

**Feature Branch**: `014-github-oss-readiness`

**Created**: 2026-09-12

**Status**: Draft

**Input**: User description: "Prepare the repository for public open-source on GitHub: add LICENSE, SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md as needed; scrub secrets risk and tighten .gitignore; improve README for first-time visitors and contributors; add community health files and GitHub issue/PR templates; ensure CI workflows and docs clearly explain local-first constraints, what not to commit (vault DBs, .env, oauth tokens, pairing tokens, .cursor/mcp.json), and how to build/test from source. Do not change product thesis or implement VISION/ROADMAP features — this is repo hygiene and public-readiness only."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stranger opens the public repo and knows what it is (Priority: P1)

A person who has never used the Hub lands on the public GitHub page. Within a short scroll they understand what the product does, that their data stays on their device, how to install or run from source, what license applies, and where to report a security issue. They do not see personal vault files, OAuth client secrets, pairing tokens, or editor connection files mixed into the tree.

**Why this priority**: Opening the code without a clear front door and without secret hygiene turns the public moment into confusion or a privacy incident. Everything else (contributing, issues) depends on this first impression being safe and understandable.

**Independent Test**: Clone a fresh copy of the tree as if discovering it cold. Read the top-level README and license notice. Confirm a stranger can state the product purpose, local-first constraint, install or from-source path, and license in under five minutes. Confirm a secrets checklist finds no vault databases, `.env`, OAuth client files, pairing tokens, or `.cursor/mcp.json` tracked by git.

**Acceptance Scenarios**:

1. **Given** a cold visitor on the repository home page, **When** they read the primary documentation, **Then** they can state what the Hub is, that it is local-first / loopback-only, and how to install or contribute from source.
2. **Given** the same visitor, **When** they look for legal terms, **Then** a clear open-source license is present at the repository root and referenced from the project metadata.
3. **Given** a secrets scan of tracked files, **When** it looks for vault databases, environment files, OAuth client JSON, pairing tokens, and editor MCP connection files, **Then** none of those are present in version control.
4. **Given** `.gitignore` and contributor docs, **When** someone tries to add the forbidden local files listed above, **Then** the ignore rules and docs both name those paths as must-not-commit.

---

### User Story 2 - Contributor knows how to help safely (Priority: P2)

A contributor who wants to fix a bug or send a small improvement finds a short contributing guide: prerequisites, setup, test and lint commands, coding boundaries (loopback only, no vault secrets in PRs, coding agent on this repo is not a Hub client), and how to open a pull request. Issue and PR templates steer them to useful reports without asking for personal vault contents.

**Why this priority**: Public code without a contribution path creates drive-by noise or unsafe PRs. This story is secondary only to making the repo readable and secret-safe.

**Independent Test**: Follow CONTRIBUTING from a clean checkout. Run the documented install, test, and lint commands. Open a sample issue using the bug template and a sample PR description using the PR template. Verify neither template asks for vault contents, pairing tokens, or OAuth secrets, and that they warn against pasting those.

**Acceptance Scenarios**:

1. **Given** a clean checkout, **When** a contributor follows the contributing guide, **Then** they can install dependencies, run tests, and run lint using only documented commands.
2. **Given** the issue templates, **When** someone files a bug, **Then** the template asks for reproduction and environment details and explicitly warns not to paste vault data, tokens, or OAuth client files.
3. **Given** the pull request template, **When** someone opens a PR, **Then** it asks for summary, test evidence, and a confirmation that no secrets or personal vault files are included.
4. **Given** the contributing guide, **When** it describes project constraints, **Then** it restates loopback-only, local-first, imported-content-is-data, and that working on this repository does not automatically pair the coding agent as a Hub client.

---

### User Story 3 - Maintainer receives security reports and community norms (Priority: P3)

A security researcher or community member finds a SECURITY policy with a clear reporting path and response expectations, plus a code of conduct that sets behavioral norms. Maintainers can point to these documents instead of inventing process in each thread.

**Why this priority**: Required for a trustworthy public project, but less urgent than secret hygiene and the first-visit README for the initial open.

**Independent Test**: Open SECURITY.md and CODE_OF_CONDUCT.md from the repository root (or the conventional GitHub community health locations). Verify a reporting channel is named, supported versions or scope are described, and the conduct document names enforcement contact and standards.

**Acceptance Scenarios**:

1. **Given** a vulnerability finder, **When** they open the security policy, **Then** they see how to report privately, what is in scope (Hub software, not a stranger's vault contents), and that public issue trackers are not the place for unpatched exploit detail.
2. **Given** a community conflict, **When** maintainers need a reference, **Then** a code of conduct is present with expected behavior and a contact for reports.

---

### Edge Cases

- Someone opens an issue that pastes vault export contents or pairing tokens: templates and security docs must discourage this; maintainers have written guidance to redact and close or edit.
- A contributor commits a local `.env` or `google_oauth.json` by force-add: ignore rules alone are not enough — contributing and security docs must state a secrets policy and remediation (rotate, purge history if needed).
- The repository becomes public while still missing license metadata in package manifests: root LICENSE and package metadata must agree.
- CI exists only for tagged releases today: public readiness MUST document how contributors validate locally; adding a PR continuous-check workflow is in scope if it only runs existing test/lint gates without changing product behavior.
- Vision and roadmap documents stay documentation; this feature MUST NOT implement product epics from them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Repository MUST include a root open-source license file that grants public use, modification, and redistribution under stated terms.
- **FR-002**: Project package metadata MUST declare the same license identifier as the root license file.
- **FR-003**: Repository MUST include a security policy that explains how to report vulnerabilities, what is in scope, and that personal vault contents and live secrets must not be posted in public issues.
- **FR-004**: Repository MUST include a contributing guide covering prerequisites, setup, test, lint, pull request expectations, and must-not-commit paths (vault databases, `.env` / `.env.*`, OAuth client files, pairing tokens, `.cursor/mcp.json`).
- **FR-005**: Repository MUST include a code of conduct with expected behavior and a reporting contact.
- **FR-006**: Repository MUST provide GitHub issue template(s) for bugs (and optionally features) that warn against pasting secrets or personal context exports.
- **FR-007**: Repository MUST provide a pull request template that requires a short summary, test/lint evidence, and an explicit no-secrets confirmation.
- **FR-008**: `.gitignore` MUST cover vault databases and sidecars, `.env` patterns, OAuth client JSON, pairing/token material patterns already used by the project, Hub data directories, and `.cursor/mcp.json`.
- **FR-009**: README MUST present, for a first-time public visitor: product purpose, local-first / loopback-only stance, install path, from-source contribute path, license pointer, and links to contributing and security docs.
- **FR-010**: A documented secrets hygiene check MUST be runnable by maintainers before making the repository public (list of forbidden path patterns and confirmation that none are tracked).
- **FR-011**: Existing product behavior, vault format, and roadmap/vision thesis documents MUST remain unchanged by this feature except for cross-links from README/community docs where helpful.
- **FR-012**: If a continuous integration workflow for pull requests is added, it MUST only exercise existing documented test and/or lint commands and MUST NOT require cloud accounts, non-loopback binds, or access to a real personal vault.

### Key Entities

- **Community health document**: License, security policy, contributing guide, or code of conduct that sets norms for public collaboration.
- **Contribution template**: Issue or pull request form that structures inbound work and blocks unsafe secret sharing by design of its prompts.
- **Secrets deny-list**: Named file and path patterns that must never be versioned (vault DB, env files, OAuth client files, pairing tokens, editor MCP config).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A cold visitor can answer four questions from the README alone in under five minutes: what it is, where data lives, how to install or run from source, and what the license is.
- **SC-002**: A secrets hygiene check over tracked files reports zero matches for the deny-list patterns (vault DBs and sidecars, `.env` / `.env.*`, `google_oauth.json`, pairing token files, `.cursor/mcp.json`).
- **SC-003**: 100% of the required community health documents are present and linked from the README (license, security, contributing, code of conduct).
- **SC-004**: A new contributor following only CONTRIBUTING can run the documented test and lint commands successfully on a clean machine that meets the stated prerequisites.
- **SC-005**: Issue and PR templates each contain an explicit warning not to paste vault data, tokens, or OAuth client material.
- **SC-006**: Making the repository public requires no product-code change beyond repository hygiene, docs, templates, ignore rules, license metadata, and optional PR CI — verified by an unchanged vision/roadmap thesis and no new Hub runtime features.

## Assumptions

- License default is **MIT**, matching common practice for developer tools unless the maintainer later chooses a different OSI license before the public flip.
- Security reporting contact defaults to GitHub private vulnerability reporting for this repository (and/or the repository owner's reachable GitHub security advisory flow); a personal email may be added later without changing the policy structure.
- Code of conduct defaults to the Contributor Covenant plain-language adaptation already common on GitHub, with enforcement contact set to the repository maintainers via GitHub.
- This feature is **repository tooling** under the constitution (allowed origin), not a roadmap epic and not a reopen of 001–003.
- “Open on GitHub” means preparing files and hygiene so the maintainer can switch visibility to public; flipping the GitHub visibility toggle itself remains a manual maintainer action outside this spec.
- No change to packaging/publish story beyond declaring license metadata; release workflow already exists for tags.
- Portuguese or bilingual docs are optional; English is the default for GitHub community health files to match existing README language.
- Product UI, vault crypto, connectors, and plugins are out of scope except where docs must warn about their secret files.
