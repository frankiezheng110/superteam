---
name: go
description: Run the full seven-stage SuperTeam workflow for a task in Claude Code. Use when the user wants end-to-end delivery with strict stage order, specialist reviews, verification, and final handoff.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Go

Run the full SuperTeam workflow for:

`$ARGUMENTS`

## Read These First

- `framework/skill-common-rules.md`
- `framework/orchestrator.md`
- `framework/development-solutions.md`
- `framework/role-contracts.md`
- `framework/verification-and-fix.md`
- `framework/frontend-aesthetics.md` when the task has UI-bearing work
- `framework/reviewer.md`

Optional support skills: `design-consultation`, `careful`, `guard`, `strategic-compact`, `inspect`

Post-execute polish workers: `simplifier`, `doc-polisher`, `release-curator`

## Workflow Contract

Follow this exact path:

`clarify -> design -> plan -> execute -> review -> verify -> finish`

Do not skip stages, even for small tasks.

Compact gate map:

- `G1` = close `clarify`
- `G2` = leave the design option loop and enter shaping
- `G3` = close `plan` and start `execute`

Core roles: `orchestrator`, `planner`, `architect`, `executor`, `reviewer`, `verifier`
Mandatory support role: `inspector` (continuity checkpoints in the first three stages + post-run audit)

## Runtime Artifact Rules

Create or update a run directory at `.superteam/runs/<task-slug>/` containing:

- `project-definition.md`
- `activity-trace.md`
- `solution-options.md`
- `solution-landscape.md`
- `ui-intent.md` for `ui-standard` and `ui-critical` tasks (with aesthetic contract sections)
- `design.md`, `plan.md`, `execution.md`, `review.md`, `verification.md`, `scorecard.md`
- `polish.md`
- `finish.md` when complete
- `retrospective.md` for meaningful completed runs
- `handoffs/` with stage-to-stage notes

Initialize Inspector trace at `.superteam/inspector/traces/<task-slug>.jsonl` when `clarify` starts. Emit trace events per `framework/inspector.md` throughout the run.

## Stage Rules

- `clarify`: create `project-definition.md`, update `activity-trace.md`, require direct user participation, capture objective, constraints, success criteria, `ui_weight`, design thinking seeds for UI work, record explicit user approval, and write `handoffs/01-clarify-to-design.md`
- `design`: create `solution-options.md`, `solution-landscape.md`, and `design.md`; create `ui-intent.md` with aesthetic contracts when required; extract requirement anchors first, then run one interaction-heavy option loop that combines internal options, anchor-driven layered search evidence, user-supplied options, comparison, challenge, and user decision; for brand-new products prioritize keyword web search and GitHub keyword search before official dependency validation; do not enter shaping until the user confirms that solution discussion is complete enough to commit to a direction; then run low-interaction shaping work and write `handoffs/02-design-to-plan.md`
- `plan`: consume `design.md`, `solution-options.md`, and `solution-landscape.md`; create `plan.md` with exact files, explicit `red -> green -> refactor` / test-first steps for code-changing work, verification commands, aesthetic implementation constraints when UI; present the final plan for review, record explicit user approval, and write `handoffs/03-plan-to-execute.md`
- `execute`: implement from approved plan and `ui-intent.md` contracts, follow `framework/frontend-aesthetics.md` execution rules, treat code-changing work as `red -> green -> refactor` by default, run local self-checks, then run the post-execute polish layer (`simplifier` for code changes by default, `doc-polisher` for changed docs when needed, `release-curator` for delivery-surface cleanup when needed), update `polish.md`, and write `handoffs/04-execute-to-review.md`
- `review`: create `review.md`, consume `polish.md`, use `reviewer` with specialist profiles as needed, enforce the TDD gate for code-changing work, apply UI quality gate when required, write `handoffs/05-review-to-verify.md`
- `verify`: create `verification.md`, issue `PASS`/`FAIL`/`INCOMPLETE`, verify the TDD evidence chain for code-changing work and aesthetic contract evidence when required
- `finish`: only after `PASS`, trigger Inspector analysis to generate the team-duty report, create `finish.md` with trace summary, Inspector summary, and aesthetic quality assessment when relevant, create `retrospective.md`, write `handoffs/06-verify-to-finish.md`
- maintain `scorecard.md` as a derived operator summary once a real plan exists

## Supplement Rule

After `plan` is approved and `execute` begins, the remaining workflow should run without further user involvement unless the user explicitly intervenes.

If the user later reopens `clarify`, `design`, or `plan`, treat that by default as `developer supplement`, not full rollback.

## Frontend Aesthetics Pipeline (ui-standard / ui-critical)

The full pipeline activates per `framework/frontend-aesthetics.md`: design thinking seeds in clarify → bold aesthetic direction in design → implementation constraints in plan → execution rules in execute → five-dimension quality gate in review → evidence coverage in verify → quality summary in finish.

For `ui-critical`, activate `design-consultation` by default during design.

## Status Rule

Keep `.superteam/state/current-run.json` synchronized per `framework/state-and-resume.md` as the canonical source.

User-facing summary prose Chinese-first; schema keys, verdict labels, and execution-facing terms English-first.

## Pause Rule

Pause only when: a real human decision is required, repair cycles exceeded the limit, security/deletion/billing/permission risk needs approval, or multiple valid aesthetic directions remain and user preference matters.

## Inspector Rule

Every run must produce:
1. A trace file at `.superteam/inspector/traces/<task-slug>.jsonl` — started at `clarify`, appended throughout
2. Inspector reports at `.superteam/inspector/reports/<task-slug>-report.html` and `.superteam/inspector/reports/<task-slug>-report.md` — generated before `finish.md`
3. All Inspector problem records must be acknowledged in `finish.md` (`acknowledged` / `addressed` / `disputed`)

This is non-negotiable. No run completes without a Inspector report.

## Completion Standard

All seven stages must be represented in run artifacts, `polish.md` must exist before `review`, verification must have a real `PASS`, meaningful runs must include `retrospective.md`, and a Inspector report must exist. For UI work, `ui-intent.md` with complete aesthetic contracts and anti-pattern gate clearance are also required.
