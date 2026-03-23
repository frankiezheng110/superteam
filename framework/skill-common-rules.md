# SuperTeam Skill Common Rules

Use this file as the shared baseline reference for `skills/**/SKILL.md`.

## Core References

Most skills should start from these documents:

- `framework/stage-model.md`
- `framework/stage-interface-contracts.md`
- `framework/runtime-artifacts.md`

Add these when the skill needs them:

- `framework/orchestrator.md` for routing, stage ownership, or specialist injection
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

## Frontend Aesthetics Integration

- when `ui_weight` is `ui-standard` or `ui-critical`, all UI-touching stages must reference `framework/frontend-aesthetics.md` as normative guidance
- aesthetic direction, typography, color, motion, spatial composition, and visual detail decisions must flow through the full pipeline via `ui-intent.md`
- the anti-pattern registry in `framework/frontend-aesthetics.md` is a binding quality standard, not optional advice
- implementation complexity must match the selected aesthetic vision

## Reviewer Integration

- every run must produce a trace file at `.superteam/reviewer/traces/<task-slug>.jsonl` — this is not optional
- the orchestrator emits stage-level trace events; individual agents emit their own event types per `framework/reviewer.md`
- every completed, failed, or cancelled run must produce a Reviewer report before `finish.md`
- improvement records from the Reviewer must be acknowledged in the finish artifact
- skills must not suppress, fabricate, or alter trace events

## Inspector Integration

- the inspector owns the review stage and runs quality checks across 8 dimensions per `framework/inspector.md`
- when the inspector finds a blocker, it immediately emits an `escalation` event to the orchestrator — it does not wait for review stage close
- the orchestrator decides what to do with inspector blocker reports: route to the appropriate agent, update the plan, or accept the risk
- inspector specialist profiles (critic, tdd, acceptance, socratic, security) are activated internally — they are not separate agents
