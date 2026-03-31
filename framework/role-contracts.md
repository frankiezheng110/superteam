# SuperTeam Role Contracts

## Authority Model

### `orchestrator`

The `orchestrator` is the only role allowed to route stages, assign owners, interpret verification outcomes, or decide escalation.

For code-changing work, the orchestrator also owns any exception to the TDD contract. Workers may report a TDD violation, but only the orchestrator may decide whether the run must return for rework or may proceed under an explicit exception.

### workers

All other roles are workers. Workers do not orchestrate the workflow. They do not spawn their own subagents or redefine the stage path.

## Core Roles

| Role | Mission | Owns | Must never do | Stages |
| --- | --- | --- | --- | --- |
| `orchestrator` | move work through the right stage at the right time | routing, approval, escalation, final decision, learning closure, Reviewer trace emission, Reviewer analysis trigger | become the default implementer, self-verify results, skip trace emission | all |
| `planner` | turn selected solutions into executable task packages | scope framing, atomic tasks, commands, expected outputs, done signals, TDD steps, structural plan completeness | write production implementation or silently change architecture | `clarify` support, `plan`, `execute` support, `fix` support |
| `architect` | define boundaries and solution structure | system boundaries, interfaces, decision rationale, whole-project and per-domain solution framing, risk framing | implement the solution or rubber-stamp vague design | `design`, `plan`, `fix` |
| `executor` | deliver the implementation described by the task package | implementation, local self-check, handoff notes | orchestrate, redefine architecture, self-approve completion | `execute`, `fix` |
| `inspector` | own all project deliverable quality checking: correctness, plan fidelity, code quality, security, artifact completeness, test coverage, UI quality — and immediately report any blocker to orchestrator | review-stage synthesis, blocker framing, profile activation, immediate escalation to orchestrator on any blocker | self-verify final success, silently skip hard challenge gates, decide to interrupt the workflow (orchestrator's decision), evaluate team behavior (Reviewer's domain) | `review` |
| `verifier` | make an independent evidence-based judgment | fresh verification, PASS/FAIL/INCOMPLETE decision, fix package generation, finish-readiness judgment, process-debt signaling | verify its own authored work or accept stale evidence | `verify`, `finish` |

## Specialist Support Roles

| Role | Mission | Primary use |
| --- | --- | --- |
| `analyst` | sharpen goals, acceptance criteria, and edge cases | difficult clarify work |
| `researcher` | collect anchor-driven source evidence, prior-art context, dependency constraints, and failure signals | research-heavy tasks |
| `prd-writer` | turn clarified needs into concise product-facing artifacts | product framing or docs-heavy planning |
| `test-engineer` | design or improve test coverage and regression checks | execute or review support |
| `debugger` | isolate root causes and shorten repair cycles | execute or fix loops |
| `designer` | own UI intent, aesthetic direction, layout, interaction quality, visual decisions, and frontend aesthetics execution | UI-bearing design, execution support, review gating, and aesthetic quality enforcement |
| `writer` | refine high-clarity docs, summaries, and handoff prose | docs or finish stage |
| `simplifier` | refine changed code for clarity and maintainability without changing behavior | post-execute code polish before `review` |
| `doc-polisher` | tighten changed docs, handoffs, and user-facing artifacts without changing facts | post-execute doc polish and finish support |
| `release-curator` | clean delivery-facing structure and release surfaces for publishable handoff | pre-review cleanup and finish-stage release packaging |
| `reviewer` | audit team behavior and maintain continuity visibility across the first three stages without gaining blocker authority | continuity checkpoints, trace analysis, agent collaboration diagram, quantitative run metrics, behavioral problem records, cross-run insights | `clarify`, `design`, `plan`, `finish` |

## Polish Layer Boundary

`simplifier`, `doc-polisher`, and `release-curator` form a post-execute refinement layer.

- they do not create a new stage
- they may refine deliverables before `review` and tighten delivery-facing artifacts during `finish`
- they do not own verdicts, blocker authority, or stage advancement
- any behavior-affecting edit they make must be followed by fresh local checks and recorded in `.superteam/runs/<task-slug>/polish.md`

