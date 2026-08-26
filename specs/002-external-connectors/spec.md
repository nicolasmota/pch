# Feature Specification: External Connectors (Real Agents, Calendar, Email)

**Feature Branch**: `002-external-connectors`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "Conectores reais: conectar agentes de verdade (Claude, ChatGPT e similares) ao Hub para que usem o contexto pessoal em conversas reais, e conectar contas externas (calendário, e-mail) como fontes de contexto com consentimento, mantendo proveniência, classificação e as garantias de permissão do MVP (001-personal-context-hub)."

## Clarifications

### Session 2026-08-21

- Q: Qual assistente real deve ser o alvo de validação da User Story 1? → A: Cursor (assistente do IDE, MCP direto no WSL); Claude/ChatGPT como segundo runtime na validação de continuidade.
- Q: Quem gera as claims derivadas do e-mail — o Hub extrai automaticamente ou só assistentes conectados propõem? → A: Só assistentes conectados propõem claims a partir dos artefatos importados; o Hub não tem extração própria.
- Q: Qual classificação padrão para eventos de calendário importados? → A: `private` — visível aos presets atuais (teto private), oculto a tetos mais baixos; usuário pode reclassificar eventos delicados como `sensitive`.
- Q: Frequência da sincronização em segundo plano? → A: Calendário a cada 15 minutos, e-mail a cada 60 minutos; ambos com "sync now" manual.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Connect a Real AI Assistant (Priority: P1)

A person opens the Hub's Connections page, picks their AI assistant (e.g., Claude, ChatGPT, or an IDE assistant) from a short catalog, and follows a copy-paste connection recipe generated for that assistant. From then on, when they chat with that assistant about their own life or projects, the assistant retrieves grounded, cited context from the Hub — subject to the exact grants the user approved — instead of guessing or asking the user to re-explain.

**Why this priority**: This is the missing "moment of value" of the whole product. The MVP proved scoped retrieval with a demo agent; nobody's daily assistant uses it yet. Until a real assistant answers a real question with vault context, the Hub is a notebook, not a context layer.

**Independent Test**: Can be fully tested by pairing Cursor (the primary validation target) using only the on-screen recipe (no code edits), asking it "what does my Atlas project prefer?", and receiving an answer that cites the vault memory; asking about an ungranted topic returns a refusal, and both requests appear in the audit timeline under that assistant's identity.

**Acceptance Scenarios**:

1. **Given** an installed Hub with the Atlas project and a cited-briefs memory, **When** the user follows the connection recipe for their assistant and grants "Can read project Atlas", **Then** the assistant can answer a question about Atlas in its own chat, quoting content that carries citations to vault objects.
2. **Given** a paired assistant with a single-project grant, **When** the assistant is asked about content outside that grant (e.g., finance memories), **Then** the Hub returns nothing beyond the grant and the denial is recorded in the audit timeline.
3. **Given** a paired assistant, **When** the user revokes the connection in the Hub, **Then** the assistant's next request fails with a revocation error within seconds.
4. **Given** two different real assistants paired with the same project grant, **When** each is asked for a project brief, **Then** both receive consistent context derived from the same canonical objects.
5. **Given** a user with no technical background, **When** they follow the recipe, **Then** pairing completes with copy-paste steps only — no file editing, no terminal, no developer settings.

---

### User Story 2 - Connect My Calendar as a Context Source (Priority: P2)

A person connects their calendar account to the Hub through an explicit consent flow. The Hub imports upcoming and recent events as referenced context (who, what, when), each carrying its source, timestamp, and classification. Assistants with an appropriate grant can then answer questions like "what's my week look like?" or prepare briefs that respect real availability. The user can see when the calendar was last synced, pause syncing, or disconnect at any time.

**Why this priority**: Calendar is the highest-signal, lowest-risk external source: structured data, clear consent boundaries, immediate everyday utility ("when am I free?"). It makes the vault feel alive without the user typing memories by hand.

**Independent Test**: Can be tested by connecting one calendar account via the consent flow, verifying events appear as context objects with provenance ("from calendar X at time Y"), asking a granted assistant about this week's schedule, and then disconnecting and verifying no further events arrive.

**Acceptance Scenarios**:

1. **Given** an installed Hub, **When** the user connects a calendar account, **Then** they see exactly what will be accessed (which calendar, read-only) before confirming, and nothing is imported before confirmation.
2. **Given** a connected calendar, **When** sync runs, **Then** events appear as context objects with source, sync time, and private classification by default, and the sync is recorded in the audit timeline.
3. **Given** imported events, **When** a granted assistant asks about the user's schedule for a stated purpose, **Then** it receives only events within its grant scope, with citations to the source events.
4. **Given** a connected calendar, **When** the user disconnects it, **Then** syncing stops immediately, the stored events remain (clearly marked as no-longer-syncing) unless the user chooses to also delete them.
5. **Given** the device is offline, **When** the user or an assistant reads previously synced events, **Then** reading works; only new syncs wait for connectivity.

