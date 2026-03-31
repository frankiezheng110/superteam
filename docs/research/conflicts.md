# SuperTeam Conflict Matrix

This document records where `Superpowers` and `OMC` overlap, conflict, or complement each other.

Rule ownership is assigned so `SuperTeam` does not become a stitched-together hybrid with unclear authority.

## Ownership Principle

- `Superpowers` owns stage methodology and transition discipline.
- `OMC` owns teammate collaboration patterns and role boundaries.
- `SuperTeam` interface rules define how stages hand work to teammates.

## Conflict Matrix

| Concern | Superpowers default | OMC default | SuperTeam owner | SuperTeam decision |
| --- | --- | --- | --- | --- |
| Stage order | Brainstorm -> Plan -> Execute -> Verify -> Finish | team-plan -> team-prd -> team-exec -> team-verify -> team-fix loop | Superpowers | Keep a strict top-level path, expanded locally into `clarify -> design -> plan -> execute -> review -> verify -> finish` |
| Design gate | Hard gate before implementation | Planning stage exists, but the pipeline is team-oriented | Superpowers | No implementation before approved design and plan |
| Planning detail | Atomic tasks with files, commands, expected outputs, TDD steps | Planner-focused stage artifacts and handoffs | Superpowers | Plans keep the stronger task-package detail level |
| Delegation model | Fresh subagent per task | Persistent teammate roles with externalized context | Interface Layer | Use persistent named roles, but keep task-package discipline |
| Authority split | Controller delegates tasks | Lead orchestrator controls stage routing; workers cannot orchestrate | OMC | Keep strict orchestrator/worker separation |
| TDD enforcement | Failing test first, then implementation | Testing is important but not the whole-system identity | Superpowers | Add explicit `tdd-guardian` review injection and keep test-first planning |
| Review structure | Layered spec review and quality review | Strong verify stage with critic escalation | Interface Layer | Split the middle gates into `review` and `verify` so challenge and verdict remain separate |
| Verification evidence | Fresh evidence required before completion claims | Fresh evidence required in separate verification pass | Shared, codified by Interface Layer | Keep a separate verifier and require fresh evidence every cycle |
| Handoff persistence | Prompt packages carry context | Handoffs and state artifacts preserve context | OMC | Make stage handoffs mandatory and file-based |
| Fix loop bounds | Re-plan or escalate when blocked | Explicit bounded fix loop | OMC | Keep a bounded verify-driven repair loop with orchestrator escalation |

## Key Integration Decisions

### 1. Superpowers owns the global path

`SuperTeam` will preserve a clear top-level progression:

1. clarify
2. design
3. plan
4. execute
5. review
6. verify
7. finish

This keeps the project aligned with `Superpowers` discipline instead of inheriting the full native `OMC` pipeline.

### 2. OMC owns teammate behavior

`SuperTeam` teammates are persistent role definitions with handoff-driven memory. They are not disposable task workers by default.

### 3. Interface rules absorb the friction

The interface layer must define:

- what artifact leaves each stage,
- which teammate receives it,
- what evidence is needed to close the stage,
- when to enter fix mode,
- when to escalate to the lead.

### 4. Review becomes two-tier

- lightweight task-level checks happen during execution;
- formal approval happens in the dedicated review / verification lane.

This preserves `Superpowers` rigor without forcing every tiny change through a full end-stage ceremony.

## Resulting Direction

`SuperTeam` is neither a literal copy of `Superpowers` nor a literal copy of `OMC`.

It is a new framework where:

- `Superpowers` defines when work may advance,
- `OMC` defines how teammates collaborate,
- `SuperTeam` defines the contracts between the two.
