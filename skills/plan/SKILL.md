---
name: plan
description: Create the execution plan. Use when design is approved and the work needs a concrete, execution-ready plan.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Plan

Plan this task:

`$ARGUMENTS`

If this skill is invoked after `execute` or later stages already happened, treat it as a `plan` supplement unless the changed information clearly invalidates design decisions.

## Read First

- `framework/skill-common-rules.md`
- `framework/development-solutions.md`
- `framework/frontend-aesthetics.md` when `ui_weight` is `ui-standard` or `ui-critical`

## Required Files

- `.superteam/runs/<task-slug>/project-definition.md`
- `.superteam/runs/<task-slug>/activity-trace.md`
- `.superteam/runs/<task-slug>/solution-options.md`
- `.superteam/runs/<task-slug>/solution-landscape.md`
- `.superteam/runs/<task-slug>/design.md`
- `.superteam/runs/<task-slug>/plan.md`
- `.superteam/runs/<task-slug>/handoffs/03-plan-to-execute.md`
- `.superteam/runs/<task-slug>/ui-intent.md` when required

## Required Output

- objective
- exact target files or bounded search scope
- constraints
- implementation steps
- verification commands
- done signal
- plan quality gate
- explicit user approval before `execute`

For UI work, also include UI intent translation and anti-pattern avoidance.

## Rules

- keep the plan executable without hidden context
- do not begin implementation here
- do not silently reopen solution debate inside `plan`
- do not close this stage until explicit user approval is recorded
- append plan presentation and reviewer continuity to `activity-trace.md`
