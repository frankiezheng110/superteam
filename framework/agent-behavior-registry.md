# Agent Behavior Registry

This document defines the **observable core behaviors** for each agent that participates in a SuperTeam run.

These behaviors are the basis of the Reviewer's tracking and final report. For each behavior:
- It must be checkable from artifacts that agents produce
- It must yield a binary result: FOUND, MISSING, or PARTIAL
- It must cite a specific file and section as evidence — not inference

The Reviewer uses this registry to emit `behavior_observed` trace events during and after the run. The final Reviewer report is a structured aggregation of these events only — no analysis added.

---

## How to Use This Registry

For each agent that participated in a run, the Reviewer:
1. Reads the artifacts that agent produced
2. For each behavior listed below, determines: FOUND / MISSING / PARTIAL
3. Emits a trace event with the determination and an evidence citation
4. Does NOT interpret, analyze, or add opinion — only records what is found

If an artifact is absent entirely: every behavior tied to that artifact = MISSING.

---

## ORCHESTRATOR

### Core Behaviors

**B-OR-1: Stage transitions are recorded in current-run.json**
- What to check: `current-run.json` fields `current_stage` and `last_completed_stage` are updated at each stage boundary
- Evidence format: `current-run.json` → `last_updated` timestamp vs stage boundary timing
- Pass condition: each stage transition has a corresponding update with correct stage name and timestamp

**B-OR-2: Gate enforcement is documented before each stage advance**
- What to check: `activity-trace.md` contains a gate check record before each stage transition
- Evidence format: `activity-trace.md` → gate check entry with pass/fail for each check
- Pass condition: every stage advance is preceded by a recorded gate check
- Fail condition: stage advanced without any gate check record

**B-OR-3: User approvals are recorded at G1, G2, and G3**
- What to check: `project-definition.md` or `activity-trace.md` contains G1 approval; `solution-options.md` or `activity-trace.md` contains G2 approval; `plan.md` or `activity-trace.md` contains G3 approval
- Evidence format: find explicit approval record in the relevant artifact
- Pass condition: all three approval records exist with timestamps

**B-OR-4: Blockers are recorded with specific detail, not buried in prose**
- What to check: `current-run.json` → `blocker_summary` and `blocked_reason` fields contain specific blocker description
- Evidence format: the field values
- Pass condition: when a blocker exists, the field is populated with specific content (not empty, not "none")

**B-OR-5: Repair cycle count is maintained**
- What to check: `current-run.json` → `repair_cycle_count` is updated after each verify-fail cycle
- Evidence format: `repair_cycle_count` field value
- Pass condition: count is accurate (can be cross-checked against number of verify cycles in activity-trace.md)

---

## DESIGNER

### Core Behaviors

**B-DS-0: Designer logged Gate 1 entry in activity-trace.md**
- What to check: `activity-trace.md` contains a designer entry log section that: (a) cites Gate 1, (b) lists the key clarify artifacts with their actual paths
- Evidence format: find the entry log section in activity-trace.md, check gate number and artifact list
- Pass condition: entry log present, cites Gate 1, lists `project-definition.md` path and at least one other Gate 1 artifact with its verified path
- Fail condition: no entry log, or entry log cites wrong gate number, or lists artifacts with wrong paths

**B-DS-1: ui-intent.md is produced for ui-standard or ui-critical work**
- What to check: file exists at `.superteam/runs/<slug>/ui-intent.md`
- Evidence format: file path existence
- Pass condition: file exists when ui_weight is ui-standard or ui-critical
- Fail condition: file absent, or aesthetic contracts embedded only in plan.md

**B-DS-2: ui-intent.md contains all seven required aesthetic sections**
- What to check: `ui-intent.md` has section headers for: Aesthetic Direction, Typography Contract, Color Contract, Motion Contract, Spatial Contract, Visual Detail Contract, Anti-Pattern Exclusions
- Evidence format: list which section headers are present
- Pass condition: all seven headers present with non-trivial content
- Partial condition: some sections present, others missing or have placeholder content

**B-DS-3: Multiple distinct design options were generated in the option loop**
- What to check: `solution-options.md` or `design.md` contains reference to multiple candidate directions
- Evidence format: count of design options in solution-options.md
- Pass condition: at least 2 distinct options presented, with rationale for each
- Fail condition: only one option presented (no real choice given to user)

