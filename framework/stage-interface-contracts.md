# SuperTeam Stage Interface Contracts

This document defines the required handoff package between stages.

Concrete artifact locations live in `framework/runtime-artifacts.md`.

## Contract Table

| Stage | Required input | Required output | Primary consumer | Completion test |
| --- | --- | --- | --- | --- |
| `clarify` | user request, known constraints, current repo context, direct user participation | `project-definition.md`, clarified objective, core task list, input/output shape, explicit constraints, non-goals, unresolved questions, recorded user approval, `ui_weight` and experience goal when UI is present, design thinking seeds when `ui-standard` or `ui-critical`, reviewer continuity note, `activity-trace.md` updates | `orchestrator`, `architect`, `planner` | the answer to "what exactly should this project do?" is specific enough to compare solutions |
| `design` | `project-definition.md`, clarified constraints, participation mode for solution work | approved `design.md`, `solution-options.md`, `solution-landscape.md`, selected whole-project solution direction, selected per-domain decisions, rejected alternatives, recorded user approval, approved `ui-intent.md` with aesthetic contracts when required, reviewer continuity note, `activity-trace.md` updates | `orchestrator`, `planner` | the chosen development solution is explicit enough to plan without hidden debate |
| `plan` | approved design artifact, `solution-options.md`, `solution-landscape.md`, and `ui-intent.md` when required | atomic task list, file targets or bounded search scope, commands, expected outputs, verification steps, TDD notes, done signals, recorded user approval of the final plan, plan quality gate result, execution mode when relevant, UI intent translation with aesthetic implementation constraints when required, reviewer continuity note, `activity-trace.md` updates | `executor`, `inspector`, `verifier` | each task is executable without hidden context |
| `execute` | approved plan, prior handoffs, and `ui-intent.md` when required | implementation result, changed artifact list, self-check output, open concerns, `polish.md`, UI intent preservation notes with aesthetic compliance evidence when required | `inspector`, `reviewer`, `verifier` | work is implemented, local checks are recorded, and post-execute polish is documented |
| `review` | execution output, `polish.md`, and evidence | blocker list or review clearance, rule-gate notes, escalation notes, UI quality gate result with aesthetic dimension checks when required, anti-pattern gate result when required | `verifier`, `orchestrator` | review-specific blockers are resolved or recorded |
| `verify` | execution output, review output, and fresh evidence | PASS / FAIL / INCOMPLETE report, fix package when needed, UI intent evidence coverage with aesthetic contract verification when required | `orchestrator`, `executor` | independent evidence supports the verdict |
| `finish` | PASS report, final artifacts, latest scorecard, Reviewer report, `activity-trace.md` | final delivery summary, residual risks, follow-up options, archive-ready handoff, retrospective artifact, trace summary, Reviewer summary, final UI intent outcome with aesthetic quality assessment when required | user or next operator | output is understandable without reopening prior context |

## First-Three-Stage Naming Rule

Use these business labels in user-facing artifacts when they improve clarity:

- `clarify` -> `Project Definition`
- `design` -> `Development Solutions`
- `plan` -> `Execution Plan`

These are aliases for the same first three stages, not new stages.

## Participation Contract

- `clarify`: direct user participation is mandatory and explicit user approval is required to close the stage
- `design`: user participation is optional during exploration, but the final solution choice must still be attributable and explicit user decision is required before shaping work begins
- `plan`: the drafting loop is internal, but explicit user approval of the final plan is required before `execute`

After `plan` is approved and `execute` begins, the workflow should proceed without further user involvement unless the user explicitly intervenes.

## Design Stage Hard-Close Checklist

Before `design` can be closed and `plan` can begin, orchestrator must verify all of the following are present on disk. Missing any item = design stage is NOT closed:

| Artifact | Path | Required when |
|---|---|---|
| `design.md` | `.superteam/runs/<task-slug>/design.md` | always |
| `solution-options.md` | `.superteam/runs/<task-slug>/solution-options.md` | always |
| `solution-landscape.md` | `.superteam/runs/<task-slug>/solution-landscape.md` | always |
| `ui-intent.md` | `.superteam/runs/<task-slug>/ui-intent.md` | when `ui_weight` is `ui-standard` or `ui-critical` |
| Cleanup confirmed | designer reports rejected preview files deleted | when designer produced preview artifacts |

**Rejected design files cleanup**: when the designer produced HTML preview files, screenshots, or other design iteration artifacts during the option loop, these must be deleted from the project directory before design closes. Confirmed by designer in handoff note. Orchestrator must check this confirmation before advancing.

