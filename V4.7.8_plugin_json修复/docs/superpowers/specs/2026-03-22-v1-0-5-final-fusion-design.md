# SuperTeam V1.0.5 Final Fusion Design

Date: 2026-03-22

## Goal

`SuperTeam` V1.0.5 should become the final fused version of the product direction established in earlier versions.

The goal is not to resemble Claude Code more closely. The goal is to preserve the essential strengths of `Superpowers` and `OMC`, remove integration friction between them, and make the whole system smoother, smaller, and more reliable for real project delivery.

## First Principles

- preserve the strongest workflow discipline from `Superpowers`
- preserve the strongest collaboration discipline from `OMC`
- define one clear integration boundary instead of letting rules drift across many files
- remove duplicated roles and duplicated prompt logic when they do not add execution value
- optimize for execution quality, not language uniformity or cosmetic consistency

## Version Thesis

V1.0.3 corrected the roadmap away from comparison-first thinking.

V1.0.4 added a self-improving productivity loop.

V1.0.5 should complete the product-level fusion: seven-stage discipline, agent-team collaboration, interface contracts, and language policy should now feel like one system instead of adjacent systems.

Fusion is complete only when:

- stage order has one authority source
- team collaboration rules have one authority source
- every cross-stage transition is governed by explicit artifact contracts rather than hidden memory

## Non-Goals

- do not add an eighth stage
- do not perform a generator-heavy or schema-heavy rebuild of the repository
- do not keep duplicate roles alive only for appearance
- do not force all user-facing and execution-facing surfaces into one language

## Final Product Shape

V1.0.5 should organize the product into four layers:

### 1. Workflow Kernel

The workflow kernel keeps the canonical path:

`clarify -> design -> plan -> execute -> review -> verify -> finish`

This layer owns:

- stage order
- stage entry and exit gates
- fix-loop bounds
- completion conditions

This is the part inherited mainly from `Superpowers`.

### 2. Team Topology

The team topology layer defines how work moves between roles without breaking authority boundaries.

This layer owns:

- orchestrator authority
- worker boundaries
- specialist injection rules
- review-profile activation rules

This is the part inherited mainly from `OMC`.

### 3. Interface Contracts

The interface contract layer is the real `SuperTeam` core.

It should define one consistent contract for:

- task packages
- handoffs
- execution reports
- review verdicts
- verification verdicts
- scorecards
- retrospectives
- improvement routing

This is where the two source systems become one product.

### 4. Product Surface

The product surface includes:

- plugin manifest
- user-facing docs
- stage skills
- compatibility wrappers
- release and validation docs

This layer should describe the product clearly, but it should not become the source of truth for kernel rules.

## Role Model Simplification

V1.0.5 should make the runtime mental model smaller and clearer.

### Core Roles

The product should treat these as the six core roles:

- `orchestrator`
- `planner`
- `architect`
- `executor`
- `inspector`
- `verifier`

### Support Specialists

The product should keep these roles as specialist support, not as equal-width top-level mental models:

- `debugger`
- `test-engineer`
- `designer`
- `writer`
- `analyst`
- `researcher`
- `prd-writer`

### Review Profiles

The following should be treated primarily as injected review profiles or narrow specialist gates:

- `critic`
- `tdd-guardian`
- `acceptance-inspector`
- `security-inspector`
- `socratic-challenger`

### Lead Alias

`lead` may remain as a compatibility or operational alias for narrow runs, but it should no longer compete with `orchestrator` as a separate core mental model.

## Stronger Stage Fusion Rules

### Preserve The Seven-Stage Kernel

The seven-stage workflow remains mandatory.

### Import OMC Collaboration Where It Helps Most

The `OMC` collaboration model should be applied inside the stage system rather than replacing the stage system.

That means:

- persistent role identity is allowed
- hidden contextual carry-over is not trusted
- every meaningful transition still depends on explicit artifacts

### Fresh Context Packet Rule

V1.0.5 should make one fusion rule explicit:

- roles may be persistent
- task context must be fresh and artifact-backed

The system should never depend on unrecorded conversational memory to move work safely between stages or teammates.

## Better Task Package Contract

The plan package should remain compact but become more operationally complete.

Required fields should include:

- objective
- target files or bounded search scope
- constraints
- implementation steps
- verification commands
- expected outputs
- done signal
- blocker and escalation note

When execution mode is non-trivial, the package should also include:

- `execution_mode`: `single` or `team`
- `conflict_domain`
- `touched_files` or expected file boundary
- `merge_owner`

This allows the system to preserve `Superpowers` task precision while making `OMC`-style collaboration safer.

## Team Execution Boundary

Parallel team execution should remain optional and tightly bounded.

V1.0.5 should clarify that:

- only `execute` may use team parallelism
- team mode requires a clean split by file boundary, module boundary, or conflict domain
- every parallel worker must return touched files, evidence, and concerns
- the orchestrator or merge owner must consolidate results before the stage can close

