# SuperTeam V3.3.0

SuperTeam is a fused project-delivery control layer packaged as a Claude Code plugin.

It combines:

- `Superpowers` for stage discipline
- source-derived teammate collaboration discipline
- `SuperTeam` for the contracts between stages, agents, and runtime artifacts
- deep frontend aesthetics intelligence absorbed from the `frontend-design` skill
- **Reviewer mechanism for full-run tracing, team behavior auditing, and continuous improvement**

## What You Can Use In Claude Code

After loading this repository as a plugin, Claude Code gets:

- 16 plugin skills under the `superteam:` namespace
- a forced seven-stage orchestrator model
- 14 custom agents: 6 core runtime roles + 8 specialist support (including reviewer)
- a formal Frontend Aesthetics Pipeline with design thinking, five aesthetic dimensions, anti-pattern registry, and implementation complexity matching
- inspector with 5 built-in specialist profiles (critic, security, acceptance, tdd, socratic)
- **Reviewer: always-on run tracing, automatic team duty report generation, and forced improvement loop**

## Canonical Workflow

`clarify -> design -> plan -> execute -> review -> verify -> finish`

Every stage transition emits trace events. Every run produces a Reviewer team duty report (HTML + MD).

## Fast Install

```bash
./install.sh
```

Or on Windows PowerShell:

```powershell
.\install.ps1
```

That creates a `claude-superteam` launcher under `~/.claude/bin`.

## Install Locally In Claude Code

```bash
cd <target-repo>
claude --plugin-dir "D:\claude code\superteam"
```

Inside Claude Code, run `/help` and look for the `superteam:` namespace.

To use `/superteam:team-execute`, enable Claude Code native agent teams first:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Primary Commands

- `/superteam:go <task>` - run the full seven-stage workflow
- `/superteam:clarify <task>` - clarify scope and success criteria
- `/superteam:design <task>` - write or refine the design artifact
- `/superteam:plan <task>` - produce the executable plan artifact
- `/superteam:execute <task>` - implement from an approved plan
- `/superteam:review <task>` - run the dedicated review gate
- `/superteam:verify <task>` - run an independent verification pass
- `/superteam:finish <task>` - package the final handoff
- `/superteam:inspect [--mid-run|--cross-run|task-slug]` - run system health diagnosis
- `/superteam:team-execute <task>` - use native agent teams for parallel execution
- `/superteam:design-consultation <task>` - generate a design-system input with aesthetic intelligence
- `/superteam:careful <task>` - activate caution mode for high-risk work
- `/superteam:guard <task>` - activate maximum safety with boundary discipline
- `/superteam:strategic-compact` - suggest context compaction at workflow checkpoints
- `/superteam:writing-skills <skill need>` - create, refine, or validate a SuperTeam skill
- `/superteam:status` - inspect current run status

## Quick Start Example

```text
/superteam:go add a --json export mode to the notes CLI without breaking current text output
```

That run creates artifacts under `.superteam/runs/<task-slug>/` and maintains status at `.superteam/state/current-run.json`.

At minimum you should see: `design.md`, `plan.md`, `execution.md`, `review.md`, `verification.md`, `scorecard.md`, `finish.md`, `retrospective.md`, `handoffs/`, and a Reviewer team duty report at `.superteam/reviewer/reports/<task-slug>-report.html`.

For UI-bearing work (`ui-standard` or `ui-critical`), also expect `ui-intent.md` with aesthetic contract sections and optionally `design-system.md`.

## Reviewer Mechanism（团队监工）

The Reviewer is the system's behavior audit layer — three layers that ensure continuous improvement:

| Layer | Mode | Function |
| --- | --- | --- |
| Trace Collector | Passive, always-on | Records runtime events covering all stage transitions, agent calls, errors, fixes, and decisions — never interrupts |
| Run Analysis | Active, post-run | Generates team duty report (HTML + MD) with data statistics, collaboration tracking, and problem detection |
| Improvement Loop | Forced, cross-run | Converts weaknesses into engineering directives with mandatory acknowledgment by orchestrator |

Key capabilities:
- **Full observability**: every stage transition, agent call, command, error, fix, and decision is traced
- **Automatic reporting**: every run produces a team duty report — no exceptions
- **Engineering directives**: improvement directions use `<owner>: [condition,] <action>` format — directly submittable for system execution
- **Cross-run pattern detection**: recurring issues auto-escalate after 3 occurrences
- **Framework health check**: triggered on-demand when backlog or file size thresholds are met

## Runtime Artifact Convention

SuperTeam writes workflow artifacts to `.superteam/runs/<task-slug>/` and Reviewer data to `.superteam/reviewer/`. See `framework/runtime-artifacts.md` for the full layout.

## Repository Map

- `.claude-plugin/plugin.json` - Claude Code plugin manifest
- `install.sh` / `install.ps1` - local install helpers
- `skills/` - 16 Claude Code skills
- `agents/` - 14 Claude Code custom agents
- `framework/` - 12 normative workflow contracts (including `frontend-aesthetics.md`, `inspector.md`, and `reviewer.md`)
- `docs/design/` - design specs
- `docs/research/` - extracted upstream rules and conflict decisions
- `docs/validation/` - validation records
- `docs/superpowers/specs/` - historical design evolution

## Normative Docs

- `framework/stage-model.md` - stage order and transition rules
- `framework/orchestrator.md` - forced seven-stage orchestration contract
- `framework/stage-interface-contracts.md` - required artifacts between stages
- `framework/runtime-artifacts.md` - where runtime files should be written
- `framework/skill-common-rules.md` - shared baseline rules for the skill surface
- `framework/role-contracts.md` - authority model and role boundaries
- `framework/verification-and-fix.md` - evidence rules, verdicts, and fix loop
- `framework/frontend-aesthetics.md` - frontend aesthetic knowledge base and anti-pattern registry
- `framework/inspector.md` - Inspector project quality check contract (review stage owner)
- `framework/reviewer.md` - Reviewer team behavior audit contract (post-run report)
- `framework/handoff-template.md` - required handoff shape
- `framework/state-and-resume.md` - resume and persistence rules

## Four-Layer Quality System

1. **Executor self-check** — runtime self-validation during implementation
2. **Inspector challenge** — adversarial quality gate with specialist profiles, immediate blocker escalation to orchestrator
3. **Verifier judgment** — independent evidence-based final verdict
4. **Reviewer analysis** — objective team behavior audit and continuous improvement

## Read This In Order

1. `CLAUDE.md`
2. `framework/role-contracts.md`
3. `framework/inspector.md`
4. `framework/reviewer.md`
5. `docs/design/2026-03-23-v3-0-0-frontend-aesthetics-fusion-design.md`
6. `framework/frontend-aesthetics.md`
7. `framework/stage-model.md`
8. `framework/orchestrator.md`
9. `framework/stage-interface-contracts.md`
10. `framework/runtime-artifacts.md`
11. `framework/state-and-resume.md`
12. `framework/verification-and-fix.md`
13. `framework/skill-common-rules.md`

## Current Status

- 14 agents (6 core + 8 specialist support)
- 16 skills
- 7-stage orchestrator
- 12 normative framework documents
- full Frontend Aesthetics Pipeline
- full Reviewer Pipeline (trace → analyze → improve)
- inspector with 5 built-in specialist profiles
- four-layer quality system
- Chinese-first user boundary with English-first execution kernel
