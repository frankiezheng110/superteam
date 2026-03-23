# SuperTeam Stage Model

`SuperTeam` uses a forced seven-stage workflow:

`clarify -> design -> plan -> execute -> review -> verify -> finish`

This is the canonical order. Stages may loop backward when evidence fails, but they may not be skipped.

## Stage Table

| Stage | Purpose | Primary owner | Required output |
| --- | --- | --- | --- |
| `clarify` | turn a request into an understood objective | `planner` | clarified objective, constraints, success criteria |
| `design` | define structure, boundaries, and tradeoffs | `architect` | design artifact |
| `plan` | convert approved design into executable task packages | `planner` | plan artifact |
| `execute` | implement the approved plan and gather local evidence | `executor` | execution artifact |
| `review` | run challenge-oriented quality gates before verification | `inspector` | review artifact with blockers or clearance |
| `verify` | independently judge the result against fresh evidence | `verifier` | PASS / FAIL / INCOMPLETE verification artifact |
| `finish` | package the verified result for handoff or delivery | `orchestrator` | finish artifact, retrospective, and final handoff |

## Transition Rules

- `clarify -> design` only when scope, constraints, and success criteria are explicit enough to design.
- `design -> plan` only when the design is approved.
- `plan -> execute` only when the task packages are concrete, `plan_quality_gate` is not `fail`, and verification steps are defined.
- `execute -> review` only when execution output and local evidence exist.
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
- `design` advances only after `architect` output and approval are recorded.
- `plan` advances only after `planner` output and approval are recorded.
- `review` may block the run but does not replace verification.
- `verify` verdict authority belongs only to `verifier`.
- `finish` starts only after a recorded `PASS`.

## Stage Output Discipline

- `clarify`, `design`, `plan`, `execute`, `review`, `verify`, and `finish` must each leave an artifact.
- once a plan exists, the run should also maintain a derived `scorecard.md` for operator visibility.
- missing artifacts are treated as an incomplete stage, not as an informal success.
- the orchestrator must keep stage state synchronized with `state/current-run.json`.
- persistent roles may participate across stages, but only artifact-backed context counts as authoritative workflow memory.
- every stage transition must produce a trace event in the Reviewer trace file per `framework/reviewer.md`.

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
