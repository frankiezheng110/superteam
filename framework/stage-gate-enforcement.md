# Stage Gate Enforcement

This document defines the **binary enforcement checklist** that orchestrator must execute at every stage transition.

This checklist serves two purposes simultaneously:
1. **Exit condition**: the current stage cannot close until all checks PASS
2. **Entry guide**: the next stage consumer reads the checks that just passed to know what artifacts exist, what their paths are, and what content they contain — no separate handoff document is needed or written

Each check is binary: **PASS** (condition is verifiably true) or **FAIL** (condition is false or cannot be confirmed).

A single FAIL in a mandatory check = stage does NOT advance. Orchestrator records the failure and the blocking reason. No exceptions without explicit override procedure (see Override Protocol at the end of this document).

## Dual-Check Mechanism

Every stage gate uses a **two-phase check protocol**. Orchestrator does NOT advance to the next stage until it has received Reviewer's gate check report.

### Phase 1: Parallel Checks

Orchestrator and Reviewer run the gate checklist independently at the same time:
- Orchestrator runs its check → records results internally
- Reviewer runs its check → emits `gate_check_report` to orchestrator AND records in trace file

Both check the same list of binary items for the gate. They use the same verification methods defined in this document.

### Phase 2: OR Makes Decision (After Receiving Reviewer's Report)

**Orchestrator must receive and read Reviewer's `gate_check_report` before making the advance/block decision.**

After receiving Reviewer's report, OR:
1. Compares Reviewer's findings with its own
2. If both agree ALL checks PASS → OR advances to next stage
3. If either finds ANY check FAIL → OR must address the failure OR issue a documented override
4. Records the decision in `activity-trace.md` and `current-run.json`

**Reviewer's role**: deliver the check results to OR, record in trace, then yield. Reviewer does not block; OR decides.

**OR's obligation**: not to advance until Reviewer's report is received. If Reviewer report is not delivered within the current interaction turn, OR requests it explicitly before proceeding.

### Trace Event Format

```json
{
  "event_type": "gate_check_report",
  "agent": "reviewer",
  "gate": "gate_2",
  "delivered_to": "orchestrator",
  "check_results": [
    {"check": 1, "result": "PASS", "evidence": "design.md exists at .superteam/runs/slug/design.md"},
    {"check": 4, "result": "FAIL", "evidence": "ui-intent.md not found at .superteam/runs/slug/ui-intent.md"},
    {"check": 9, "result": "PASS", "evidence": "designer handoff note line 12: '12 rejected files deleted'"}
  ],
  "summary": "1 FAIL found: check 4",
  "recommendation": "Block advance until ui-intent.md is produced",
  "timestamp": "..."
}
```

After OR makes its decision, Reviewer records the outcome:

```json
{
  "event_type": "gate_decision_observed",
  "agent": "reviewer",
  "gate": "gate_2",
  "or_decision": "blocked | advanced | advanced_with_override",
  "override_recorded": false,
  "discrepancy": false,
  "notes": "OR correctly blocked advance pending ui-intent.md production",
  "timestamp": "..."
}
```

If OR advances despite one or more FAIL checks, Reviewer records:

```json
{
  "event_type": "gate_decision_observed",
  "discrepancy": true,
  "discrepancy_detail": "Check 4 FAILED (ui-intent.md missing) but OR advanced without documented override",
  "or_decision": "advanced_without_override"
}
```

This discrepancy record becomes a finding in the post-run Reviewer report under "Gate Enforcement Quality."

---

## Agent Entry Log Requirement

Every agent that starts a stage **must write an entry log in `activity-trace.md` before doing any work**. The entry log records which gate the agent read and what key artifacts it found there.

### Entry log format

```
## [Agent name] Entry — Gate [N]
Gate read: Gate N ([from stage] → [to stage])
Key artifacts confirmed from gate checks:
- [artifact name]: [exact path]
- [artifact name]: [exact path]
[executor/inspector/verifier only] MUST items I will work from:
- [item 1]
- [item 2]
[executor only] TDD exception in effect: YES (reason: ...) | NO
[verifier only] Test command I will run: [exact command]
[inspector only] polish.md: present at [path] | not present
```

