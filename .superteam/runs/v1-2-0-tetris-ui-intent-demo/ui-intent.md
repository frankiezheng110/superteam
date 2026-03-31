# UI Intent

## UI Weight

- `ui-critical`

## Experience Goal

- user: casual and returning puzzle players
- primary scenario: immediate playable session with low friction and high board readability
- success condition: the board feels readable, responsive, and satisfying within the first minute of play

## Aesthetic Direction

- tone: arcade clarity with modern restraint
- style archetype: polished neon utility rather than retro clutter
- differentiation target: tactile block feedback and a high-contrast playfield that keeps the eye on the stack, not on chrome

## Design Tokens

- typography: bold condensed display for score and light but clear numeric secondary font for timing and level
- color: dark field, luminous block colors, limited accent palette for meta UI
- spacing: generous padding around playfield, tight spacing within status modules
- radius: low radius for game surfaces, slightly softer radius for meta panels
- motion baseline: quick, tactile transitions rather than floating decorative motion

## Composition Rules

- the playfield is the visual anchor and must dominate hierarchy
- score, level, and next-piece panels remain secondary but readable without stealing focus
- overlays should dim context without hiding critical board state

## Interaction Rules

- keyboard controls must feel immediate
- drop, rotate, line-clear, pause, and game-over states require distinct visual feedback
- error or blocked actions should be obvious but not noisy

## Implementation Intent

- preserve high-contrast board readability in all states
- do not flatten the UI into generic cards and utility panels
- if performance limits appear, reduce ornamental effects before reducing gameplay feedback clarity

## Validation Checklist

- playfield remains the strongest visual anchor
- scoring and next-piece info are readable at a glance
- major game states have distinct feedback
- implementation does not degrade into generic dashboard styling
