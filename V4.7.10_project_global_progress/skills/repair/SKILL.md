---
name: repair
description: Back up the current mode.json and rewrite a fresh schema-valid one. Use when /superteam:status reports health=corrupt or unknown_schema, or when the OR-mode banner shows mode.json is in a bad state.
argument-hint: [--slug task-slug]
disable-model-invocation: true
---

# SuperTeam Repair

Recover from a corrupt or schema-mismatched `.superteam/state/mode.json`.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" repair $ARGUMENTS
```

Behavior:

1. The existing `mode.json` (if present) is copied to `mode.json.bak.<timestamp>`
   so the corrupt state is preserved for forensics.
2. A new `mode.json` is written with `schema_version=1`, `mode=active`,
   `entered_by="/superteam:repair"`.
3. The `active_task_slug` is anchored to either:
   - `--slug <task-slug>` if provided, or
   - the slug salvaged from the broken file (if `active_task_slug` was readable
     before the corruption).
4. **Run history is untouched** — `spawn-log.jsonl`, `gate-violations.jsonl`,
   `bypass-log.jsonl`, and `.superteam/runs/<slug>/*` artifacts stay as they were.

## When To Use

- `/superteam:status` shows `health: corrupt` or `health: unknown_schema`.
- The SessionStart / UserPromptSubmit banner says "mode.json 状态异常".
- You upgraded SuperTeam and the new plugin reports an unknown_schema state.

## When NOT To Use

- `mode.json` is fine but the run is stuck — that's a `/superteam:doctor` case.
- You want to abandon the run — use `/superteam:end` instead (preserves audit).
- You want to restart from scratch — use `/superteam:end` then `/superteam:go <slug>`.

## After Repair

The OR-mode banner should reappear cleanly on the next user message. If it does
not, run `/superteam:doctor` to see what else is off.