**B-DS-4: Rejected design files were deleted and confirmed**
- What to check: designer's handoff note in `activity-trace.md` or `design.md` confirms deletion of rejected preview files
- Evidence format: find deletion confirmation statement with file count or file list
- Pass condition: confirmation is explicit and specific
- Fail condition: no confirmation present, or confirmation is vague ("files cleaned up")
- Not applicable: when designer produced no preview files

**B-DS-5: Approved design file is marked as approved**
- What to check: approved reference file (HTML preview or design doc) contains approval marker, OR `ui-intent.md` explicitly identifies which reference was the approved one
- Evidence format: find the approval marker or the identification in ui-intent.md
- Pass condition: marker exists and is dated
- Fail condition: no clear identification of which design was approved

---

## PLANNER

### Core Behaviors

**B-PL-0: Planner logged Gate 2 entry in activity-trace.md**
- What to check: `activity-trace.md` contains a planner entry log section that: (a) cites Gate 2, (b) lists key design artifacts with their actual paths (design.md, solution-options.md, solution-landscape.md, and ui-intent.md when applicable)
- Evidence format: find the entry log section in activity-trace.md
- Pass condition: entry log present, cites Gate 2, lists correct artifacts with correct paths
- Fail condition: no entry log, wrong gate cited, or artifact paths don't match actual files

**B-PL-1: Every task in plan.md has all five critical fields**
- What to check: for each task in plan.md, verify presence of: objective, target files or bounded scope, implementation steps, verification commands, done signal
- Evidence format: list which tasks are missing which fields
- Pass condition: 100% of tasks have all five fields
- Partial condition: some tasks complete, some missing fields
- Fail condition: majority of tasks missing one or more critical fields

**B-PL-1b: Every MUST item is a single observable behavior with a specified test case**
- What to check: for each MUST item in plan.md delivery scope, verify: (a) it describes a specific action + observable result, not a phase/module/category name; (b) it has a test case field with test type, test tool, and assertion
- Evidence format: list which MUST items pass and which fail each condition
- Pass condition: every MUST item names a concrete behavior AND has a test case with all three fields
- Fail condition: any MUST item is a phase name ("Phase 6") or module name ("Settings UI"); or any MUST item has no test case or a test case with missing fields

**B-PL-2: Delivery scope uses explicit MUST / DEFERRED tier labels**
- What to check: delivery scope section in plan.md has MUST or DEFERRED label on every item
- Evidence format: count of items with tier labels vs total items
- Pass condition: every item has explicit tier label
- Fail condition: items use only ✅ with no tier label, or no delivery scope section

**B-PL-3: Code-changing tasks have red→green→refactor steps or tdd_exception citation**
- What to check: for each task involving code changes, find either: explicit red→green→refactor steps in the task, or citation of `tdd_exception` from current-run.json
- Evidence format: list which tasks have TDD steps and which cite exception
- Pass condition: every code task has one or the other
- Fail condition: code tasks exist with neither TDD steps nor exception citation

**B-PL-4: plan_quality_gate is assigned and recorded**
- What to check: `current-run.json` → `plan_quality_gate` is `pass`, `at_risk`, or `fail` (not absent)
- Evidence format: field value
- Pass condition: field is present and has valid value
- Fail condition: field absent or has no value

**B-PL-5: UI intent translation section exists for UI-bearing work**
- What to check: `plan.md` contains a UI intent translation section referencing `ui-intent.md` when ui_weight is ui-standard or ui-critical
- Evidence format: find section in plan.md
- Pass condition: section exists with specific references to design tokens, interaction states, anti-patterns
- Not applicable: when ui_weight is ui-none

---

## EXECUTOR

### Core Behaviors

**B-EX-0: Executor logged Gate 3 entry in activity-trace.md**
- What to check: `activity-trace.md` contains an executor entry log section that: (a) cites Gate 3, (b) lists plan.md path, (c) lists MUST delivery items found in plan.md, (d) states whether tdd_exception is in effect
- Evidence format: find the entry log section in activity-trace.md
- Pass condition: entry log present, cites Gate 3, MUST items list is non-empty and matches plan.md delivery scope
- Fail condition: no entry log; or cites wrong gate; or MUST items list is empty/vague ("various tasks"); or tdd status not stated

