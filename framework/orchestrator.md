# SuperTeam Orchestrator

This document defines the top-level orchestration contract for `SuperTeam`.

## Forced Stage Order

The orchestrator must enforce this order:

`clarify -> design -> plan -> execute -> review -> verify -> finish`

The order is mandatory. Small tasks may use shorter artifacts, but they still pass through the same sequence.

## What The Orchestrator Owns

- decide which stage is active
- decide which agent owns that stage
- record approvals for `design` and `plan`
- prevent execution without an approved plan
- enforce the plan quality gate before `execute`
- maintain `.superteam/state/current-run.json`
- maintain a derived `scorecard.md` for operator visibility
- route captured learning into an explicit improvement action
- initialize and maintain the Reviewer trace file (`.superteam/reviewer/traces/<task-slug>.jsonl`)
- emit trace events at every stage transition, decision point, and quality gate
- trigger Reviewer analysis before producing `finish.md`
- acknowledge all Reviewer improvement tickets in the finish artifact
- choose the lightest valid execution mode: `single` or `team`
- recommend support skills only when stage, risk, and user intent justify them
- classify `ui_weight` and enforce the UI Intent Pipeline when UI is present
- enforce the Frontend Aesthetics Pipeline for `ui-standard` and `ui-critical` work
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

- skip stages for convenience
- replace the verifier's verdict with its own opinion
- hide blockers inside vague progress summaries
- let specialist workers redefine stage order
- silently convert delivery runs into unrelated product-refactor runs
- delegate its authority to another agent
- skip Reviewer trace emission or analysis
- suppress or soften Reviewer findings

## Stage Entry And Exit Gates

| Stage | Entry gate | Exit gate |
| --- | --- | --- |
| `clarify` | task exists but success criteria are not yet explicit | clarified objective, constraints, and success criteria are written |
| `design` | clarify artifact exists | design artifact approved |
| `plan` | design artifact approved | plan artifact approved, quality-gated, and executable |
| `execute` | approved plan exists | execution artifact and local evidence exist |
| `review` | execution artifact exists | review result is `CLEAR` or `CLEAR_WITH_CONCERNS` |
| `verify` | review artifact exists | verifier issues `PASS`, `FAIL`, or `INCOMPLETE` |
| `finish` | verifier issued `PASS` | final handoff, retrospective, and Reviewer report are written |

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

## Recommended Stage Owners

| Stage | Default owner | Optional support |
| --- | --- | --- |
| `clarify` | `planner` | `analyst`, `researcher` |
| `design` | `architect` | `designer`, `design-consultation` |
| `plan` | `planner` | `architect`, `prd-writer` |
| `execute` | `executor` | `debugger`, `test-engineer`, `designer`, `writer` |
| `review` | `inspector` | `designer` (inspector activates specialist profiles internally) |
| `verify` | `verifier` | `test-engineer` |
| `finish` | `orchestrator` | `writer`, `verifier`, `reviewer` |

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
- recommend `strategic-compact` after `plan` closes when the next phase is a large execution push

### During `clarify` and `design`

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
- recommend `careful` or `guard` when destructive or high-risk execution appears
- for `ui-standard` and `ui-critical`, require execution to preserve `ui-intent.md` aesthetic contracts, not just functional correctness
- for `ui-critical`, executor must reference `framework/frontend-aesthetics.md` anti-pattern registry during implementation

### During `review`

The orchestrator should inject stronger review gates when risk increases.

- `inspector` is always the default review-stage owner
- request the inspector to activate its critic profile when design drift, weak planning, or high-cost assumptions require a hard challenge gate
- code-changing tasks: request the inspector to activate its tdd profile
- explicit user-visible acceptance criteria: request the inspector to activate its acceptance profile
- unclear or assumption-heavy reasoning: request the inspector to activate its socratic profile
- auth, secrets, or permissions: request the inspector to activate its security profile
- for `ui-standard` and `ui-critical`, apply a mandatory UI quality gate including aesthetic dimension checks and anti-pattern gate before verification
- for `ui-critical`, `designer` participation in review is mandatory, not optional

