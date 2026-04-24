---
name: careful
description: Activate explicit caution for destructive or high-risk work. Use when the task touches production, destructive actions, data migrations, secrets, permissions, or other irreversible operations.
argument-hint: [task or risk context]
disable-model-invocation: true
---

# SuperTeam Careful

Use this skill to activate an explicit caution mode for high-risk work.

## Read First

- `framework/skill-common-rules.md`
- `framework/state-and-resume.md`

## Purpose

This skill adds a stronger caution layer around execution.

It does not replace `review`, `verify`, or the inspector's security profile.

## Trigger Rules

- use when the user explicitly asks for careful mode
- recommend for production, deletion, migration, force-push, secret handling, permission changes, or other irreversible operations
- use it only as an `execute` or fix-package safety helper

## Rules

- restate the high-risk action before executing it
- verify scope, target, and rollback or recovery expectations before destructive work
- escalate to the user when the action is destructive, production-facing, or policy-sensitive
- record that `careful` mode is active in the run status when a run exists
- prefer English-first risk labels and Chinese-first user explanations
- never treat `careful` as a replacement for `review` or `verify`

## Status Guidance

When active, treat `careful` as:

- an execution helper
- a reminder to slow down and confirm intent
- a stricter standard for evidence and operator awareness