**Why this exists**: the entry log is the only observable artifact that confirms an agent read and understood the incoming gate checks. The Reviewer checks this log against the gate check results. If the paths are wrong, the gate number is wrong, or the MUST items don't match plan.md — Reviewer records a B-*-0 FAIL.

**This is not a compliance form.** The content comes from actually reading the gate results. An agent that copies paths without reading them will produce incorrect work — the downstream failure is the consequence.

---

## Gate 1: CLARIFY → DESIGN

**Executor**: orchestrator runs this gate before allowing design to begin.

### 1A — Artifact Existence

| # | Check | How to verify |
|---|-------|---------------|
| 1 | `project-definition.md` exists at `.superteam/runs/<slug>/project-definition.md` | file exists on disk |
| 2 | `activity-trace.md` exists at `.superteam/runs/<slug>/activity-trace.md` | file exists on disk |

### 1B — Content Requirements

| # | Check | How to verify |
|---|-------|---------------|
| 3 | `project-definition.md` contains an `objective` section with specific goal statement | read file, find section |
| 4 | `project-definition.md` contains explicit `constraints` | read file, find section |
| 5 | `project-definition.md` contains `non-goals` or `out-of-scope` | read file, find section |
| 6 | `project-definition.md` contains `ui_weight` classification (`ui-none`, `ui-standard`, or `ui-critical`) | read file, find field |
| 7 | If `ui_weight` is `ui-standard` or `ui-critical`: `project-definition.md` contains design thinking seeds (purpose, tone seed, differentiation seed) | read file, find section |
| 8 | `project-definition.md` contains an initial feature scope list — a flat list of user-facing capabilities the project must deliver | read file, find feature scope section; each item must name a user-facing capability, not a technical component |

### 1C — Approval Record

| # | Check | How to verify |
|---|-------|---------------|
| 9 | User approval (G1 closed) is recorded in `activity-trace.md` or `project-definition.md` | read file, find approval record |
| 10 | Reviewer continuity checkpoint for `clarify` stage is present in `activity-trace.md` | read activity-trace.md, find clarify checkpoint |

### Gate 1 Failure Action

If any check FAILS: record `gate_1_fail` with the failed check numbers. Do not begin `design`. Surface the specific missing item to the user and request it before proceeding.

---

## Gate 2: DESIGN → PLAN

**Executor**: orchestrator runs this gate before allowing planning to begin.

### 2A — Artifact Existence

| # | Check | How to verify |
|---|-------|---------------|
| 1 | `design.md` exists at `.superteam/runs/<slug>/design.md` | file exists on disk |
| 2 | `solution-options.md` exists at `.superteam/runs/<slug>/solution-options.md` | file exists on disk |
| 3 | `solution-landscape.md` exists at `.superteam/runs/<slug>/solution-landscape.md` | file exists on disk |
| 4 | If `ui_weight` is `ui-standard` or `ui-critical`: `ui-intent.md` exists at `.superteam/runs/<slug>/ui-intent.md` | file exists on disk |

### 2B — Content Requirements

| # | Check | How to verify |
|---|-------|---------------|
| 5 | `design.md` contains selected whole-project direction with rationale | read file, find selected direction section |
| 6 | `design.md` contains rejected alternatives and reasons for rejection | read file, find rejected alternatives section |
| 7 | `solution-options.md` contains recorded user decision on solution direction | read file, find user decision record |
| 8 | If `ui_weight` is `ui-standard` or `ui-critical`: `ui-intent.md` contains ALL of: Aesthetic Direction, Typography Contract, Color Contract, Motion Contract, Spatial Contract, Visual Detail Contract, Anti-Pattern Exclusions | read ui-intent.md, check each section header exists and has content |

### 2C — Design Cleanup (UI-bearing work only)

