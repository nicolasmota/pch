# Feature Specification: One-Command Install

**Feature Branch**: `013-one-command-install`

**Created**: 2026-09-07

**Status**: Draft

**Input**: User description: "Instalação em um comando, sem chave de API, offline. Hoje o Hub exige clonar o repositório, Python 3.14 via uv, Node 22 para construir a UI e `make install`; a UI construída não é versionada, então uma instalação fora do checkout não tem interface; as receitas de pareamento emitem um comando que só funciona de dentro do repositório. O concorrente mais próximo (OpenMemory) exige Docker, Postgres, Qdrant e uma chave da OpenAI. Resultado: uma pessoa copia um comando do README, executa em uma máquina limpa, e o Hub abre com o setup guiado, sem chave de API, sem conta, sem etapa de build; depois da instalação, tudo funciona offline; a receita de pareamento funciona de qualquer diretório; atualizar preserva o vault; desinstalar não apaga o vault sem confirmação. Spec filha de 001 (instalação e primeiro uso, FR-001, SC-001) e de 002/009 (receitas de conexão). Origem: repository tooling / child spec. Não reabre 001–003 como epic."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and open the Hub with one command (Priority: P1)

A person who has never seen this repository reads one line in the README, pastes it into a terminal on a clean machine, and within a few minutes the Hub is running on their own device and its guided first-run setup is open in front of them. They were not asked for an API key, an account, a cloud login, or a build tool. They did not clone anything. From that moment on, reading, editing, and searching their context works with the network disconnected.

**Why this priority**: Every other recommendation for making the Hub essential (real-user validation, Hermes provider, importing existing exports) depends on a stranger being able to get the Hub running without help. Today the entry cost is a repository checkout, two language runtimes, and a build step. 001 promised "installable by a non-technical user" (FR-001) and "under 15 minutes" (SC-001); the current path does not meet either for someone outside the project.

**Independent Test**: On a machine (or fresh container/VM) with only the operating system and at most one documented prerequisite tool, run the single documented command. Verify the Hub UI opens, the guided setup completes, one project with a memory can be created and searched, and after disconnecting the network and restarting the Hub, the same data is still readable and editable. Verify at no point was any API key, account, or cloud login requested.

**Acceptance Scenarios**:

1. **Given** a machine with only the OS and the one documented prerequisite, **When** the person runs the single documented install-and-launch command, **Then** the Hub starts on the local machine and the guided first-run setup is shown, without any prompt for API keys, accounts, or cloud services.
2. **Given** the Hub was installed by that command, **When** the person opens it, **Then** the full interface is present (not a blank page or an API-only response), including Connections and the review queue.
3. **Given** the Hub is installed and the machine is offline, **When** the person starts the Hub and reads, edits, and searches their context, **Then** everything works and no error about missing network is shown.
4. **Given** the machine has no native window toolkit, **When** the Hub starts, **Then** it opens in the system browser instead of failing.
5. **Given** the Hub's usual port is taken by an unrelated program, **When** the person runs the command, **Then** the Hub picks another local port and tells the person where it opened.
6. **Given** the Hub is already running from an earlier launch, **When** the person runs the command again, **Then** the existing Hub is reused and its window or tab is opened, not a second copy.

---

### User Story 2 - Pair an assistant from anywhere (Priority: P2)

Right after installing, the person opens Connections, picks their assistant (Cursor, Hermes, or OpenClaw), and copies the recipe. The recipe works as pasted: it does not depend on the person being inside the project repository, on a checkout existing at all, or on a developer tool being on the path of their assistant. The assistant connects on the first try.

**Why this priority**: A recipe that only works from inside the repository undoes the value of the one-command install. This is the second thing every new person does, and it is the moment the product either connects or is abandoned.

**Independent Test**: Install with the single command in a directory that is not the repository. Generate a Cursor recipe and a Hermes recipe. Paste each into the corresponding assistant's configuration from an unrelated working directory. Verify the assistant lists the Hub's tools and can request the situation package under the granted scope. Verify the recipe text contains no path or command that assumes a repository checkout.

**Acceptance Scenarios**:

