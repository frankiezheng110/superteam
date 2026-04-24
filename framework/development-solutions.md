# SuperTeam Development Solutions Contract

This document defines how `SuperTeam` should run the second stage inside the existing seven-stage workflow:

`design` = `Development Solutions`

This is an enhancement layer over the existing `design` stage. It does not create a new stage.

## Purpose

Stage 2 answers three practical questions:

- what whole-project solution direction should we take?
- what should each important domain or subsystem do?
- how do those choices fit together well enough for `plan` to consume them directly?

## Core Rule

This stage must not be reduced to one quick opinion or one search sweep.

It should include:

- internal solution generation
- external evidence gathering
- explicit comparison and rejection
- cross-domain fit checking
- reviewer continuity checkpoints

## Relationship To The Kernel

- the seven-stage kernel stays unchanged
- `design.md` remains the structural design artifact
- `ui-intent.md` remains the UI/aesthetics contract for UI-bearing work
- `solution-options.md` and `solution-landscape.md` are support artifacts for better `design` and `plan`
- `framework/solution-search.md` defines the Stage-2 anchor-driven search model for brand-new products and internal projects
- `.superteam/reviewer/traces/<task-slug>.jsonl` remains the machine-auditable source of truth
- `activity-trace.md` is a human-readable run summary for the first three stages, not a replacement for the Reviewer trace

## Participation Contract

- `Project Definition / clarify`: direct user participation is mandatory, and the stage cannot close without explicit user approval
- `Development Solutions / design`: user participation may be `co-create`, `observe`, or `decision-only`; explicit user decision is required before the stage may leave the option loop and enter shaping work
- `Execution Plan / plan`: the drafting loop is internal, but the stage cannot close without explicit user approval of the final plan
- after `plan` is approved and `execute` begins, the workflow should continue without further user involvement unless the user explicitly intervenes

## Required Team Shape For Meaningful Stage-2 Work

- `orchestrator` - stage host, participation-mode owner, decision recorder
- `architect` - internal solution generation and structural framing
- `researcher` - anchor-driven external evidence, analogous products, mature implementations, dependency constraints, community signals, and failure signals
- `reviewer` - continuity checkpoints, trace coverage, decision-trail integrity

Optional additions:

- `designer` when UI-bearing work materially affects solution direction
- `analyst` when the project definition is still unstable
- `inspector` only when deliverable-quality concerns must be previewed early; this does not replace the real `review` stage

## Required Outputs

- `design.md`
- `solution-options.md`
- `solution-landscape.md`
- `activity-trace.md` updates
- `ui-intent.md` when UI work requires it

Keep these compact. Smaller tasks use shorter sections, not extra ceremony.

## Stage Structure

`design` stays one stage, with two internal segments.

### Segment 1 - Option Loop

This is the interaction-heavy part.

The goal is to bring all meaningful candidate directions into one comparison loop and close on a chosen direction.

The loop should combine:

- internally generated options
- externally researched options and evidence
- user-supplied options, constraints, preferences, or anti-examples
- unified comparison, challenge, and tradeoff discussion
- explicit user decision on the chosen direction

Required work:

- propose at least one real alternative when the task is meaningful enough to justify comparison
- identify important domains or subsystems
- generate candidate whole-project and per-domain solution choices
- extract Stage-2 anchors from `project-definition.md` before searching outward
- search outward after internal options exist so external evidence improves thinking rather than replacing it
- use search breadth and search validation where meaningful
- note cross-domain dependencies, conflicts, and likely planning risks
- record the selected direction and user decision attribution

When relevant, cover these lanes:

- `market-patterns`
- `mature-implementations`
- `official-constraints`
- `community-signals`
- `failure-signals`

Default search order for brand-new products:

1. web keyword search (`Google` or an equivalent search engine) for `market-patterns`
2. GitHub keyword search for `mature-implementations`
3. official docs for `official-constraints`
4. community material for `community-signals`
5. postmortems, issue clusters, and negative evidence for `failure-signals`

Do not search the project name alone when the project itself is new and has no established public surface. Search the clarified problem anchors instead.

Minimum expectation for meaningful work:

- at least 3 evidence cards
- at least 2 source types
- coverage of the major decision anchors
- both `market-patterns` and `mature-implementations` unless clearly irrelevant
- both breadth-pass findings and validation-pass findings

### Segment 2 - Solution Shaping

This is the lower-interaction part.

Once the direction is chosen, the team should stop reopening broad option debate and shape the selected direction into formal design artifacts.

Required work:

- turn the chosen direction into `design.md`
- turn UI-bearing work into approved `ui-intent.md` when required
- formalize structure, boundaries, interfaces, data/flow notes, and risk framing
- keep `solution-options.md` and `solution-landscape.md` as the decision/evidence support package, not as a second unfinished debate

## Internal Gate Between The Two Segments

`Option Loop -> Solution Shaping` only when:

- candidate options are concrete enough to compare
- unified comparison and challenge have happened
- the strongest direction is selected
- explicit user decision or approval is recorded

This is the main user-facing gate inside `design`. Once shaping starts, avoid reopening broad option debate unless the direction becomes unstable.

If the user later adds material new information, the orchestrator should reopen this gate as a `design` supplement rather than treating it as an automatic rollback.

## `solution-options.md` Minimum Shape

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

## `solution-landscape.md` Minimum Shape

- search framing
- anchor list
- representative keyword matrix
- search lanes covered or explicitly skipped
- option-loop breadth findings
- option-loop validation findings
- evidence cards
- patterns worth borrowing
- patterns worth rejecting
- official constraints or platform limits
- unresolved contradictions

## Evidence Card Shape

- source
- source type
- search layer
- matched anchors
- problem it solves
- solution pattern
- supports or challenges which option
- what is worth borrowing
- what should not be copied blindly
- applicability conditions
- risks or caveats

## Failure Modes

- external-copy bias
- project-name search bias
- fake diversity
- top-level-only design
- domain fragmentation
- one-pass search
- missing user decision attribution
- weak trace coverage
- planning starts while major solution debate is still open

## Exit Gate

`design` is only complete when:

- `design.md` exists and is approved
- `solution-options.md` and `solution-landscape.md` are current
- important whole-project and per-domain decisions are explicit
- reviewer continuity checkpoints are captured
- the option-loop closure decision is recorded
- the selected direction is concrete enough for `plan`

## Supplement Behavior

The `design` gate should be re-enterable later in the run.

- if the user adds a new option, new constraint, or a missing requirement that changes solution comparison, reopen the option loop
- if the chosen direction stays stable and only execution details change, reopen `plan` instead of `design`
- if shaping was already completed, preserve the existing `design.md` as the previous approved shape until the supplement finishes and a new shape is approved