| # | Check | How to verify |
|---|-------|---------------|
| 9 | If designer produced HTML preview files, screenshots, or design drafts during option loop: designer's handoff note confirms they have been deleted from the project directory | read designer handoff note, find deletion confirmation |

### 2D — Feature Checklist (finalized at design close)

| # | Check | How to verify |
|---|-------|---------------|
| 10 | `feature-checklist.md` exists at `.superteam/runs/<slug>/feature-checklist.md` | file exists on disk |
| 11 | Every item in `feature-checklist.md` describes a single observable user-facing behavior — not a phase name, module name, or category | read file, check each item: it must state a specific user action and a specific observable result |
| 12 | Every item in `feature-checklist.md` specifies a test type (unit / integration / E2E) and test tool | read file, check each item has both fields |

**FAIL condition for check 11**: any item that is a phase name ("Phase 6 mobile"), module name ("Settings UI"), or category ("timer features") — must be decomposed into single behaviors before G2 can close.

**FAIL condition for check 12**: any item with no test type or no test tool specified.

### 2E — Approval Record

| # | Check | How to verify |
|---|-------|---------------|
| 13 | User approval (G2 closed) is recorded | read solution-options.md or activity-trace.md, find approval record |
| 14 | Reviewer continuity checkpoint for `design` stage is present in `activity-trace.md` | read activity-trace.md, find design checkpoint |

### Gate 2 Failure Action

If any check FAILS: record `gate_2_fail` with the failed check numbers. Do not begin `plan`.

Specific rules:
- If check 10 fails (feature-checklist.md missing): **OR must surface this to the user immediately.** Present the initial feature scope from `project-definition.md` and ask the user to confirm and expand it into a behavior-level feature list. OR cannot proceed to plan without user-confirmed feature checklist — this is not a task for designer or planner to self-generate.
- If check 11 fails (items are phase/module names, not behaviors): **OR must present the non-conforming items to the user** and ask them to clarify what specific behaviors each item represents. Do not infer behaviors on behalf of the user.
- If check 12 fails (test type or tool missing): OR asks the user or returns to planner to specify testing approach for each item.
- If check 4 fails (ui-intent.md missing): tell designer to produce it. Do not embed aesthetic contracts in plan.md as a substitute.
- If check 9 fails (cleanup not confirmed): tell designer to delete rejected files and confirm before advancing.
- If checks 5–7 fail: return to design stage for the missing content.

---

## Gate 3: PLAN → EXECUTE

**Executor**: orchestrator runs this gate after user approves plan (G3) and before execution begins.

### 3A — Artifact Existence

| # | Check | How to verify |
|---|-------|---------------|
| 1 | `plan.md` exists at `.superteam/runs/<slug>/plan.md` | file exists on disk |

### 3B — Plan Quality Gate

| # | Check | How to verify |
|---|-------|---------------|
| 2 | `plan_quality_gate` is `pass` or `at_risk` — not `fail` | check current-run.json field `plan_quality_gate` |
| 3 | Every task in plan.md has an `objective` field | read plan.md, check every task entry |
| 4 | Every task in plan.md has `target files` or `bounded search scope` | read plan.md, check every task entry |
| 5 | Every task in plan.md has `implementation steps` | read plan.md, check every task entry |
| 6 | Every task in plan.md has `verification commands` | read plan.md, check every task entry |
| 7 | Every task in plan.md has a `done signal` | read plan.md, check every task entry |

### 3C — Delivery Scope Clarity

| # | Check | How to verify |
|---|-------|---------------|
| 8 | Every delivery item in plan.md is classified as either `MUST` or `DEFERRED` — no items use only ✅ without tier label | read plan.md delivery scope section, verify each item has explicit tier |
| 9 | Every `DEFERRED` item has a stated reason and target version | read plan.md, check deferred items |

### 3D — Feature Checklist Coverage

