# Plan

## Objective

Add an admin usage dashboard plus a guarded cache-reset flow without weakening operator safety or dashboard readability.

## Constraints

- keep destructive actions visually and behaviorally distinct
- preserve existing operator permissions model
- require test-first work for the cache reset confirmation path

## Design Inputs

- `.superteam/runs/v1-1-0-ui-dashboard-safety-demo/design.md`
- `.superteam/runs/v1-1-0-ui-dashboard-safety-demo/design-system.md`

## Tasks

### task-1
- objective: add dashboard layout and metrics panels
- target files: `app/admin/dashboard.tsx`, `app/admin/dashboard.css`
- implementation steps: add metric cards, activity table, and maintenance panel shell
- test-first step: add UI state test for metrics and maintenance panel rendering
- verification commands: `npm test -- admin-dashboard`
- expected outputs: dashboard renders metrics area and maintenance area distinctly
- done signal: tests pass and layout matches design intent
- blocker and escalation note: escalate if auth or existing admin shell assumptions are wrong

### task-2
- objective: implement guarded cache reset interaction
- target files: `app/admin/reset-cache.ts`, `app/admin/reset-cache.test.ts`
- implementation steps: add confirmation gate, permission check, and operator-visible result state
- test-first step: write failing tests for cancel, confirm, and unauthorized flows
- verification commands: `npm test -- cache-reset`
- expected outputs: reset only runs after explicit confirmation and correct permission checks
- done signal: all reset-flow tests pass and destructive path is guarded
- blocker and escalation note: escalate if backend reset contract is unsafe or unclear

## Plan Quality Gate

- Result: `pass`
- Reason: all critical and support fields exist for both tasks

## Execution Mode

- `execution_mode`: `single`
- `conflict_domain`: `admin-dashboard-and-cache-controls`
- `touched_files`: `app/admin/dashboard.tsx`, `app/admin/dashboard.css`, `app/admin/reset-cache.ts`, `app/admin/reset-cache.test.ts`
- `merge_owner`: `executor`

## Review Focus

- confirm the destructive action remains visually and behaviorally segregated
- confirm tests cover cancel, confirm, and unauthorized paths
- confirm guard mode remains active during risky execution
