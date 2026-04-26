---
name: end
description: Exit SuperTeam OR mode for the current project. Use when the user wants the main session to stop acting as Orchestrator and resume normal Claude Code behavior. The current run's artifacts are preserved.
disable-model-invocation: true
---

# SuperTeam End

Exit V4.7.0 OR mode immediately.

## Action

Run exactly one command:

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" end
```

This atomically rewrites `.superteam/state/mode.json` with:
- `mode=ended`
- `ended_by=user_command`
- `ended_at=<now>`

User invocation is itself confirmation — do not ask again.

## After Exit

- The run directory `.superteam/runs/<slug>/` is **kept** for audit; nothing is deleted.
- Hooks remain installed but stop injecting the OR banner (they short-circuit when
  `mode != active`).
- Direct file writes by the main session are no longer blocked.
- Tell the user OR mode is off and that `/superteam:go <task>` re-enters with a fresh slug.

## When NOT To Use

- During `finish` stage with a successful run, prefer the project-completion path: ask the user
  to confirm the project is done, then call `mode_cli.py end --completion`. This records
  `ended_by=project_completion` in the audit log.
- If the user says "暂不", "later", or just acknowledges finish without a clear yes/no,
  do not call this command — keep `mode=active`.
