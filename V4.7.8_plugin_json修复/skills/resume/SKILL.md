---
name: resume
description: Resume a paused SuperTeam OR run. Use when the user wants the orchestrator to pick up driving the run again after a /superteam:pause (e.g., "resume", "恢复", "continue"). Sets project_lifecycle=running, which re-arms the V4.7.7 stop hook so OR cannot self-stop until paused or ended.
disable-model-invocation: true
---

# SuperTeam Resume

Set `mode.json.project_lifecycle = running`. The V4.7.7 stop hook
re-arms — the OR cannot self-stop until the user pauses again or
ends the run.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" resume
```

User invocation is itself confirmation — do not ask again.

## After Resume

- `mode.json.project_lifecycle` = `running`; `paused_at` / `paused_by` cleared.
- The OR resumes seven-stage execution from wherever the previous run left
  off. Read `.superteam/state/current-run.json.current_stage` and
  `next_action` (if set) to decide the next spawn.
- If the prior pause was issued mid-stage (e.g., during `execute`), the
  next OR action is to spawn the responsible specialist for that stage —
  see `framework/main-session-orchestrator.md`.

## When NOT To Use

- The project is already running (resume is a no-op then; status shows it).
- The project has been `ended` — use `/superteam:go <slug>` to start a new
  run (resume does not revive ended projects).
