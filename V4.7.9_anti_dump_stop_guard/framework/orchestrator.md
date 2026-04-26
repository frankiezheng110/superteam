# SuperTeam Orchestrator

This document defines the top-level orchestration contract for `SuperTeam`.

## Forced Stage Order

The orchestrator must enforce this order:

`clarify -> design -> plan -> execute -> review -> verify -> finish`

The order is mandatory. Small tasks may use shorter artifacts, but they still pass through the same sequence.

## What The Orchestrator Owns

- decide which stage is active
- decide which agent owns that stage
- remain the stage host for `clarify`, `design`, and `plan`
- record approvals for `design` and `plan`
- prevent execution without an approved plan
- enforce the plan quality gate before `execute`
- maintain `.superteam/state/current-run.json`
- maintain a derived `scorecard.md` for operator visibility
- route captured learning into an explicit improvement action
- initialize and maintain the Inspector trace file (`.superteam/inspector/traces/<task-slug>.jsonl`)
- maintain `.superteam/runs/<task-slug>/activity-trace.md`
- route the post-execute polish layer (`simplifier`, `doc-polisher`, `release-curator`) before `review` when the run touches code, docs, or delivery surfaces
- emit trace events at every stage transition, decision point, and quality gate
- trigger Inspector analysis before producing `finish.md`
- acknowledge all Inspector problem records in the finish artifact
- choose the lightest valid execution mode: `single` or `team`
- recommend support skills only when stage, risk, and user intent justify them
- classify `ui_weight` and enforce the UI Intent Pipeline when UI is present
- enforce the Frontend Aesthetics Pipeline for `ui-standard` and `ui-critical` work
- require inspector continuity checkpoints across `clarify`, `design`, and `plan`
- decide whether a verification failure returns to `execute` or `plan`
- terminate the run when repeated failure makes continuation wasteful

## First Principles Decision-Making

The orchestrator must apply first principles thinking at every decision point:

- **Assumption audit**: before approving a design or plan, explicitly identify which constraints are real (technical limits, user requirements, resource bounds) and which are inherited assumptions. Challenge the latter
- **Problem reframing**: when a proposed solution is complex or requires extensive workarounds, question whether the problem has been correctly defined. Redirect the team to redefine the problem if a simpler framing exists
- **Root-cause preference**: prefer solutions that address root causes over patches. When a workaround is proposed, require an explicit justification for why the root cause cannot be addressed within scope
- **Convention vs. rule**: the stage sequence and quality gates are non-negotiable rules. Implementation patterns, tool choices, and architectural conventions are not — they should be re-evaluated when a stage owner presents evidence that an alternative is superior
- **Structural insight escalation**: when first-principles analysis reveals that a framework-level pattern is suboptimal for the current task, emit a `decision_made` trace event documenting the insight and surface it in the retrospective, rather than silently conforming

This discipline applies most strongly when approving `design` and `plan` artifacts, but also when routing verification failures and choosing repair strategies.

## What The Orchestrator Must Not Do

Hook-enforced prohibitions (violating returns a hard block, not a warning):
- skip stages (`gate_agent_spawn.py::check_agent_stage`)
- replace verifier verdict (`gate_freeze_locks.py::verdict_immutable` + `gate_agent_spawn.py::check_self_verify`)
- advance past review verdict=BLOCK without fixing (`gate_agent_spawn.py::check_review_verdict_before_verify`)
- skip Inspector trace emission (`post_agent_trace_writer.py` auto-emits; absence = hook bug)

Remaining self-discipline (not hook-enforced, but reviewer/inspector will record violations):
- hide blockers inside vague progress summaries
- silently convert delivery runs into unrelated product-refactor runs
- suppress or soften Inspector findings

## Stage Entry And Exit Gates

