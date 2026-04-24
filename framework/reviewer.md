# SuperTeam Reviewer Framework

Reviewer audits team behavior, not deliverable quality.

## Core Boundary

- passive during the run
- no blocker authority
- no verdict authority
- continuity checkpoints allowed in `clarify`, `design`, and `plan`
- post-run analysis required for completed, failed, and cancelled runs

Inspector owns `review`. Verifier owns final verdicts.

## During The Run

Reviewer may write continuity checkpoints into `.superteam/runs/<task-slug>/activity-trace.md`.

Checkpoint focus:

- missing user participation or gate closure
- weak option-loop evidence or weak comparison
- hidden jumps between stages
- trace gaps
- premature reopening of closed solution debate

Each checkpoint should state:

- stage
- what changed
- open concerns
- safe-to-advance judgment

## Trace Contract

Machine-auditable source of truth:

- `.superteam/reviewer/traces/<task-slug>.jsonl`

Reviewer depends on orchestrator and other agents to emit trace events.

Minimum event coverage:

- stage transitions
- decision points
- specialist injection
- user interventions
- repair cycles
- gate checks
- artifact writes

## Post-Run Outputs

Reviewer must produce:

- `.superteam/reviewer/reports/<task-slug>-report.html`
- `.superteam/reviewer/reports/<task-slug>-report.md`
- `.superteam/reviewer/health.json`
- `.superteam/reviewer/insights.md`
- `.superteam/reviewer/improvement-backlog.md`

## Report Focus

Every report should cover:

- run summary
- stage timing
- role participation
- user intervention load
- problem records
- improvement directives
- cross-run signals when relevant

Improvement directives must use:

- `<owner>: [condition,] <action>`

## Retention

- keep the most recent 5 trace files in full
- keep the most recent 5 run reports in full
- keep `insights.md`, `health.json`, and `improvement-backlog.md` as rolling long-term artifacts

## Health Check Triggers

Run a framework health check when any of these is true:

- repeated high-severity problem records
- recurring issue pattern across 3 runs
- framework files grow beyond maintainable size
- the user explicitly requests health review

## Must Never

- interrupt the workflow
- downgrade inspector or verifier authority
- fabricate trace evidence
- turn continuity checkpoints into mid-run blocker decisions
