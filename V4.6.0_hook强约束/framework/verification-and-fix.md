# SuperTeam Verification And Fix Rules

## Core Rule

No completion claim without fresh evidence.

## Four Quality Layers

`SuperTeam` uses four distinct quality layers:

1. execution-time self-checks by `executor`
2. challenge-oriented quality gate by `reviewer`, with specialist profiles (critic, security, tdd, etc.) activated when risk justifies them
3. independent final judgment by `verifier`
4. post-run team behavior analysis by `inspector` — judges the team process, not the deliverable

Layers 1-3 judge the work product. Layer 4 judges the system that produced it. None of them may silently replace the others.

## TDD Core Contract

TDD (`red → green → refactor`) is enforced by `gate_tdd_redgreen.py` + `observer_test_runner.py` as a state machine (PENDING → RED_LOCKED → GREEN_CONFIRMED). Editing production code before RED_LOCKED is physically blocked. The only exception is an orchestrator-signed `tdd_exception` record in `current-run.json` + `plan.md`; `validator_plan.py::check_tdd_exception_format` validates the record.

## Post-Execute Polish Bridge

Before layer 2 (`reviewer`), `SuperTeam` may run a refinement bridge:

- `simplifier` for changed code
- `doc-polisher` for changed docs and handoffs
- `release-curator` for delivery-facing cleanup or release-surface tightening

These workers improve presentation and maintainability, but they do not own review verdicts.

- all polish activity must be recorded in `.superteam/runs/<task-slug>/polish.md`
- any behavior-affecting polish edit requires fresh local checks before `review`
- `reviewer` must still independently judge whether the deliverable is good enough to continue

## Evidence Requirements

Fresh evidence should be produced in the active verification pass and should include real outputs when available.

Accepted evidence examples:

- test command output
- evidence that a failing test existed before the implementation step, when applicable
- build command output
- lint or type-check output
- review findings with file references
- polish findings and post-polish re-check evidence
- explicit confirmation that required artifact sections exist
- visual inspection evidence for UI quality (screenshot references, rendered output descriptions)

Recommended strong evidence set for a `PASS` verdict:

- build output
- focused test output
- diagnostics or lint output when applicable
- acceptance mapping to plan requirements
- confirmation that review-stage blockers were resolved

For `ui-standard` and `ui-critical` work, also require:

- aesthetic contract compliance evidence — confirmation that implemented UI matches the typography, color, motion, spatial, and visual detail contracts in `ui-intent.md`
- anti-pattern gate evidence — confirmation that no mandatory anti-pattern violations exist
- implementation complexity match — confirmation that code complexity matches the aesthetic vision

The verifier should also judge whether the run is actually ready to finish, not just whether one command passed.

The verifier should also note whether the run exposed a systemic process weakness, such as a weak task package, late specialist injection, or missing evidence expectations. These observations should be emitted as `gate_check` trace events so the Inspector can correlate them with other evidence in post-run analysis.

If the run used team execution, the verifier should also check whether merge boundaries, touched files, and merge ownership stayed inside the approved plan contract.

Weak evidence examples:

- "should pass"
- old outputs from a prior run
- implementation claims without verification
- "the UI looks fine" without reference to the aesthetic contracts

## Verdicts

### `PASS`

Use only when required outputs exist and verification evidence supports the success criteria.

For `ui-standard` and `ui-critical` work, `PASS` also requires aesthetic contract evidence coverage and anti-pattern gate clearance.

### `FAIL`

Use when evidence shows the result does not meet the requirements but can likely be fixed through another execution pass.

### `INCOMPLETE`

Use when evidence is missing, context is insufficient, or the verifier cannot safely determine success.

For `ui-critical` work, missing aesthetic evidence should produce `INCOMPLETE`, not a lenient `PASS`.

## Verifier Checklist

The verifier should normally check:

