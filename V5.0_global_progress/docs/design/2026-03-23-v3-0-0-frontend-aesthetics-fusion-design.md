# SuperTeam V3.0.0 — Frontend Aesthetics Deep Fusion Design

## Date

2026-03-23

## Version

V3.0.0

## Motivation

SuperTeam V1.2.0 established the UI Intent Pipeline — a seven-stage contract for carrying UI quality from `clarify` through `finish`. However, the actual **aesthetic substance** inside that pipeline was thin. It defined *where* UI intent should live but not *what* high-quality UI actually looks like.

Meanwhile, the `frontend-design` skill (by Anthropic) provides rich, battle-tested aesthetic intelligence: distinctive font pairing, bold color strategies, high-impact motion, unexpected spatial composition, and atmospheric visual detail. But it is a monolithic execution-time skill with no stage discipline, no review gate, no verification, and no separation between design and code.

V3.0.0 fuses these two systems at the deepest level:

- **frontend-design's aesthetic substance** is decomposed, absorbed, and distributed across all seven stages
- **SuperTeam's stage discipline** ensures that aesthetic decisions are captured, planned, executed, reviewed, verified, and delivered — not lost between design and code
- The result is a system that matches frontend-design's output quality on pure frontend work while retaining SuperTeam's full-stack orchestration, test-first discipline, and verification rigor

## Design Principles

1. **Decompose, don't copy** — frontend-design is a monolithic prompt. V3.0.0 breaks it into stage-appropriate pieces distributed across framework, skills, and agents.
2. **Aesthetic knowledge as framework** — The aesthetic guidelines become a normative framework document (`framework/frontend-aesthetics.md`), referenced by multiple stages, not buried in one skill.
3. **Stage-native integration** — Each stage gets the aesthetic intelligence it needs at the moment it needs it: clarify gets design thinking, design gets aesthetic direction, plan gets implementation constraints, execute gets execution rules, review gets quality gates, verify gets evidence checks.
4. **Preserve full-stack capability** — Frontend aesthetics activate only when `ui_weight` is `ui-standard` or `ui-critical`. Backend-only work (`ui-none`) is unaffected.
5. **Anti-pattern enforcement** — frontend-design's NEVER list becomes a formal quality gate, not just advice.
6. **Match implementation to vision** — The principle that maximalist designs need elaborate code while minimalist designs need precision becomes an execution contract.

## Fusion Map

### Source: frontend-design SKILL.md → Target: SuperTeam V3.0.0

| frontend-design Element | Target Stage(s) | Target File(s) |
| --- | --- | --- |
| Design Thinking (Purpose, Tone, Constraints, Differentiation) | `clarify`, `design` | `skills/clarify/SKILL.md`, `skills/design/SKILL.md`, `framework/frontend-aesthetics.md` |
| Aesthetic Direction Selection (extreme tone options) | `design`, `design-consultation` | `skills/design-consultation/SKILL.md`, `framework/frontend-aesthetics.md` |
| Typography Guidelines | `design`, `plan`, `execute`, `review` | `framework/frontend-aesthetics.md`, `skills/design-consultation/SKILL.md`, `agents/designer.md` |
| Color & Theme Guidelines | `design`, `plan`, `execute`, `review` | `framework/frontend-aesthetics.md`, `skills/design-consultation/SKILL.md`, `agents/designer.md` |
| Motion Guidelines | `plan`, `execute`, `review` | `framework/frontend-aesthetics.md`, `agents/designer.md`, `agents/executor.md` |
| Spatial Composition Guidelines | `design`, `execute`, `review` | `framework/frontend-aesthetics.md`, `agents/designer.md` |
| Backgrounds & Visual Details | `execute`, `review` | `framework/frontend-aesthetics.md`, `agents/designer.md`, `agents/executor.md` |
| NEVER List (anti-patterns) | `execute`, `review`, `verify` | `framework/frontend-aesthetics.md`, all UI-gate-aware files |
| Implementation Complexity Matching | `plan`, `execute` | `framework/frontend-aesthetics.md`, `skills/plan/SKILL.md`, `skills/execute/SKILL.md` |
| Creative Differentiation Mandate | `clarify`, `design` | `skills/clarify/SKILL.md`, `skills/design/SKILL.md` |

## New Artifacts and Fields

### New Framework Document

- `framework/frontend-aesthetics.md` — the full aesthetic knowledge base, normative reference for all stages

### Enhanced ui-intent.md Schema

New required sections for `ui-standard` and `ui-critical`:

- `Aesthetic Direction` (with tone selection and differentiation target)
- `Typography Contract` (display font, body font, hierarchy rules)
- `Color Contract` (dominant palette, accent strategy, CSS variable plan)
- `Motion Contract` (animation philosophy, key moments, technology choice)
- `Spatial Contract` (layout philosophy, composition rules)
- `Visual Detail Contract` (atmosphere, texture, depth strategy)
- `Anti-Pattern Exclusions` (explicit list of what must NOT appear)

