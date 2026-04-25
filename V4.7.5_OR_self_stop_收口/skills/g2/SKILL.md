---
name: g2
description: Reopen Gate 2 for a design option-loop supplement. Use when the user wants to add a new solution idea, new constraint, or a missing requirement that should restart solution discussion.
argument-hint: [supplement]
disable-model-invocation: true
---

# SuperTeam G2

Reopen `G2` for:

`$ARGUMENTS`

## Meaning

- `G2` = reopen the `design` option loop
- default to `developer supplement`, not `rollback`

## Required Effect

- reopen the option loop before shaping work continues
- update `.superteam/runs/<task-slug>/solution-options.md`
- update `.superteam/runs/<task-slug>/solution-landscape.md`
- append `.superteam/runs/<task-slug>/activity-trace.md`
- record the supplement in `.superteam/state/current-run.json`

## Rules

- use this when solution discussion must restart
- keep shaping work separate until the new option loop is closed again
- only upgrade to rollback when the new input structurally invalidates too much downstream work