---

### User Story 3 - Connect Email as a Selective Context Source (Priority: P3)

A person connects an email account, but — unlike calendar — nothing is imported wholesale. The user selects narrow slices (for example: specific senders, labels, or a date range), and the Hub imports those messages as referenced artifacts classified as sensitive by default. The Hub itself performs no extraction: when a connected assistant reads those artifacts and infers a durable claim (e.g., "flight confirmed for the 12th"), it must submit it through the memory-proposal queue rather than it becoming a canonical fact silently.

**Why this priority**: Email is high value but the highest-risk source (secrets, third parties, prompt-injection payloads). It must ride on the trust mechanics proven in the MVP (proposals, classification, untrusted-content rules), so it comes after calendar.

**Independent Test**: Can be tested by connecting an email account, selecting a single label, verifying only messages under that label are imported as sensitive artifacts, having a granted assistant propose a claim citing those messages and seeing it land in the review queue (not canonical memory), and confirming an assistant without a sensitive-classification grant cannot retrieve any of it.

**Acceptance Scenarios**:

1. **Given** a connected email account, **When** the user selects a label and date range, **Then** only matching messages are imported, each as an artifact with source, time, and sensitive classification.
2. **Given** imported email artifacts, **When** a granted assistant infers a durable claim from them, **Then** the claim is submitted as a memory proposal with the source messages as evidence, requiring user review.
3. **Given** an assistant whose grant excludes sensitive classification, **When** it searches topics covered by imported email, **Then** email-derived content is withheld and the response notes a redaction occurred.
4. **Given** an imported message containing instructions aimed at an agent (prompt injection), **When** any assistant retrieves context, **Then** the message content is treated as data only — it cannot alter grants, trigger actions, or change policy.
5. **Given** a connected email account, **When** the user disconnects it, **Then** no further messages are imported and the user chooses whether existing artifacts are kept or deleted.

---

### Edge Cases

- What happens when an assistant's runtime does not support the Hub's connection method? The catalog entry says so upfront, and the recipe screen lists supported assistants; no dead-end pairing.
- What happens when the account provider's consent expires or is revoked provider-side? Sync fails visibly: the connector shows a "reconnect needed" state, and stale data remains readable with its last-synced timestamp.
- What happens when a synced event or message is edited or deleted at the source? The next sync updates or tombstones the local reference; derived memories keep their provenance and are flagged for review if their source disappeared.
- What happens when two sources supply conflicting facts (calendar says meeting moved, memory says original time)? The conflict is surfaced for the user; connector data never silently overwrites user-confirmed memory.
- What happens when the same event or message is imported twice (overlapping syncs, reconnects)? Duplicates are recognized by source identity and do not create duplicate context objects.
- What happens when a sync would import thousands of items at once (first sync of a busy account)? The first sync is bounded by the user's selection (date range/labels/calendars) and reports progress; the Hub stays responsive.
- What happens when the assistant embeds retrieved context into its own provider-side memory? Out of the Hub's control; the grant screen states plainly that disclosed context leaves the vault and revocation stops future disclosures, not past ones.
- What happens when connector credentials would be exported in a portable archive? They are excluded by default, consistent with the MVP's "no third-party secrets in exports" rule.

## Requirements *(mandatory)*

### Functional Requirements

**Real agent connections**

- **FR-001**: The Hub MUST offer a catalog of supported real assistants, each with a guided, copy-paste connection recipe requiring no code or file editing by the user.
- **FR-002**: A paired real assistant MUST authenticate with its own per-connection identity, and every context request it makes MUST be evaluated against that connection's grants, purposes, and classification ceilings — identical to the MVP's policy path.
- **FR-003**: Context disclosed to a real assistant MUST carry citations to vault objects, and refusals/redactions MUST be visible in the Hub's audit timeline under that assistant's identity.
- **FR-004**: Revoking a real assistant's connection MUST invalidate its credentials promptly so that subsequent requests fail with an explicit revocation error.
- **FR-005**: The pairing recipe MUST work while the Hub runs on the user's own device, with the connection kept local (loopback) unless the user explicitly configures otherwise.

**Account connectors (shared rules)**

