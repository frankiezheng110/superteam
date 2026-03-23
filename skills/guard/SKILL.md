---
name: superteam:guard
description: Activate maximum safety for high-risk work. Use when the task needs destructive-action caution plus an explicit edit boundary around the allowed scope.
argument-hint: [task or allowed scope]
disable-model-invocation: true
---

# SuperTeam Guard

Use this skill when the task needs maximum execution safety.

## Read First

- `framework/skill-common-rules.md`
- `framework/state-and-resume.md`

## Purpose

`guard` extends `careful` by adding explicit scope-boundary discipline.

It is useful when the task must stay inside one directory, subsystem, or approved file boundary.

## Trigger Rules

- use when the user explicitly asks for guard mode
- recommend when a risky task must stay inside one approved boundary
- prefer this over `careful` when edit-boundary control matters as much as command caution
- use it only as an `execute` or fix-package safety helper

## Rules

- apply all `careful` rules
- restate the allowed edit boundary before execution begins
- refuse silent drift outside the approved boundary; escalate instead
- align the boundary with `touched_files`, `conflict_domain`, and `merge_owner` when those fields exist
- record that `guard` mode is active in the run status when a run exists
- never treat `guard` as a replacement for `review`, `verify`, or the main workflow gates

## Output Expectation

When used inside a run, note:

- active boundary
- why guard mode was chosen
- whether any attempted action would have crossed the boundary
