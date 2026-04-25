# SuperTeam Version Index

**Current**: V4.7.4 — see `V4.7.4_TierB收口/VERSION.md` for the full release notes.

## Release timeline

| Version | Date | One-liner |
|---|---|---|
| **V4.7.4** | 2026-04-25 | PLAN Tier B close-out — per-role Output Discipline (reviewer/verifier/writer/planner/architect/executor); Stop-hook escalation diagnostic on 3+ gate-block clusters in 60s; three new slash commands /superteam:debug, /superteam:repair, /superteam:doctor for triage and recovery. Only Tier C1 (end-to-end pytest trust-chain suite) remains — testing infrastructure, not bug-fix backlog. |
| V4.7.3 | 2026-04-25 | PLAN Tier A close-out — `gate_stage_advance` blocks current_stage advances missing spawn-log/artifact preconditions; `validator_frontmatter` audits specialist artifact provenance. All three rationalization-bypass routes — self-stop, stage-skip, artifact-forge — are now hook-blocked. |
| V4.7.2 | 2026-04-25 | V4.7 conversation-flow + tool-set patches: Stop hook blocks main-session self-stop in execute-class stages when no specialist was spawned this turn; specialist subagents (designer/architect/executor/verifier/reviewer/researcher/debugger/test-engineer) get MCP tool whitelists (pencil/chrome-devtools/playwright/context7/gpt-researcher). |
| V4.7.1 | 2026-04-25 | V4.7 closeout: active-subagent window restricted to `superteam:*`, corrupt mode.json now warns loudly, `/superteam:bypass` skill added, repo-root metadata resynced. |
| V4.7.0 | 2026-04-25 | Architectural — moves Orchestrator from subagent to main Claude Code session; adds `mode.json` state machine, `gate_main_session_scope`, `spawn-log.jsonl`, `/superteam:end` and revamped `/superteam:go` / `/superteam:status`. Disk-enforced trust chain. |
| V4.6.4 | 2026-04-24 | Hotfix — TDD state-machine init deadlock: `_maybe_init_active_feature` derives `active_feature_id` from `execution.md` in PostToolUse. |
| V4.6.3 | 2026-04-24 | Hotfix — anchor hook resolution to `$CLAUDE_PROJECT_DIR` instead of `os.getcwd()` so unrelated sessions never trigger SuperTeam Stop hook. |
| V4.6.2 | 2026-04-24 | Hotfix — move `hooks.json` from `.claude-plugin/` to `hooks/hooks.json` per Claude Code's official File Locations table. |
| V4.6.1 | 2026-04-24 | Hotfix — register hooks via plugin-native `hooks.json` so marketplace install works without running `install.ps1`/`install.sh`. |
| V4.6.0 | 2026-04 (in progress, never released) | Hook Enforcement Matrix — 137 rules × 30 checkers; promote rules from "agent .md" to Python hooks. |
| V4.5.0 | 2026-03-28 | Feature checklist + per-feature TDD loop. |

Each version directory under the repo root contains its own `VERSION.md` with the full notes for that release. Per the upgrade rule, prior version directories are preserved unchanged.
