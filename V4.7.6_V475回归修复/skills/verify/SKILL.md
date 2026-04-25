---
name: verify
description: Run an independent SuperTeam verification pass. Use after execution to produce PASS, FAIL, or INCOMPLETE with fresh evidence.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Verify

Verify this run:

`$ARGUMENTS`

## Read First

- `framework/skill-common-rules.md`
- `framework/state-and-resume.md`
- `framework/verification-and-fix.md`
- `framework/frontend-aesthetics.md` when `ui_weight` is `ui-standard` or `ui-critical`

## Required Files

- `.superteam/runs/<task-slug>/execution.md`
- `.superteam/runs/<task-slug>/review.md`
- `.superteam/runs/<task-slug>/verification.md`
- `.superteam/runs/<task-slug>/ui-intent.md` for `ui-standard` and `ui-critical` tasks

## Verification Rules

- verdict must be one of: `PASS`, `FAIL`, `INCOMPLETE`
- require fresh evidence — tie the verdict to success criteria and plan requirements
- if fixable, create a minimal fix package and send work back to execution
- if evidence is missing, return `INCOMPLETE`
- if the plan is structurally wrong, escalate back toward planning
- for code-changing work, verify the TDD evidence chain; missing or unbelievable TDD evidence should not quietly pass as healthy execution
- state what is proven done, what risks remain, and whether `finish` is ready
- synchronize `.superteam/state/current-run.json` with verdict, readiness, evidence freshness, delivery confidence, `learning_status`, and `improvement_action`
- refresh `scorecard.md` from the latest verification state
- if team mode was used, verify merge ownership and file boundaries stayed inside the plan contract

## Frontend Aesthetics Verification (ui-standard / ui-critical)

Verify aesthetic contract compliance per `framework/frontend-aesthetics.md`:

- **Evidence coverage**: confirm each aesthetic section in `ui-intent.md` (typography, color, motion, spatial, visual detail) has real supporting evidence in the implementation
- **Anti-pattern gate**: confirm no mandatory violations (AP-01 through AP-05) exist. Record result as `clear` or `block`.
- **Complexity match**: confirm implementation complexity matches the aesthetic vision
- For `ui-critical`: missing aesthetic evidence → `INCOMPLETE`, anti-pattern gate block → `FAIL`

Default check areas: build, tests, diagnostics/lint, acceptance criteria, review blocker resolution, artifact completeness.

Verification must not substitute for the missing `review` stage.

## Loop Limit

After 3 failed verification-driven repair cycles, escalate to the orchestrator for re-plan, scope reduction, or termination.
