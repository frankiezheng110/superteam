---
name: superteam:finish
description: Finish a verified SuperTeam run. Use after PASS to package the delivery, summarize artifacts, and record the final handoff.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Finish

Finish this run:

`$ARGUMENTS`

## Read First

- `framework/skill-common-rules.md`
- `framework/state-and-resume.md`
- `framework/inspector.md`

## Required Files

- `.superteam/runs/<task-slug>/verification.md`
- `.superteam/runs/<task-slug>/scorecard.md`
- `.superteam/runs/<task-slug>/finish.md`
- `.superteam/runs/<task-slug>/retrospective.md` for meaningful runs
- `.superteam/runs/<task-slug>/handoffs/06-verify-to-finish.md`
- `.superteam/inspector/reports/<task-slug>-report.md` (generated during finish)

## Finish Rules

- only finish after a recorded `PASS`
- **before writing `finish.md`**, trigger Inspector analysis:
  1. read the trace file at `.superteam/inspector/traces/<task-slug>.jsonl`
  2. analyze per `framework/inspector.md` Layer 2
  3. generate the Inspector report at `.superteam/inspector/reports/<task-slug>-report.md`
  4. update `.superteam/inspector/health.json` and `.superteam/inspector/insights.md`
  5. generate improvement tickets in `.superteam/inspector/improvement-backlog.md`
- summarize what was delivered
- list the key artifacts and evidence sources
- state any residual non-blocking risks explicitly
- note any recommended next actions, not hidden assumptions
- make the output understandable without reopening the full conversation
- capture reusable learning in `retrospective.md`
- record one concrete `improvement_action`
- use `learning_status=applied` only when the referenced SuperTeam improvement was completed inside the same run; otherwise keep it `deferred`
- include an **Inspector Summary** section in `finish.md`:
  - reference the Inspector report path
  - list key findings and their severity
  - acknowledge every improvement ticket: `applied`, `deferred` (with reason), or `rejected` (with evidence)
  - if any `critical` tickets exist, they must appear prominently
- synchronize `.superteam/state/current-run.json` with `status=completed`, `last_completed_stage=finish`, latest handoff, `learning_status`, `improvement_action`, `inspector_report_status=acknowledged`, and `inspector_open_tickets`
- refresh `scorecard.md` after finish so final state and learning closure agree
- keep user-facing finish prose Chinese-first while leaving verdict and status vocabulary English-first

## Frontend Aesthetics Finish Summary (ui-standard / ui-critical)

For `ui-standard` and `ui-critical` work, the finish artifact must also include:

- **Aesthetic direction achieved** — which direction was selected and how well the implementation realized it
- **Aesthetic quality assessment** — a brief evaluation across the five dimensions (typography, color, motion, spatial, visual detail)
- **Anti-pattern compliance** — confirmation that no mandatory anti-pattern violations remain
- **Aesthetic compromises** — any intentional degradations or residual mismatches between the intended and delivered aesthetic
- **Aesthetic learning** — what worked well and what aesthetic decisions should inform future projects

The retrospective for `ui-standard` and `ui-critical` runs should also include:

- **Aesthetic direction effectiveness** — did the chosen direction serve the product well?
- **Aesthetic execution quality** — where did aesthetic intent survive best? Where did it degrade?
- **Aesthetic pipeline learning** — was the aesthetic contract specific enough to execute from? What was missing?

## Inspector-Driven Retrospective Enhancement

The retrospective for every meaningful run should reference the Inspector report and include:

- **Process efficiency** — which stages were bottlenecks? Where was time wasted?
- **Error pattern** — what types of errors occurred? Were they addressed at root cause?
- **Decision quality** — which routing/specialist decisions proved correct? Which didn't?
- **Improvement tickets** — what concrete changes should be made to the system?

The retrospective complements but does not duplicate the Inspector report. The retrospective is a human-oriented narrative; the Inspector report is a data-driven analysis.
