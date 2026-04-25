---
name: g3
description: Reopen Gate 3 for an execution-plan supplement. Use when the user wants to change task order, execution scope, verification steps, or planning constraints without automatically reopening design.
argument-hint: [supplement]
disable-model-invocation: true
---

# SuperTeam G3

Reopen `G3` for:

`$ARGUMENTS`

## Meaning

- `G3` = reopen `plan`
- default to `developer supplement`, not `rollback`

## Required Effect

- update `.superteam/runs/<task-slug>/plan.md`
- append `.superteam/runs/<task-slug>/activity-trace.md`
- record the supplement in `.superteam/state/current-run.json`
- keep `design` closed unless the new input invalidates solution decisions

## Rules

- use this when only the execution plan must change
- do not reopen solution debate unless plan changes prove design is unstable
- only upgrade to rollback when the new plan input structurally invalidates too much downstream work
