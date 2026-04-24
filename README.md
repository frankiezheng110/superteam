# SuperTeam

Seven-stage delivery plugin for [Claude Code](https://claude.com/claude-code) with **hook-level hard constraints**: physically enforces TDD red/green, plan MUST accounting, commit gate, and inspector continuity — so that delivery quality no longer depends on AI self-discipline.

**Version**: 4.6.0
**License**: MIT

---

## What V4.6.0 delivers

V4.5.0 and earlier versions encoded quality rules in agent `.md` files and relied on the orchestrator to self-police. V4.5.0's post-mortem diagnosis (see `V4.6.0_hook强约束/DIAGNOSIS-V4.5.0-self-enforce-flaw.md`) showed this is unreliable: an orchestrator that rationalizes skipping review/verify has no external check.

V4.6.0 moves enforcement from "rules in .md" to **Python hooks registered in `~/.claude/settings.json`**. Hooks run outside Claude's reasoning chain. A rationalization cannot skip them.

### What the hooks enforce (condensed)

- **TDD red/green state machine** — cannot edit production code before a failing test is recorded
- **Plan MUST accounting** — every MUST item in `plan.md` must be present in `execution.md` with evidence; multi-category IDs (F- / UI- / API- / MIG-) tracked independently
- **Orchestrator Decision Log** — spawning executor/reviewer requires a prior `## Orchestrator Decision — <Unit>` section; Unit id must be in plan and not already completed
- **Entry Log reconciliation** — each downstream agent must restate plan MUST items verbatim; mismatches block the next spawn
- **Commit gate** — `git commit` / `tag` / `push` is blocked unless `verification.md` carries `verdict: PASS`
- **Finish (G7) closure** — `finish.md` must acknowledge each inspector problem, `retrospective.md` must have a non-empty `improvement_action`, rolling artifacts must be updated
- **Plan progress tracking** — `plan-progress.json` records COMPLETE / PENDING / BLOCKED per MUST item; interrupted sessions resume cleanly without redoing finished work
- **G4-G7 auto-chain** — after G3 user approval, stages 4 through 7 run without further user confirmation; all next-step directives carry "no user confirmation needed"

Full rule matrix: [`V4.6.0_hook强约束/framework/hook-enforcement-matrix.md`](V4.6.0_hook强约束/framework/hook-enforcement-matrix.md) (135 rules × 32 hook checkers, with self-check).

## Install (Claude Code marketplace)

```text
/plugin marketplace add frankiezheng110/superteam
/plugin install superteam@superteam
/reload-plugins
```

After installation, register the hooks once:

```text
# Linux / macOS
~/.claude/plugins/superteam/V4.6.0_hook强约束/install.sh

# Windows (PowerShell)
& "$HOME\.claude\plugins\superteam\V4.6.0_hook强约束\install.ps1"
```

The install script merges SuperTeam's hook configuration into your `~/.claude/settings.json` (existing hooks are preserved) and runs `matrix_selfcheck.py` to confirm the 32 hook files are present and importable.

## Entry points

- `/superteam:go` — start a fresh run
- `/superteam:status` — show current run state
- `/superteam:g1` / `/superteam:g2` / `/superteam:g3` — reopen a user approval gate

## Project layout

```
.
├── .claude-plugin/
│   └── marketplace.json           # marketplace manifest
├── V4.6.0_hook强约束/             # active plugin source
│   ├── .claude-plugin/
│   │   └── plugin.json            # plugin manifest
│   ├── agents/                    # agent definitions (orchestrator / reviewer / inspector / ...)
│   ├── framework/                 # rule documentation + hook-enforcement-matrix.md
│   ├── skills/                    # slash-command skills
│   ├── hooks/                     # Python hook scripts (32 checkers + dispatchers)
│   │   ├── dispatch/              # event entry points
│   │   ├── validators/            # product-file validators
│   │   ├── gates/                 # PreToolUse gate checkers
│   │   ├── observers/             # PostToolUse observers (test runners, git, ...)
│   │   ├── post_agent/            # post-agent entry-log + trace writer + chain
│   │   ├── session/               # SessionStart injection + Stop guard
│   │   ├── lib/                   # shared libraries (state, parser, trace, plan_progress, ...)
│   │   └── matrix_selfcheck.py    # verify matrix ↔ hook files stay in sync
│   ├── tests/                     # 44 smoke + integration test cases
│   ├── install.ps1 / install.sh   # hook registration + launcher setup
│   └── VERSION.md
├── README.md
└── LICENSE
```

## Terminology (防混淆)

In V4.6.0 the review/inspect roles were renamed to match English semantics:

| English | 中文 | Responsibility | Output |
|---------|------|---------------|--------|
| `reviewer` | 审查者 | review-stage quality gate — code, plan fidelity, security, TDD, UI quality; has BLOCK authority | `review.md` |
| `inspector` | 监察者 | continuity auditor — observes team behavior throughout; zero interrupt authority | `activity-trace.md` checkpoints + `inspector/reports/*-report.md` |

## License

MIT — see [LICENSE](LICENSE).
