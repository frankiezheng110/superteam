---
name: superteam:go
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
- `framework/role-contracts.md`
- `framework/verification-and-fix.md`
- `framework/frontend-aesthetics.md` when the task has UI-bearing work
- `framework/inspector.md`

Optional support skills: `design-consultation`, `careful`, `guard`, `strategic-compact`, `inspect`

## Workflow Contract

Follow this exact path:

`clarify -> design -> plan -> execute -> review -> verify -> finish`

Do not skip stages, even for small tasks.

Core roles: `orchestrator`, `planner`, `architect`, `executor`, `reviewer`, `verifier`
Mandatory cross-cutting role: `inspector` (activated automatically at finish)

## Runtime Artifact Rules

Create or update a run directory at `.superteam/runs/<task-slug>/` containing:

- `ui-intent.md` for `ui-standard` and `ui-critical` tasks (with aesthetic contract sections)
- `design.md`, `plan.md`, `execution.md`, `review.md`, `verification.md`, `scorecard.md`
- `finish.md` when complete
- `retrospective.md` for meaningful completed runs
- `handoffs/` with stage-to-stage notes

Initialize Inspector trace at `.superteam/inspector/traces/<task-slug>.jsonl` when `clarify` starts. Emit trace events per `framework/inspector.md` throughout the run.

## Stage Rules

- `clarify`: capture objective, constraints, success criteria, `ui_weight`, design thinking seeds for UI work, and `handoffs/01-clarify-to-design.md`
- `design`: create `design.md`, create `ui-intent.md` with aesthetic contracts when required, record approval, write `handoffs/02-design-to-plan.md`
- `plan`: create `plan.md` with exact files, test-first steps, verification commands, aesthetic implementation constraints when UI, record approval, write `handoffs/03-plan-to-execute.md`
- `execute`: implement from approved plan and `ui-intent.md` contracts, follow `framework/frontend-aesthetics.md` execution rules, write `handoffs/04-execute-to-review.md`
- `review`: create `review.md`, use `reviewer` with specialist profiles as needed, apply UI quality gate when required, write `handoffs/05-review-to-verify.md`
- `verify`: create `verification.md`, issue `PASS`/`FAIL`/`INCOMPLETE`, verify aesthetic contract evidence when required
- `finish`: only after `PASS`, trigger Inspector analysis to generate run report, create `finish.md` with Inspector summary and aesthetic quality assessment when relevant, create `retrospective.md`, write `handoffs/06-verify-to-finish.md`
- maintain `scorecard.md` as a derived operator summary once a real plan exists

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
2. An Inspector report at `.superteam/inspector/reports/<task-slug>-report.md` — generated before `finish.md`
3. All improvement tickets must be acknowledged in `finish.md` (applied / deferred with reason / rejected with evidence)

This is non-negotiable. No run completes without an Inspector report.

## Completion Standard

All seven stages must be represented in run artifacts, verification must have a real `PASS`, meaningful runs must include `retrospective.md`, and an Inspector report must exist. For UI work, `ui-intent.md` with complete aesthetic contracts and anti-pattern gate clearance are also required.
