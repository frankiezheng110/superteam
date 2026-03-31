---
name: inspect
description: Trigger Reviewer analysis for a run. Use for post-run reports, cross-run health review, or a non-authoritative mid-run diagnostic.
argument-hint: [--cross-run | --mid-run | task-slug]
disable-model-invocation: true
---

# SuperTeam Inspect

Analyze:

`$ARGUMENTS`

## Read First

- `framework/reviewer.md`
- `agents/reviewer.md`
- `framework/runtime-artifacts.md`

## Modes

### Default

- read the run trace and run artifacts
- generate HTML + Markdown Reviewer reports
- refresh `health.json`, `insights.md`, and `improvement-backlog.md`
- output a concise Chinese summary to the user

### `--mid-run`

- read the trace so far
- output a trace-health summary only
- do not create blocker signals or problem records

### `--cross-run`

- read all available reports and traces
- refresh aggregate health metrics
- summarize recurring problems and priority actions

## Rule

- Reviewer analysis is diagnostic and audit-facing
- it never replaces Inspector review or Verifier verdicts