- **FR-006**: Connecting any external account MUST use an explicit consent flow that states, before confirmation, what will be read, how often, and read-only scope; nothing is imported before the user confirms.
- **FR-007**: All connector-imported content MUST carry provenance (source system, source identifier, sync time), a default classification, and imported authority — never user-confirmed.
- **FR-008**: Connector-imported content MUST be treated as untrusted data: it cannot expand permissions, alter policy, trigger actions, or become canonical durable memory without going through the proposal/review pipeline.
- **FR-009**: Every sync run (start, outcome, item counts, failures) MUST be recorded in the audit timeline, and each connector MUST display last-sync status and a manual "sync now" control; background sync runs on a per-connector default cadence (calendar every 15 minutes, email every 60 minutes) while the Hub is running.
- **FR-010**: Users MUST be able to pause or disconnect any connector at any time; disconnecting stops future syncs immediately and lets the user choose whether existing imported content is kept or deleted.
- **FR-011**: Provider credentials/tokens MUST be stored encrypted on-device, never inside exported archives, and MUST never be disclosed to any assistant.
- **FR-012**: Re-syncing the same source items MUST NOT create duplicates; source identity determines updates and tombstones.

**Calendar connector**

- **FR-013**: Users MUST be able to connect at least one mainstream calendar provider, choosing which calendars are included, with read-only access; imported events default to private classification, and the user can reclassify individual events (e.g., to sensitive).
- **FR-014**: Imported events MUST be retrievable by granted assistants (scope- and classification-filtered) to answer schedule questions and build briefs, with citations to the source events.

**Email connector**

- **FR-015**: Email import MUST be selective by construction: the user picks senders, labels/folders, or date ranges; there is no "import everything" option.
- **FR-016**: Imported messages MUST default to sensitive classification, so they are excluded from any grant without an explicit sensitive-classification ceiling.
- **FR-017**: The Hub MUST NOT extract claims from email content itself; durable claims derived from email MUST be proposed by connected assistants through the memory-proposal queue, with the source messages as evidence, and MUST NOT become canonical without the user's review policy being satisfied.

### Key Entities

- **Assistant Catalog Entry**: A supported real assistant — its name, connection method, capabilities, and the recipe template used to pair it.
- **Connector Account**: A user-consented link to an external provider account (calendar or email) — provider, scope of consent, sync schedule, status (active, paused, reconnect-needed, disconnected).
- **Sync Run**: One execution of a connector — start/end time, items created/updated/tombstoned, outcome, errors.
- **Imported Artifact/Event**: A context object originating from a connector, carrying source identity, provenance, default classification, and imported authority; source of citations for derived claims.
- **Derived Claim Proposal**: A memory proposal submitted by a connected assistant based on connector content, holding evidence references to the imported items.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A non-technical user pairs at least one real, third-party assistant using only the on-screen recipe in under 10 minutes, and receives a correctly cited answer about their own project in that assistant's chat.
- **SC-002**: 100% of context requests from real assistants are policy-evaluated and audited; seeded forbidden-context tests show zero out-of-grant leaks through a real assistant connection.
- **SC-003**: Revoking a real assistant takes effect within seconds; 100% of its subsequent requests are refused.
- **SC-004**: A user connects a calendar and, within 5 minutes, a granted assistant answers a schedule question grounded in synced events with citations.
- **SC-005**: 100% of connector-imported objects carry provenance, sync timestamp, and imported (non-user-confirmed) authority; zero connector items become canonical memory without passing the proposal pipeline.
- **SC-006**: 100% of email-derived content defaults to sensitive classification and is withheld from grants lacking a sensitive ceiling, with the redaction noted in responses.
- **SC-007**: Zero provider credentials appear in exports, agent disclosures, or audit summaries across the pilot test suite.
- **SC-008**: Prompt-injection fixtures imported via email/calendar produce zero grant changes, zero actions, and zero policy alterations across the seeded safety suite.

## Assumptions

- **Agent connection method**: Real assistants connect through the prevailing open agent-connection standard already exposed by the Hub's tool facade; assistants without such support are listed as unsupported in the catalog rather than worked around. The primary validation target is Cursor (IDE assistant, connects to the Hub's loopback directly on the user's platform); the second, independently implemented runtime for continuity validation is Claude or ChatGPT.
- **First providers**: Google is the first calendar and email provider (largest coverage, single consent system). Additional providers are follow-on work, not part of this feature's acceptance.
- **Read-only sync**: All connectors in this feature are read-only imports. Writing back to external systems (sending mail, creating events) remains governed by the MVP's action-intent/approval flow and is out of scope here.
- **Sync cadence**: Periodic background sync while the Hub runs (calendar every 15 minutes, email every 60 minutes), plus manual "sync now"; real-time push is out of scope.
- **Local-first unchanged**: The Hub still runs on-device with no mandatory cloud account; connectors reach out to providers, not the other way around.
- **Provider limits**: Sync respects provider rate limits; first sync is bounded by the user's selection rather than a full-history crawl.
- **MVP dependency**: This feature builds on 001-personal-context-hub (grants, policy evaluation, proposals, audit, classification); it does not redefine those mechanics.
