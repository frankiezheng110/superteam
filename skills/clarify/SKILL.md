---
name: clarify
description: Clarify a task before design. Use when the request is ambiguous, the success criteria are weak, or a SuperTeam run needs a proper clarify-stage artifact.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Clarify

Clarify this task:

`$ARGUMENTS`

## Read First

- `framework/skill-common-rules.md`
- `framework/development-solutions.md`

## Your Goal

Produce the clarify-stage output for a SuperTeam run.

If this skill is invoked after later stages already happened, treat it as a `clarify` supplement unless the orchestrator explicitly upgrades it into rollback.

Write or update:

- `.superteam/runs/<task-slug>/project-definition.md`
- `.superteam/runs/<task-slug>/activity-trace.md`
- `.superteam/runs/<task-slug>/handoffs/01-clarify-to-design.md`

## Required Output

- one-sentence answer to: what exactly should this project do?
- core task list
- input/output shape
- explicit constraints
- non-goals
- success criteria
- unresolved questions, if any
- approval status placeholder for the next stage
- explicit user approval record for stage closure
- reviewer continuity checkpoint
- `ui_weight` when UI is present
- primary experience goal when UI is present

## Frontend Aesthetics Discovery (ui-standard / ui-critical)

When the task has a user-facing interface classified as `ui-standard` or `ui-critical`, also capture the Design Thinking seeds from `framework/frontend-aesthetics.md`:

- **Purpose seed**: What problem does this interface solve? Who uses it? What is the primary experience success condition?
- **Tone seed**: Initial aesthetic direction preference — capture what the user wants or what the context suggests. Reference the tone spectrum in `framework/frontend-aesthetics.md` but do not force a choice yet.
- **Differentiation seed**: What should make this interface unforgettable? What is the one thing someone should remember?
- **Constraint seed**: Technical framework, performance, accessibility, or device requirements that constrain aesthetic choices.

These seeds become formal inputs for the `design` stage and `design-consultation` when activated.

## Rules

- ask at most one user question at a time if truly blocked
- do not ask for repo facts you can discover yourself
- keep the artifact compact and actionable
- do not start design or implementation in this stage
- direct user participation is mandatory in this stage
- do not close this stage until explicit user approval is recorded
- keep user-facing clarify prose Chinese-first when the user is Chinese-speaking
- classify UI impact as `ui-none`, `ui-standard`, or `ui-critical` when the task has a user-facing interface
- when UI is present, capture who uses it and the top experience success condition
- when the request is clearly UI-heavy and design-system direction is missing, recommend `/superteam:design-consultation`
- for `ui-critical` tasks, recommend `/superteam:design-consultation` by default — aesthetic direction is too important to leave to chance
- capture design thinking seeds (purpose, tone, differentiation, constraints) for `ui-standard` and `ui-critical` work so that aesthetic intent begins in clarify, not later
- update `activity-trace.md` with key user answers and the Reviewer continuity checkpoint before closing the stage
