# SuperTeam Frontend Aesthetics

This document is the normative aesthetic knowledge base for all UI-bearing work in SuperTeam.

It applies when `ui_weight` is `ui-standard` or `ui-critical`. It does not apply to `ui-none` work.

All stages that touch UI intent, UI execution, UI review, or UI verification should reference this document.

## Design Thinking Framework

Before any UI design work, establish four pillars:

### Purpose

- What problem does this interface solve?
- Who uses it and what do they need?
- What is the primary experience success condition?

### Tone

Select a **bold, intentional** aesthetic direction. Choose from the spectrum below or define a custom direction that is true to the context:

- brutally minimal
- maximalist chaos
- retro-futuristic
- organic / natural
- luxury / refined
- playful / toy-like
- editorial / magazine
- brutalist / raw
- art deco / geometric
- soft / pastel
- industrial / utilitarian
- dark cinematic
- neo-grotesque
- hand-crafted / artisan
- data-dense / dashboard
- narrative / storytelling

These are starting points, not templates. The final direction should be uniquely suited to the product context.

### Constraints

- framework and technology requirements
- performance budget
- accessibility requirements
- browser or device targets
- existing design-system alignment needs

### Differentiation

Every UI should have at least one element that makes it unforgettable. Define what that element is before implementation begins.

## Aesthetic Dimensions

### 1. Typography

Choose fonts that are distinctive and characterful. Typography is the single most visible signal of design quality.

**Do:**

- pair a distinctive display font with a refined body font
- use font weight, size, and spacing to create clear visual hierarchy
- consider variable fonts for nuanced weight control
- match font personality to the aesthetic direction

**Never:**

- Inter, Roboto, Arial, Helvetica, or system font stacks as primary choices
- single-font designs without deliberate hierarchy
- font sizes that create ambiguous visual weight

**Guidance by tone:**

- minimalist → geometric sans with generous spacing (e.g., Satoshi, General Sans)
- editorial → elegant serif + clean sans pairing (e.g., Playfair Display + Source Sans)
- brutalist → monospace or industrial sans (e.g., Space Mono, Archivo Black)
- luxury → high-contrast serif or thin sans (e.g., Cormorant Garamond, Tenor Sans)
- playful → rounded or hand-drawn display fonts (e.g., Quicksand, Caveat)

These are examples, not prescriptions. Never converge on the same font across different projects.

### 2. Color & Theme

Color strategy must be intentional and cohesive. Use CSS custom properties for consistency.

**Do:**

- establish a dominant color with sharp accent colors
- use color to encode meaning and guide attention
- support both light and dark themes when the context warrants it
- create depth through layered opacity and tonal variation
- commit to a palette that matches the aesthetic direction

**Never:**