| # | Check | How to verify |
|---|-------|---------------|
| 10 | Every item in `feature-checklist.md` is traceable to at least one task in plan.md | read feature-checklist.md items one by one; for each item find the corresponding task in plan.md |
| 11 | No MUST item in plan.md is absent from `feature-checklist.md` — plan must not introduce new scope beyond the checklist | read plan.md MUST items; each must map to an item in feature-checklist.md |

**FAIL condition for check 10**: any feature-checklist.md item with no corresponding plan task — that feature is unplanned.

**FAIL condition for check 11**: any plan MUST item that cannot be traced back to feature-checklist.md — that is undeclared scope.

### 3E — TDD Protocol

| # | Check | How to verify |
|---|-------|---------------|
| 12 | For every task in plan.md: either (a) red→green→refactor steps reference the test tool specified in `feature-checklist.md` for that item, or (b) `tdd_exception` is recorded in `current-run.json` with a reason | read plan.md tasks and current-run.json |

### 3F — UI Work

| # | Check | How to verify |
|---|-------|---------------|
| 13 | If `ui_weight` is `ui-standard` or `ui-critical`: plan.md contains a `UI intent translation` section referencing `ui-intent.md` | read plan.md, find UI intent section |

### 3G — Approval Record

| # | Check | How to verify |
|---|-------|---------------|
| 14 | User approval (G3 closed) is recorded | read plan.md or activity-trace.md, find G3 approval record |
| 15 | Reviewer continuity checkpoint for `plan` stage is present in `activity-trace.md` | read activity-trace.md, find plan checkpoint |

### Gate 3 Failure Action

If `plan_quality_gate` is `fail` (check 2): return to planner to fix critical missing fields. Do not allow execution to begin regardless of user approval.

If tasks are missing critical fields (checks 3–7): return to planner to add them.

If any feature-checklist.md item has no plan task (check 10): return to planner — that feature is unplanned and cannot be silently omitted.

If any plan MUST item is not in feature-checklist.md (check 11): return to planner to either remove the undeclared scope or reopen G2 to add it to the checklist.

If TDD steps are absent and no `tdd_exception` exists (check 12): orchestrator may choose to issue a `tdd_exception` with documented reason, or return to planner to add TDD steps. Cannot silently skip.

---

## Gate 4: EXECUTE → REVIEW

**Executor**: orchestrator runs this gate after executor completes and polish layer finishes.

### 4A — Artifact Existence

| # | Check | How to verify |
|---|-------|---------------|
| 1 | `execution.md` exists at `.superteam/runs/<slug>/execution.md` | file exists on disk |
| 2 | `polish.md` exists at `.superteam/runs/<slug>/polish.md` | file exists on disk |

### 4B — Per-Feature Execution Evidence

| # | Check | How to verify |
|---|-------|---------------|
| 3 | `execution.md` contains one section per feature from `feature-checklist.md` | read execution.md, count feature sections vs feature-checklist.md items |
| 4 | Every COMPLETE feature section contains RED evidence: test file path + actual failing test output | read each feature section, find RED evidence with real output |
| 5 | Every COMPLETE feature section contains GREEN evidence: actual passing test output + full suite run result | read each feature section, find GREEN evidence with real output |
| 6 | No feature section is missing or silently skipped — every feature is either COMPLETE, BLOCKED (with escalation record), or DEFERRED (with OR decision) | read execution.md, verify every feature-checklist.md item has a section with one of the three statuses |

### 4C — Summary Evidence

| # | Check | How to verify |
|---|-------|---------------|
| 7 | `execution.md` contains an Execution Summary section with: features completed count, blocked count, deferred count, full files-changed list, files-not-changed list | read execution.md, find summary section |
| 8 | `execution.md` records TDD exception status: either `tdd_exception: YES (reason: ...)` or `tdd_exception: NO` | read execution.md summary section |

### 4D — Polish Layer

| # | Check | How to verify |
|---|-------|---------------|
| 9 | If polish layer ran and made behavior-relevant file changes: `polish.md` records fresh post-polish local checks | read polish.md, find post-polish check evidence |

