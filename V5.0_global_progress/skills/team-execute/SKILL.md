---
name: team-execute
description: Run the execute stage with native Claude Code agent teams. Use when an approved SuperTeam plan can be split into independent parallel tasks and agent teams are enabled.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Team Execute

Use native Claude Code agent teams for the execution phase of:

`$ARGUMENTS`

## Preconditions

- design and plan already exist in `.superteam/runs/<task-slug>/`
- the task can be decomposed into independent execution units
- agent teams are enabled in Claude Code
- the approved plan explicitly declares `execution_mode=team`
- the approved plan defines `conflict_domain` and `merge_owner`
- the approved plan defines `touched_files` or an expected file boundary

## Read First

- `framework/skill-common-rules.md`
- `framework/verification-and-fix.md`

## Team Execution Rules

- keep top-level ownership with the orchestrator
- use teams only for the `execute` stage, not for clarify, review, or final verification
- split by file set, module boundary, or explicit conflict domain to avoid edit conflicts
- require each teammate to report touched files, what changed, local evidence, and concerns
- require the merge owner to consolidate results before execution can hand off to review
- consolidate results into `.superteam/runs/<task-slug>/execution.md`
- after team execution, run a separate review stage and then a separate verify stage; do not self-certify completion inside the team

## Fallback Rule

If agent teams are unavailable or the task is too interdependent, stop using this skill and fall back to regular execution under `/superteam:execute`.
