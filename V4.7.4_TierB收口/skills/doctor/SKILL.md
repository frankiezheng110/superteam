---
name: doctor
description: Run a comprehensive trust-chain health check (mode.json schema, hook heartbeat staleness, stage prerequisites, bypass volume, stale active-subagent flag, recent block clustering). Use when something feels off but the specific symptom is not obvious.
disable-model-invocation: true
---

# SuperTeam Doctor

Comprehensive V4.7 trust-chain diagnosis.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" doctor
```

The output is JSON with a `findings` array. Each finding has `severity`
(high / medium / low) and a `msg` describing the issue.

## Checks performed

1. **mode.json schema** — corrupt or unknown_schema → high severity, recommend `/superteam:repair`
2. **Hook heartbeat** — `last_verified_at` older than 30 minutes while `mode=active` → medium severity (hooks may not be running)
3. **Stage prerequisites** — `current_stage` is review/verify/finish but spawn-log lacks the corresponding specialist → high severity (stage was advanced without the prerequisite spawn — likely a hook bypass or pre-V4.7.3 history)
4. **Bypass volume** — 3+ consumed `/superteam:bypass` in this run → low severity (review whether gate rules need adjustment)
5. **Block clustering** — 3+ gate violations in last 60 seconds → medium severity (the OR may be confused or hooks may be misjudging)
6. **Stale active-subagent flag** — `active-subagent.json` set 15+ minutes ago without a SubagentStop → medium severity (next spawn cycle will overwrite it; or remove manually)

## Exit code

`0` if no high-severity findings; `1` otherwise. Useful when scripting health
checks (`mode_cli.py doctor || echo broken`).

## Companion commands

- `/superteam:debug` — raw log dump (use after doctor to see specific records)
- `/superteam:status` — operational view (current stage / next action)
- `/superteam:repair` — fix mode.json corruption
- `/superteam:bypass <reason>` — one-shot override for a hook misjudgment
- `/superteam:end` — exit OR mode if the run is genuinely abandoned
