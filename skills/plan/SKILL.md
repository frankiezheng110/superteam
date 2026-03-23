---
name: superteam:plan
description: Create the SuperTeam execution plan. Use when design is approved and the task needs a concrete, testable, execution-ready plan.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Plan

Plan this task:

`$ARGUMENTS`

## Read First

- `framework/skill-common-rules.md`
- `framework/frontend-aesthetics.md` when `ui_weight` is `ui-standard` or `ui-critical`

## Required Files

- `.superteam/runs/<task-slug>/plan.md`
- `.superteam/runs/<task-slug>/handoffs/03-plan-to-execute.md`
- `.superteam/runs/<task-slug>/ui-intent.md` for `ui-standard` and `ui-critical` tasks

## Planning Requirements

Every meaningful task should include:

- objective
- exact target files or a bounded search scope
- constraints
- implementation steps
- test-first step when code changes are involved
- verification commands
- expected outputs
- done signal
- blocker and escalation note

For `ui-standard` and `ui-critical` tasks, also include:

- `ui_weight`
- reference to `.superteam/runs/<task-slug>/ui-intent.md`
- `UI intent translation`
- `aesthetic_implementation_complexity` — whether the aesthetic vision demands elaborate or restrained implementation, derived from the aesthetic direction in `ui-intent.md`

## UI Intent Translation (ui-standard / ui-critical)

The plan must translate aesthetic contracts from `ui-intent.md` into concrete execution constraints:

- **Typography implementation** — which font files or CDN imports are needed, what CSS font-family declarations to use, what size/weight hierarchy to implement
- **Color implementation** — which CSS custom properties to define, what specific hex/hsl values to use, how the palette maps to component states
- **Motion implementation** — which technology to use (CSS transitions, CSS @keyframes, Motion library, GSAP), which elements get which animation, timing values
- **Spatial implementation** — which CSS layout approach (Grid, Flexbox, custom), breakpoint strategy, composition technique
- **Visual detail implementation** — which background treatments, shadow values, texture approaches, decorative element techniques
- **Anti-pattern avoidance** — explicit constraints on what must NOT be used (specific fonts, color patterns, layout templates)
- **Complexity contract** — whether this aesthetic demands elaborate code (maximalist) or precise minimal code (minimalist), so the executor knows the expected implementation depth

When collaboration boundaries matter, also include:

- `execution_mode`: `single` or `team`
- `conflict_domain`
- `touched_files` or expected file boundary
- `merge_owner`

Before `plan` is approved, assign a plan quality gate result:

- `pass` when all critical and support fields exist
- `at_risk` when all critical fields exist but one support field is missing
- `fail` when any critical field is missing

For `ui-critical` work: missing aesthetic implementation constraints in the UI intent translation should be treated as `at_risk` at minimum.

Critical fields:

- objective
- exact target files or bounded search scope
- implementation steps
- verification commands
- done signal

Support fields:

- constraints
- expected outputs
- blocker and escalation note

Recommended additions for strong plans:

- review focus note
- acceptance-risk note for user-visible behavior changes
- explicit fallback if test-first work is blocked by missing infrastructure

## Rules

- make the plan executable without hidden context
- allow exploratory work only when bounded search scope and clear exit conditions are written
- prefer atomic tasks over vague phases
- do not begin implementation in this skill
- record approval status before execution begins
- do not allow `execute` to start from a `fail` plan quality gate
- if any critical field is missing, set `plan_quality_gate=fail`
- create or refresh `scorecard.md` once a real plan exists
- only set `execution_mode=team` when the work splits cleanly by conflict domain or file boundary
- include explicit review expectations when a later review gate is likely to block the run
- for `ui-standard` and `ui-critical`, translate UI intent into implementation, review, and verification constraints instead of leaving it implicit
- for `ui-standard` and `ui-critical`, the plan must include anti-pattern avoidance as explicit execution constraints — do not assume the executor will independently consult the anti-pattern registry
