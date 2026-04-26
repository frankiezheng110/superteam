# Superpowers Research Notes

Source repository: `obra/superpowers`
Focus: workflow discipline, planning rules, execution model, quality gates

## Overview

`Superpowers` is best understood as a staged software-delivery method encoded in skill files.

Its core behavior is not "use subagents sometimes". Its real core is a gated flow:

1. brainstorm and clarify;
2. write and review a plan;
3. execute tasks through controlled delegation;
4. enforce TDD and verification;
5. finish the branch only after tests and review pass.

## Stage Rules

### 1. Brainstorming is a hard gate

- Design must be explored before implementation.
- The workflow asks clarifying questions one at a time.
- It requires proposing 2-3 approaches before choosing one.
- A written design/spec is required before implementation planning.
- The design then goes through a review loop and a user approval gate.

### 2. Planning is mandatory after design

- The approved spec must be converted into a detailed implementation plan.
- The plan is expected to contain exact file paths, commands, expected outputs, TDD steps, and commit steps.
- Tasks should be atomic, usually 2-5 minutes each.
- The plan itself should be reviewed before execution starts.

### 3. Branch finishing is a formal terminal phase

- Tests must be verified before offering integration options.
- Merge, PR, or cleanup actions happen only after verification.
- Destructive branch-discard flows require explicit confirmation.

## Agent / Execution Rules

### Fresh subagent per task

- Execution is controller-led.
- Each task should be delegated to a fresh implementer subagent.
- The implementer should receive the task package directly, not just a reference to a plan file.
- The controller interprets implementer status and decides the next action.

### Normalized implementer status

- `DONE`
- `DONE_WITH_CONCERNS`
- `NEEDS_CONTEXT`
- `BLOCKED`

These statuses let the controller decide whether to review, supply more context, or re-plan.

### Execution style

- Subagent-driven development is the preferred mode.
- Inline execution is the fallback mode.
- Parallel implementation subagents are discouraged because of conflict risk.
- Git worktrees are an expected companion workflow for isolation.

## Quality Gates

### TDD is non-optional

- No production code should be written before a failing test exists.
- The workflow is explicitly red -> green -> refactor.
- If implementation was written before the failing test, the rule says it should be removed and re-done correctly.

### Fresh verification is mandatory

- Completion claims require fresh evidence.
- The same message claiming success should include the verification evidence.
- Passing earlier tests is not enough if they were not re-run.

### Review is layered

- Spec compliance review comes before code quality review.
- Review is required after tasks, major features, and before merge.
- Review severity is explicit, with blocking issues treated separately from suggestions.

## Key Evidence

- `skills/brainstorming/SKILL.md`: do not implement before design approval.
- `skills/brainstorming/SKILL.md`: the only next skill after brainstorming is planning.
- `skills/writing-plans/SKILL.md`: tasks are atomic and include files, commands, expected outputs, TDD steps, and commit steps.
- `skills/subagent-driven-development/SKILL.md`: fresh subagent per task plus layered review.
- `skills/test-driven-development/SKILL.md`: no production code without a failing test first.
- `skills/verification-before-completion/SKILL.md`: evidence before claims.
- `skills/finishing-a-development-branch/SKILL.md`: verify tests before offering branch-finishing actions.

## Integration Implications

- `Superpowers` should own stage order and transition discipline in `SuperTeam`.
- Planning cannot be optional in the final framework.
- TDD and fresh verification should remain separate hard gates.
- Review should stay multi-step instead of collapsing into one generic approval pass.
- The original fresh-subagent model is valuable as a discipline pattern, but it does not need to be copied literally if `SuperTeam` chooses persistent teammates.