1. **Given** the Hub installed by the single command and no repository checkout on the machine, **When** the person generates a recipe for a supported assistant, **Then** the recipe references only commands available after that install.
2. **Given** the recipe pasted into the assistant from an unrelated directory, **When** the assistant starts, **Then** it connects to the Hub and the connection appears as active in Connections.
3. **Given** a recipe generated on a machine where the Hub runs on a non-default port, **When** it is pasted, **Then** it points at the port actually in use.

---

### User Story 3 - Upgrade and uninstall without losing the vault (Priority: P3)

A person who has used the Hub for weeks runs the documented upgrade command. When it finishes, everything they stored is still there and the Hub works the same. Later, if they decide to remove the Hub, the uninstall step tells them plainly where their data lives and removes the program without touching the vault unless they explicitly ask for that too.

**Why this priority**: The thesis is that the person owns the context and the software is replaceable. An upgrade that loses data, or an uninstall that silently deletes years of context, contradicts the product. This story is lower priority only because it happens after install and pairing.

**Independent Test**: Install an older release with the single command, populate the vault, run the documented upgrade, verify 100% of objects, history, grants, and audit entries are still present and the Hub starts. Then run the documented uninstall, verify the program is gone, the vault directory is untouched, and the uninstall output named the vault location.

**Acceptance Scenarios**:

1. **Given** a populated Hub from a previous release, **When** the person runs the upgrade command, **Then** the Hub starts on the new release and every stored object, version, grant, and audit entry is still present.
2. **Given** the upgrade requires a change to how data is stored, **When** it runs, **Then** the change is applied automatically before the Hub accepts requests, and the person is told if anything needs their attention.
3. **Given** an installed Hub, **When** the person runs the uninstall step, **Then** the program is removed, the vault and its key material are not deleted, and the output states where the data remains.
4. **Given** the person explicitly asks to remove their data as well, **When** they confirm, **Then** the vault is removed; without that explicit confirmation it never is.

---

### Edge Cases

- The one prerequisite tool is missing: the README gives its one-line install and the Hub command fails with a message naming exactly that, not a stack trace.
- The install command runs while the machine is offline: it fails early with a clear message that the first install needs a connection; after that no connection is required.
- A vault already exists in the default data directory from a source checkout install: the packaged Hub reuses it; it does not create a second vault or ask the person to migrate.
- The operating system's secure credential store is unavailable (headless Linux, restricted account): key material falls back to a file readable only by the person, and the Hub says so in the setup screen.
- The person has no administrator rights: the install completes at user level; nothing requires elevation.
- Two people share a machine: each user account gets its own Hub data directory and key; one cannot open the other's vault.
- The person passes a non-loopback host to bind: the Hub refuses and explains that it is not a public server.
- Antivirus or a corporate proxy blocks the first fetch: the failure names the fetch that failed so the person can ask IT, rather than leaving a half-installed program.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Hub MUST be installable and launchable with one documented command on a clean machine, with at most one prerequisite tool, itself installable with a single documented command.
- **FR-002**: The install and first run MUST NOT request or require an API key, an account, a cloud login, or any paid service.
- **FR-003**: The install MUST NOT require a repository checkout, a second language runtime, or a build step on the person's machine; the complete user interface MUST ship inside what is installed.
- **FR-004**: After installation, all reading, editing, searching, context assembly, and assistant connections MUST work with no network access; only the initial fetch of the program itself MAY need a connection.
- **FR-005**: The installed Hub MUST keep every existing protection: vault encrypted at rest by default, loopback-only binding, grants, review queue, and audit. The install path MUST NOT introduce a plaintext or non-loopback default.
- **FR-006**: The installed Hub MUST refuse to bind a non-loopback address and MUST explain why.
- **FR-007**: The launch command MUST reuse an already-running Hub instead of starting a second one, and MUST choose a nearby free local port when the default is taken, telling the person which one.
- **FR-008**: When no native window toolkit is present, the Hub MUST open in the system browser rather than fail.
- **FR-009**: Every pairing recipe generated by the Hub MUST work from any directory and MUST reference only commands available after the one-command install; recipes MUST NOT assume a repository checkout or developer tooling.
- **FR-010**: Recipes MUST reflect the actual local address and port the Hub is using.
- **FR-011**: The Hub MUST provide a documented upgrade command that preserves 100% of stored objects, versions, grants, connections, and audit entries, applying any storage changes automatically before serving requests.
- **FR-012**: The Hub MUST provide a documented uninstall step that removes the program, never removes the vault or key material without a separate explicit confirmation, and states where the data remains.
- **FR-013**: The packaged Hub MUST reuse an existing vault in the default data directory created by a source-checkout install, without duplication or manual migration.
- **FR-014**: When the secure credential store is unavailable, key material MUST fall back to a file readable only by the current user, and the first-run screen MUST tell the person which storage is in use.
- **FR-015**: The install MUST complete without administrator or root privileges.
- **FR-016**: The README's install section MUST contain exactly the one command for install-and-launch, the one prerequisite (with its install line), the upgrade command, and the uninstall step, and nothing that only applies to contributors; contributor setup MUST move to a separate section.
- **FR-017**: Install, upgrade, and uninstall MUST be verified on macOS, Linux, and Windows; on any of them where a native window is not possible, the browser fallback MUST satisfy the acceptance scenarios.
- **FR-018**: The install MUST NOT write anything to the vault, pair any assistant, or send any telemetry. First-run setup remains the person's action.