**B-EX-1: execution.md has one section per feature with COMPLETE / BLOCKED / DEFERRED status**
- What to check: count sections in execution.md vs items in feature-checklist.md; every item must have a section with one of the three statuses
- Evidence format: section headers in execution.md matched against feature-checklist.md
- Pass condition: count matches, every section has an explicit status
- Partial condition: some features have sections, others are absent
- Fail condition: any feature-checklist.md item has no section (silently skipped)

**B-EX-2: Every COMPLETE feature has RED evidence with actual test output**
- What to check: for each COMPLETE feature section in execution.md, find RED evidence block containing test file path and actual failing test output (not a summary)
- Evidence format: RED evidence blocks in execution.md
- Pass condition: every COMPLETE feature has a RED block with real output
- Fail condition: any COMPLETE feature has no RED block, or RED block says "test failed" without showing output

**B-EX-3: Every COMPLETE feature has GREEN evidence with actual test output**
- What to check: for each COMPLETE feature section in execution.md, find GREEN evidence block containing passing test output and full suite run result
- Evidence format: GREEN evidence blocks in execution.md
- Pass condition: every COMPLETE feature has a GREEN block with real output
- Fail condition: any COMPLETE feature has no GREEN block, or GREEN block says "tests passed" without showing output

**B-EX-4: Every BLOCKED feature has an escalation record**
- What to check: for each BLOCKED feature section in execution.md, find the escalation block: which step blocked, attempt count, test output, what was tried, what is needed from OR
- Evidence format: escalation blocks in execution.md
- Pass condition: every BLOCKED feature has a complete escalation block
- Fail condition: BLOCKED feature with no escalation detail, or feature silently absent

**B-EX-5: Execution Summary section accounts for all features and declares TDD exception status**
- What to check: execution.md summary section has: completed count, blocked count, deferred count totalling to feature-checklist.md total; TDD exception explicitly declared
- Evidence format: summary section in execution.md
- Pass condition: counts add up correctly, TDD status declared
- Fail condition: summary absent, counts don't add up, or TDD status not declared

---

## INSPECTOR

### Core Behaviors

**B-IN-0: Inspector logged Gate 4 entry in activity-trace.md**
- What to check: `activity-trace.md` contains an inspector entry log section that: (a) cites Gate 4, (b) lists execution.md path, (c) confirms polish.md was checked (or states not present), (d) lists MUST items it will check against
- Evidence format: find the entry log section in activity-trace.md
- Pass condition: entry log present, cites Gate 4, MUST items list matches plan.md
- Fail condition: no entry log; wrong gate cited; MUST items list missing or doesn't match plan.md

**B-IN-1: review.md contains delivery scope check for every MUST item**
- What to check: `review.md` has a delivery scope check section that lists every MUST item from plan.md and records whether it was delivered
- Evidence format: find the delivery scope check section
- Pass condition: section exists, every MUST item is listed, each has DELIVERED or MISSING status
- Fail condition: section absent, or some MUST items not covered

**B-IN-2: Missing MUST items are recorded as BLOCK findings (not MINOR)**
- What to check: if any MUST item is MISSING in the delivery scope check, find the corresponding finding in the blocker list — it must be classified BLOCK
- Evidence format: blocker list in review.md
- Pass condition: every missing MUST item has a BLOCK entry in the blocker list
- Fail condition: missing MUST item recorded as MINOR or CONCERN instead of BLOCK

**B-IN-3: TDD gate section exists and is not self-waived**
- What to check: `review.md` contains TDD gate section with either TDD chain evidence or citation of orchestrator tdd_exception
- Evidence format: find TDD gate section
- Pass condition: section exists with one of the two valid forms
- Fail condition: section says "N/A" without citing an orchestrator waiver; or section is absent entirely

**B-IN-4: UI quality gate is applied for ui-standard or ui-critical work**
- What to check: `review.md` contains UI quality gate section checking five aesthetic dimensions
- Evidence format: find UI quality gate section with dimension checks
- Pass condition: section exists with all five dimensions covered
- Not applicable: when ui_weight is ui-none

**B-IN-5: Verdict is one of three valid values (CLEAR, CLEAR_WITH_CONCERNS, BLOCK) — not mixed or absent**
- What to check: `review.md` → verdict field
- Evidence format: field value
- Pass condition: verdict is exactly one of the three valid values
- Fail condition: no verdict field, or non-standard value

