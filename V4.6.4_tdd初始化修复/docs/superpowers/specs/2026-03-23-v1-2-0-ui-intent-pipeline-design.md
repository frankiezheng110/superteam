# SuperTeam V1.2.0 UI Intent Pipeline Design

Date: 2026-03-23

## Goal

`SuperTeam` V1.2.0 should turn UI intent into a first-class workflow asset instead of treating it as a weak side input to the design stage.

The goal is not to hand every UI-bearing project to an external frontend skill. The goal is to preserve the seven-stage kernel while ensuring that UI intent remains coherent, reviewable, implementable, and verifiable from `clarify` through `verify`.

## First Principles

- design and code may live in separate stages, but design intent must not break between them
- structure quality and experience quality are both delivery concerns
- UI-heavy tasks should not depend on ad hoc aesthetic intuition or accidental external-skill recall
- stronger external capabilities should be decomposed and internalized where they improve the system consistently
- stage discipline should remain, but stage outputs must become rich enough to preserve intent

## Problem Statement

The current `SuperTeam` flow preserves structural design more reliably than visual and interaction intent.

Today:

- `design.md` is mainly boundary, tradeoff, and risk oriented
- `design-consultation` produces a bounded visual-system input, but it is still too light to anchor the full UI chain
- `plan` does not yet force a strong translation from design intent into implementation constraints
- `execute` can preserve functionality while silently flattening UI quality
- `review` and `verify` do not yet treat UI intent preservation as a formal quality responsibility

This gap becomes severe for UI-bearing work, including but not limited to frontend-heavy products.

## Version Thesis

V1.1.0 correctly added `design-consultation` as a bounded UI support skill.

V1.2.0 should go further by formalizing a `UI Intent Pipeline` across all UI-bearing tasks.

The system should not rely on giving entire UI projects to one stronger external skill. Instead, it should decompose the strongest parts of that capability and redistribute them across the existing seven stages.

## Non-Goals

- do not remove the seven-stage workflow
- do not make `frontend-design` the default owner of all UI work
- do not collapse design and execution into a single uncontrolled stage
- do not turn UI quality into a purely subjective aesthetic preference check

## Scope Model

V1.2.0 should apply to all tasks with UI impact, using graded intensity.

### UI Weight

Every UI-bearing run should be classified during `clarify` as one of:

- `ui-none`
- `ui-standard`
- `ui-critical`

Definitions:

- `ui-none`: no meaningful UI surface or negligible user-facing impact
- `ui-standard`: UI quality matters and affects delivery quality, but the interface is not itself the core product value
- `ui-critical`: interface, interaction, feel, visual identity, or frontend experience is central to success

## Core Design: UI Intent Pipeline

V1.2.0 should add a five-part pipeline that runs through the existing seven stages.

### 1. Intent Discovery

Mapped primarily to `clarify`.

Purpose:

- determine whether UI quality is a material delivery factor
- classify `ui_weight`
- capture the basic experience goal before design begins

Required output additions in clarify artifacts:

- `ui_weight`
- primary user and usage context when UI is present
- top experience success condition

### 2. Intent Definition

Mapped primarily to `design`.

Purpose:

- define the formal UI intent in a durable artifact
- preserve the strongest parts of frontend-design style thinking without collapsing design into immediate implementation

The design stage should now produce two parallel but connected artifacts when `ui_weight` is not `ui-none`:

- `design.md`
- `ui-intent.md`

`design.md` continues to own structural shape, boundaries, interfaces, tradeoffs, and risks.

`ui-intent.md` becomes the official contract for experience intent.

### 3. Intent Translation

Mapped primarily to `plan`.

Purpose:

- translate UI intent into implementation constraints and verification targets

The plan package should explicitly consume `ui-intent.md` when `ui_weight` is not `ui-none`.

This means planning must no longer treat UI as a secondary aesthetic afterthought.

### 4. Intent Preservation

Mapped primarily to `execute`.