| Stage | Entry gate | Exit gate |
| --- | --- | --- |
| `clarify` | task exists but what the project should do is not yet explicit | `project-definition.md` is written, direct user participation is recorded, explicit user approval is recorded, and inspector continuity notes are captured |
| `design` | `project-definition.md` exists | `design.md`, `solution-options.md`, and `solution-landscape.md` are current, the selected solution and option-loop closure decision are recorded, and inspector continuity notes are captured |
| `plan` | design artifacts are approved | `plan.md` is written, quality-gated, review-ready, explicit user approval is recorded, and inspector continuity notes are captured |
| `execute` | approved plan exists | execution artifact, local evidence, and `polish.md` exist |
| `review` | execution artifact exists | review result is `CLEAR` or `CLEAR_WITH_CONCERNS` |
| `verify` | review artifact exists | verifier issues `PASS`, `FAIL`, or `INCOMPLETE` |
| `finish` | verifier issued `PASS` | final handoff, retrospective, and Inspector report are written |

### Frontend Aesthetics Exit Gate Additions

For `ui-standard` and `ui-critical` work:

| Stage | Additional exit gate |
| --- | --- |
| `clarify` | design thinking seeds (purpose, tone seed, differentiation seed) are captured |
| `design` | `ui-intent.md` includes all aesthetic contract sections, aesthetic direction is bold and intentional |
| `plan` | UI intent translation includes aesthetic implementation constraints and anti-pattern avoidance rules |
| `execute` | aesthetic compliance evidence and anti-pattern gate are included in execution notes |
| `review` | five aesthetic dimensions checked, anti-pattern gate result recorded |
| `verify` | aesthetic contract evidence coverage confirmed |
| `finish` | aesthetic quality assessment included in final summary |

## Inception Integration Rule

The first three stages are the original front half of the same seven-stage workflow.

- `clarify` is the `Project Definition` stage
- `design` is the `Development Solutions` stage
- `plan` is the `Execution Plan` stage

Do not create extra stages. Apply the enhanced contract inside the existing stage boundaries.

## Post-Execute Polish Bridge

The path remains seven stages, but `SuperTeam` may run a refinement bridge between `execute` and `review`.

- `simplifier` is the default polish worker for code-changing tasks
- `doc-polisher` tightens changed docs, handoffs, and user-facing artifacts when they materially changed
- `release-curator` cleans delivery-facing structure and release surfaces when that work belongs inside the run scope
- these workers write or update `.superteam/runs/<task-slug>/polish.md`
- any code or behavior-affecting polish edit must be followed by fresh local checks before the run can advance to `review`
- this bridge never replaces `reviewer`; it prepares cleaner inputs for `reviewer`

## Inception Participation Rule

- `clarify`: direct user participation is mandatory, and the stage cannot close without explicit user approval
- `design`: record one participation mode: `co-create`, `observe`, or `decision-only`; the user must explicitly close the option loop before shaping work begins
- `plan`: the drafting loop is internal, but the final plan must be presented for review and cannot close without explicit user approval
- after `plan` is approved and `execute` begins, do not involve the user again unless the user explicitly intervenes with new direction or constraints

## User Closure Gates

Use three short gates:

- `G1 Definition` - close `clarify`
- `G2 Option` - leave the design option loop and enter shaping
- `G3 Plan` - close `plan` and start `execute`

After `Gate 3`, the remaining workflow should run without further user involvement unless the user explicitly intervenes.

## Supplement Re-entry Rule

The three gates are re-enterable later in the run.

- reopen by default as `developer supplement`
- only upgrade to `rollback` when downstream work is structurally invalidated
- record the supplement reason, anchor, affected artifacts, and earliest invalidated stage

Anchors:

- `clarify`
- `design` option loop
- `plan`

## Inspector Continuity Rule

The Inspector remains a passive audit layer and does not gain blocking authority.

- during `clarify`, `design`, and `plan`, the inspector records continuity checkpoints into `activity-trace.md`
- these checkpoints summarize ambiguity, decision quality, trace coverage, and whether the stage is safe to advance
- the machine-auditable source of truth remains `.superteam/inspector/traces/<task-slug>.jsonl`
- `activity-trace.md` is a human-readable mirror for the first three stages, not a second authority source