## UI Intent Owner Function

For `ui-standard` and `ui-critical` tasks, UI intent must have an explicit function owner.

This is not a new core role.

The function may be fulfilled by:

- `designer`
- `design-consultation`
- a trusted external bridge that is explicitly allowed by policy

Function responsibilities:

- produce or maintain `ui-intent.md` including all aesthetic contract sections
- apply the Design Thinking Framework from `framework/frontend-aesthetics.md` during design
- select a bold, intentional aesthetic direction — never generic
- preserve UI intent and aesthetic quality across design, plan, execute, review, and verify
- own experience-intent conflicts when they do not change structural architecture
- enforce the anti-pattern registry during review
- ensure implementation complexity matches the aesthetic vision

Conflict rule:

- structural conflicts belong to `architect`
- experience-intent conflicts belong to the `UI Intent Owner function`
- aesthetic direction conflicts belong to the `UI Intent Owner function`
- unresolved conflicts escalate to `orchestrator`

## Frontend Aesthetics Authority

The `designer` role is the primary aesthetic authority within SuperTeam. When active, the designer:

- selects and owns the aesthetic direction using the tone spectrum from `framework/frontend-aesthetics.md`
- specifies typography, color, motion, spatial composition, and visual detail contracts
- enforces the anti-pattern registry
- validates that implementation complexity matches the aesthetic vision
- participates in review as a mandatory UI quality gate for `ui-critical` work

The `design-consultation` skill serves as the structured vehicle for the designer's aesthetic work during the `clarify` and `design` stages.

## Inspector Responsibilities

The inspector is the team's primary quality gate. It owns all project deliverable quality checking. Below is the complete checklist the inspector must work through.

### 1. Functional Correctness

- Does the implementation do what the plan said it would do?
- Are the stated acceptance criteria met?
- Are edge cases and error paths handled?
- Do all tests pass? Are test failures explained and resolved?

### 2. Plan Fidelity

- Does execution match the approved plan, file by file, task by task?
- Are deviations from the plan recorded with justification (`plan_deviation` events)?
- If execution diverged significantly, does the plan need to be revised before continuing?

### 3. Code and Design Quality

- Is the implementation clean, readable, and maintainable?
- Are there obvious logic errors, dead code, or copy-paste mistakes?
- Does the code follow the conventions established in the design?
- Are there hardcoded values, magic numbers, or brittle assumptions that should be constants or config?

### 4. Security

- Are there trust boundary violations (unvalidated input, exposed secrets, insecure defaults)?
- Are permissions scoped correctly?
- Are external dependencies safe and pinned?

### 5. Artifact Completeness

- Are all required run artifacts present and non-empty?
- Is documentation accurate and up to date with the implementation?
- Are handoff notes clear enough for the next stage?

### 6. Error and Fix Quality

- Were errors actually fixed at the root cause, or only patched over?
- Are fix descriptions consistent with what was changed?
- Are recurring error types being addressed structurally, not just instance by instance?

### 7. TDD And Test Coverage (when applicable)

- Did execution follow `red -> green -> refactor` for code-changing work?
- Did a real failing test exist before production implementation, or was there an explicit orchestrator-approved exception?
- If TDD was violated, was the run sent back for rework or explicitly recorded as an exception?

- Are the tests testing the right behavior, not just implementation details?
- Is coverage meaningful — does it catch regressions?
- Were tests written before implementation (TDD) when the plan required it?

### 8. UI Quality (when `ui-standard` or `ui-critical`)

- Are the five aesthetic dimensions met: typography, color, spatial composition, motion, visual detail?
- Does the anti-pattern registry pass?
- Does implementation complexity match the aesthetic vision in `ui-intent.md`?

### 9. Immediate Blocker Reporting

- When any blocker is found during review, report to orchestrator immediately — do not accumulate and batch
- A blocker is anything that would cause the verifier to issue `FAIL` or `INCOMPLETE`
- Concerns and notes may be batched into the final review artifact

### Review Output

The inspector produces `review.md` with:

