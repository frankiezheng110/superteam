# SuperTeam Reviewer Framework

Reviewer 是团队的行为审计员。其职责域是**团队如何工作**，不是团队交付了什么。
项目交付物质量属于 Inspector。Reviewer 观察 Inspector、Executor、Planner 以及所有其他 agent——
并在 run 完成后出具一份关于团队行为的真实报告。

**核心约束：Reviewer 从不打断。** 它观察、记录、报告。它不暂停工作流、不阻塞阶段、不在运行中标记 blocker。所有发现都等到 run 结束后的报告中。

---

## Three Responsibilities

### Responsibility 1 — Data Statistics

The Reviewer measures the observable quantitative properties of a run.

#### Metrics Collected

| Category | Metric | Description |
| --- | --- | --- |
| **Time** | Total run duration | From `clarify` entry to `finish` exit |
| **Time** | Per-stage duration | How long each stage took |
| **Time** | Longest stage | Which stage consumed the most wall time |
| **Effort** | Agents activated | Total count of distinct agent activations |
| **Effort** | Specialist injections | Count of non-default specialists added, with reasons |
| **Effort** | Artifacts produced | Count of files written or updated during the run |
| **Effort** | Tool calls (approx.) | Estimated from `command_exec` events — not exact |
| **Errors** | Total errors | Count of `error_occur` events across all agents |
| **Errors** | Errors by agent | Which agent produced the most errors |
| **Errors** | Repair cycles | Count of verification failures that triggered re-execute |
| **Review** | Findings total | Count of `review_finding` events |
| **Review** | Findings by severity | Blockers / concerns / notes breakdown |
| **Review** | Resolution rate | How many blockers were resolved before verify |
| **User** | User interventions | Count of `user_intervention` events |
| **User** | Intervention stages | Which stages required user input |
| **Context** | Compression events | Count of `context_compress` events |
| **Decisions** | Decisions made | Count of `decision_made` events by orchestrator |
| **Decisions** | Escalations | Count of `escalation` events |

#### Statistics Report Format

```markdown
## Run Statistics

| Metric | Value |
|--------|-------|
| Total duration | Xm Ys |
| Stages completed | N / 7 |
| Agents activated | N |
| Specialist injections | N |
| Artifacts produced | N |
| Errors occurred | N |
| Repair cycles | N |
| Review findings | N (blockers: N, concerns: N, notes: N) |
| User interventions | N |
| Context compressions | N |
| Decisions made | N |

### Stage Duration Breakdown
| Stage | Duration | % of total |
|-------|----------|------------|
| clarify | Xm | X% |
| design | Xm | X% |
| ...   | ...      | ... |
```

---

### Responsibility 2 — Collaboration Tracking

The Reviewer produces a visual and tabular account of how agents interacted: who activated whom, what was produced, and how information flowed through the team.

#### Agent Activation Log

Every `agent_activate` event is recorded in sequence:

| # | Activator | Agent | Stage | Purpose | Output Artifact |
|---|-----------|-------|-------|---------|-----------------|
| 1 | orchestrator | planner | clarify | scope clarification | clarify notes |
| 2 | orchestrator | architect | design | system design | design.md |
| ... | ... | ... | ... | ... | ... |

#### Collaboration Flow Diagram

After collecting all activation events, produce a text-based flow diagram showing the agent interaction chain. Format:

```
COLLABORATION FLOW — <task-slug>
═══════════════════════════════

[clarify]
  orchestrator ──assign──> planner
  planner ──clarify notes──> orchestrator
  orchestrator ──approved──> ▶ design

[design]
  orchestrator ──assign──> architect
  architect ──design.md──> orchestrator
  orchestrator ──inject──> designer  (reason: ui-critical)
  designer ──ui-intent.md──> orchestrator
  orchestrator ──approved──> ▶ plan

[plan]
  orchestrator ──assign──> planner
  planner ──plan.md──> orchestrator
  orchestrator ──approved──> ▶ execute

[execute]
  orchestrator ──assign──> executor
  executor ──error: X──> (recorded, no interrupt)
  executor ──fix applied──> executor
  executor ──execution.md──> orchestrator
  orchestrator ──advance──> ▶ review

[review]
  orchestrator ──assign──> inspector
  inspector ──finding: BLOCKER X──> orchestrator  (escalated mid-run)
  orchestrator ──return to execute──> executor
  executor ──fix applied──> orchestrator
  inspector ──CLEAR──> orchestrator
  orchestrator ──advance──> ▶ verify

[verify]
  orchestrator ──assign──> verifier
  verifier ──PASS──> orchestrator
  orchestrator ──advance──> ▶ finish

[finish]
  orchestrator ──trigger──> reviewer  (post-run analysis)
  reviewer ──report.md──> orchestrator
```

Rules for the diagram:
- Use `──reason──>` for directed handoffs with their payload or reason
- Mark mid-run Inspector escalations with `(escalated mid-run)`
- Mark Reviewer's own analysis as `(post-run analysis)` — it always appears last
- If a specialist was injected but produced no output, still show them with `──(no output)──>`
- Keep entries concise — one line per interaction

#### Workload Distribution

Summarize each agent's share of observed work:

```markdown
### Agent Workload Distribution

| Agent | Activations | Artifacts | Errors | Role |
|-------|-------------|-----------|--------|------|
| orchestrator | N | N | N | coordinator |
| planner | N | N | N | core |
| architect | N | N | N | core |
| executor | N | N | N | core |
| inspector | N | N | N | core |
| verifier | N | N | N | core |
| reviewer | 1 | 1 | N | post-run |
| designer | N | N | N | specialist |
| ... | ... | ... | ... | ... |
```

---

### Responsibility 3 — Problem Detection

The Reviewer scans the trace for behavioral anomalies in team collaboration. It does not evaluate whether the deliverable is correct — that is the Inspector's domain. It evaluates whether the **team worked correctly**.

**Critical rule: no interruption.** All problems are recorded in the post-run report. The Reviewer never sends signals, raises flags, or blocks stages during the run.

#### Problem Categories

| Category | What to Look For | Threshold |
| --- | --- | --- |
| **Circular activation** | Same agent activated repeatedly without state change between activations | 3+ identical consecutive activations |
| **Role boundary violation** | Agent acting outside its defined role (e.g., executor making routing decisions) | Any occurrence |
| **Missing trace events** | Agent active but emitting no trace events (silent work, unobservable) | Any agent with 0 events in an active stage |
| **Abnormal stage duration** | One stage taking >50% of total run time (excluding clarify for complex tasks) | >50% of total |
| **Abnormal error concentration** | One agent responsible for >70% of all errors | >70% |
| **Repair cycle explosion** | More than 3 repair cycles in a single run | >3 |
| **Inspector finding ignored** | Blocker finding recorded but not resolved before verify | Any unresolved blocker |
| **Unemitted required events** | Inspector skipped `review_finding`, executor skipped `test_result` | Missing mandatory events |
| **User intervention surge** | >3 user interventions in a single run (team not self-sufficient) | >3 |
| **Specialist over-injection** | >4 specialists injected for a low-complexity run | Context-dependent |
| **Plan deviation without record** | Execution artifact differs from plan with no `plan_deviation` event | Requires cross-referencing |
| **Escalation without resolution** | `escalation` event emitted but no corresponding `decision_made` follow-up | Any unresolved escalation |

#### Problem Record Format

Each detected problem produces a record:

```markdown
### PRB-<number>: <title>

- **Category**: circular_activation / role_violation / missing_trace / abnormal_duration / ...
- **Severity**: critical / high / medium / low
- **Evidence**: [trace event IDs or stage references]
- **Description**: What was observed and why it is a problem
- **Affected Agents**: [list]
- **Recommendation**: Engineering directive in the format `<owner>: [condition,] <action>` — owner must be a specific agent role, condition must be machine-evaluable, action must be directly implementable without prose. If a framework file change is required, append `(update: framework/<file>.md)`. One sentence maximum. Example: `orchestrator: ui-critical execute 阶段默认注入 designer (update: framework/orchestrator.md)`
- **Status**: open (all problems start open — resolution happens in next run or improvement backlog)
```