**Why this gate exists**: In prior runs, the design stage was never formally closed (state.json showed `current_stage: "design"` while execution was already complete). There was no `ui-intent.md`, no `design.md`. Aesthetic contracts were informally embedded in `plan.md`, and 12+ rejected design preview files remained in the project directory permanently.

## Plan Delivery Scope Rule

Plan artifacts must classify each delivery item into one of two tiers:

- **MUST** — committed for this version; absence at review is a BLOCKER
- **DEFERRED** — planned but not committed; must state reason and target version

Inspector treats every MUST item as a delivery contract. Absence = BLOCKER, not MINOR.

Do not use ambiguous ✅ for items that are actually DEFERRED. If something is not committed for this version, mark it DEFERRED explicitly.

## Supplement Contract

The three user closure gates are re-enterable by developer supplement.

- `clarify` supplement - reopens project-definition discussion without automatically declaring full rollback
- `design` supplement - reopens the option loop without automatically discarding all shaping work
- `plan` supplement - reopens execution planning without automatically reopening solution debate

When a supplement happens, record at least:

- supplement type
- supplement reason
- supplement anchor
- earliest invalidated stage
- affected downstream artifacts
- whether the supplement stayed local or escalated into rollback

When `design` begins, record one participation mode:

- `co-create`
- `observe`
- `decision-only`

## Reviewer Continuity Contract

The Reviewer remains a passive auditor, but must leave continuity checkpoints across `clarify`, `design`, and `plan`.

For each of those stages, record at least:

- stage name
- checkpoint summary
- open concern count
- safe-to-advance judgment

## Post-Execute Polish Contract

Before `review`, `SuperTeam` may run a refinement bridge without creating a new stage.

- `simplifier` refines changed code while preserving behavior
- `doc-polisher` tightens changed docs and handoffs without changing facts
- `release-curator` cleans delivery-facing structure or release surfaces within scope
- the bridge must write `.superteam/runs/<task-slug>/polish.md`
- if the bridge changes behavior-relevant files, fresh local checks are required before `review`

## Approval Record

Every stage handoff that closes `design`, `plan`, `review`, or `finish` should record:

- approval status
- approved by
- approval date
- blocking findings, if any

For `ui-standard` and `ui-critical` tasks, `ui-intent.md` should be approved with `design.md` rather than treated as an optional side note.

For `clarify`, also record whether direct user participation happened and whether the definition closure gate was approved.

For `design`, also record whether the option loop was explicitly closed by the user before shaping began.

For `plan`, also record whether the final plan approval gate was explicitly approved by the user.

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
- green step for the smallest passing implementation when code changes are involved
- refactor step that preserves passing behavior when code changes are involved
- verification commands
- expected outputs
- done signal
- blocker and escalation note
- reference to selected Stage-2 decisions rather than reopening solution debate inside planning

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
- red-green-refactor note
- review focus note
- acceptance-risk note when user-visible behavior changes

## Execution Result Schema

Every execution handoff should contain:

- what changed
- what was intentionally not changed
- touched files or file boundary actually used
- TDD path used: `red -> green -> refactor` or recorded exception
- failing test reference that existed before implementation, when applicable
- green evidence showing the smallest passing implementation, when applicable
- refactor summary with behavior-preservation note, when applicable
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
- TDD evidence-chain status for code-changing work
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
- trace summary for the first three stages
- Reviewer summary reference and acknowledgment status

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
- TDD gate result for code-changing work
- blocking issues
- non-blocking concerns
- required fixes before verification, if any
- explicit recommendation: `CLEAR`, `CLEAR_WITH_CONCERNS`, or `BLOCK`

## Development Solutions Package

`design` should be run as one stage with two internal segments:

- `Option Loop` - interaction-heavy work that combines internal options, external evidence, user-supplied options, unified comparison, challenge, and user decision
- `Solution Shaping` - lower-interaction work that turns the chosen direction into `design.md` and `ui-intent.md` when required

`solution-options.md` should contain:

- project-definition reference
- participation mode
- user-supplied options or constraints when relevant
- whole-project candidate options
- per-domain candidate options
- selected whole-project direction
- selected per-domain decisions
- recorded user decision and approval
- rejected alternatives and rationale
- cross-domain fit notes
- planning risks

`solution-landscape.md` should contain:

- search framing
- anchor list
- representative keyword groups
- search lanes covered or explicitly skipped
- option-loop breadth findings
- option-loop validation findings
- evidence cards
- patterns worth borrowing
- patterns worth rejecting
- official constraints or platform limits
- unresolved contradictions

For `ui-standard` and `ui-critical` tasks, also include:

- aesthetic dimension assessment (typography, color, motion, spatial, visual detail)
- anti-pattern gate result (pass / violations found)
- aesthetic intent preservation assessment