### Key Entities *(include if feature involves data)*

- **Release**: a versioned, downloadable form of the Hub that contains the service, the command-line tools, the assistant bridge, and the built user interface, obtainable by the one documented command.
- **Data directory**: the person's local home for the vault, key material, plugins, and connection state; survives install, upgrade, and uninstall; is never created twice for one user.
- **Recipe**: the copyable configuration a person pastes into an assistant; after this feature it depends only on the installed Release and the Hub's actual local address.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a clean machine with the one prerequisite present, a person reaches the guided first-run setup in under 5 minutes from pasting the command, with zero manual steps in between.
- **SC-002**: 100% of test installs on macOS, Linux, and Windows complete without any prompt for API keys, accounts, or cloud services, and without administrator rights.
- **SC-003**: With the network disconnected after install, 100% of the read, edit, search, and context-assembly scenarios from 001 and 004 pass.
- **SC-004**: 100% of generated recipes for Cursor, Hermes, and OpenClaw connect on first paste from a directory that is not the repository, with no repository checkout present.
- **SC-005**: Upgrade from the previous release preserves 100% of objects, versions, grants, connections, and audit entries, verified by count and by content hash.
- **SC-006**: Uninstall never deletes the vault without the separate confirmation, in 100% of test runs, and the uninstall output names the data location every time.
- **SC-007**: Zero network requests leave the machine during first run and normal use after install; only loopback traffic is observed.
- **SC-008**: The README install section fits on one screen and contains one install-and-launch command; a reader with no prior knowledge can identify the command to run within 30 seconds.

## Assumptions

- The one allowed prerequisite is the widely available package-runner tool for the language the Hub is written in, which can also fetch the required language version on its own; its one-line install is linked, not reimplemented. A standalone native installer or app bundle (the existing packaging skeleton points there) is a follow-up spec, not this one.
- The Release is published to a public package index under a fixed name, with a direct-from-repository URL as fallback; publishing is part of this feature's delivery, not a separate spec.
- The built user interface is produced at release time by the maintainer and shipped inside the Release; the person's machine never builds it.
- Running the Hub at login or as a background service is out of scope; the "reuse an already-running Hub" behavior is sufficient for this feature.
- The desktop shell keeps its current behavior (native window when a toolkit exists, browser otherwise); no new window technology is introduced.
- Default data directory remains the person's home data folder used today; the key continues to live in the OS credential store with the existing file fallback.
- Google Calendar and Gmail plugins remain optional and keep their own credential setup; they are not part of "no API key" because they are not required to use the Hub.
- Windows support means the native Windows path; running under a Linux compatibility layer on Windows is acceptable as an additional path but does not substitute for it.
- This spec is a child of 001 (install and first run) and of 002/009 (pairing recipes). It does not reopen those chapters; it fixes the delivery path for what they already specify. Origin per constitution 1.1.0: repository tooling and child spec.
