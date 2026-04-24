# SuperTeam Skill Common Rules

Use this file as the shared baseline reference for `skills/**/SKILL.md`.

## Core References

Most skills should start from these documents:

- `framework/stage-model.md`
- `framework/stage-interface-contracts.md`
- `framework/runtime-artifacts.md`

Add these when the skill needs them:

- `framework/orchestrator.md` for routing, stage ownership, or specialist injection
- `framework/development-solutions.md` for Stage-2 solution generation, external search rules, or per-domain option work
- `framework/solution-search.md` for Stage-2 anchor extraction, keyword generation, layered search order, and evidence-card search discipline
- `framework/role-contracts.md` for role boundaries or review-profile logic
- `framework/state-and-resume.md` for status fields, resume behavior, or long-run continuity
- `framework/verification-and-fix.md` for review, verify, repair, or finish-adjacent behavior
- `framework/frontend-aesthetics.md` for UI-bearing work that needs aesthetic quality guidance
- `framework/reviewer.md` for trace emission, run analysis, and improvement tracking
- `framework/inspector.md` for review-stage quality checking, blocker escalation, and specialist profiles

## Shared Boundaries

- skills support the seven-stage workflow, they do not create new stages
- skills must not create a second authority source beside the orchestrator-led model
- stage progress should depend on artifacts, not hidden conversation memory
- user-facing prose is Chinese-first, execution-facing contract terms are English-first
- optional support skills may help a run, but they do not replace stage gates, review, or verify

## Stage-2 Search Integration

- Stage-2 outward search is anchor-driven: search the clarified problem, workflows, roles, constraints, and decision points — not the new project's name
- for brand-new products, the default first tier is `web keyword search` (`Google` or equivalent) plus `GitHub keyword search`
- official docs are a constraint-validation layer for dependencies and platforms, not the default starting point for a product that does not yet exist
- meaningful design work should usually include both a breadth pass and a validation pass
- search results must map back to anchors and candidate options, not sit as an unstructured link pile

## TDD Integration

- for code-changing work, `SuperTeam` defaults to `red -> green -> refactor`
- no production implementation should be accepted before a failing test exists, unless the orchestrator records an explicit exception path
- test-first is a workflow contract, not a style preference
- skills must not silently downgrade missing failing tests into a soft suggestion

## Frontend Aesthetics Integration

- when `ui_weight` is `ui-standard` or `ui-critical`, all UI-touching stages must reference `framework/frontend-aesthetics.md` as normative guidance
- aesthetic direction, typography, color, motion, spatial composition, and visual detail decisions must flow through the full pipeline via `ui-intent.md`
- the anti-pattern registry in `framework/frontend-aesthetics.md` is a binding quality standard, not optional advice
- implementation complexity must match the selected aesthetic vision

## Reviewer Integration

- every run must produce a trace file at `.superteam/reviewer/traces/<task-slug>.jsonl` — this is not optional
- the orchestrator emits stage-level trace events; individual agents emit their own event types per `framework/reviewer.md`
- every completed, failed, or cancelled run must produce a Reviewer report
- completed runs acknowledge Reviewer problem records in `finish.md`; failed or cancelled runs acknowledge them in the terminal handoff or retrospective note
- skills must not suppress, fabricate, or alter trace events

## Inspector Integration

- the inspector owns the review stage and runs quality checks across 8 dimensions per `framework/inspector.md`
- when the inspector finds a blocker, it immediately emits an `escalation` event to the orchestrator — it does not wait for review stage close
- the orchestrator decides what to do with inspector blocker reports: route to the appropriate agent, update the plan, or accept the risk
- inspector specialist profiles (critic, tdd, acceptance, socratic, security) are activated internally — they are not separate agents

## Polish Layer Integration

- `simplifier`, `doc-polisher`, and `release-curator` are refinement workers, not stage owners
- they operate in the execute-to-review bridge or as finish support without creating extra stages
- they must record their work in `.superteam/runs/<task-slug>/polish.md`
- any behavior-affecting polish edit requires fresh local checks before `review`
- polish workers do not weaken `inspector` or `verifier` authority
