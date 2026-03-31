# SuperTeam State And Resume

`SuperTeam` treats workflow memory as an external artifact rather than hidden conversational state.

## Persistence Rules

- every stage transition should leave a human-readable handoff
- important decisions should be written, not implied
- verification verdicts should be preserved for later audit
- cancellation should preserve enough context to resume safely.
- `.superteam/state/current-run.json` should always reflect the latest known run state

## Status Contract

The minimal status file lives at:

`.superteam/state/current-run.json`

`current-run.json` is the source of truth for compact run state. Any scorecard or status output should derive from it plus the latest artifacts.

`activity-trace.md` is the human-readable continuity trail for the first three stages. It must agree with the Reviewer trace on stage order and key decisions.

Suggested fields:

```json
{
  "version": "4.0.1",
  "task_slug": "example-task",
  "current_stage": "review",
  "last_completed_stage": "execute",
  "status": "active",
  "repair_cycle_count": 1,
  "latest_handoff": ".superteam/runs/example-task/handoffs/04-execute-to-review.md",
  "run_path": ".superteam/runs/example-task",
  "next_action": "resolve review blockers and refresh local evidence",
  "blocker_summary": "review found unresolved acceptance mismatch",
  "blocked_reason": null,
  "blocker_owner": null,
  "readiness_execute": "ready",
  "readiness_verify": "at_risk",
  "readiness_finish": "not_ready",
  "evidence_freshness": "fresh",
  "delivery_confidence": "medium",
  "plan_quality_gate": "pass",
  "design_participation_mode": "observe",
  "supplement_mode": "none",
  "supplement_anchor": null,
  "supplement_reason": null,
  "earliest_invalidated_stage": null,
  "affected_artifacts": [],
  "guard_mode": "off",
  "execution_mode": "single",
  "conflict_domain": null,
  "merge_owner": null,
  "ui_weight": "ui-critical",
  "ui_intent_status": "approved",
  "ui_quality_gate_status": "pending",
  "aesthetic_direction": "editorial / magazine",
  "anti_pattern_gate_status": "pending",
  "learning_status": "captured",
  "improvement_action": "tighten plan schema examples for exploratory tasks",
  "active_task_id": "task-2",
  "active_specialists": ["reviewer", "designer"],
  "specialist_reason": "review stage requires UI quality gate plus general quality gate",
  "reviewer_trace_path": ".superteam/reviewer/traces/example-task.jsonl",
  "reviewer_trace_events": 42,
  "reviewer_report_status": "pending",
  "reviewer_open_problems": 0,
  "last_updated": "2026-03-23T12:00:00Z"
}
```

`status` should be one of:

- `active`
- `blocked`
- `completed`
- `cancelled`
- `failed`

Readiness should be one of:

- `ready`
- `at_risk`
- `not_ready`

Evidence freshness should be one of:

- `fresh`
- `stale`
- `missing`

Delivery confidence should be one of:

- `high`
- `medium`
- `low`

Plan quality gate should be one of:

- `pass`
- `at_risk`
- `fail`

`plan_quality_gate` is a historical judgment recorded when `plan` exits. It should not be reused as a dynamic substitute for readiness.

Learning status should be one of:

- `missing`
- `captured`
- `deferred`
- `applied`

Use this transition rule:

- `missing -> captured -> deferred`
- `missing -> captured -> applied`

`applied` is valid only when the referenced `SuperTeam` improvement was completed inside the same run. If the run only records a follow-up task, use `deferred`.

Execution mode should be one of:

- `single`
- `team`

Guard mode should be one of:

- `off`
- `careful`
- `guard`

Design participation mode should be one of:

- `not_applicable`
- `co-create`
- `observe`
- `decision-only`

Supplement mode should be one of:

- `none`
- `developer_supplement`
- `rollback`

UI weight should be one of:

- `ui-none`
- `ui-standard`
- `ui-critical`

UI intent status should be one of:

- `not_required`
- `draft`
- `approved`
- `degraded`

UI quality gate status should be one of:

- `not_required`
- `pending`
- `clear`
- `clear_with_concerns`
- `block`

Aesthetic direction should be a descriptive label (e.g., `editorial / magazine`, `brutally minimal`, `luxury / refined`) or `null` when not applicable.

Anti-pattern gate status should be one of:

- `not_required`
- `pending`
- `clear`
- `block`

Reviewer report status should be one of:

- `pending` — trace is being collected, report not yet generated
- `generated` — report has been produced
- `acknowledged` — all improvement records have been acknowledged by the orchestrator

## Resume Checklist

Before resuming a paused workflow, the `orchestrator` should review:

- latest completed stage
- latest handoff
- latest `activity-trace.md` entries when resuming from or after `clarify`
- `solution-options.md` and `solution-landscape.md` when resuming from or after `design`
- supplement reason and earliest invalidated stage when supplement mode is active
- active risks
- unfinished fix package, if any
- whether verification evidence is still fresh enough to trust
- whether `state/current-run.json` agrees with the latest run artifact timestamps
- whether learning was already captured or still needs a retrospective before terminal closure
- whether `ui-intent.md` aesthetic contracts are still valid or need refresh
- the existing Reviewer trace file for the run, to restore event history context
- any open Reviewer improvement records from the improvement backlog

## Minimal Resume Decision

On resume, the `orchestrator` should explicitly choose one of:

- continue current stage
- re-run verification
- roll back to planning
- terminate the workflow

## Status Skill Expectation

Any `status` surface should summarize:

- current stage
- last completed stage
- current overall status
- repair cycle count
- latest handoff path
- immediate next required action
- blocker summary, blocker reason, and blocker owner when relevant
- readiness for `execute`, `verify`, and `finish`
- evidence freshness and delivery confidence
- plan quality gate when a plan exists
- design participation mode when relevant
- supplement mode, anchor, and earliest invalidated stage when relevant
- learning status and improvement action when relevant
- guard mode when relevant
- execution mode and merge boundary context when relevant
- `ui_weight`, `ui_intent_status`, and `ui_quality_gate_status` when relevant
- `aesthetic_direction` and `anti_pattern_gate_status` when relevant
- Reviewer trace event count, report status, and open problem count when relevant
- active specialists and the reason they were injected when relevant