- build state
- test state
- TDD evidence-chain state for code-changing work
- lint or diagnostics state when relevant
- functionality against stated acceptance criteria
- review-stage blocker resolution
- task completion and handoff completeness
- unresolved errors or warnings in the final evidence set
- merge-boundary compliance when execution used team mode

For `ui-standard` and `ui-critical` work, also check:

- aesthetic direction compliance — does the implementation match the selected tone?
- typography compliance — are the specified fonts used correctly?
- color compliance — does the palette match the contract?
- motion compliance — are the key animation moments present and appropriate?
- spatial compliance — is the layout intentional and composition-aware?
- visual detail compliance — is there atmosphere and depth, not flat defaults?
- anti-pattern gate — are any mandatory anti-pattern violations present?

For productivity-first delivery quality, every `PASS`-leaning verification should also summarize:

- what is proven done
- what remains open but non-blocking
- whether `finish` is `ready`, `at_risk`, or `not_ready`
- whether a product-improvement action should be captured in `finish`

Delivery confidence should use this lightweight rubric:

- `high`: fresh evidence exists for the required success criteria and no blocker remains open
- `medium`: the run likely passes, but some evidence or non-blocking risk still needs explicit closure
- `low`: missing evidence, unclear ownership, or unresolved blockers make finish unsafe

## Fix Package Rules

When verification returns `FAIL`, the verifier should create a fix package containing:

- failed requirement
- evidence of failure
- suspected scope of repair
- minimal recommended task list
- re-verification command set

For UI-related failures, the fix package should also specify:

- which aesthetic contract was violated
- whether the fix requires aesthetic re-direction or just implementation adjustment

If the main issue is structural plan weakness rather than implementation failure, the verifier should say so explicitly and prefer return to `plan` over repeated execution churn.

## Fix Loop Limits

- default maximum: 3 verification-driven fix attempts
- after the limit, `orchestrator` must choose: re-plan, reduce scope, or terminate

## Return Paths

- `FAIL` with clear repair path -> back to `execute`
- `INCOMPLETE` because plan was weak -> back to `plan`
- `INCOMPLETE` because context is missing -> escalate to `orchestrator`
- repeated systemic failure -> escalate to `orchestrator` and consider `failed`

## Review Gate Notes

The review stage should check for:

- plan drift
- whether polish-layer edits preserved behavior and stayed inside scope
- whether code-changing work followed `red -> green -> refactor` or has a recorded orchestrator-approved exception
- missing tests or weak test intent
- unverified acceptance criteria
- unsafe assumptions or unchallenged reasoning

For `ui-standard` and `ui-critical` work, the review gate should also check:

- aesthetic dimension quality across five areas: typography, color, motion, spatial composition, visual detail
- anti-pattern registry compliance — any mandatory anti-pattern violation is a blocking finding
- aesthetic intent preservation — whether the implementation preserves or degrades the aesthetic contracts in `ui-intent.md`
- implementation complexity match — whether the code complexity matches the aesthetic vision

If the review result is `BLOCK`, the workflow must return to execution before verification.

## Inspector Layer (Layer 4)

The Inspector layer operates after delivery work is complete or terminated. For successful runs, this means after `verify` and before `finish.md`; for failed or cancelled runs, this means after the terminal decision. It does not judge the deliverable — it judges the team process:

- Was the stage sequence followed correctly?
- Were quality gates evaluated honestly?
- Were errors diagnosed at root cause or just patched?
- Were specialists injected at the right time?
- Did the plan hold, or did execution deviate significantly?
- Were there recurring patterns that indicate a systemic weakness?

The Inspector produces its analysis as reports (`.superteam/inspector/reports/<task-slug>-report.html` and `.superteam/inspector/reports/<task-slug>-report.md`) and generates improvement records for any weaknesses found. See `framework/inspector.md` for the full specification.

Key distinction: the verifier asks "did we build the right thing?" — the Inspector asks "did the team work correctly, and how do we work better next time?"
