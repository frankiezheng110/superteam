---
name: design
description: Produce or refine the SuperTeam design artifact. Use when a task has been clarified and needs an approved design before planning or implementation.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Design

Create or refine the design for:

`$ARGUMENTS`

If this skill is invoked after later stages already happened, treat it as a `design` supplement that reopens the option loop unless the orchestrator explicitly upgrades it into rollback.

## Read First

- `framework/skill-common-rules.md`
- `framework/development-solutions.md`
- `framework/solution-search.md`
- `framework/frontend-aesthetics.md` when `ui_weight` is `ui-standard` or `ui-critical`

## Required Inputs

- `.superteam/runs/<task-slug>/project-definition.md`
- `.superteam/runs/<task-slug>/activity-trace.md`
- `.superteam/runs/<task-slug>/design-system.md` when `design-consultation` is used

## Required Outputs

- `.superteam/runs/<task-slug>/solution-options.md`
- `.superteam/runs/<task-slug>/solution-landscape.md`
- `.superteam/runs/<task-slug>/design.md`
- `.superteam/runs/<task-slug>/handoffs/02-design-to-plan.md`
- `.superteam/runs/<task-slug>/ui-intent.md` for `ui-standard` and `ui-critical` tasks

## Design Requirements

- define boundaries and responsibilities
- record one participation mode for this stage: `co-create`, `observe`, or `decision-only`
- generate candidate development solutions before selecting one
- include both whole-project solution choices and important per-domain solution choices
- include internally generated options even when strong external references exist
- extract requirement anchors before outward search: functions, workflows, roles, constraints, and decision points
- for meaningful work, run search breadth and search validation inside one unified option loop before closing the stage
- for brand-new products, start with keyword-driven web search and GitHub search around the clarified anchors; use official docs later for dependency/platform validation
- explain important tradeoffs
- note rejected alternatives when relevant
- capture risks that planning must respect
- record approval status, approved by, and approval date
- record the explicit user decision that closes the option loop and unlocks shaping work
- when UI is present, keep structural design and UI intent aligned but distinct
- for `ui-standard` and `ui-critical`, produce an approval-ready `ui-intent.md` alongside `design.md`
- append major solution decisions and inspector checkpoints to `activity-trace.md`

## Mandatory Internal Structure

Run this stage in order:

1. `Option Loop` - combine internal options, external evidence, user-supplied options, unified comparison, challenge, and user decision
2. `Solution Shaping` - turn the chosen direction into `design.md` and `ui-intent.md` when required

Do not enter `Solution Shaping` until the user confirms that solution discussion is complete enough to commit to a direction.

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
- use the `researcher` agent when external evidence would materially improve the quality of the decision
- keep `inspector` attached for continuity checkpoints
- do not advance to planning until the design is reviewable and approved
- if `design-consultation` exists, consume it as design support input
- do not allow `plan` to start for UI work if `ui-intent.md` is missing or lacks required aesthetic contract sections
- the aesthetic direction must be bold and intentional — generic choices are a design failure
- do not let one quick search sweep substitute for meaningful option-loop evidence gathering and validation
- do not let "official docs first" become a cargo-cult rule for new products that have no official surface yet