### Gate 4 Failure Action

If feature sections are missing from execution.md (check 3): return to executor — every feature-checklist.md item must have a section.

If RED or GREEN evidence is just a claim without actual output (checks 4–5): return to executor — "test passed" without output is not evidence.

If any feature is silently absent (check 6): this is a process violation — the feature was silently skipped. Treat as BLOCKED, require executor to explain and OR to decide.

If TDD exception status is absent (check 8): return to executor to declare it explicitly.

---

## Gate 5: REVIEW → VERIFY

**Executor**: orchestrator runs this gate after inspector completes review.

### 5A — Artifact Existence

| # | Check | How to verify |
|---|-------|---------------|
| 1 | `review.md` exists at `.superteam/runs/<slug>/review.md` | file exists on disk |

### 5B — Review Verdict

| # | Check | How to verify |
|---|-------|---------------|
| 2 | `review.md` verdict is `CLEAR` or `CLEAR_WITH_CONCERNS` — NOT `BLOCK` | read review.md, find verdict field |
| 3 | If verdict was `BLOCK`: all blocking issues are recorded as either resolved (with evidence) or explicitly accepted by orchestrator | read review.md, find blocker resolution record |

### 5C — Delivery Scope Completeness (Inspector's mandatory check)

| # | Check | How to verify |
|---|-------|---------------|
| 4 | `review.md` contains a `delivery scope check` section listing every MUST item from plan.md and its delivery status | read review.md, find delivery scope check section |
| 5 | Every MUST item from plan.md delivery scope is either: (a) confirmed delivered in execution.md, or (b) recorded as an explicit BLOCK finding in review.md | read review.md delivery scope check, cross-reference plan.md |

### 5D — TDD Gate (Inspector's mandatory check)

| # | Check | How to verify |
|---|-------|---------------|
| 6 | `review.md` contains a `TDD gate` section recording either: (a) TDD chain evidence, or (b) citation of orchestrator-issued tdd_exception | read review.md, find TDD gate section |
| 7 | Inspector did NOT declare TDD "N/A" without citing the orchestrator waiver | read review.md TDD gate section |

### Gate 5 Failure Action

If verdict is BLOCK (check 2): do not advance to verify. Return work to executor with the blocker list. Record `gate_5_fail` and the specific blocker items.

If delivery scope check section is absent (check 4): inspector must add it before the gate is re-evaluated.

If a MUST item is undelivered and not recorded as BLOCK (check 5): this is a gate enforcement failure. Record it as a process finding and treat the missing item as a BLOCK.

---

## Gate 6: VERIFY → FINISH

**Executor**: orchestrator runs this gate after verifier issues verdict.

### 6A — Artifact Existence

| # | Check | How to verify |
|---|-------|---------------|
| 1 | `verification.md` exists at `.superteam/runs/<slug>/verification.md` | file exists on disk |

### 6B — Verification Verdict

| # | Check | How to verify |
|---|-------|---------------|
| 2 | `verification.md` verdict is `PASS` — NOT `FAIL` or `INCOMPLETE` | read verification.md, find verdict field |
| 3 | `verification.md` contains `evidence summary` section with citations to actual command outputs | read verification.md, find evidence summary with real evidence |
| 4 | `verification.md` contains requirement-by-requirement status for every MUST item | read verification.md, find per-requirement status table |
| 5 | `delivery_confidence` is recorded | read verification.md, find delivery_confidence field |

### 6C — Test Suite Evidence (code-changing work)

| # | Check | How to verify |
|---|-------|---------------|
| 6 | For code-changing work: `verification.md` contains evidence of test suite execution (`cargo test`, `pytest`, `npm test`, etc.) — not just compilation | read verification.md, find test run output |

### Gate 6 Failure Action

If verdict is FAIL (check 2): do not advance to finish. Route back to executor with fix package. Increment `repair_cycle_count` in current-run.json.

