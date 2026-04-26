---
name: pause
description: Pause an active SuperTeam OR run. Use when the user wants the orchestrator to stop driving forward temporarily without ending the project (e.g., "pause", "暂停", "let me take over for a bit"). Sets project_lifecycle=paused; the V4.7.7 stop hook then allows the main session to stop, and the user can manually edit / chat without OR self-stop block. Use /superteam:resume to come back.
disable-model-invocation: true
---

# SuperTeam Pause

Set `mode.json.project_lifecycle = paused`. The V4.7.7 stop hook reads
this single field; once paused, the main session is allowed to stop,
and the OR yields the floor without ending the project.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" pause
```

User invocation is itself confirmation — do not ask again.

## After Pause

- `mode.json.project_lifecycle` = `paused`; `paused_at` / `paused_by` recorded.
- `mode.json.mode` stays `active` (the OR identity is unchanged — gate_main_session_scope still recognizes the project).
- The run directory `.superteam/runs/<slug>/` is untouched. spawn-log /
  current-run.json / activity-trace.md continue to reflect the in-flight state.
- Tell the user the project is paused and that `/superteam:resume` returns
  to running, or `/superteam:end` exits the project entirely.

## When NOT To Use

- The user wants to **end** the project (use `/superteam:end` instead).
- The project is already in `finish` stage and the user just confirmed
  completion (use `mode_cli.py end --completion`).
- mode.json doesn't exist (no active OR run — nothing to pause).