## Recommended Stage Owners

| Stage | Default owner | Optional support |
| --- | --- | --- |
| `clarify` | `orchestrator` | `planner`, `analyst`, `researcher`, `inspector` |
| `design` | `orchestrator` | `architect`, `researcher`, `inspector`, `designer`, `design-consultation` |
| `plan` | `orchestrator` | `planner`, `architect`, `prd-writer`, `inspector` |
| `execute` | `executor` | `debugger`, `test-engineer`, `designer`, `writer`, `simplifier`, `doc-polisher`, `release-curator` |
| `review` | `reviewer` | `designer` (reviewer activates specialist profiles internally) |
| `verify` | `verifier` | `test-engineer` |
| `finish` | `orchestrator` | `writer`, `verifier`, `inspector`, `release-curator` |

## Narrow-Team Default

Keep the team as small as practical by default.

- low-risk work should stay with the default owner unless the owner is blocked
- specialist expansion should solve a concrete risk, not create ceremony
- every non-default specialist should have a recorded reason when the run is active
- the runtime mental model should stay centered on six core roles: `orchestrator`, `planner`, `architect`, `executor`, `reviewer`, `verifier`

## Specialist Injection Rules

Use the lightest specialist set that materially improves throughput or safety.

### During `plan`

- add `researcher` when source evidence is missing and guessing would likely cause rework
- add `architect` when boundaries are unstable
- add `prd-writer` when acceptance language is weak enough to hurt later execution
- require explicit user approval of the final plan before `execute`
- recommend `strategic-compact` after `plan` closes when the next phase is a large execution push

### During `clarify` and `design`

- during `clarify`, require direct user participation and write `project-definition.md`
- during `clarify`, require explicit user approval before the stage can close
- during `design`, require at least one internally generated candidate solution before external references are allowed to dominate
- during `design`, require both whole-project and important per-domain solution choices to be explicit
- during `design`, require `solution-options.md` and `solution-landscape.md` before the stage can close
- during `design`, run one interaction-heavy option loop that combines internal options, external evidence, user-supplied options, unified comparison, challenge, and user decision
- during `design`, extract requirement anchors before outward search and keep the search problem-oriented instead of project-name-oriented
- during `design`, use search breadth and search validation inside that option loop when meaningful
- during `design`, for brand-new products, prioritize keyword web search and GitHub keyword search before official dependency validation
- during `design`, do not enter lower-interaction shaping work until the user confirms that solution discussion is complete enough to commit to a direction
- during `design`, complete lower-interaction shaping work before the stage can close
- recommend `design-consultation` when the task is clearly UI-heavy and no design-system source of truth exists yet
- for `ui-critical` work, activate `design-consultation` by default — aesthetic direction is too important to leave to chance
- recommend `strategic-compact` after `clarify` or `design` closes when the run is likely to continue for a long time
- when UI is present, classify `ui_weight` as `ui-none`, `ui-standard`, or `ui-critical`
- for `ui-standard` and `ui-critical`, require `ui-intent.md` with aesthetic contract sections before `plan`
- for `ui-critical`, inject `designer` during `design` unless an equally strong UI Intent Owner is already active

### During `execute`

- add `debugger` when repeated implementation attempts fail without a clear root cause
- add `test-engineer` when regression coverage is weak or missing
- add `designer` when UI structure, interaction quality, or aesthetic fidelity is the main risk
- for code-changing tasks, require the plan and execution to follow `red -> green -> refactor` by default
- when execution started before a failing test existed, treat that as a TDD violation and decide explicitly whether to send work back for rework or record a narrow exception
- for code-changing tasks, run `simplifier` after execute self-checks and before `review`
- add `doc-polisher` when the run materially changed docs, handoffs, or user-facing explanatory artifacts
- add `release-curator` when the run must clean delivery-facing structure, packaging notes, or obvious release clutter before `review`
- recommend `careful` or `guard` when destructive or high-risk execution appears
- for `ui-standard` and `ui-critical`, require execution to preserve `ui-intent.md` aesthetic contracts, not just functional correctness
- for `ui-critical`, executor must reference `framework/frontend-aesthetics.md` anti-pattern registry during implementation