---

## VERIFIER

### Core Behaviors

**B-VR-0: Verifier logged Gate 5 entry in activity-trace.md**
- What to check: `activity-trace.md` contains a verifier entry log section that: (a) cites Gate 5, (b) lists review.md path and its verdict, (c) lists MUST items it will verify, (d) states the test command it will run
- Evidence format: find the entry log section in activity-trace.md
- Pass condition: entry log present, cites Gate 5, verdict matches review.md, MUST items match plan.md, test command is specific (not "run tests")
- Fail condition: no entry log; wrong gate cited; test command is vague; MUST items missing

**B-VR-1: Test suite was executed (not just compilation)**
- What to check: `verification.md` contains evidence of test suite run with actual output
- Evidence format: find test run command and output in verification.md evidence section
- Pass condition: a test execution command (e.g., `cargo test`, `pytest`, `npm test`) appears with its output
- Fail condition: only compilation command output present; or no command evidence at all

**B-VR-2: Every MUST item has an explicit requirement status**
- What to check: `verification.md` contains per-requirement status for every MUST item from plan.md
- Evidence format: find requirement-by-requirement status table
- Pass condition: every MUST item appears in the table with VERIFIED/UNVERIFIED/INCOMPLETE status
- Partial condition: some MUST items covered, others missing from table
- Fail condition: no per-requirement status table

**B-VR-3: Evidence is fresh (from this verification cycle)**
- What to check: `verification.md` evidence references are dated to the current verification run, not copied from older execution records
- Evidence format: timestamps on evidence citations in verification.md
- Pass condition: evidence is clearly from current run
- Fail condition: evidence appears to be reused from prior stage outputs without fresh verification

**B-VR-4: Verdict is one of three valid values (PASS, FAIL, INCOMPLETE)**
- What to check: `verification.md` → verdict field
- Evidence format: field value
- Pass condition: verdict is exactly one valid value
- Fail condition: absent, mixed, or non-standard value

**B-VR-5: delivery_confidence is recorded with matching evidence**
- What to check: `verification.md` → delivery_confidence is `high`, `medium`, or `low`, and the evidence summary matches this assessment
- Evidence format: delivery_confidence field and evidence summary
- Pass condition: field is present and the evidence summary clearly supports the stated confidence level
- Fail condition: field absent, or confidence level contradicts the evidence summary

---

## REVIEWER (Self-Check)

The Reviewer applies these checks to its own trace before generating the final report.

**B-RV-1: Continuity checkpoints were emitted for clarify, design, and plan stages**
- What to check: `activity-trace.md` contains reviewer checkpoint entries for each of the first three stages
- Evidence format: checkpoint entries in activity-trace.md
- Pass condition: three checkpoints present, one per stage
- Fail condition: any checkpoint absent

**B-RV-2: Reviewer report was generated before finish.md was written**
- What to check: `.superteam/reviewer/reports/<slug>-report.md` timestamp is earlier than `finish.md` timestamp
- Evidence format: file timestamps
- Pass condition: report predates finish.md

**B-RV-3: Final report contains only trace-grounded facts (no unsupported analysis)**
- What to check: every claim in the Reviewer report either cites a trace event or cites a specific artifact location
- Evidence format: self-audit of the report's evidence citations
- Pass condition: 100% of factual claims have citations
- Fail condition: any claim like "appears to have", "probably", "seems like" without supporting citation

---

## Behavior Compliance Summary

At the end of a run, the Reviewer aggregates all behavior observations into a compliance table:

| Agent | Behavior | Result | Evidence |
|-------|----------|--------|----------|
| orchestrator | B-OR-1 | FOUND/MISSING/PARTIAL | `current-run.json` last_updated: ... |
| orchestrator | B-OR-2 | FOUND/MISSING/PARTIAL | `activity-trace.md` line X |
| ... | ... | ... | ... |

This table is the authoritative source for the Reviewer report. It contains no interpretation — only the raw observation results and their citations.

**Compliance rating** (derived mechanically from the table, not from judgment):
- COMPLIANT: all behaviors for that agent = FOUND
- PARTIAL: some behaviors FOUND, some MISSING or PARTIAL
- NON-COMPLIANT: majority of behaviors MISSING
