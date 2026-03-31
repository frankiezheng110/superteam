# Design

## Structural Decisions

- split the experience into a dominant playfield, a compact meta-information rail, and transient overlays for pause/game-over
- keep game loop logic isolated from rendering and input handling
- maintain a dedicated state layer for score, level, next-piece queue, and active board state

## Tradeoffs

- prefer a single-screen layout over expansive settings surfaces during core play
- keep visual polish subordinate to input clarity and board readability

## Risks

- excessive decorative chrome could weaken game-state readability
- overloading the meta rail could reduce glanceability during active play

## Approval

- Status: approved
- Approved by: orchestrator
- Approval basis: structural design and UI intent align on a focused game experience
