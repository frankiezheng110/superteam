---
name: g1
description: Reopen Gate 1 for a project-definition supplement. Use when the user wants to add or correct goals, scope, key features, constraints, or non-goals after work has already moved on.
argument-hint: [supplement]
disable-model-invocation: true
---

# SuperTeam G1

Reopen `G1` for:

`$ARGUMENTS`

## Meaning

- `G1` = reopen `clarify`
- default to `developer supplement`, not `rollback`

## Required Effect

- update `.superteam/runs/<task-slug>/project-definition.md`
- append `.superteam/runs/<task-slug>/activity-trace.md`
- record the supplement in `.superteam/state/current-run.json`
- mark downstream artifacts for re-check based on impact

## Rules

- use this when project definition changed
- do not silently reopen `design` or `plan` without recording impact
- only upgrade to rollback when the new definition structurally invalidates too much downstream work
