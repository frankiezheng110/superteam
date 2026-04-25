# SuperTeam

Seven-stage delivery plugin for [Claude Code](https://claude.com/claude-code) with **hook-level hard constraints** and a **main-session-as-orchestrator** trust chain — so delivery quality no longer depends on AI self-discipline.

**Version**: 4.7.1
**License**: MIT

---

## What V4.7 delivers

V4.6 and earlier shipped the orchestrator (OR) as a subagent. But Claude Code's runtime physically prevents subagents from spawning other subagents — the OR subagent therefore could not delegate to specialists, and the seven-stage trust chain was theatrical (one agent self-impersonating reviewer/verifier/writer).

V4.7 moves the OR role to the **main Claude Code session**, the only layer that can spawn subagents. Trust-chain enforcement now lives on disk, not in agent self-discipline:

- A persistent `mode.json` state machine (active / ended) drives main-session identity, with schema versioning, atomic writes, and exactly four legitimate write paths (`/superteam:go`, `/superteam:end`, finish-stage user confirmation, hook heartbeat).
- A PreToolUse gate (`gate_main_session_scope.py`) blocks the main session from directly writing substantive work files — code, `review.md`, `verify.md`, `polish.md`, `final.md`, `test-plan.md`, etc. The main session must spawn the corresponding specialist instead. OR-coordination artifacts (`activity-trace.md`, `task-list.md`, `decision-log.md`, `.superteam/state/*`) remain writable.
- A PostToolUse hook writes `spawn-log.jsonl` (append-only) on every `Agent` call so spawn history cannot be forged.
- SessionStart and UserPromptSubmit hooks reinject an OR identity banner on every user message, surviving auto-compact, usage-limit pause, and unexpected session resume.
- Three new slash commands: `/superteam:go [task]`, `/superteam:end`, `/superteam:bypass <reason>`. `/superteam:status` is upgraded to surface mode + recent spawns + recent gate violations.

V4.7.1 (this release) is a four-item closeout fix on V4.7.0:

1. The active-subagent window now opens **only** for `superteam:*` specialists (V4.7.0 leaked the bypass to any subagent).
2. Corrupt or unknown-schema `mode.json` triggers a loud warning instead of a silent fall-through.
3. The missing `/superteam:bypass` slash-command skill was added (CLI was already there).
4. Repo-root metadata (this README, `CLAUDE.md`, `VERSION.md`) is brought back in sync with the active plugin version.

V4.6's hook strictness is preserved: TDD red/green state machine, plan MUST accounting, commit gate, polish layer, inspector continuity. V4.7 only adds the OR identity dimension on top.

## Install

```
/plugin marketplace add frankiezheng110/superteam
/plugin install superteam@superteam
/reload-plugins
```

Hooks register automatically (the plugin's `hooks/hooks.json` is loaded by Claude Code on plugin install — no manual `install.sh` step). The `install.ps1` / `install.sh` scripts remain in the version directory for users who clone the repo directly outside the marketplace flow.

Upgrade:

```
/plugin marketplace update superteam
/plugin update superteam
/reload-plugins
```

## Entry points

- `/superteam:go [task]` — enter OR mode and start the seven-stage run
- `/superteam:end` — exit OR mode (preserves run artifacts for audit)
- `/superteam:status` — show mode, current stage, recent spawns, recent gate violations
- `/superteam:bypass <reason>` — one-shot escape valve for misjudged hook blocks (audited)
- `/superteam:g1` / `/superteam:g2` / `/superteam:g3` — reopen a user approval gate (supplement)

## Project layout

```
.
├── .claude-plugin/
│   └── marketplace.json                # marketplace manifest (points to active version source)
├── V4.7.1_主会话OR收口修复/             # active plugin source
│   ├── .claude-plugin/plugin.json
│   ├── agents/                         # specialist subagents (orchestrator subagent is DEPRECATED)
│   ├── framework/                      # contracts incl. main-session-orchestrator.md
│   ├── skills/                         # slash-command skills
│   ├── commands/cli/mode_cli.py        # mode.json CLI (enter / end / status / bypass)
│   ├── hooks/                          # Python hooks
│   │   ├── dispatch/                   # event entry points
│   │   ├── gates/                      # PreToolUse gate checkers (incl. gate_main_session_scope)
│   │   ├── validators/                 # product-file validators
│   │   ├── observers/                  # PostToolUse observers
│   │   ├── post_agent/                 # post-Agent chain (writes spawn-log)
│   │   ├── session/                    # SessionStart injection + Stop guard
│   │   ├── lib/                        # shared libs (incl. mode_state.py)
│   │   └── matrix_selfcheck.py
│   ├── tests/
│   ├── VERSION.md
│   └── ...
├── V4.6.4_tdd初始化修复/               # prior version (preserved per upgrade rule)
├── V4.6.0_hook强约束/ ... V4.6.3_项目根锚定/
├── V4.7.0_主会话即OR_信任链重建/       # immediate prior, kept for diffability
├── README.md
├── CLAUDE.md
├── VERSION.md
└── LICENSE
```

## Terminology

V4.6.0 swapped the review/inspect role names to match English semantics; V4.7 keeps the same convention:

| English | 中文 | Responsibility | Output |
|---------|------|---------------|--------|
| `reviewer` | 审查者 | review-stage quality gate — code, plan fidelity, security, TDD, UI quality; has BLOCK authority | `review.md` |
| `inspector` | 监察者 | continuity auditor — observes team behavior throughout; zero interrupt authority | `activity-trace.md` checkpoints + `inspector/reports/*-report.md` |
| `orchestrator` | 协调者 | seven-stage routing and gate decisions. **In V4.7 this role is the main Claude Code session**, not a subagent. | `current-run.json`, `mode.json`, `activity-trace.md`, `decision-log.md`, `spawn-log.jsonl` |

## License

MIT — see [LICENSE](LICENSE).