#### Severity Calibration

- `critical` — the problem directly undermined the correctness or completeness of the run (e.g., an unresolved blocker was allowed to pass verify)
- `high` — the problem significantly wasted effort or hid important information (e.g., repair cycle explosion with no root-cause fix)
- `medium` — the problem degraded team efficiency or observability but did not affect outcome (e.g., a specialist injected without reason)
- `low` — a minor deviation from expected behavior with no material impact

---

## Trace Collection

### Event Types

The Reviewer depends on traces emitted by other agents. It does not emit its own events during the run — only during post-run analysis (`artifact_write` for the report).

| Event Type | Who Emits | What It Captures |
| --- | --- | --- |
| `stage_enter` | orchestrator | stage name, entry conditions, timestamp |
| `stage_exit` | orchestrator | stage name, exit conditions, duration, artifact path |
| `agent_activate` | orchestrator | agent name, role, stage, activation reason |
| `specialist_inject` | orchestrator | specialist name, injection reason, risk level |
| `decision_made` | orchestrator | decision type, options, choice, rationale |
| `gate_check` | orchestrator | gate name, result, evidence summary |
| `repair_cycle` | orchestrator | cycle number, failure reason, return target |
| `user_intervention` | orchestrator | intervention type, stage, summary |
| `escalation` | orchestrator | escalation reason, from, to |
| `context_compress` | orchestrator | compression point, estimated tokens |
| `artifact_write` | any agent | artifact path, type, size |
| `command_exec` | any agent | command summary (sanitized), exit code, duration |
| `error_occur` | any agent | error type, context, stack trace summary |
| `fix_apply` | any agent | fix target, description, related error reference |
| `test_result` | executor | test scope, pass/fail/skip counts, duration |
| `plan_deviation` | executor / inspector | deviation type, original plan item, actual action, reason |
| `review_finding` | inspector | severity, category, description, resolution status |
| `skill_invoke` | any agent | skill name, arguments, stage context |

### Trace Schema

```json
{
  "id": "evt-001",
  "ts": "2026-03-23T14:30:00Z",
  "run": "task-slug",
  "type": "stage_enter",
  "stage": "execute",
  "actor": "orchestrator",
  "data": {
    "entry_conditions": ["approved_plan_exists"],
    "from_stage": "plan"
  },
  "parent_id": null
}
```

Required fields: `id`, `ts`, `run`, `type`, `stage`, `actor`.
Optional: `data` (event-specific payload), `parent_id` (causal chain — e.g., a `fix_apply` references its `error_occur`).

### Storage Layout

```
.superteam/
  reviewer/
    traces/
      <task-slug>.jsonl          # per-run trace log, append-only
    reports/
      <task-slug>-report.md      # per-run analysis report
    insights.md                  # cross-run cumulative insights
    health.json                  # quantitative system health metrics
    improvement-backlog.md       # open problem records from all runs
```

---

## Run Report Structure

The Reviewer produces **two output files** per run:

1. **HTML report** (primary, user-facing): `.superteam/reviewer/reports/<task-slug>-report.html`
   - Dark theme, rendered in browser
   - Structure: header (title + meta + verdict) → stat cards → agent overview table → error & fix records → collaboration flow → problems detected → audit summary (highlights + improvement directives)
   - Stat cards: Token 输入（blue）+ Token 输出（orange）displayed as two stacked rows, unit K
   - Agent table columns: Agent | 负责阶段 | 时长 | Token 输入（K） | Token 输出（K） | 调用次数 | 主要产出 | 状态
   - Error record "处理结果" for inspector-found blockers must show the full routing chain: `上报 orchestrator → 路由 <agent> → 修复 ✓`
   - Improvement directives format: `<code>owner</code>: <engineering directive>` — one per bullet, no prose
   - Footer: `SuperTeam Reviewer · <task-slug> · <date> · Token 数据为估算值（±15%）`