### During `review`

The orchestrator should inject stronger review gates when risk increases.

- `reviewer` is always the default review-stage owner
- request the reviewer to activate its critic profile when design drift, weak planning, or high-cost assumptions require a hard challenge gate
- code-changing tasks: request the reviewer to activate its tdd profile
- if TDD evidence is missing or violated, prefer return to `execute` unless the exception is explicit and justified
- explicit user-visible acceptance criteria: request the reviewer to activate its acceptance profile
- unclear or assumption-heavy reasoning: request the reviewer to activate its socratic profile
- auth, secrets, or permissions: request the reviewer to activate its security profile
- for `ui-standard` and `ui-critical`, apply a mandatory UI quality gate including aesthetic dimension checks and anti-pattern gate before verification
- for `ui-critical`, `designer` participation in review is mandatory, not optional

**Reviewer Reporting Rule**: the reviewer must report blockers to the orchestrator immediately upon discovery — it does not hold findings until the review stage closes. However, the reviewer does not decide what to do about them. The orchestrator owns that decision: route the problem to the appropriate agent (executor to fix, planner to revise, architect to redesign, debugger to diagnose, etc.), or accept the risk and continue. The orchestrator must act decisively — do not pause and ask the user unless the problem genuinely requires a policy or priority decision that only the user can make. The orchestrator must not suppress or silently defer reviewer blocker reports.

### During `verify`

- add `test-engineer` when the evidence set depends heavily on test quality or regression coverage
- for `ui-critical`, verify aesthetic contract evidence coverage — aesthetic gaps should produce `INCOMPLETE`, not `PASS`

### During `finish`

- add `release-curator` when the finish package, install surface, release notes, or delivery-facing structure still needs cleanup after a successful `PASS`
- during `finish`, `release-curator` may polish finish-facing artifacts but must not reopen product implementation scope

Use a simple threshold model:

- `low-risk`: narrow team
- `medium-risk`: add one specialist tied to the active risk
- `high-risk`: add the required specialists and record the reason in state and scorecard

## Native Team Execution Rule

The orchestrator may use native Claude Code agent teams only inside `execute`, and only when the approved plan declares:

- `execution_mode=team`
- a clean `conflict_domain`
- `touched_files` or an explicit file boundary
- a `merge_owner`

If these are missing, the orchestrator should fall back to single-owner execution.

## Learning Closure Rule

Every meaningful run must leave explicit reusable learning behind.

- a meaningful run is any run with an approved `plan` or any run that entered `execute`
- `finish` must create `retrospective.md`
- `improvement_action` must name the next product-improvement action or explicitly mark it as deferred
- delivery runs may capture product-improvement work, but must not silently expand into unrelated `SuperTeam` changes unless the task itself is a `SuperTeam` self-improvement task

## Frontend Aesthetics Pipeline Rule

For `ui-standard` and `ui-critical` work, the UI Intent Pipeline and aesthetic substance from `framework/frontend-aesthetics.md` are unified into a single cross-stage contract:

- `clarify` must capture design thinking seeds: purpose, tone seed, differentiation seed
- `design` must produce both `design.md` and `ui-intent.md` with full aesthetic contract sections
- `plan` must translate UI intent into execution and verification constraints, including aesthetic implementation complexity
- `execute` must record UI intent preservation notes with aesthetic compliance evidence
- `review` must apply a UI quality gate with aesthetic dimension checks and anti-pattern gate
- `verify` must confirm UI intent evidence coverage including aesthetic contract verification
- `finish` must summarize the final UI intent outcome including aesthetic quality assessment

