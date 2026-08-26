# Feature Specification: Development Loop Automation

**Feature Branch**: `006-dev-loop-automation`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Given the whole development loop we already have — specify, Gauntlet loop, delivery-validation flows, tests, quality checks, and so on — automate that workflow so I do not have to drive each stage by hand."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One Trigger Runs the Whole Loop (Priority: P1)

The person who owns this repository wants a feature built. Today they must start specify, then plan, then freeze a Gauntlet bar, then dispatch critics, then tasks, then consistency analysis, then implement, then tests, then delivery checks, then close remaining gaps — each as a separate request. After this feature, they give one starting instruction (a new feature description, a roadmap epic, or an existing spec folder that is mid-loop) and the workflow runs the remaining stages in order until the work is verified complete or it must stop.

They do not re-type the next command after each stage succeeds. They still see what ran, what passed, and where it stopped.

**Why this priority**: This is the reason the feature exists. Without a single driver, Gauntlet, tests, and delivery checks remain optional chores the person has to remember. Chaining the stages is the MVP; richer progress UI and extra quality flavors come after.

**Independent Test**: Start the workflow with a small in-scope feature description (or resume an existing spec folder that already has a spec and no plan). Do not issue the usual per-stage commands. Confirm each expected remaining stage runs in order, later stages do not start until earlier gates pass, and the person is not asked to invoke the next stage by name.

**Acceptance Scenarios**:

1. **Given** no spec folder for the request yet, **When** the person starts the workflow with a feature description, **Then** a spec is produced first, then a plan pack with Gauntlet, then tasks, then consistency analysis, then implementation, then automated tests and delivery validation, without the person naming those stages again.
2. **Given** a spec folder that already has a spec but no plan, **When** the person starts the workflow pointing at that folder, **Then** the workflow resumes at plan (with Gauntlet) and continues the rest of the sequence; it does not recreate the spec from scratch.
3. **Given** a stage fails a gate (Gauntlet LOSE after allowed retries, tests fail, or delivery validation fails), **When** the retry budget for that stage is exhausted, **Then** the workflow stops, names the failed stage and the reason, and does not start later stages.
4. **Given** the person starts the workflow in design-only mode, **When** the plan pack reaches Gauntlet WIN, **Then** the workflow stops before tasks and implementation and reports that design is ready.

---

### User Story 2 - Gauntlet Is a Gate, Not a Memory (Priority: P2)

When the workflow reaches a stage that this repository treats as Gauntlet-graded (today: the plan pack; also the spec when a bar is defined for it), it freezes a quality bar **before** the draft is written. Independent critics with no stake in the draft then judge the files on disk against that frozen bar. A LOSE causes a rewrite of the **artifact**, never of the bar. The stage is not complete until critics return WIN, or the retry budget is exhausted and the loop stops as failed.

The person does not have to remember to say "run this with Gauntlet." Skipping Gauntlet to save time is a defect, not an option.

**Why this priority**: The loop they already trust for vision and for E2 planning is the quality backstop. Automating specify → implement without it would ship thinner plans. It is P2 only because US1 can still prove chaining on stages that have no bar; Gauntlet is what makes the chain honest.