- purple gradients on white backgrounds (the most common AI-generated cliché)
- evenly-distributed palettes with no hierarchy
- random color choices without a cohesive system
- pure black (#000) text on pure white (#FFF) backgrounds without tonal softening

**Color architecture:**

- primary: the dominant brand or mood color
- accent: the sharp contrast color for CTAs and highlights
- surface: background layers with tonal depth
- semantic: success, warning, error, info — contextual meaning
- neutral: text and border hierarchy

### 3. Motion & Animation

Motion creates delight when used with intention. It becomes noise when used everywhere.

**Do:**

- focus on high-impact moments: page load, state transitions, key interactions
- use staggered reveals with `animation-delay` for orchestrated entry
- add scroll-triggered animations for progressive disclosure
- create hover and focus states that surprise and inform
- match motion intensity to the aesthetic direction

**Technology guidance:**

- HTML/CSS projects → prefer CSS-only animations and transitions
- React projects → use Motion (formerly Framer Motion) when available
- complex sequences → use Web Animations API or GSAP when justified

**Never:**

- animate everything — select high-impact moments
- use motion that delays or interrupts the user's primary task
- apply identical easing to every element — vary timing for rhythm

**Motion intensity by tone:**

- minimalist → subtle fades and precise slides (200-400ms, ease-out)
- maximalist → dramatic reveals, parallax, morphing (400-800ms, spring)
- editorial → elegant scroll-driven typography transitions
- brutalist → abrupt cuts, hard transitions, glitch effects

### 4. Spatial Composition

Layout is the structural foundation of visual quality. Unexpected layouts create memorability.

**Do:**

- use asymmetry and intentional imbalance
- overlap elements for depth and connection
- break the grid deliberately — not accidentally
- use generous negative space OR controlled density — both work when intentional
- create diagonal flow and visual tension
- use z-index layering to create atmospheric depth

**Never:**

- predictable, symmetric card grids without variation
- identical spacing everywhere — use rhythm and contrast
- layouts that could have been generated by any template system

**Composition strategies:**

- bento grid: asymmetric tile layouts with varied proportions
- editorial spread: full-bleed images with overlapping text blocks
- floating elements: cards and panels that break container boundaries
- scroll-driven narrative: content that reveals through spatial progression

### 5. Backgrounds & Visual Details

Atmosphere and depth separate designed interfaces from template output.

**Do:**

- create visual atmosphere through layered backgrounds
- use gradient meshes, noise textures, or geometric patterns
- add grain overlays for organic warmth
- use dramatic shadows for depth hierarchy
- add decorative borders, dividers, or ornamental elements that match the tone
- consider custom cursors for high-impact interactive areas
- use backdrop-filter for glass morphism effects when appropriate

**Never:**

- flat solid-color backgrounds without any visual treatment
- generic drop shadows without relationship to the light source
- decorative elements that contradict the aesthetic direction

## Anti-Pattern Registry

These patterns indicate generic AI-generated output and must be actively avoided in `ui-standard` and `ui-critical` work.

### Mandatory Anti-Patterns (blocking quality gate violations)

| ID | Anti-Pattern | Why it fails |
| --- | --- | --- |
| AP-01 | Generic font families: Inter, Roboto, Arial, system fonts as primary | signals zero design intent |
| AP-02 | Purple gradient on white background | the most common AI aesthetic cliché |
| AP-03 | Predictable symmetric card grids | indistinguishable from template output |
| AP-04 | Cookie-cutter component patterns without context-specific character | every interface looks the same |
| AP-05 | Converging on the same font/color/layout across different projects | defeats the purpose of distinctive design |

### Advisory Anti-Patterns (non-blocking but flagged in review)

| ID | Anti-Pattern | Why it matters |
| --- | --- | --- |
| AP-06 | Pure #000/#FFF without tonal softening | harsh and unrefined |
| AP-07 | Identical animation timing on all elements | mechanical, not organic |
| AP-08 | Decoration that contradicts the chosen aesthetic | visual incoherence |
| AP-09 | Missing hover/focus states on interactive elements | incomplete interaction design |
| AP-10 | No visual hierarchy in text sizing | flat information architecture |

## Implementation Complexity Matching

The aesthetic vision determines the implementation approach. This is a binding contract, not a suggestion.

### Maximalist / elaborate aesthetic

- extensive animations and transitions
- complex layered backgrounds
- custom interactive effects
- rich micro-interactions
- higher code complexity is expected and justified

### Minimalist / refined aesthetic

- restraint and precision in every detail
- carefully controlled spacing and typography
- subtle, almost invisible animations
- fewer elements, each perfectly crafted
- simplicity in code does not mean simplicity in thinking

### The rule

Match implementation complexity to the aesthetic vision. A maximalist design with minimal code execution is a broken contract. A minimalist design with excessive animation is a broken contract.

## UI Intent Contract Sections

When `ui-intent.md` is produced for `ui-standard` or `ui-critical` work, it should include these aesthetic sections in addition to the existing structural sections:

### Required Aesthetic Sections

- `Aesthetic Direction` — the selected tone, its rationale, and the differentiation target
- `Typography Contract` — display font, body font, hierarchy rules, specific font-family choices
- `Color Contract` — dominant palette, accent strategy, semantic colors, CSS variable naming
- `Motion Contract` — animation philosophy, key moments, technology choice, timing guidance
- `Spatial Contract` — layout philosophy, composition strategy, responsive behavior
- `Visual Detail Contract` — atmosphere approach, texture/depth strategy, decorative elements
- `Anti-Pattern Exclusions` — which AP-xx items are most relevant to this project and why

### Validation Checklist Enhancement

Add to the existing `ui-intent.md` validation checklist:

- [ ] typography is distinctive and matches the aesthetic direction
- [ ] color palette is cohesive with clear accent hierarchy
- [ ] motion is high-impact and coordinated, not scattered
- [ ] spatial composition is intentional, not template-derived
- [ ] visual details create atmosphere and depth
- [ ] no mandatory anti-pattern violations present
- [ ] implementation complexity matches the aesthetic vision

## Stage Activation Rules

| Stage | Activation condition | What to reference |
| --- | --- | --- |
| `clarify` | `ui_weight` is `ui-standard` or `ui-critical` | Design Thinking Framework |
| `design` | `ui_weight` is `ui-standard` or `ui-critical` | Full document, especially Aesthetic Dimensions |
| `design-consultation` | explicitly triggered for UI-heavy work | Full document |
| `plan` | `ui-intent.md` exists | Implementation Complexity Matching, Anti-Pattern Registry |
| `execute` | `ui-intent.md` exists | Anti-Pattern Registry, Implementation Complexity Matching |
| `review` | `ui_weight` is `ui-standard` or `ui-critical` | Anti-Pattern Registry, Aesthetic Dimensions |
| `verify` | `ui_weight` is `ui-standard` or `ui-critical` | Validation Checklist Enhancement |
| `finish` | `ui_weight` is `ui-standard` or `ui-critical` | summary reference only |

## Creative Excellence Standard

SuperTeam is capable of extraordinary creative frontend work. When the aesthetic direction is bold, the implementation must match that boldness. When the direction is refined, the implementation must match that refinement.

The goal is not to follow rules mechanically but to internalize the aesthetic intelligence and produce interfaces that feel genuinely designed — not generated.

Every frontend project should produce something distinctive. No two projects should converge on the same aesthetic choices. Variety, context-sensitivity, and intentionality are the hallmarks of design quality.
