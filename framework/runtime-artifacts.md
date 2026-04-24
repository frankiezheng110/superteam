# SuperTeam Runtime Artifacts

When `SuperTeam` is used inside a real repository, it writes workflow artifacts under `.superteam/` at the project root.

## Directory Layout

```text
.superteam/
  runs/
    <task-slug>/
      project-definition.md
      activity-trace.md
      solution-options.md
      solution-landscape.md
      ui-intent.md
      design.md
      plan.md
      execution.md
      polish.md
      review.md
      verification.md
      scorecard.md
      finish.md
      retrospective.md
      design-system.md
      supplements/
      handoffs/
        01-clarify-to-design.md
        02-design-to-plan.md
        03-plan-to-execute.md
        04-execute-to-review.md
        05-review-to-verify.md
        06-verify-to-finish.md
  reviewer/
    traces/
      <task-slug>.jsonl
    reports/
      <task-slug>-report.html
      <task-slug>-report.md
    insights.md
    health.json
    improvement-backlog.md
  state/
    current-run.json
```

## Rules

- one top-level run directory per meaningful task or feature
- use a stable kebab-case task slug
- keep stage artifacts in predictable filenames so later agents can resume safely
- handoffs must be append-only stage summaries, not full duplicate specs
- verification and finish artifacts must reference fresh evidence, not claims
- meaningful completed runs must include `retrospective.md`
- `state/current-run.json` is the compact source of truth for operational state
- `scorecard.md` is a derived human-readable summary, not a second source of truth
- `state/current-run.json` should stay small and status-oriented rather than duplicating full stage artifacts
- mixed artifacts should keep user-facing prose Chinese-first and machine-style keys or verdicts English-first

## Minimum Required Files

- `design.md` after `design`
- `project-definition.md` after `clarify`
- `activity-trace.md` once `clarify` starts
- `solution-options.md` after `design`
- `solution-landscape.md` after `design`
- `ui-intent.md` after `design` for `ui-standard` and `ui-critical` tasks — must include aesthetic contract sections (aesthetic direction, typography, color, motion, spatial, visual detail, anti-pattern exclusions)
- `plan.md` after `plan`
- `execution.md` after `execute`
- `polish.md` before `review` — records any `simplifier`, `doc-polisher`, and `release-curator` work plus post-polish checks
- `review.md` after `review`
- `verification.md` after `verify`
- `scorecard.md` from the point a real plan exists
- `finish.md` after `finish`
- `retrospective.md` after `finish` for any run that had an approved `plan` or entered `execute`
- `design-system.md` when `design-consultation` is used
- `supplements/` when any of the three user closure gates is reopened later in the run
- Reviewer trace at `.superteam/reviewer/traces/<task-slug>.jsonl` from the moment `clarify` starts
- Reviewer reports at `.superteam/reviewer/reports/<task-slug>-report.html` and `.superteam/reviewer/reports/<task-slug>-report.md` before `finish.md` is written

## Handoff Naming

Use numeric prefixes so the run reads in chronological order.

- `01-clarify-to-design.md`
- `02-design-to-plan.md`
- `03-plan-to-execute.md`
- `04-execute-to-review.md`
- `05-review-to-verify.md`
- `06-verify-to-finish.md`

If verification fails and loops back, write an additional handoff such as `05b-verify-to-execute-fix.md`.

## Resume Rule

Before resuming a partially completed workflow, the orchestrator should read:

1. the latest handoff file
2. `project-definition.md` if it exists
3. `activity-trace.md` if it exists
4. `solution-options.md` if it exists
5. `solution-landscape.md` if it exists
6. `plan.md`
7. `ui-intent.md` if it exists
8. `design-system.md` if it exists
9. `polish.md` if it exists
10. `review.md` if it exists
11. `verification.md` if it exists
12. `retrospective.md` if it exists
13. the Reviewer trace file at `.superteam/reviewer/traces/<task-slug>.jsonl` if it exists
14. the latest Reviewer report if one exists

This keeps `SuperTeam` aligned with explicit externalized memory rather than hidden conversational state.

## State File

`state/current-run.json` is the compact operational source of truth.

Keep the full field contract in `framework/state-and-resume.md` so the state schema has one detailed definition.