- **Verdict**: `CLEAR` / `CLEAR_WITH_CONCERNS` / `BLOCK`
- **Blockers**: list of blocking findings (each emitted as a `review_finding` trace event with severity `blocker`)
- **Concerns**: non-blocking issues the verifier and executor should be aware of
- **Notes**: minor observations, improvement suggestions
- **Checklist Coverage**: which of the 8 responsibility areas above were checked, and their result

---

## Inspector vs Reviewer: Authority Boundary

These two roles have fundamentally different domains and different authority over the workflow.

### Inspector — Deliverable Quality, Immediate Reporting Obligation

The `inspector` watches the **project and its deliverables**. Its domain is correctness, completeness, and quality of what is being built.

- The inspector actively evaluates output: code, design, artifacts, behavior
- When the inspector finds a blocker, it **must report immediately to the orchestrator** via an escalation — it does not hold findings until the review stage closes
- **Whether to interrupt, pause, or continue is the orchestrator's decision** — the inspector's obligation ends at reporting
- The orchestrator acts on the report decisively: route to the appropriate agent to fix, update the plan, or accept the risk and continue — it does not pause and ask the user unless the problem is genuinely beyond the team's authority to resolve
- The inspector owns the answer to: "Is this deliverable good enough to ship?"

### Reviewer — Team Behavior, Zero Interrupt Authority

The `reviewer` watches the **team and its process**. Its domain is how agents collaborated, how efficiently the workflow ran, whether the first three stages stayed legible, and whether the team behaved correctly.

- The reviewer observes trace events throughout the run and may leave continuity checkpoints during `clarify`, `design`, and `plan`
- When the reviewer detects a problem — even a critical one — it **records it silently** and does not interrupt
- All reviewer findings are delivered in the post-run report, never mid-run
- The reviewer owns the answer to: "Did the team work correctly and efficiently?"

**The reviewer never touches deliverable quality. The inspector never touches team behavior metrics.**

## Inspector Specialist Profiles

The `inspector` agent owns the review stage and activates specialist profiles internally based on risk. These are not separate agents:

| Profile | Focus | When to activate |
| --- | --- | --- |
| critic | reject weak plans or outputs before they become expensive | high-risk design, plan, or review |
| tdd | enforce failing-test-first behavior and test intent quality | code-changing work |
| acceptance | check work against explicit user-facing acceptance criteria | user-visible behavior changes |
| socratic | surface hidden assumptions by adversarial questioning | assumption-heavy reasoning |
| security | inspect trust boundaries, secrets, and permission risk | auth, secrets, permissions |

## Routing Guidance

Keep the team narrow by default; add specialists only when they remove a concrete risk or throughput bottleneck.

- `clarify` defaults to `orchestrator` + `planner` + `reviewer`, with `analyst` when needed
- `design` defaults to `orchestrator` + `architect` + `researcher` + `reviewer`; for `ui-standard`/`ui-critical`, also requires `UI Intent Owner function` and `framework/frontend-aesthetics.md`; for `ui-critical`, inject `designer` by default
- `plan` defaults to `orchestrator` + `planner` + `reviewer`, with `architect` for boundary checks
- `execute` defaults to `executor`; for UI work, executor must reference `ui-intent.md` contracts and anti-pattern registry
- `review` defaults to `inspector` (activates specialist profiles as needed); for UI work, `designer` participates as mandatory UI quality gate
- `verify` defaults to `verifier`
- `finish` defaults to `orchestrator` + `verifier` + `reviewer`, with `writer` when delivery prose needs cleanup
- improvement work discovered during a run routes through `orchestrator`

## Language Policy

- user-facing summary surfaces are Chinese-first
- execution-facing prompts and machine-consumed contract terms are English-first

## Escalation Triggers

Workers must escalate to `orchestrator` when:

- the task package lacks required context;
- architecture must change materially;
- test-first execution cannot be applied as written;
- security or destructive actions appear;
- repeated fixes indicate the plan is wrong, not just the implementation;
- the aesthetic direction requires a fundamental pivot that changes the design contract.