**Independent Test**: Run the workflow through plan on a fixture feature. Confirm a bar file exists and is unchanged after a LOSE-and-rewrite cycle (or, if the first pass WINs, confirm the bar's frozen time predates the pack). Confirm critics are instructed to read disk files and the bar, not a builder recap. Confirm a simulated LOSE leads to a revised pack and a new critic pass, not an edited bar.

**Acceptance Scenarios**:

1. **Given** the workflow is about to produce a Gauntlet-graded pack, **When** drafting starts, **Then** the quality bar is already frozen and later drafts cannot change its pass/fail criteria to match the draft.
2. **Given** independent critics return LOSE, **When** the workflow retries, **Then** it revises the graded files, leaves the bar intact, and asks new independent critics to judge the files on disk.
3. **Given** critics return WIN on all required criteria, **When** the Gauntlet stage completes, **Then** later stages (tasks, implementation) may start, and the WIN verdict is recorded with the run.
4. **Given** two critic judgments are required by the bar, **When** they disagree, **Then** the stage is not treated as WIN; the workflow retries or stops per the retry budget rather than averaging the disagreement away.

---

### User Story 3 - The Person Only Intervenes When a Human Must (Priority: P3)

The person can see which stage is running, which have passed, and the last Gauntlet or test verdict, without asking. They can stop a run. They can resume after a stop or a failure once they have answered or unblocked it.

The workflow pauses for them only when a human decision is actually required: an underspecified product choice, a constitution-level exception, or a failed gate they must accept or redirect. It does not pause after every successful stage to ask "shall I continue?"

**Why this priority**: Automation fails if it either nags at every step or goes silent until something is on fire. Progress and resume make a long loop usable; they are not the MVP of chaining.

**Independent Test**: Start a run; confirm a status view lists stages and outcomes without a follow-up question. Interrupt the run; resume and confirm it continues from the last completed stage. Seed a spec that needs a product choice; confirm the run pauses with the question and does not invent an answer. After the person answers, resume and confirm the loop continues.

**Acceptance Scenarios**:

1. **Given** a run is in progress or just finished a stage, **When** the person looks at run status, **Then** they see current stage, completed stages with pass/fail, and the latest Gauntlet or validation verdict.
2. **Given** the person stops a run, **When** they later resume the same feature, **Then** completed stages are not redone unless they explicitly request a redo, and work continues from the next incomplete stage.
3. **Given** a spec or plan cannot proceed without a product choice from the person, **When** that point is reached, **Then** the run pauses with the question and does not guess; after they answer, the run continues.
4. **Given** a stage succeeds, **When** the next stage is eligible, **Then** it starts without the person confirming "continue."

---

### User Story 4 - Delivery Is Not Done Until Evidence Says So (Priority: P4)

Implementation is not the end of the loop. After code exists, the workflow runs the project's automated tests and the delivery-quality checks this repository already expects (including constitution gates, forbidden-context coverage where grants or assembly changed, and a check that success criteria have failing tests before the code that is supposed to satisfy them). It claims complete only with fresh evidence from that run. If requirements remain unmet, it records the remaining work and either continues to close the gap or stops with a named shortfall — it does not report success on a builder's summary.

The workflow never treats the vision essay or the roadmap document as a feature to implement.

**Why this priority**: The person's complaint is the whole loop, including tests and delivery validation. Without this story, automation would stop at "the agent said it implemented the tasks."

**Independent Test**: On a fixture that implements a tiny requirement, confirm tests and delivery checks run after implementation and that a "complete" report cites those results. On a fixture that leaves a requirement unmet, confirm the run does not claim complete. On a request to implement the vision or roadmap documents, confirm the workflow refuses.

**Acceptance Scenarios**:

1. **Given** implementation tasks for the feature are marked done, **When** the workflow proceeds, **Then** it runs automated tests and delivery-quality validation before reporting complete, and the report cites the fresh results.
2. **Given** tests or delivery checks fail, **When** the retry budget is exhausted, **Then** the run is not complete; remaining gaps are named.
3. **Given** a success criterion is supposed to have a test that failed before the satisfying implementation, **When** that evidence is missing, **Then** delivery validation fails even if tests are green afterward.
4. **Given** the person asks the workflow to implement the vision essay or the roadmap as if they were a feature spec, **When** the run starts, **Then** it refuses and does not generate implementation tasks against those documents.

---

### Edge Cases

- Starting instruction is empty: the workflow does not invent a feature; it stops and asks for a description, a roadmap epic, or an existing spec folder.
- Two workflow runs for the same spec folder: a second start does not clobber in-flight artifacts; it either resumes the existing run or refuses until the person chooses resume, redo-from-stage, or cancel.
- Gauntlet critics return WIN on a pack that contradicts the spec: consistency analysis (or an equivalent gate before implementation) must fail; WIN on style is not a license to drop requirements.
- The feature is a Hub product change that would reopen a closed chapter (001–003) as an epic: the workflow refuses and tells the person to spawn a child spec instead.
- The feature would require a constitution exception (new listener, cloud dependency, kernel I/O in plugins, and similar): the run pauses for an explicit person decision; it does not grant the exception itself.
- Design-only mode plus an already-complete plan: the run reports that design is already done and does not rewrite the pack unless the person requests redo.
- Implementation touches the Hub UI: delivery validation includes exercising the changed flow the way a person would, not only a screenshot or a unit-test pass.
- Network-unrelated core Hub behavior: tests for that behavior still run without requiring an external network; the workflow does not add a cloud dependency to prove the loop works.
- Secrets, vault databases, pairing tokens, and local agent config remain uncommitted; a delivery check that would publish them fails the run.
- Retry budget is finite and visible. Infinite critic/implement loops are a defect. After exhaustion the person gets a stop report, not a silent hang.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The person MUST be able to start one workflow from (a) a natural-language feature description, (b) a named roadmap epic, or (c) an existing spec folder, and have remaining stages execute without naming each stage again.
- **FR-002**: The default sequence MUST be: specify → (clarify only if a human product choice is required) → freeze Gauntlet bar for graded stages → plan pack → Gauntlet critics until WIN or budget exhausted → tasks → cross-artifact consistency analysis → implement → automated tests → delivery-quality validation → close remaining specified work or stop with named gaps.
- **FR-003**: The person MUST be able to start in design-only mode, which ends after plan Gauntlet WIN (no tasks, no implementation).
- **FR-004**: The workflow MUST resume from the last completed stage when pointed at an existing spec folder, unless the person explicitly requests a redo from a named stage.
- **FR-005**: A later stage MUST NOT start until the previous stage's gate has passed. Failed gates after retry budget MUST stop the run with a named reason.
- **FR-006**: For every Gauntlet-graded stage, the quality bar MUST be frozen before the graded artifact is written, MUST be the critics' only quality bar, and MUST NOT be edited to match a failing draft.
- **FR-007**: Gauntlet critics MUST judge the artifacts as they exist on disk, MUST NOT be given a builder recap as evidence, and MUST produce a pass/fail verdict in the repository's existing verdict shape (WIN or LOSE, failing criteria, evidence).
- **FR-008**: A Gauntlet LOSE MUST trigger a rewrite of the artifact and a fresh critic pass. Exhausting retries MUST fail the stage. Disagreement among required critics MUST NOT be treated as WIN.
- **FR-009**: Plan and spec stages that this repository already Gauntlet-grades MUST run Gauntlet as part of the workflow. The person MUST NOT have to request Gauntlet as a separate instruction.
- **FR-010**: The workflow MUST pause for the person when a product choice, constitution exception, or failed gate requires a human decision. It MUST NOT pause merely because a stage succeeded.
- **FR-011**: The person MUST be able to inspect run status (current stage, completed outcomes, latest verdicts) and MUST be able to stop a run.
- **FR-012**: After implementation, the workflow MUST run this project's automated tests and delivery-quality validation and MUST NOT report the feature complete without fresh evidence from that run.
- **FR-013**: Delivery validation MUST include: constitution gates relevant to the change; mapping of each success criterion to executed checks; the rule that tests for a success criterion fail before the implementation that satisfies them; and, when grants or context assembly change, coverage that forbidden context does not leak.
- **FR-014**: If implementation finishes with unmet spec/plan/task items, the workflow MUST record those remaining items and either continue to close them or stop unsuccessful with the shortfall named. It MUST NOT rewrite the spec or plan to match a thinner delivery.
- **FR-015**: The workflow MUST refuse to treat `docs/VISION.md` or `docs/ROADMAP.md` as a Speckit feature to implement, and MUST refuse to reopen closed Hub chapters 001–003 as epics.
- **FR-016**: The workflow is repository development tooling. It MUST NOT write canonical Hub memories, MUST NOT pair as a Hub client, and MUST NOT require the Hub to be a public server.
- **FR-017**: The workflow MUST NOT create commits, publish branches, or open reviews unless the person explicitly asked for that in the starting instruction or a later decision. Completeness of the loop is verified work, not a published change.
- **FR-018**: Retry budgets per stage MUST be finite, visible in status, and leave the last failing evidence in place for the person.

### Key Entities

- **Workflow Run**: one execution of the loop for one spec folder. Attributes: starting mode (full or design-only), current stage, stop reason, retry counts, resume pointer.
- **Stage**: a named step in the sequence (specify, clarify, bar freeze, plan, Gauntlet, tasks, analyze, implement, test, delivery validation, close gaps). Each has a gate: pass, fail, or blocked-on-person.
- **Quality Bar**: frozen pass/fail criteria for a Gauntlet-graded artifact. Created before the draft; not updated to excuse a LOSE.
- **Critic Verdict**: independent judgment against a bar: WIN or LOSE, failing criteria, evidence pointing at the files on disk.
- **Feature Pack**: the spec folder's artifacts (spec, plan pack, tasks, checklists, implementation result). The run's job is to produce and gate these, not to replace them with a chat summary.
- **Delivery Evidence**: fresh results of tests and quality checks cited when the run claims complete or failed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of successful fixture runs, the person issues one start instruction and does not issue a follow-up that names the next Speckit or Gauntlet stage; every remaining stage in the selected mode still runs.
- **SC-002**: 100% of Gauntlet-graded fixture runs freeze the bar before the graded files exist, and 0% of LOSE retries edit the bar's criteria.
- **SC-003**: 100% of runs that exhaust a stage's retry budget stop before later stages and present a named failed stage plus evidence; 0% hang or skip to implementation after a failed design gate.
- **SC-004**: 100% of "complete" reports for a fixture include fresh test and delivery-validation results from that run; 0% of complete reports are based only on a builder saying tasks are done.
- **SC-005**: When a fixture leaves a specified requirement unmet, 100% of runs refuse to report complete, and the unmet item is listed.
- **SC-006**: Resume from a spec folder that already finished specify starts at the next incomplete stage in 100% of trials; specify is not redone unless redo was requested.
- **SC-007**: A request to implement the vision or roadmap documents is refused in 100% of trials, with no implementation tasks written against those files.
- **SC-008**: After the person learns the start instruction once, they can start a full or design-only run without a checklist of intermediate commands; a new contributor following the start instruction alone reaches the same stage sequence as someone who previously drove the loop by hand.

## Assumptions

- This is **repository development tooling**, not a Hub product epic and not E3 (project state / situation intent). It does not jump the product queue and does not change vault, grants, or connectors.
- The existing Speckit commands and the Gauntlet practice already used on the vision essay and on the E2 plan pack are the stages being chained. This feature does not invent a second specification method or a weaker critic.
- Default mode is the **full loop** (through verified delivery). Design-only is opt-in at start. There is no mandatory "approve spec" / "approve plan" pause when those stages WIN; the person who wants a look uses design-only or stops the run.
- Clarify runs only when a human product choice is required (the existing cap on open questions still applies). Routine gaps get documented defaults in Assumptions rather than blocking the loop.
- Gauntlet-graded in v1: the plan pack always; the spec when a spec bar is present or produced. Tasks are gated by consistency analysis, not a literary Gauntlet. Implementation is gated by tests and delivery validation, not by rewriting a prose bar to match the code.
- Two independent critics per Gauntlet pass, matching the E2 plan practice. Retry budget default: three critic rounds per graded stage; two repair cycles after failing tests/delivery checks. The person may tighten these at start; they may not remove Gauntlet.
- Automated tests and lint/quality commands are whatever this repository already uses to prove a change. This spec does not change product test policy; it makes running that policy a required stage.
- Committing, pushing, and opening a review stay explicit person actions (existing working rule), not automatic side effects of a green loop.
- Closed chapters 001–003 stay closed; vision and roadmap stay non-features. Constitution 1.0.0 still wins over a convenient automation shortcut.
- A coding agent executing this workflow is still not a Hub client. Vault pairing and Hub access remain a separate connection.
- Existing in-flight product specs (for example temporal validity) can be resumed by this workflow; automating the loop must not require finishing or discarding them first.
- Out of scope: replacing Speckit; autonomous Personal Agency for the Hub; publishing the Hub as a hosted service; silent commit of secrets; moving a frozen Gauntlet bar because critics were harsh; using this loop to implement vision or roadmap documents.
