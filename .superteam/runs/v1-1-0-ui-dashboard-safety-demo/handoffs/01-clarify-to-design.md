# Handoff: clarify -> design

- Date: 2026-03-22
- Owner: planner
- Iteration: 1
- Related task ids: task-1, task-2
- Guard Mode: off
- Execution Mode: single
- Conflict Domain: admin-dashboard-and-cache-controls
- Merge Owner: executor
- Approval Status: ready for design

## Objective

Clarify the admin dashboard request and isolate the risky cache-reset requirement.

## Inputs Used

- user request for a dashboard plus safe reset action
- repository-level V1.1.0 workflow rules

## Outputs Produced

- clarified objective and success criteria
- recommendation to use `design-consultation`

## Decisions Locked

- this is UI-heavy work
- the risky action requires stronger safety treatment than normal settings UI

## Evidence

- clear split between informative UI and destructive action path

## Risks Or Open Questions

- no visual-system source of truth existed yet

## Next Consumer Instructions

- use `design-consultation` before design approval
- keep the dangerous action behaviorally separate from the metrics UI

## Escalate If

- the dashboard request secretly includes broader admin IA work
