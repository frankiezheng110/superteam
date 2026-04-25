---
name: debug
description: Dump recent spawn-log, gate-violations, and bypass-log entries for triage. Use when a hook block looks wrong, when /superteam:status is not enough, or when you need to check what specialists actually ran.
disable-model-invocation: true
---

# SuperTeam Debug

Dump the V4.7 trust-chain audit logs for diagnosis.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" debug --limit 20
```

The output is JSON containing:

- `health` — mode.json health (missing / corrupt / unknown_schema / active / ended)
- `recent_spawns` — last N entries from `.superteam/runs/<slug>/spawn-log.jsonl`
- `recent_violations` — last N entries from `.superteam/state/gate-violations.jsonl`
- `violations_in_60s` — recent block clusters that may be triggering escalation
- `recent_bypasses` — last N `/superteam:bypass` records (pending + consumed)

Pass `--limit N` to change how many records each list shows (default 10).

## When To Use

- A hook just blocked a write that you believe is legitimate — the violation reason in
  `recent_violations` plus the spawn-log will usually tell you why.
- The OR claims to have spawned a specialist but its work seems missing — check
  `recent_spawns` to confirm the spawn actually happened (PostToolUse hook records
  every real `Agent` tool call; absence here means it never happened).
- You consumed a `/superteam:bypass` and want to confirm it actually unblocked the
  intended write.
- Block escalation is firing — `violations_in_60s` shows the cluster the hook saw.

## Companion commands

- `/superteam:status` — operational view (current stage, spawns)
- `/superteam:doctor` — health-checks across the trust chain
- `/superteam:repair` — fix a corrupt mode.json