**Inspector Reporting Rule**: the inspector must report blockers to the orchestrator immediately upon discovery — it does not hold findings until the review stage closes. However, the inspector does not decide what to do about them. The orchestrator owns that decision: route the problem to the appropriate agent (executor to fix, planner to revise, architect to redesign, debugger to diagnose, etc.), or accept the risk and continue. The orchestrator must act decisively — do not pause and ask the user unless the problem genuinely requires a policy or priority decision that only the user can make. The orchestrator must not suppress or silently defer inspector blocker reports.

### During `verify`

- add `test-engineer` when the evidence set depends heavily on test quality or regression coverage
- for `ui-critical`, verify aesthetic contract evidence coverage — aesthetic gaps should produce `INCOMPLETE`, not `PASS`

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

## Status Update Rule

After every stage transition, update `.superteam/state/current-run.json` with:

- current stage
- last completed stage
- overall status
- repair cycle count
- blocker summary when relevant
- latest handoff path
- blocked reason when blocked
- next action
- blocker owner when blocked
- readiness for `execute`, `verify`, and `finish`
- evidence freshness
- delivery confidence
- plan quality gate
- learning status
- improvement action when relevant
- guard mode when relevant
- execution mode when relevant
- conflict domain when relevant
- merge owner when relevant
- `ui_weight` when relevant
- `ui_intent_status` when relevant
- `ui_quality_gate_status` when relevant
- `aesthetic_direction` when relevant
- `anti_pattern_gate_status` when relevant
- active task id when relevant
- active specialists when relevant
- specialist reason when non-default specialists are active
- `reviewer_trace_path` from run start
- `reviewer_trace_events` count
- `reviewer_report_status` when relevant
- `reviewer_open_problems` when relevant

Then refresh `scorecard.md` from the current state and latest artifacts.

## Reviewer Trace Emission Rule

The orchestrator must emit trace events to `.superteam/reviewer/traces/<task-slug>.jsonl` per `framework/reviewer.md`:

- **Run start**: emit `stage_enter` for `clarify` — this initializes the trace file
- **Every stage transition**: emit `stage_exit` for the departing stage and `stage_enter` for the arriving stage
- **Every non-trivial decision**: emit `decision_made` with options considered and rationale
- **Every specialist injection**: emit `specialist_inject` with the reason
- **Every quality gate check**: emit `gate_check` with the result
- **Every repair cycle**: emit `repair_cycle` with the failure reason and return target
- **Every user intervention**: emit `user_intervention` with a summary
- **Run termination**: emit `stage_exit` for the final stage regardless of outcome

Individual agents are responsible for emitting their own event types (`error_occur`, `fix_apply`, `command_exec`, `test_result`, `review_finding`, `plan_deviation`, `artifact_write`) as defined in `framework/reviewer.md`.

Trace emission must never be skipped "for convenience" or "because the run is small". Every run produces a trace.

## Reviewer Analysis Rule

The Reviewer monitors team behavior — not project quality. It never interrupts. All Reviewer output is post-run.

Before producing `finish.md`, the orchestrator must:

1. Trigger Reviewer post-run analysis of the complete trace file
2. Wait for the Reviewer report at `.superteam/reviewer/reports/<task-slug>-report.md`
3. Include a "Reviewer Summary" section in `finish.md` with: run statistics, collaboration diagram reference, and count of problems detected
4. Acknowledge every problem record from the Reviewer report: `acknowledged` (team is aware, will address next run), `addressed` (fixed in this run's retrospective), or `disputed` (with evidence it is not a real problem)
5. If any `critical` problem records exist, they must appear prominently in the retrospective

For runs that end in `failed` or `cancelled`, the orchestrator should still trigger a partial Reviewer analysis.

**Important**: the Reviewer does not evaluate deliverable quality. The Inspector owns that. The Reviewer evaluates whether the team worked correctly — collaboration patterns, efficiency, role compliance, trace completeness.

## Completion Rule

A run is complete only when all of the following exist:

- `design.md`
- `plan.md`
- `execution.md`
- `review.md`
- `verification.md` with `PASS`
- `scorecard.md`
- `finish.md`
- `retrospective.md`
- Reviewer report at `.superteam/reviewer/reports/<task-slug>-report.md`

For `ui-standard` and `ui-critical` tasks, also require `ui-intent.md` with complete aesthetic contract sections.
