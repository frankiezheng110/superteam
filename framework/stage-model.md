# SuperTeam Stage Model

`SuperTeam` uses a forced seven-stage workflow:

`clarify -> design -> plan -> execute -> review -> verify -> finish`

This is the canonical order. Stages may loop backward when evidence fails, but they may not be skipped.

## User-Facing Names For The First Three Stages

`SuperTeam` keeps the internal stage keys `clarify`, `design`, and `plan`, but the user-facing business names are:

- `clarify` = `Project Definition`
- `design` = `Development Solutions`
- `plan` = `Execution Plan`

These are not extra stages. They are the first three stages of the same seven-stage workflow.

## Participation Contract

- `clarify / Project Definition`: direct user participation is mandatory and the stage cannot close without explicit user approval
- `design / Development Solutions`: user participation may be `co-create`, `observe`, or `decision-only`; explicit user decision is required before the stage may leave the option loop and enter shaping work
- `plan / Execution Plan`: drafting is internal, the final plan is presented for review, and the stage cannot close without explicit user approval
- after `plan` is approved and `execute` starts, the remaining workflow should continue without further user involvement unless the user explicitly intervenes

`reviewer` must stay attached across the first three stages as a continuity auditor. This does not change Reviewer into a stage owner or blocker source.

## Stage Table

| Stage | Purpose | Primary owner | Required output |
| --- | --- | --- | --- |
| `clarify` | define exactly what the project should do | `orchestrator` | `project-definition.md`, clarify handoff, trace entries |
| `design` | generate, compare, and select development solutions | `orchestrator` | `design.md`, `solution-options.md`, `solution-landscape.md`, trace entries |
| `plan` | convert the selected solution into executable task packages | `orchestrator` | `plan.md`, plan handoff, trace entries |
| `execute` | implement the approved plan, gather local evidence, and leave a polish-ready handoff | `executor` | execution artifact and polish artifact |
| `review` | run challenge-oriented quality gates before verification | `inspector` | review artifact with blockers or clearance |
| `verify` | independently judge the result against fresh evidence | `verifier` | PASS / FAIL / INCOMPLETE verification artifact |
| `finish` | package the verified result for handoff or delivery | `orchestrator` | finish artifact, retrospective, and final handoff |

## Transition Rules

- `clarify -> design` only when `project-definition.md` clearly states what the project should do, direct user participation is recorded, explicit user approval is recorded, and Reviewer continuity notes are current.
- `design -> plan` only when the design is approved, `solution-options.md` and `solution-landscape.md` are current, major whole-project and per-domain decisions are explicit, the user decision that closed the option loop is recorded, and the stage has completed its shaping work.
- `plan -> execute` only when the task packages are concrete, `plan_quality_gate` is not `fail`, verification steps are defined, and explicit user approval of the final plan is recorded.
- `execute -> review` only when execution output, local evidence, and `polish.md` exist.
- `review -> verify` only when blocking review issues are either fixed or explicitly resolved.
- `verify -> finish` only on `PASS`.
- `verify -> execute` on fixable `FAIL`.
- `verify -> plan` when the failure proves the plan is wrong or incomplete.

## Frontend Aesthetics Gate

For `ui-standard` and `ui-critical` work, the following additional transition constraints apply:

- `design -> plan` requires approved `ui-intent.md` with aesthetic direction, typography, color, motion, spatial, and visual detail contracts
- `execute -> review` requires UI intent preservation notes including aesthetic compliance evidence
- `review -> verify` requires that the anti-pattern gate has no blocking violations

## Approval Authority

- `orchestrator` grants stage advancement authority.
- `clarify` advances only after direct user participation and explicit user approval are recorded.
- `design` advances only after the chosen solution, the user decision that closed the option loop, and shaping completion are recorded.

## User Closure Gates

Use three short gates:

- `G1 Definition`: end `clarify`
- `G2 Option`: leave the design option loop and enter shaping
- `G3 Plan`: end `plan` and start `execute`

After `Gate 3`, the remaining four stages should run without further user involvement unless the user explicitly intervenes.

## User Supplement Re-entry

The three gates are re-enterable.

- reopen `G1` when the project definition changes
- reopen `G2` when solution discussion must restart
- reopen `G3` when only the execution plan must change
- default to `developer supplement`, not `rollback`

## Approval Authority

- `orchestrator` grants stage advancement authority.
- `clarify` advances only after direct user participation and explicit user approval are recorded.
- `design` advances only after the chosen solution, the user decision that closed the option loop, and shaping completion are recorded.
- `plan` advances only after the final plan has been presented for review and explicit user approval is recorded.
- `review` may block the run but does not replace verification.
- `verify` verdict authority belongs only to `verifier`.
- `finish` starts only after a recorded `PASS`.

## Post-Execute Polish Bridge

`SuperTeam` may refine deliverables between `execute` and `review` without creating an eighth stage.

- `simplifier` refines changed code
- `doc-polisher` tightens changed docs and handoffs
- `release-curator` cleans delivery-facing structure or release surfaces within scope
- these workers write or update `.superteam/runs/<task-slug>/polish.md`
- if polish changes behavior-relevant files, fresh local checks are required before `review`
- `inspector` remains the sole owner of the `review` stage

## Stage Output Discipline

- `clarify`, `design`, `plan`, `execute`, `review`, `verify`, and `finish` must each leave an artifact.
- any run that reaches `review` must also leave `polish.md` documenting the post-execute refinement bridge
- once a plan exists, the run should also maintain a derived `scorecard.md` for operator visibility.
- missing artifacts are treated as an incomplete stage, not as an informal success.
- the orchestrator must keep stage state synchronized with `state/current-run.json`.
- persistent roles may participate across stages, but only artifact-backed context counts as authoritative workflow memory.
- every stage transition must produce a trace event in the Reviewer trace file per `framework/reviewer.md`.
- the first three stages must also update `.superteam/runs/<task-slug>/activity-trace.md` with human-readable continuity checkpoints.

## Bounded Fix Loop

The top-level path remains seven stages. Repair work loops back through the middle of the flow:

`execute -> review -> verify -> execute`

Rules:

- each verification failure must generate a new fix package;
- each retry must carry fresh evidence;
- the default maximum is 3 verification-driven repair cycles;
- exceeding the limit forces `orchestrator` escalation for re-plan, scope reduction, or termination.

## Terminal States

- `completed` - verification passed, finish artifacts and Reviewer report were produced
- `cancelled` - the workflow was intentionally stopped (partial Reviewer analysis still required)
- `failed` - the repair loop was exhausted or a hard blocker could not be resolved safely (partial Reviewer analysis still required)

## Evidence Rule

No stage may claim completion without the artifact and evidence required by `framework/stage-interface-contracts.md` and `framework/verification-and-fix.md`.