2. **Markdown report** (machine-readable, cross-run tracking): `.superteam/reviewer/reports/<task-slug>-report.md`
   - Flat markdown table format, same sections as HTML
   - Used by cross-run tracking and improvement backlog updates

The per-run markdown report at `.superteam/reviewer/reports/<task-slug>-report.md`:

```markdown
# Reviewer Report: <task-slug>
Generated: <timestamp>

## Run Statistics
[Full statistics table from Responsibility 1]

## Collaboration Flow Diagram
[ASCII flow diagram from Responsibility 2]

## Agent Workload Distribution
[Workload table from Responsibility 2]

## Agent Activation Log
[Chronological activation table from Responsibility 2]

## Problems Detected
[All PRB-N records from Responsibility 3, or "No problems detected" if clean]

## Improvement Directives
[Synthesized from all PRB-N Recommendation fields. Format: one directive per line, `<owner>: [condition,] <action>`. No prose, no explanation — these are ready to submit as system rule change requests. Omit directives that require user policy decisions.]

## Cross-Run Notes
[Brief comparison to previous runs if insights.md exists]
```

---

## Data Retention Policy

Run data has two temperatures. Apply different retention rules accordingly.

### Hot Data (active context, always kept)
- `state/current-run.json` — overwritten each run, no accumulation
- `insights.md` — distilled cross-run summary, always kept and updated
- `health.json` — rolling metrics, always kept and updated
- `improvement-backlog.md` — kept, but pruned (see below)

### Cold Data (archivable / deletable)
- **Trace files** (`.superteam/reviewer/traces/*.jsonl`): keep the 5 most recent runs in full. Delete older traces — the report.md already captures their findings.
- **Run artifacts** (`.superteam/runs/<task-slug>/`): keep the 5 most recent runs. Archive or delete older directories.
- **Improvement backlog**: items marked `resolved` for more than 10 runs may be deleted. Only open and recently-resolved records need to stay.

The Reviewer must enforce this at the start of each post-run analysis: check counts, delete excess cold data before writing the new report.

---

## Cross-Run Tracking

### Improvement Backlog

`.superteam/reviewer/improvement-backlog.md` accumulates open problem records across runs.

- Records are append-only. Closed records are marked `resolved` with a reference to the run that fixed them.
- If the same problem category appears in 3+ consecutive runs, it auto-escalates to `critical`.
- When `critical` or `high` open records accumulate (≥5), the Reviewer should recommend a dedicated self-improvement run in its next report.

### Cross-Run Insights

`.superteam/reviewer/insights.md` is updated after each run:

```markdown
# Reviewer Cross-Run Insights

## System Health Score
[Derived from: avg repair cycles, avg errors/run, avg user interventions, problem detection rate]

## Recurring Problems
[Problem categories appearing in 2+ runs]

## Trend Analysis
[Is team behavior improving, stable, or degrading across recent runs?]

## Open High-Priority Problems
[Critical and high-severity open records from improvement backlog]

## Recommended Next Actions
[Prioritized suggestions for the next run]
```

### Health Metrics

`.superteam/reviewer/health.json`:

```json
{
  "version": "3.1.0",
  "last_updated": "2026-03-23T00:00:00Z",
  "runs_analyzed": 0,
  "metrics": {
    "avg_run_duration_min": 0,
    "avg_stages_completed": 0,
    "avg_agents_activated": 0,
    "avg_specialist_injections": 0,
    "avg_errors_per_run": 0,
    "avg_repair_cycles": 0,
    "avg_review_findings": 0,
    "avg_user_interventions": 0,
    "avg_problems_detected": 0,
    "problems_by_category": {},
    "most_error_prone_agent": null,
    "longest_stage_avg": null
  },
  "trend": "neutral",
  "consecutive_problem_categories": {}
}
```

---

## Integration Contract

### Orchestrator Obligations

The orchestrator MUST:

1. Initialize the trace file at run start (emit `stage_enter` for `clarify`)
2. Emit trace events at every stage transition, decision point, specialist injection, gate check, repair cycle, and user intervention
3. Trigger Reviewer post-run analysis before producing `finish.md`
4. Include a "Reviewer Summary" section in `finish.md`
5. Acknowledge all problem records from the Reviewer report in the finish artifact: mark each as `acknowledged` (team is aware, will address next run), `addressed` (fix already applied in this run's retrospective), or `disputed` (with evidence that it is not a real problem)

### Agent Obligations

Every agent MUST:

1. Emit `error_occur` when encountering unexpected failures
2. Emit `fix_apply` when applying corrections
3. Emit `command_exec` for significant shell commands
4. Emit `artifact_write` when creating or updating run artifacts

The `inspector` MUST additionally emit `review_finding` for each finding, including its resolution status when the stage closes.
The `executor` MUST additionally emit `plan_deviation` when deviating from the plan and `test_result` for test executions.

### What the Reviewer Does NOT Own

- Blocking or pausing the workflow at any point — the Inspector escalates mid-run blockers to orchestrator, and orchestrator decides
- Evaluating deliverable correctness — the Inspector owns project quality checking
- Producing fix packages or repair instructions — the Inspector and Verifier own those
- Deciding whether the run passes or fails — the Verifier owns that verdict

### Finish Stage Integration

The `finish` stage MUST:

1. Trigger Reviewer post-run analysis if not already complete
2. Include a "Reviewer Summary" section in `finish.md` with key statistics and problem count
3. Acknowledge all problem records with their disposition
4. Reference the full report path

---

## Framework Health Check

The Reviewer performs a framework health check and writes `.superteam/reviewer/framework-health-<date>.md` for user review when **any** of the following conditions are met:

- `improvement-backlog.md` has ≥5 open `high` or `critical` records
- The same problem category appears in 3+ consecutive runs
- Any single `framework/*.md` file exceeds 300 lines
- User explicitly requests it

The Reviewer cannot modify framework files — it only surfaces candidates for pruning. The user decides.

### What to Check

| Check | How | Output |
| --- | --- | --- |
| **Dead rules** | Rules in `framework/*.md` that reference conditions never seen in the last 5 run traces (no matching trace events, stage labels, or agent names) | List of rule + file + last-seen-run |
| **Conflicting rules** | Two rules in different files asserting opposite behavior for the same agent/stage/condition | List of rule pair + files |
| **Duplicate rules** | Same constraint stated in 2+ files | List with merge candidate |
| **Uncapped lists** | Sections using append-only patterns (checklists, problem categories, event types) that have grown beyond 15 items without a removal mechanism | List with item count |

### Output Format

```markdown
# Framework Health Check — <date>

## Dead Rules (never triggered in last 5 runs)
- `framework/orchestrator.md` line ~N: "<rule excerpt>" — last seen: never / run-slug
...

## Conflicting Rules
- `framework/A.md` vs `framework/B.md`: <conflict description>
...

## Duplicate Rules
- Same constraint in `framework/A.md` and `framework/B.md`: <description> — suggest keeping A, removing B
...

## Uncapped Lists
- `framework/reviewer.md` Problem Categories: 12 items — consider setting a max and retiring low-value entries
...

## Recommendation
[Total: N candidates for pruning. Submit to user for approval before any framework modification.]
```

---

## Anti-Gaming Rules

1. **Traces must be factual** — no inflating success metrics or hiding errors in trace events
2. **Analysis must be honest** — if team behavior was chaotic, report it plainly
3. **Problems must be specific** — "team could communicate better" is not a problem record
4. **Severity must be calibrated** — not every deviation is critical; not every anomaly is low
5. **The Reviewer never interrupts delivery** — all findings, including critical ones, wait for the post-run report
6. **Framework-level structural issues** — if analysis reveals a problem with the SuperTeam framework itself (stage model, role authority, core process rules), mark it `framework_escalation` in the backlog. The Reviewer cannot self-modify the framework; this requires user decision
