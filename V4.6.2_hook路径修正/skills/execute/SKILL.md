---
name: execute
description: Execute an approved SuperTeam plan. Use when design and plan already exist and implementation should proceed with recorded local evidence.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Execute

Execute the approved plan for:

`$ARGUMENTS`

## Read First

- `framework/skill-common-rules.md`
- `framework/verification-and-fix.md`
- `framework/frontend-aesthetics.md` when `ui_weight` is `ui-standard` or `ui-critical`

## Required Files

- `.superteam/runs/<task-slug>/plan.md`
- `.superteam/runs/<task-slug>/execution.md`
- `.superteam/runs/<task-slug>/handoffs/04-execute-to-review.md`
- `.superteam/runs/<task-slug>/ui-intent.md` when UI intent is required

## Execution Rules

- do not proceed unless design and plan exist
- implement from the approved plan, not from memory alone
- capture what changed, what did not, and what remains uncertain
- include fresh local self-check evidence
- escalate if the plan is wrong or architecture must change materially
- treat test-first as the default for code changes
- treat code-changing work as `red -> green -> refactor` by default
- if implementation happened before a failing test existed, stop and escalate the TDD violation
- record touched files during execution
- if the plan says `execution_mode=team`, use `/superteam:team-execute` when available
- recommend `/superteam:careful` or `/superteam:guard` for destructive or production-facing work

## Frontend Aesthetics Execution (ui-standard / ui-critical)

When implementing UI-bearing work, follow the binding execution rules from `framework/frontend-aesthetics.md`:

- implement from `ui-intent.md` as a formal contract, not just from functional plan text
- follow the five-dimension execution rules (typography, color, motion, spatial, visual detail) as specified in the framework
- actively check against the anti-pattern registry — stop and find alternatives if any mandatory anti-pattern (AP-01 through AP-05) would be introduced
- match code complexity to the aesthetic vision per the implementation complexity contract
- record UI intent preservation notes, including intentional degradations and unresolved mismatches
- record anti-pattern compliance in execution notes

## Parallelism Rule

If the approved plan uses `execution_mode=team` and agent teams are enabled, use `/superteam:team-execute`. Otherwise downgrade to `single` or return to `plan` to repair.

Execution does not advance directly to finish. It must go through `review` and then `verify`.
