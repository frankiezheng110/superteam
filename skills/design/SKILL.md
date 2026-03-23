---
name: superteam:design
description: Produce or refine the SuperTeam design artifact. Use when a task has been clarified and needs an approved design before planning or implementation.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Design

Create or refine the design for:

`$ARGUMENTS`

## Read First

- `framework/skill-common-rules.md`
- `framework/frontend-aesthetics.md` when `ui_weight` is `ui-standard` or `ui-critical`

## Required Files

- `.superteam/runs/<task-slug>/design.md`
- `.superteam/runs/<task-slug>/handoffs/02-design-to-plan.md`
- `.superteam/runs/<task-slug>/ui-intent.md` for `ui-standard` and `ui-critical` tasks
- `.superteam/runs/<task-slug>/design-system.md` when `design-consultation` is used

## Design Requirements

- define boundaries and responsibilities
- explain important tradeoffs
- note rejected alternatives when relevant
- capture risks that planning must respect
- record approval status, approved by, and approval date
- when UI is present, keep structural design and UI intent aligned but distinct
- for `ui-standard` and `ui-critical`, produce an approval-ready `ui-intent.md` alongside `design.md`

## Frontend Aesthetics Design (ui-standard / ui-critical)

When the task is `ui-standard` or `ui-critical`:

- **Select a bold aesthetic direction** using the Design Thinking Framework from `framework/frontend-aesthetics.md`
- **Commit to a differentiation target** — the one element that makes this interface unforgettable
- **Produce aesthetic contract sections in `ui-intent.md`**: Aesthetic Direction, Typography Contract, Color Contract, Motion Contract, Spatial Contract, Visual Detail Contract, Anti-Pattern Exclusions. See `framework/frontend-aesthetics.md` for dimension details and anti-pattern registry.
- **State implementation complexity direction** — elaborate or restrained — so planner and executor know the expected code depth

For `ui-critical` tasks, the `designer` agent should be actively involved.

## Rules

- do not implement the task in this stage
- pull in the `architect` agent when appropriate
- activate the reviewer's critic profile when the reasoning feels weak or under-argued
- do not advance to planning until the design is reviewable and approved
- if `design-consultation` exists, consume it as design support input
- do not allow `plan` to start for UI work if `ui-intent.md` is missing or lacks required aesthetic contract sections
- the aesthetic direction must be bold and intentional — generic choices are a design failure