Purpose:

- preserve the agreed UI intent during real implementation

Execution should no longer be allowed to silently flatten visual and interaction quality while still claiming functional success.

### 5. Intent Validation

Mapped primarily to `review` and `verify`.

Purpose:

- ensure that UI intent is actually preserved in the delivered result

This does not mean pure subjective art criticism. It means validating that declared UI intent made it into the product with evidence.

## New Artifact: ui-intent.md

`ui-intent.md` should become a formal workflow artifact for all `ui-standard` and `ui-critical` tasks.

### Purpose

- preserve experience intent across stage boundaries
- convert visual and interaction quality from informal taste into a reviewable contract

### Formal Contract

- owner: `UI Intent Owner function`
- produced during `design`
- approved together with `design.md`
- for `ui-standard` and `ui-critical`, `plan` must not begin if `ui-intent.md` is missing
- `plan`, `execute`, `review`, `verify`, and `finish` must each record how they consumed or preserved the UI intent contract

### Required Sections

1. `UI Weight`
2. `Experience Goal`
3. `Aesthetic Direction`
4. `Design Tokens`
5. `Composition Rules`
6. `Interaction Rules`
7. `Implementation Intent`
8. `Validation Checklist`

### Section Meaning

#### UI Weight

- one of `ui-none`, `ui-standard`, `ui-critical`

#### Experience Goal

- target user
- primary scenario
- key experience success condition

#### Aesthetic Direction

- tone
- style archetype
- differentiation target
- what should feel memorable or distinctive

#### Design Tokens

- typography
- color system
- spacing
- radius
- elevation
- motion baseline

#### Composition Rules

- hierarchy rules
- density rules
- layout principles
- when asymmetry or grid-breaking is allowed

#### Interaction Rules

- hover, focus, loading, empty, error, success behavior
- dangerous action treatment
- feedback rhythm

#### Implementation Intent

- which design requirements must survive into code
- what may be simplified if constraints block the ideal output
- what must not be degraded into generic templates

#### Validation Checklist

- the UI quality checks that `review` and `verify` must later confirm

## Role Adjustments

V1.2.0 should keep the six-core-role runtime model intact while introducing stronger UI-specific responsibility boundaries.

### Keep Intact

- `orchestrator`
- `planner`
- `architect`
- `executor`
- `inspector`
- `verifier`

### Rebalance

#### architect

`architect` remains the owner of `design.md`.

It should continue to own:

- structural shape
- interface boundaries
- architectural tradeoffs
- risk framing

It should no longer be treated as the sole design authority for all UI-bearing work.

#### UI Intent Owner function

For `ui-standard` and `ui-critical` tasks, UI intent must have an explicit owner.

V1.2.0 should avoid prematurely inventing too many new core roles. The best near-term move is to formalize a `UI Intent Owner` function that may be fulfilled by:

- the strengthened `design-consultation` skill
- a bridge to stronger frontend design capabilities
- `designer` as the primary UI-intent specialist

This owner is responsible for `ui-intent.md`.

This is not a new core role. It is a function slot fulfilled by existing UI-capable support.

Conflict rule:

- structural conflicts are owned by `architect`
- experience-intent conflicts are owned by the `UI Intent Owner function`
- unresolved conflicts escalate to `orchestrator`

#### UI Quality Gate

`inspector` remains the review-stage owner.

But for `ui-standard` and `ui-critical` tasks, a mandatory UI quality gate should be added.

This may initially be implemented as a required review profile or expanded review contract rather than a totally new core role.

## How frontend-design Should Be Decomposed

V1.2.0 should not wholesale import frontend-design as a replacement pipeline.

It should decompose that capability into two buckets.

### Bucket A: Intent Generation

These parts should be absorbed into the local design pipeline:

- bold aesthetic direction setting
- anti-generic / anti-AI-slop design discipline
- differentiation logic
- typography, color, composition, and motion framing

Primary destination:

