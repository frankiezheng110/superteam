# SuperTeam Project Plan

## Phase 1: Design Lock

Goal: finalize the architecture and initial scope for the independent SuperTeam project.

- [x] Read the exported Claude Code conversation for context
- [x] Decide to build an independent version instead of mirroring startup exactly
- [x] Write the initial design spec
- [x] Review the design spec and adjust wording if needed

## Phase 2: Research Extraction

Goal: build a local source library for both upstream systems.

- [x] Extract core `Superpowers` stage rules into `docs/research/superpowers.md`
- [x] Extract collaborator-source teammate rules into `docs/research/omc.md`
- [x] Record source links and direct rule evidence

## Phase 3: Conflict Mapping

Goal: decide which system owns each overlapping concern.

- [x] Map stage-order rules, TDD rules, review timing, and handoff rules
- [x] Write a conflict matrix in `docs/research/conflicts.md`
- [x] Mark each concern with a primary owner and integration note

## Phase 4: Framework Definition

Goal: define the local orchestration contracts.

- [x] Write stage contract docs in `framework/`
- [x] Define handoff template format
- [x] Define verification and escalation rules

## Phase 5: Agent and Skill Adaptation

Goal: adapt teammate roles and workflow entry points for SuperTeam.

- [x] Draft core teammate definitions in `agents/`
- [x] Draft stage entry skill files in `skills/`
- [x] Ensure each file follows the phase ownership model

## Phase 6: Validation

Goal: test SuperTeam on a sample engineering task and collect improvement notes.

- [x] Run one end-to-end workflow on a sample engineering task
- [x] Record what worked and what broke
- [x] Revise framework documents based on evidence

## Phase 7: Productivity Upgrade

Goal: strengthen SuperTeam as an AI agent team product rather than a comparison artifact.

- [x] Write a V1.0.3 productivity-first design spec
- [x] Review and approve the spec
- [x] Strengthen framework contracts for routing, state, scorecard, and finish readiness
- [x] Update skills and agent prompts to match the stronger contracts
- [x] Add V1.0.3 release notes and productivity validation
- [x] Add a local `writing-skills` meta skill so the skill surface can evolve inside SuperTeam itself

## Phase 8: Self-Improving Productivity Loop

Goal: make `SuperTeam` capture reusable learning from real runs and route it into product improvement.

- [x] Write a V1.0.4 self-improving productivity loop design spec
- [x] Review and approve the spec
- [x] Add a plan quality gate to framework and planning skill contracts
- [x] Add `retrospective.md` as a required artifact for meaningful completed runs
- [x] Extend state/status contracts with learning capture and improvement routing fields
- [x] Add V1.0.4 release notes and productivity validation

## Phase 9: Final Fusion

Goal: complete the product-level fusion of `Superpowers` workflow discipline and OMC team collaboration.

- [x] Write a V1.0.5 final-fusion design spec
- [x] Review and approve the spec
- [x] Reorganize the product around workflow kernel, team topology, interface contracts, and product surface
- [x] Simplify the runtime role model into core roles plus specialist support and review profiles
- [x] Tighten team-execution boundaries with `execution_mode`, `conflict_domain`, and `merge_owner`
- [x] Formalize the language boundary between Chinese-first user surfaces and English-first execution surfaces
- [x] Add V1.0.5 release notes and productivity validation

## Current Status

V1.0.5 final-fusion version delivered with a cleaner four-layer architecture, a smaller core role model, tighter team-execution boundaries, a clearer language policy, and the V1.0.4 learning loop retained inside a more coherent product.

## Phase 10: Adapted Skill Fusion

Goal: absorb a small set of high-value external skill ideas into SuperTeam without breaking the V1.0.5 fused architecture.

- [x] Research gstack and everything-claude-code skill candidates
- [x] Decide which skill patterns should be adapted versus copied or rejected
- [x] Write a V1.1.0 skill-fusion design spec
- [x] Add adapted `design-consultation`, `careful`, `guard`, and `strategic-compact` skills
- [x] Update framework and skill docs to define trigger boundaries and optional-mode behavior
- [x] Add V1.1.0 release notes and productivity validation

## Current Status

V1.1.0 skill-fusion version delivered with adapted design consultation, explicit safety modes, stage-aware compaction guidance, and updated framework contracts that keep these additions inside the existing seven-stage kernel.

## Phase 11: UI Intent Pipeline

Goal: make UI intent a first-class cross-stage contract so design quality is preserved into implementation and verification.

- [x] Analyze the mismatch between frontend-design and the current SuperTeam design/execute split
- [x] Write a V1.2.0 UI Intent Pipeline design spec
- [x] Formalize `ui_weight` and `ui-intent.md` as workflow concepts
- [x] Refactor framework contracts, skills, and agent guidance to carry UI intent across stages
- [x] Add V1.2.0 release notes, productivity validation, and a sample run

## Current Status

V1.2.0 UI Intent Pipeline version delivered with graded UI task handling, a formal `ui-intent.md` contract, stronger design-to-code continuity, and explicit UI quality gates in review and verification.
