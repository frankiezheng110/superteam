---
name: review
description: Run the dedicated SuperTeam review stage. Use after execution to apply challenge-oriented quality gates before independent verification.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Review

Review this run:

`$ARGUMENTS`

## Read First

- `framework/skill-common-rules.md`
- `framework/verification-and-fix.md`
- `framework/frontend-aesthetics.md` when `ui_weight` is `ui-standard` or `ui-critical`

## Required Files

- `.superteam/runs/<task-slug>/activity-trace.md`
- `.superteam/runs/<task-slug>/solution-options.md`
- `.superteam/runs/<task-slug>/solution-landscape.md`
- `.superteam/runs/<task-slug>/execution.md`
- `.superteam/runs/<task-slug>/polish.md`
- `.superteam/runs/<task-slug>/review.md`
- `.superteam/runs/<task-slug>/handoffs/05-review-to-verify.md`
- `.superteam/runs/<task-slug>/ui-intent.md` for `ui-standard` and `ui-critical` tasks

## Review Rules

- run a general `reviewer` pass by default
- activate the reviewer's specialist profiles as needed: critic (high-risk reasoning), security (auth/secrets/permissions), acceptance (user-facing criteria), tdd (test discipline), socratic (hidden assumptions)
- for code-changing work, enforce the TDD gate: failing test first, smallest green, then behavior-preserving refactor — unless an explicit exception exists
- inspect the post-execute polish layer for scope discipline and behavior preservation; `polish.md` is an input, not a substitute for review judgment
- for `ui-standard` and `ui-critical`, apply a mandatory UI quality gate before verification
- emit a clear recommendation: `CLEAR`, `CLEAR_WITH_CONCERNS`, or `BLOCK`
- cite blockers concretely so execution knows exactly what to repair
- keep the specialist profile set as small as practical for the active risk
- check whether execution drifted from selected Stage-2 whole-project or per-domain solution decisions when that drift matters
- check whether inspector continuity and trace expectations were actually maintained across the first three stages

## Frontend Aesthetics Quality Gate (ui-standard / ui-critical)

Apply the five-dimension aesthetic quality check and anti-pattern gate as defined in `framework/frontend-aesthetics.md`. Reference the project's `ui-intent.md` as the quality baseline.

- Check all five dimensions: typography, color, motion, spatial composition, visual detail
- Mandatory anti-patterns (AP-01 through AP-05): any violation is **blocking**
- Advisory anti-patterns (AP-06 through AP-10): non-blocking concerns
- Verify implementation complexity matches the aesthetic vision
- Treat loss of declared aesthetic intent as a real quality issue

For `ui-critical` work, `designer` participation in this quality gate is **mandatory**.

## Gate Rule

If the result is `BLOCK`, the workflow returns to execution before verification.
