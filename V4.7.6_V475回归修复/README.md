# SuperTeam V4.2.0

SuperTeam is a Claude Code plugin for disciplined project delivery.

Core contract:

- seven fixed stages
- three user gates: `G1`, `G2`, `G3`
- supplement-first reopening
- inspector audit + polish layer + reviewer quality gate
- strong TDD contract for code-changing work
- anchor-driven Stage-2 search for brand-new products
- UI intent as a formal cross-stage contract

## Formal Install

Local install:

```text
/plugin marketplace add "D:\opencode项目\superteam"
/plugin install superteam@superteam
/reload-plugins
```

GitHub install:

```text
/plugin marketplace add <owner>/<repo>
/plugin install superteam@superteam
/reload-plugins
```

Upgrade:

```text
/plugin marketplace update superteam
/reload-plugins
```

Marketplace root: `D:\opencode项目\superteam`

Plugin source: `D:\opencode项目\superteam\V4.2.0_立项搜索优化`

To use `/superteam:team-execute`, enable Claude Code native agent teams first:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Core Commands

- `/superteam:go <task>` - full workflow
- `/superteam:status` - current run status
- `/superteam:g1 <supplement>` - reopen project definition
- `/superteam:g2 <supplement>` - reopen solution discussion
- `/superteam:g3 <supplement>` - reopen execution planning

## Advanced Commands

- `/superteam:clarify`
- `/superteam:design`
- `/superteam:plan`
- `/superteam:execute`
- `/superteam:review`
- `/superteam:verify`
- `/superteam:finish`
- `/superteam:inspect`
- `/superteam:team-execute`
- `/superteam:design-consultation`
- `/superteam:careful`
- `/superteam:guard`
- `/superteam:strategic-compact`
- `/superteam:writing-skills`

## Quick Start Example

```text
/superteam:go add a --json export mode to the notes CLI without breaking current text output
```

That run creates artifacts under `.superteam/runs/<task-slug>/` and maintains status at `.superteam/state/current-run.json`.

At minimum you should see: `project-definition.md`, `activity-trace.md`, `solution-options.md`, `solution-landscape.md`, `design.md`, `plan.md`, `execution.md`, `polish.md`, `review.md`, `verification.md`, `scorecard.md`, `finish.md`, `retrospective.md`, `handoffs/`, and Inspector team duty reports at `.superteam/inspector/reports/<task-slug>-report.html` and `.superteam/inspector/reports/<task-slug>-report.md`.

For UI-bearing work (`ui-standard` or `ui-critical`), also expect `ui-intent.md` with aesthetic contract sections and optionally `design-system.md`.

## Workflow

`clarify -> design -> plan -> execute -> review -> verify -> finish`

Internal bridge before `review`:

`execute -> self-check/test -> simplifier / doc-polisher / release-curator -> polish.md -> reviewer`

For code-changing work, the default development rhythm is:

`red -> green -> refactor`

For brand-new products, Stage-2 search now defaults to:

`requirement anchors -> web keyword search -> GitHub keyword search -> official dependency constraints -> community signals -> failure signals`

- `G1` closes `clarify`
- `G2` closes the design option loop and starts shaping
- `G3` closes `plan` and starts `execute`

After `G3`, the remaining four stages should normally run without further user input.

Later user additions reopen the matching gate as supplement by default.

## Runtime Output

Main run outputs live under `.superteam/runs/<task-slug>/`.

Required artifacts:

- `project-definition.md`
- `activity-trace.md`
- `solution-options.md`
- `solution-landscape.md`
- `design.md`
- `plan.md`
- `execution.md`
- `polish.md`
- `review.md`
- `verification.md`
- `finish.md`

## Inspector

Inspector stays passive during the run and generates post-run reports.

- HTML report for operators
- Markdown report for system tracking
- improvement backlog for future cleanup

## Package Layout

- `.claude-plugin/` - plugin manifest
- `LICENSE` - release license
- `UPGRADE.md` - version-switch upgrade note
- `skills/` - 19 plugin skills
- `agents/` - 17 custom agents
- `framework/` - 14 workflow contracts
- `docs/validation/` - release notes and validation index

## Normative Docs

- `framework/stage-model.md` - stage order and transition rules
- `framework/orchestrator.md` - forced seven-stage orchestration contract
- `framework/development-solutions.md` - mandatory Stage-2 solution and search rules
- `framework/solution-search.md` - anchor extraction, keyword generation, layered search order, and evidence-card search discipline
- `framework/stage-interface-contracts.md` - required artifacts between stages
- `framework/runtime-artifacts.md` - where runtime files should be written
- `framework/skill-common-rules.md` - shared baseline rules for the skill surface
- `framework/role-contracts.md` - authority model and role boundaries
- `framework/verification-and-fix.md` - evidence rules, verdicts, and fix loop
- `framework/frontend-aesthetics.md` - frontend aesthetic knowledge base and anti-pattern registry
- `framework/reviewer.md` - Reviewer project quality check contract (review stage owner)
- `framework/inspector.md` - Inspector team behavior audit contract (post-run report)
- `framework/handoff-template.md` - required handoff shape
- `framework/state-and-resume.md` - resume and persistence rules

## Four-Layer Quality System

1. **Executor self-check** — runtime self-validation during implementation
2. **Polish layer** — `simplifier`, `doc-polisher`, `release-curator` refine the delivery surface without taking verdict authority
3. **Reviewer challenge** — adversarial quality gate with specialist profiles, including TDD gate enforcement on code-changing work
4. **Verifier judgment** — independent evidence-based final verdict with TDD evidence-chain checking when relevant
5. **Inspector analysis** — objective team behavior audit and continuous improvement

## Read First

1. `CLAUDE.md`
2. `VERSION.md`
3. `UPGRADE.md`
4. `framework/stage-model.md`
5. `framework/orchestrator.md`
6. `framework/stage-interface-contracts.md`
7. `framework/runtime-artifacts.md`
