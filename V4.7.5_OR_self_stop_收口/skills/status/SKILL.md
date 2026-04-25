---
name: status
description: Show the current SuperTeam run status. Use when the user wants to know the active stage, blocker, next action, readiness, or delivery confidence.
argument-hint: [task-slug optional]
disable-model-invocation: true
---

# SuperTeam Status

Inspect the latest run status.

## V4.7.0 First Step — Read Mode

Run:

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" status
```

The output is JSON containing: mode, active_task_slug, current_stage, schema check, the last
five `Agent` spawns (from `spawn-log.jsonl`), and the last five gate violations (from
`gate-violations.jsonl`). Surface these to the user before reading other artifacts.

If `mode_present=false`, this project has never entered OR mode — say so and skip the rest.
If `mode == "ended"`, OR mode is off; report when it ended and who ended it.
If `schema_ok=false`, mode.json is corrupt — tell the user and recommend recreating with
`/superteam:go`.

## Primary Source

Read:

- `.superteam/state/current-run.json`

If needed, cross-check with:

- the latest run directory under `.superteam/runs/`
- `scorecard.md` when present
- the latest handoff file
- `verification.md` when the run is near completion

## Report Shape

Return:

- current stage
- last completed stage
- overall status
- repair cycle count
- latest handoff path
- blocker summary, if any
- blocked reason, if any
- blocker owner, if any
- immediate next required action
- readiness for `execute`, `verify`, and `finish`
- evidence freshness
- delivery confidence
- plan quality gate, when available
- supplement mode, when relevant
- supplement anchor, when relevant
- supplement reason, when relevant
- earliest invalidated stage, when relevant
- affected artifacts, when relevant
- learning status, when relevant
- improvement action, when relevant
- guard mode, when relevant
- execution mode, when relevant
- conflict domain, when relevant
- merge owner, when relevant
- UI weight, when relevant
- UI intent status, when relevant
- UI quality gate status, when relevant
- aesthetic direction, when relevant
- anti-pattern gate status, when relevant
- active task id, when relevant
- active specialists, when relevant
- specialist routing reason, when relevant
- Inspector trace event count, when available
- Inspector report status, when available
- Inspector open problem count, when available

## Rules

- if the state file is missing, say so clearly
- if the state file conflicts with run artifacts, call out the inconsistency
- treat `current-run.json` as the compact source of truth and `scorecard.md` as a derived summary when available
- keep the explanation Chinese-first for Chinese-speaking users, while preserving English verdict and status labels