- `design-consultation`
- `ui-intent.md`

### Bucket B: Intentful Implementation

These parts should strengthen execution rules for UI-bearing tasks:

- preserving tokens and UI direction in code
- translating visual principles into implementation choices
- refusing generic template collapse when intent requires stronger execution

Primary destination:

- `execute`
- UI-specific execution constraints
- UI review and verification evidence

## Stage-by-Stage Contract Changes

### clarify

Add:

- `ui_weight`
- early experience goal when UI exists

### design

Add:

- required `ui-intent.md` for `ui-standard` and `ui-critical`
- stronger `design-consultation` behavior focused on intent, not just lightweight style tokens

### plan

Add a required `UI intent translation` section when `ui_weight` is not `ui-none`.

This section should map:

- token usage
- interaction-state requirements
- non-degradable UX commitments
- review and verify focus areas

### execute

Add `UI intent preservation notes` in `execution.md` for UI-bearing tasks.

This should record:

- which intent requirements were preserved
- where technical constraints forced degradation
- where implementation still deviates from the intended result

### review

Add a mandatory UI quality gate for `ui-standard` and `ui-critical` tasks.

This gate should check at least:

- visual consistency
- hierarchy expression
- dangerous action treatment when relevant
- state completeness
- whether the result degraded into generic UI despite stronger declared intent

### verify

Add UI-intent evidence confirmation.

Verification should confirm:

- whether the key items in `ui-intent.md` have supporting evidence
- whether major UI intent was lost during plan or execution

### finish

Add UI-intent closure to the final delivery packaging.

`finish.md` should record:

- final UI intent outcome summary
- residual degradations or compromises that remain
- links to the evidence that supports the claimed outcome
- recommended follow-up improvements when the final UI result intentionally falls short of the intended design quality

## Sample Enforcement Rules

- `ui-none`: no `ui-intent.md` required
- `ui-standard`: `ui-intent.md` required, UI review gate required, UI evidence required
- `ui-critical`: stronger `design-consultation`, stronger UI review gate, richer execution notes, and stricter UI evidence expectations

## File Changes Expected

- `framework/orchestrator.md`
- `framework/stage-interface-contracts.md`
- `framework/runtime-artifacts.md`
- `framework/state-and-resume.md`
- `framework/role-contracts.md`
- `skills/clarify/SKILL.md`
- `skills/design/SKILL.md`
- `skills/design-consultation/SKILL.md`
- `skills/plan/SKILL.md`
- `skills/execute/SKILL.md`
- `skills/review/SKILL.md`
- `skills/verify/SKILL.md`
- `agents/architect.md`
- `agents/designer.md`
- `agents/inspector.md`
- `docs/validation/V1.2.0-release-notes.md`
- `docs/validation/V1.2.0-productivity-validation.md`
- `docs/validation/V1.2.0-sample-run.md`
- `plan/PROJECT_PLAN.md`

## Risks

- over-specifying low-value UI work and adding ceremony where it is not needed
- turning UI quality into subjective taste warfare instead of a contract-driven review process
- creating dual design authorities if `architect` and `UI Intent Owner` are not clearly separated
- importing frontend-design too literally and letting external capability shape the whole workflow instead of strengthening it selectively

## Guardrails

- keep the seven-stage kernel intact
- keep `design.md` and `ui-intent.md` distinct but connected
- do not let UI-intent work bypass `plan`, `review`, or `verify`
- do not make all UI work `ui-critical`
- ensure that stronger external UI capability is decomposed into local workflow contracts instead of replacing them wholesale

## Verification Strategy

V1.2.0 is successful when:

- all UI-bearing tasks have a clear, graded path through the workflow
- `ui-intent.md` becomes a real contract rather than optional prose
- `plan`, `execute`, `review`, and `verify` explicitly consume and validate UI intent
- the system preserves UI quality without abandoning stage discipline
- stronger external frontend capability becomes institutionalized instead of remaining an unstable external dependency