If verdict is INCOMPLETE (check 2): escalate to orchestrator decision. Options: (a) resolve the incomplete evidence, (b) reduce scope and re-verify, (c) terminate run.

If repair_cycle_count reaches 3: orchestrator must choose between re-plan or terminate. Cannot continue cycling.

---

## Gate 7: FINISH (Completion Checks)

**Executor**: orchestrator runs this gate before marking the run complete.

### 7A — Required Finish Artifacts

| # | Check | How to verify |
|---|-------|---------------|
| 1 | `finish.md` exists at `.superteam/runs/<slug>/finish.md` | file exists on disk |
| 2 | `retrospective.md` exists at `.superteam/runs/<slug>/retrospective.md` | file exists on disk |
| 3 | Reviewer report exists at `.superteam/reviewer/reports/<slug>-report.md` | file exists on disk |

### 7B — Finish Content

| # | Check | How to verify |
|---|-------|---------------|
| 4 | `finish.md` contains acknowledgment of Reviewer report (`reviewer_report_acknowledged: true` or equivalent) | read finish.md, find acknowledgment |
| 5 | `retrospective.md` contains `improvement_action` — a concrete next action (not left blank or "none") | read retrospective.md, find improvement_action field |
| 6 | `current-run.json` is updated with `status: completed` and `current_stage: finish` | read current-run.json |

### 7C — Reviewer Report (Hard Requirement)

**finish.md CANNOT be written until `.superteam/reviewer/reports/<slug>-report.md` exists.**

This is an absolute gate. The Reviewer report must be generated by the reviewer agent BEFORE orchestrator writes finish.md. There is no waiver for this requirement.

If the reviewer report does not exist: trigger reviewer post-run analysis NOW before continuing.

### Gate 7 Failure Action

If Reviewer report is absent (check 3): halt finish. Trigger reviewer agent to produce the report. Resume after report is written.

If `improvement_action` is blank (check 5): orchestrator must record at minimum "no improvement actions identified this run" as an explicit statement. Blank is not acceptable.

---

## Override Protocol

In exceptional cases, orchestrator may override a failed gate check. Overrides are rare and require documentation.

**Override conditions**: only these conditions justify an override:
1. The check's requirement is genuinely inapplicable to this specific run (e.g., a documentation-only change has no TDD requirement)
2. The user has explicitly instructed the override and understood the risk

**Override record** (must be written to current-run.json and activity-trace.md):
```json
{
  "override": {
    "gate": "gate_3",
    "check_number": 10,
    "check_description": "TDD steps present or tdd_exception recorded",
    "override_reason": "Run is documentation-only, no code changes, TDD not applicable",
    "authorized_by": "orchestrator",
    "user_informed": true,
    "timestamp": "2026-03-28T12:00:00"
  }
}
```

**Override must never be used to skip**:
- User approval records (G1, G2, G3)
- Missing artifacts (production of artifacts is required, not optional)
- Missing Reviewer report before finish
- Unresolved BLOCK findings from inspector
- FAIL or INCOMPLETE from verifier

These have no valid override justification.

---

## Enforcement Summary Table

| Gate | From → To | Mandatory checks | Blocks on |
|------|-----------|-----------------|-----------|
| Gate 1 | clarify → design | 10 checks | any missing, especially initial feature scope list |
| Gate 2 | design → plan | 14 checks | any missing, especially feature-checklist.md with behavior-level items |
| Gate 3 | plan → execute | 15 checks | plan_quality_gate=fail, feature coverage gaps, or G3 not recorded |
| Gate 4 | execute → review | 9 checks | missing per-feature evidence, silently skipped features |
| Gate 5 | review → verify | 7 checks | verdict=BLOCK, or MUST item undelivered |
| Gate 6 | verify → finish | 6 checks | verdict=FAIL or INCOMPLETE |
| Gate 7 | finish | 6 checks | Reviewer report absent |

**Total: 66 binary checks across 7 gates.**

Every check has a stated verification method. "Looks right" is not a verification method.
