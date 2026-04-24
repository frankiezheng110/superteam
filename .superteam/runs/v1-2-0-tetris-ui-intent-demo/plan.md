# Plan

## Objective

Build a browser Tetris implementation whose interaction feel and UI hierarchy match the declared `ui-critical` intent.

## Constraints

- preserve playfield readability above decorative styling
- use test-first for gameplay state changes and input handling
- keep implementation within the Tetris UI shell and gameplay modules

## Design Inputs

- `.superteam/runs/v1-2-0-tetris-ui-intent-demo/design.md`
- `.superteam/runs/v1-2-0-tetris-ui-intent-demo/ui-intent.md`

## Tasks

### task-1
- objective: implement the core playfield and meta-information shell
- target files: `src/tetris/App.tsx`, `src/tetris/ui.css`
- implementation steps: build playfield container, score/level/next-piece rail, and responsive shell hierarchy
- test-first step: add a rendering test that asserts playfield and meta rail hierarchy
- verification commands: `npm test -- tetris-ui-shell`
- expected outputs: the playfield dominates visual hierarchy and meta rail remains readable
- done signal: tests pass and UI hierarchy matches `ui-intent.md`
- blocker and escalation note: escalate if responsive constraints force layout collapse

### task-2
- objective: implement tactile game-state feedback
- target files: `src/tetris/game.ts`, `src/tetris/game.test.ts`, `src/tetris/feedback.ts`
- implementation steps: add line-clear, pause, game-over, and blocked-action feedback tied to core game events
- test-first step: write failing tests for line-clear and game-over state transitions
- verification commands: `npm test -- tetris-gameplay`
- expected outputs: major gameplay states produce distinct user feedback
- done signal: tests pass and key states remain visually distinct
- blocker and escalation note: escalate if feedback timing causes gameplay lag or visual ambiguity

## UI Intent Translation

- preserve the playfield as the dominant visual anchor
- implement distinct states for line-clear, pause, and game-over
- keep meta UI secondary and glanceable
- do not replace the intended game shell with generic dashboard cards
- review must check hierarchy, state feedback, and generic-UI drift
- verify must check evidence against the `ui-intent.md` checklist

## Plan Quality Gate

- Result: `pass`
- Reason: structural and UI-intent requirements are explicit and executable

## Execution Mode

- `execution_mode`: `single`
- `conflict_domain`: `tetris-playfield-and-ui-shell`
- `touched_files`: `src/tetris/App.tsx`, `src/tetris/ui.css`, `src/tetris/game.ts`, `src/tetris/game.test.ts`, `src/tetris/feedback.ts`
- `merge_owner`: `executor`