This keeps team collaboration useful without turning every task into a merge-risk exercise.

## Review And Verification Simplification

The product should keep `review` and `verify` separate.

However, V1.0.5 should simplify the operator model:

- `inspector` is the default owner of the review stage
- review profiles are activated based on risk instead of being treated as co-equal default lanes
- `verifier` remains the only verdict authority for `PASS`, `FAIL`, and `INCOMPLETE`

`critic` remains a hard challenge gate in high-risk `design`, `plan`, and `review` work. Even as a profile-style injection, it must still be allowed to produce blocking findings instead of being reduced to advisory commentary.

## Language Policy

V1.0.5 should explicitly reject all-Chinese or all-English purity.

Use a boundary-based language policy instead:

### Chinese-first surfaces

- user-facing summaries
- compatibility documentation
- product-level onboarding and status presentation

### English-first surfaces

- execution-facing agent prompts
- schema names and status fields
- evidence and verdict vocabulary
- task-package fields that interact closely with code, tools, and command output

Rule: optimize for execution quality first, then presentation quality.

Mixed artifacts should follow a field-level rule:

- user-facing summary prose is Chinese-first
- schema keys, verdict names, status fields, and evidence labels are English-first

## Learning Loop Retained

V1.0.4 learning-loop gains should remain intact.

V1.0.5 should preserve:

- `retrospective.md`
- `plan_quality_gate`
- `learning_status`
- `improvement_action`

But these should now live inside a cleaner fused system rather than as add-ons to a still-fragmented control plane.

## Files Expected To Change

- `README.md`
- `CLAUDE.md`
- `.claude-plugin/plugin.json`
- `framework/orchestrator.md`
- `framework/stage-model.md`
- `framework/stage-interface-contracts.md`
- `framework/role-contracts.md`
- `framework/runtime-artifacts.md`
- `framework/state-and-resume.md`
- `framework/verification-and-fix.md`
- `framework/handoff-template.md`
- `skills/go/SKILL.md`
- `skills/brainstorm/SKILL.md`
- `skills/clarify/SKILL.md`
- `skills/design/SKILL.md`
- `skills/plan/SKILL.md`
- `skills/execute/SKILL.md`
- `skills/team-execute/SKILL.md`
- `skills/review/SKILL.md`
- `skills/verify/SKILL.md`
- `skills/finish/SKILL.md`
- `skills/status/SKILL.md`
- `skills/superteam/SKILL.md`
- `skills/exec/SKILL.md`
- `skills/writing-skills/SKILL.md`
- `agents/orchestrator.md`
- `agents/planner.md`
- `agents/architect.md`
- `agents/executor.md`
- `agents/inspector.md`
- `agents/verifier.md`
- `agents/critic.md`
- `agents/lead.md`
- `docs/validation/V1.0.5-release-notes.md`
- `docs/validation/V1.0.5-productivity-validation.md`
- `plan/PROJECT_PLAN.md`

## Risks

- if role simplification is only cosmetic, prompt drift will remain
- if team-execution boundaries stay vague, merge conflicts will keep leaking into execution quality
- if the language policy is unclear, files will drift back into inconsistent mixed-language prompts

## Guardrails

- preserve the seven-stage kernel exactly
- reduce mental-model duplication before adding any new capability
- keep execution prompts English-first unless a Chinese prompt is clearly better for task performance
- keep user-visible delivery and status surfaces Chinese-first
- prefer contract tightening over surface-area expansion

## Fusion Acceptance Matrix

| User fusion goal | V1.0.5 implementation response | Evidence to check |
| --- | --- | --- |
| preserve the essence of `Superpowers` seven-stage workflow | keep one forced seven-stage kernel and hard gates | `framework/stage-model.md`, `framework/orchestrator.md` |
| preserve the essence of `OMC` agent-team collaboration | keep strict orchestrator/worker boundaries and specialist injection, with `lead` retained only as an operational alias for narrow runs | `framework/role-contracts.md`, key agent prompts |
| fuse both systems without unresolved conflict | define one interface-contract layer for all stage transitions | `framework/stage-interface-contracts.md`, `framework/handoff-template.md` |
| remove whole-system logic gaps and chain conflicts | simplify the role model and clarify team-execution boundaries | `framework/role-contracts.md`, `skills/team-execute/SKILL.md`, `agents/inspector.md` |
| perform final review and appropriate simplification | align docs, skills, agents, and validation around one language and role policy | `README.md`, `CLAUDE.md`, validation docs |

## Verification Strategy

The implementation is successful when:

- the repo describes `SuperTeam` as a fused product, not a layered compromise
- the role model clearly distinguishes core roles from support specialists and review profiles
- the plan and team-execution contracts define safer collaboration boundaries
- the language policy is explicit and consistent across docs, framework, skills, and key agents
- V1.0.4 learning-loop mechanisms remain present inside the simplified V1.0.5 model
