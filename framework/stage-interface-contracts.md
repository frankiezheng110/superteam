# SuperTeam Stage Interface Contracts

This document defines the required handoff package between stages.

Concrete artifact locations live in `framework/runtime-artifacts.md`.

## Contract Table

| Stage | Required input | Required output | Primary consumer | Completion test |
| --- | --- | --- | --- | --- |
| `clarify` | user request, known constraints, current repo context | clarified objective, constraints, success criteria, unresolved questions, `ui_weight` and experience goal when UI is present, design thinking seeds when `ui-standard` or `ui-critical` | `architect`, `planner` | problem statement is specific enough to design |
| `design` | clarified objective and constraints | approved `design.md`, approved `ui-intent.md` with aesthetic contracts when required, architectural decisions, risk notes | `planner` | design is reviewable and approved |
| `plan` | approved design artifact and `ui-intent.md` when required | atomic task list, file targets or bounded search scope, commands, expected outputs, verification steps, TDD notes, done signals, plan quality gate result, execution mode when relevant, UI intent translation with aesthetic implementation constraints when required | `executor`, `reviewer`, `verifier` | each task is executable without hidden context |
| `execute` | approved plan, prior handoffs, and `ui-intent.md` when required | implementation result, changed artifact list, self-check output, open concerns, UI intent preservation notes with aesthetic compliance evidence when required | `reviewer`, `verifier` | work is implemented and local checks are recorded |
| `review` | execution output and evidence | blocker list or review clearance, rule-gate notes, escalation notes, UI quality gate result with aesthetic dimension checks when required, anti-pattern gate result when required | `verifier`, `orchestrator` | review-specific blockers are resolved or recorded |
| `verify` | execution output, review output, and fresh evidence | PASS / FAIL / INCOMPLETE report, fix package when needed, UI intent evidence coverage with aesthetic contract verification when required | `orchestrator`, `executor` | independent evidence supports the verdict |
| `finish` | PASS report, final artifacts, latest scorecard | final delivery summary, residual risks, follow-up options, archive-ready handoff, retrospective artifact, final UI intent outcome with aesthetic quality assessment when required | user or next operator | output is understandable without reopening prior context |

## Approval Record

Every stage handoff that closes `design`, `plan`, `review`, or `finish` should record:

- approval status
- approved by
- approval date
- blocking findings, if any

For `ui-standard` and `ui-critical` tasks, `ui-intent.md` should be approved with `design.md` rather than treated as an optional side note.

## UI Weight

Every task should classify UI impact as one of:

- `ui-none`
- `ui-standard`
- `ui-critical`

Use:

- `ui-none` when no meaningful user-facing interface quality is in scope
- `ui-standard` when UI quality affects delivery quality but is not the sole product value
- `ui-critical` when interface quality, interaction feel, visual identity, or frontend experience is central to success

`ui-standard` and `ui-critical` require `ui-intent.md`.

## UI Intent Package

`ui-intent.md` is the formal cross-stage contract for UI-bearing work.

It should:

- be owned by the `UI Intent Owner function`
- be produced during `design`
- be approved together with `design.md`
- block `plan` from starting when required but missing
- be consumed explicitly by `plan`, `execute`, `review`, `verify`, and `finish`

### Structural Sections (existing)

- `UI Weight`
- `Experience Goal`
- `Implementation Intent`

### Aesthetic Sections (V3.0.0)

These sections are required for `ui-standard` and `ui-critical` work. They carry the aesthetic intelligence from `framework/frontend-aesthetics.md` into the concrete project context.

- `Aesthetic Direction` — the selected tone from the Design Thinking Framework, its rationale, and the differentiation target. Must be bold and intentional, not generic.
- `Typography Contract` — specific display font, body font, hierarchy rules, and why these fonts serve the aesthetic direction. Must avoid the anti-pattern registry fonts.
- `Color Contract` — dominant palette with hex values, accent strategy, semantic color mapping, CSS variable naming plan. Must avoid cliché color schemes.
- `Motion Contract` — animation philosophy, key high-impact moments, technology choice (CSS-only / Motion / GSAP), timing and easing guidance. Must match the aesthetic direction intensity.
- `Spatial Contract` — layout philosophy (bento / editorial / floating / scroll-narrative / custom), composition rules, responsive behavior, negative space strategy.
- `Visual Detail Contract` — atmosphere approach (gradients / textures / patterns / overlays), depth strategy (shadows / layers / blur), decorative elements that match the tone.
- `Anti-Pattern Exclusions` — which items from the anti-pattern registry are most relevant to this project and explicit commitments to avoid them.

### Validation Checklist

- [ ] UI weight is classified
- [ ] experience goal is stated
- [ ] aesthetic direction is bold and intentional, not generic
- [ ] typography is distinctive and matches the aesthetic direction
- [ ] color palette is cohesive with clear accent hierarchy
- [ ] motion is high-impact and coordinated, not scattered
- [ ] spatial composition is intentional, not template-derived
- [ ] visual details create atmosphere and depth
- [ ] no mandatory anti-pattern violations present
- [ ] implementation complexity matches the aesthetic vision
- [ ] design tokens are specified enough to implement
- [ ] interaction states are defined

## Plan Package Schema

Every executable task package should contain:

- task id
- objective
- exact target files or a bounded search scope
- constraints
- implementation steps
- test-first step when code changes are involved
- verification commands
- expected outputs
- done signal
- blocker and escalation note

For `ui-standard` and `ui-critical` tasks, the package should also contain:

- `ui_weight`
- reference to `ui-intent.md`
- `UI intent translation`
- `aesthetic_implementation_complexity` — whether the aesthetic vision demands elaborate or restrained implementation

Before `plan` exits, the orchestrator should assign one structural quality result to the package:

- `pass`: all critical and support fields exist
- `at_risk`: all critical fields exist but one support field is missing
- `fail`: one or more critical fields are missing

Critical fields:

- objective
- exact target files or a bounded search scope
- implementation steps
- verification commands
- done signal

Support fields:

- constraints
- expected outputs
- blocker and escalation note

Exploratory work may use a bounded search scope instead of exact target files, but it must also declare a clear exit condition.

For UI-heavy work that used `design-consultation`, the plan package should reference the visual-system input artifact explicitly.

`UI intent translation` should state:

- which design tokens must survive into implementation (specific fonts, colors, spacing values)
- which interaction states must exist
- which UI qualities must not degrade into generic templates
- which UI-specific review and verify checks are required
- which anti-patterns from the registry must be actively avoided during implementation
- what level of implementation complexity the aesthetic vision demands

When the package is intended for team execution, it should also contain:

- `execution_mode`: `single` or `team`
- `conflict_domain`
- `touched_files` or expected file boundary
- `merge_owner`

Strongly recommended for code-changing tasks:

- parallelism note
- risk level
- failing-test-first note
- review focus note
- acceptance-risk note when user-visible behavior changes

## Execution Result Schema

Every execution handoff should contain:

- what changed
- what was intentionally not changed
- touched files or file boundary actually used
- local checks performed
- raw evidence references
- concerns or uncertainty

For `ui-standard` and `ui-critical` tasks, also include:

- UI intent preservation notes
- aesthetic compliance evidence — confirmation that the implemented UI matches the aesthetic contracts in `ui-intent.md`
- any intentional UI degradation caused by technical constraints
- any remaining mismatch between intended and implemented interface quality
- anti-pattern compliance — confirmation that no mandatory anti-pattern violations exist in the implementation

If execution used team mode, also include:

- team split used
- merge owner
- conflict notes, if any

## Verification Result Schema

Every verification report should contain:

- verdict: `PASS`, `FAIL`, or `INCOMPLETE`
- checked requirements
- evidence summary
- missing evidence, if any
- what is proven done
- remaining risks
- exposed process weakness, if any
- recommended improvement sink: `writing-skills`, framework docs, or deferred follow-up
- fix tasks, if any
- escalation recommendation, if any

For `ui-standard` and `ui-critical` tasks, also include:

- UI intent evidence coverage
- aesthetic contract verification — whether each aesthetic section in `ui-intent.md` has supporting evidence
- anti-pattern gate result — whether any mandatory anti-pattern violations were found
- unresolved UI intent loss, if any

## Scorecard Schema

Every active run should maintain a compact scorecard containing:

- current objective
- active stage
- next action
- blocker summary
- blocker owner when blocked
- active specialists when relevant
- routing rationale when non-default specialists are active
- readiness state for downstream work: `ready`, `at_risk`, or `not_ready`
- evidence freshness: `fresh`, `stale`, or `missing`
- evidence summary
- unresolved risks
- delivery confidence: `high`, `medium`, or `low`
- plan quality gate when a plan exists
- learning status when relevant
- next improvement action when relevant
- execution mode when relevant
- `ui_weight` when relevant
- `ui_intent_status` when relevant
- `ui_quality_gate_status` when relevant
- `aesthetic_direction` when relevant
- `anti_pattern_gate_status` when relevant

## Orchestrator Status Schema

See `framework/orchestrator.md` → Status Update Rule for the full field list.

## Finish Result Schema

Every finish artifact should contain:

- delivered result summary
- key evidence sources
- residual non-blocking risks
- recommended next actions
- final handoff summary
- learning capture summary
- improvement routing decision

For `ui-standard` and `ui-critical` tasks, also include:

- final UI intent outcome summary
- aesthetic quality assessment — how well the implementation matches the intended aesthetic direction
- anti-pattern compliance confirmation
- residual UI degradations or compromises
- evidence links for the claimed UI outcome

## Optional Support Skill Rule

The following support skills may appear in a run without changing stage order:

- `design-consultation`
- `careful`
- `guard`
- `strategic-compact`

They assist the existing workflow. They do not create new stages or new authority lanes.

## Review Profile Rule

`inspector` owns the review stage by default and activates specialist profiles (critic, tdd, acceptance, socratic, security) internally based on risk. See `framework/role-contracts.md` → Inspector Specialist Profiles for details.

For `ui-standard` and `ui-critical` tasks, the review stage must apply a UI quality gate before `verify`, checking the five aesthetic dimensions and anti-pattern registry per `framework/frontend-aesthetics.md`.

## Mixed Artifact Language Rule

- user-facing summary prose is Chinese-first
- schema keys, verdict labels, status values, and evidence labels are English-first

## Retrospective Schema

Every meaningful completed run should also produce `retrospective.md` containing:

- main bottleneck
- avoidable rework source
- weakest task-package field, if any
- missing or late specialist support, if any
- strongest confidence-building evidence
- one concrete improvement action for `SuperTeam`

For `ui-standard` and `ui-critical` runs, also include:

- aesthetic direction effectiveness — did the chosen direction serve the product well?
- aesthetic execution quality — where did aesthetic intent survive or degrade?

Keep each section short and decision-oriented.

## Review Result Schema

Every review artifact should contain:

- scope reviewed
- applied gate set
- blocking issues
- non-blocking concerns
- required fixes before verification, if any
- explicit recommendation: `CLEAR`, `CLEAR_WITH_CONCERNS`, or `BLOCK`

For `ui-standard` and `ui-critical` tasks, also include:

- aesthetic dimension assessment (typography, color, motion, spatial, visual detail)
- anti-pattern gate result (pass / violations found)
- aesthetic intent preservation assessment