### Enhanced State Fields

- `aesthetic_direction`: the selected aesthetic direction label
- `anti_pattern_gate_status`: `not_required` | `pending` | `clear` | `block`

## Stage-by-Stage Fusion Detail

### clarify

- When UI is present, apply the Design Thinking framework from frontend-design:
  - **Purpose**: What problem does this interface solve? Who uses it?
  - **Tone seed**: Initial aesthetic direction preference (user input or discovery)
  - **Differentiation seed**: What should make this unforgettable?
- Capture these as new fields in the clarify-to-design handoff
- For `ui-critical`, recommend `design-consultation` by default

### design

- For `ui-standard` and `ui-critical`, the design stage must select a clear aesthetic direction
- The aesthetic direction must be **bold and intentional**, not generic
- `ui-intent.md` must include the enhanced aesthetic sections
- The NEVER list becomes a design constraint: the design must explicitly avoid generic AI aesthetics
- `design-consultation` becomes the primary vehicle for aesthetic direction when activated

### plan

- UI intent translation must include:
  - `aesthetic_implementation_complexity`: what level of code complexity the aesthetic vision demands
  - Specific font, color, and motion implementation requirements extracted from `ui-intent.md`
  - Anti-pattern avoidance as explicit plan constraints
  - Technology choices for motion (CSS-only vs Motion library vs custom)
- Plan quality gate enhanced: for `ui-critical`, missing aesthetic implementation constraints = `at_risk`

### execute

- Frontend execution rules absorbed from frontend-design:
  - NEVER use generic fonts (Inter, Roboto, Arial, system fonts)
  - NEVER use cliché color schemes (purple gradients on white)
  - NEVER produce predictable layouts and component patterns
  - NEVER produce cookie-cutter design lacking context-specific character
  - Match implementation complexity to aesthetic vision
  - Maximalist designs → elaborate code + extensive animations
  - Minimalist designs → restraint + precision + subtle details
- Executor must consume `ui-intent.md` aesthetic sections as binding implementation contract
- Record aesthetic decisions and any intentional degradations

### review

- UI quality gate enhanced with five aesthetic dimensions:
  1. **Typography quality**: distinctive, appropriate, well-paired?
  2. **Color quality**: cohesive palette, sharp accents, CSS variables?
  3. **Motion quality**: high-impact, coordinated, technology-appropriate?
  4. **Spatial quality**: intentional layout, not template-like?
  5. **Visual detail quality**: atmosphere, depth, not flat/generic?
- Anti-pattern gate: any NEVER-list violation is a blocking review finding
- `designer` agent mandatory for `ui-critical` review

### verify

- UI intent evidence coverage enhanced:
  - Each aesthetic contract section in `ui-intent.md` must have supporting evidence
  - Anti-pattern absence confirmation required
  - Implementation complexity match verification
- For `ui-critical`: aesthetic evidence gaps = `INCOMPLETE`, not `PASS`

### finish

- UI outcome summary includes:
  - Aesthetic direction achieved vs intended
  - Anti-pattern compliance summary
  - Notable aesthetic decisions and their rationale
  - Residual aesthetic compromises

## Role Enhancements

### designer agent

Becomes the **aesthetic authority** within SuperTeam, absorbing frontend-design's full creative capability:

- Owns aesthetic direction selection
- Provides typography, color, motion, spatial, and visual detail guidance
- Enforces anti-pattern avoidance
- Carries aesthetic intent across stages
- Knows when to push for bold choices vs when restraint serves the vision

### executor agent

Gains **frontend execution awareness**:

- Understands implementation complexity matching
- Knows the NEVER list and enforces it during implementation
- Can produce distinctive, production-grade frontend code
- Records aesthetic preservation evidence

### inspector agent

Gains **aesthetic quality gate capability**:

- Can evaluate against the five aesthetic dimensions
- Can identify anti-pattern violations
- Treats aesthetic intent loss as a real quality issue

## Version Policy

- V3.0.0 is a major version because it fundamentally changes how SuperTeam handles frontend work
- V1.2.0 files are preserved in their current state in docs/validation/ records
- The plugin version in plugin.json changes from 1.2.0 to 3.0.0
- Command namespace remains `st110` for compatibility

## Success Criteria

When V3.0.0 SuperTeam handles a pure frontend project with `ui_weight=ui-critical`:

1. The aesthetic output quality matches what frontend-design would produce standalone
2. But the work goes through all seven stages with proper review and verification
3. Generic AI aesthetics (Inter font, purple gradients, predictable layouts) are caught and rejected
4. The aesthetic direction is documented, planned, executed, reviewed, and verified — not just coded
5. Backend-only work is completely unaffected by the fusion
