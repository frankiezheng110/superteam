# OMC Research Notes

Source repository: `Yeachan-Heo/oh-my-claudecode`
Focus: team orchestration, teammate boundaries, persistence, verification model

## Overview

`OMC` treats multi-agent work as a lead-driven orchestration system.

Its center of gravity is not just role prompts. It is a staged team pipeline with:

- explicit phase routing,
- specialist teammate boundaries,
- persisted state,
- mandatory handoffs,
- a verify/fix loop,
- strong separation between orchestrator and worker authority.

## Pipeline Rules

Canonical pipeline:

1. `team-plan`
2. `team-prd`
3. `team-exec`
4. `team-verify`
5. `team-fix` -> loop back when needed

### Stage routing

- `team-plan` favors `explore` and `planner`, sometimes `analyst` or `architect`.
- `team-prd` uses `analyst`, optionally `critic`.
- `team-exec` is execution-heavy and can route to `executor`, `debugger`, `designer`, `writer`, or `test-engineer`.
- `team-verify` centers on `verifier` and may add review specialists.
- `team-fix` routes based on failure type, usually back to execution specialists.

### Transition discipline

- Stage transitions are constrained, not free-form.
- `team-verify` can complete the run or generate fix tasks.
- `team-fix` is bounded and should not loop forever.

## Teammate Rules

### Lead vs worker authority

- The lead orchestrator chooses stage agents.
- Workers are not allowed to perform orchestration behavior.
- Workers must not spawn their own subagents.
- User overrides mainly affect execution-stage agent choice, not the whole pipeline.

### Specialist boundaries

- `planner` plans and does not implement.
- `executor` implements but should not make architecture decisions.
- `critic` is a rejection-oriented quality gate.
- `verifier` is a separate approval lane and should not self-approve authored work.

This creates strong role separation across planning, execution, critique, and verification.

## Coordination and Persistence

### Persisted state

- Team state is written to local state artifacts.
- State includes phase, phase history, iteration, artifacts, and resume information.
- Cancellation can preserve enough state for later resume.

### Handoffs are mandatory

- Each completed stage should produce a handoff document.
- Handoffs survive cancellation and are read by later stages.
- This externalizes project memory instead of relying on conversational carry-over.

### Coordination model

- Workers coordinate through task and message protocols.
- Team execution is not ad hoc chat; it is explicit orchestration with tracked work items.

## Quality Gates

### Verification is a separate stage

- Verification is distinct from execution.
- Verification requires fresh evidence and actual command output.
- Results should be reported in structured PASS / FAIL / INCOMPLETE style.

### Review escalation

- Higher-risk changes can trigger stronger review roles.
- Security review and stronger code review are added when complexity or sensitivity increases.

### Fix loop bounds

- Verification failures create fix work.
- Fix attempts are bounded.
- Too many failed iterations should force termination instead of silent looping.

## Key Evidence

- `skills/team/SKILL.md`: canonical team pipeline and lead-selected routing.
- `skills/team/SKILL.md`: each stage must produce a handoff document.
- `agents/planner.md`: planner plans only and does not implement.
- `agents/executor.md`: executor implements only and is not responsible for architecture or review.
- `agents/critic.md`: critic is a hard quality gate.
- `agents/verifier.md`: verification is a separate reviewer pass and requires fresh evidence.
- `docs/ARCHITECTURE.md`: state, verification evidence rules, and orchestration model.
- `src/team/worker-bootstrap.ts`: workers are not leaders and must not spawn subagents.

## Integration Implications

- `OMC` should supply the teammate collaboration model in `SuperTeam`.
- Persistent handoffs and state artifacts are worth carrying over directly.
- The lead/worker split should remain strict.
- Verification should remain a separate lane instead of collapsing into execution.
- `OMC` role boundaries can be reused, but the pipeline itself should be adapted so it aligns with the `Superpowers` stage discipline.
