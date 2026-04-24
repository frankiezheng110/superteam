---
name: design-consultation
description: Establish a visual design-system direction for UI-heavy work with full aesthetic intelligence. Use when a task needs stronger visual-system thinking before or during the design stage.
argument-hint: [task]
disable-model-invocation: true
---

# SuperTeam Design Consultation

Use this skill when the task is clearly UI, dashboard, marketing, brand, onboarding, or design-system heavy.

## Read First

- `framework/skill-common-rules.md`
- `framework/role-contracts.md`
- `framework/frontend-aesthetics.md` — this is the canonical aesthetic knowledge base; all creative guidance flows from it

## Purpose

This skill brings `framework/frontend-aesthetics.md` into a concrete project context. It produces a distinctive, bold, context-specific aesthetic direction that can survive planning, execution, review, and verification.

It does not replace the `design` stage, the `architect`, or design approval.

## Trigger Rules

- prefer this skill when the task is clearly interface-heavy or no design-system source of truth exists
- for `ui-critical` tasks, activate by default
- use only during `clarify` or `design`
- do not use for backend-only, infra-only, or tiny UI tweaks

## Design Thinking Process

Work through the four pillars from `framework/frontend-aesthetics.md`:

1. **Purpose** — problem, users, success condition, emotional response
2. **Tone** — select a bold aesthetic direction from the tone spectrum in the framework. The direction must be uniquely suited to the product context.
3. **Constraints** — framework, performance, accessibility, device targets, existing design-system alignment
4. **Differentiation** — the one unforgettable element

## Required Output

Write or update:

- `.superteam/runs/<task-slug>/design-system.md`
- `.superteam/runs/<task-slug>/ui-intent.md` sections when `ui-standard` or `ui-critical`

### design-system.md Must Include

- product context, aesthetic direction with rationale, differentiation target
- **Typography Direction** — display + body font with rationale, pairing logic, hierarchy rules. Refer to `framework/frontend-aesthetics.md` tone-typography table for guidance.
- **Color Direction** — dominant color, accent strategy, surface layering, semantic mapping, CSS custom property convention
- **Spacing and Layout Direction** — layout philosophy, composition strategy, negative space, responsive behavior
- **Motion Direction** — animation philosophy, key moments, technology, timing guidance. Refer to framework motion intensity table.
- **Visual Detail Direction** — atmosphere, depth strategy, decorative elements, texture
- **Component Tone Notes** — how buttons/cards/inputs express the aesthetic, interaction state personality
- **Anti-Pattern Awareness** — acknowledge and avoid the anti-pattern registry from the framework. State which are most relevant and how the direction avoids them.
- **Implementation Complexity Guidance** — elaborate or restrained. This becomes a binding contract for the executor.

## Creative Excellence Standard

- commit fully to the aesthetic direction — no design should look the same as another
- vary themes, fonts, aesthetics across projects
- interpret creatively for the context — elegance comes from executing the vision well, not safe defaults

## Rules

- execution-facing instructions English-first, user-facing summary Chinese-first
- produce a compact design-system artifact, not a second workflow
- hand off into `design`, not directly into implementation
- never trigger during `execute`, `review`, `verify`, or `finish`
- the aesthetic direction must be bold and intentional — generic is not an acceptable output