Binding aesthetic principles:

- the aesthetic direction must be bold and intentional, never generic or template-like
- the anti-pattern registry is a binding quality standard — mandatory violations are blocking review findings
- implementation complexity must match the aesthetic vision — this is a formal contract, not a suggestion
- every frontend project must produce something distinctive — convergence on the same choices across projects is itself an anti-pattern

## Language Boundary Rule

- user-facing summary prose should be Chinese-first
- schema keys, verdict names, status fields, and execution-facing prompts should be English-first

## Pause And Escalation Conditions

The orchestrator should stop and surface a human decision when:

- design or plan has been revised 3 times without convergence
- repair cycle count exceeds 3
- security-sensitive work needs a policy decision
- the verifier reports `INCOMPLETE` because required evidence cannot be produced safely
- multiple valid design directions remain and preferences materially affect the outcome
- the aesthetic direction requires a fundamental pivot that would invalidate existing implementation

## Status + Trace (hook-maintained)

`.superteam/state/current-run.json` schema (33+ fields) is validated by `validator_current_run_json.py`. The orchestrator updates the semantic fields (`current_stage`, `last_completed_stage`, `plan_quality_gate`, `ui_weight`, `improvement_action`, etc.); the hook layer stamps `last_updated`, rejects invalid stage transitions, and auto-syncs `inspector_trace_path` / `inspector_trace_events` / `inspector_report_status`.

Inspector trace events (`stage_enter`, `stage_exit`, `agent_spawn`, `agent_stop`, `gate_check_report`, `gate_decision_observed`, `discrepancy_observed`, `override_recorded`, ...) are auto-emitted by `post_agent_trace_writer.py` — orchestrator does not manually write them. Agents may still emit their own domain events (`error_occur`, `fix_apply`, `command_exec`, `test_result`, `review_finding`, `plan_deviation`, `artifact_write`).

`activity-trace.md` continuity checkpoints during `clarify` / `design` / `plan` are validated by `validator_activity_trace.py`; missing checkpoints block the next stage transition.

## Inspector Analysis Rule

The Inspector monitors team behavior — not project quality. It never interrupts. All Inspector output is post-run.

Before producing `finish.md`, the orchestrator must:

1. Trigger Inspector post-run analysis of the complete trace file
2. Wait for the Inspector reports at `.superteam/inspector/reports/<task-slug>-report.html` and `.superteam/inspector/reports/<task-slug>-report.md`
3. Include a "Inspector Summary" section in `finish.md` with: run statistics, collaboration diagram reference, and count of problems detected
4. Acknowledge every problem record from the Inspector report: `acknowledged` (team is aware, will address next run), `addressed` (fixed in this run's retrospective), or `disputed` (with evidence it is not a real problem)
5. If any `critical` problem records exist, they must appear prominently in the retrospective

For runs that end in `failed` or `cancelled`, the orchestrator should still trigger a partial Inspector analysis and acknowledge the resulting problem records in the terminal handoff or retrospective note, since `finish` will not run.

**Important**: the Inspector does not evaluate deliverable quality. The Reviewer owns that. The Inspector evaluates whether the team worked correctly — collaboration patterns, efficiency, role compliance, trace completeness.

## Completion Rule

A run is complete only when all of the following exist:

- `project-definition.md`
- `activity-trace.md`
- `solution-options.md`
- `solution-landscape.md`
- `design.md`
- `plan.md`
- `execution.md`
- `review.md`
- `verification.md` with `PASS`
- `scorecard.md`
- `finish.md`
- `retrospective.md`
- Inspector reports at `.superteam/inspector/reports/<task-slug>-report.html` and `.superteam/inspector/reports/<task-slug>-report.md`

For `ui-standard` and `ui-critical` tasks, also require `ui-intent.md` with complete aesthetic contract sections.
