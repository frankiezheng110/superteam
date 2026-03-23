# SuperTeam Handoff Template

Use this template whenever a stage hands off to another stage or role.

```md
# Handoff: <stage> -> <next-stage-or-role>

- Date:
- Owner:
- Iteration:
- Related task ids:
- Guard Mode:
- Execution Mode:
- Conflict Domain:
- Merge Owner:
- UI Weight:
- Aesthetic Direction:
- Approval Status:
- Approved By:
- Approval Date:

## Objective

<What this stage was trying to achieve>

## Inputs Used

- <artifact 1>
- <artifact 2>

## Outputs Produced

- <artifact 1>
- <artifact 2>

## Decisions Locked

- <decision 1>
- <decision 2>

## Evidence

- <command / review / document reference>

## Aesthetic Contract Status (ui-standard / ui-critical only)

- Typography: <compliant / at-risk / violated>
- Color: <compliant / at-risk / violated>
- Motion: <compliant / at-risk / violated>
- Spatial: <compliant / at-risk / violated>
- Visual Detail: <compliant / at-risk / violated>
- Anti-Pattern Gate: <clear / pending / block>

## Risks Or Open Questions

- <risk 1>
- <question 1>

## Next Consumer Instructions

- <what the next role must do>
- <what the next role must not assume>

## Escalate If

- <condition 1>
- <condition 2>
```

## Current State File Alignment

`.superteam/state/current-run.json` is already the active machine-readable state file. Handoffs should align with it.

At minimum, the state file should track:

- `version`
- `task_slug`
- `current_stage`
- `last_completed_stage`
- `status`
- `repair_cycle_count`
- `latest_handoff`
- `run_path`
- `blocker_summary` when relevant
- `blocked_reason` when relevant
- `blocker_owner` when relevant
- `next_action`
- `readiness_execute`
- `readiness_verify`
- `readiness_finish`
- `evidence_freshness`
- `delivery_confidence`
- `plan_quality_gate` when a plan exists
- `learning_status` when relevant
- `improvement_action` when relevant
- `guard_mode` when relevant
- `execution_mode` when relevant
- `conflict_domain` when relevant
- `merge_owner` when relevant
- `ui_weight` when relevant
- `ui_intent_status` when relevant
- `ui_quality_gate_status` when relevant
- `aesthetic_direction` when relevant
- `anti_pattern_gate_status` when relevant
- `active_task_id` when relevant
- `active_specialists` when relevant
- `specialist_reason` when non-default specialists are active
- `last_updated`
