---
name: superteam:inspect
description: Trigger Inspector analysis for a SuperTeam run. Use to generate run reports, cross-run insights, or mid-run diagnostics. Also invoked automatically at every run completion.
argument-hint: [--cross-run | --mid-run | task-slug]
disable-model-invocation: true
---

# SuperTeam Inspect

Analyze run:

`$ARGUMENTS`

## Read First

- `framework/inspector.md`
- `agents/inspector.md`
- `framework/runtime-artifacts.md`

## Modes

### Default: Post-Run Report (automatic at every finish)

Triggered automatically at `finish`, `failed`, or `cancelled`. Also callable manually with a task slug.

1. Read `.superteam/inspector/traces/<task-slug>.jsonl`
2. Read all run artifacts in `.superteam/runs/<task-slug>/`
3. Perform full analysis per `framework/inspector.md` Layer 2
4. Generate `.superteam/inspector/reports/<task-slug>-report.md`
5. Update `.superteam/inspector/health.json`
6. Update `.superteam/inspector/insights.md`
7. Update `.superteam/inspector/improvement-backlog.md`
8. Output a Chinese-language executive summary to the user

### `--mid-run`: Mid-Run Diagnostic

For use during a live run when something feels wrong.

1. Read the trace file so far
2. Analyze what has happened up to this point
3. Identify any emerging problems or inefficiencies
4. Output a diagnostic summary — no improvement tickets (run is not complete)

### `--cross-run`: Cross-Run System Analysis

For use between runs to assess overall system health.

1. Read all available trace files and reports
2. Refresh `health.json` with aggregate metrics
3. Refresh `insights.md` with cross-run patterns
4. Identify top unresolved weaknesses
5. Recommend priority actions
6. Output a system health report

## Run Report Structure

Every completed run MUST produce a report with these sections:

```markdown
# 运行报告: <task-slug>

## 执行摘要
[一段话总结：做了什么、结果如何、花了多长时间、遇到了什么问题]

## 运行概览
| 指标 | 值 |
| --- | --- |
| 任务 | <task description> |
| 最终结果 | PASS / FAIL / CANCELLED |
| 阶段完成数 | N/7 |
| 修复循环次数 | N |
| 错误总数 | N |
| 评审发现数 | N (阻塞: N, 关注: N, 备注: N) |
| 用户干预次数 | N |
| 质量门通过率 | N% |
| 计划偏差数 | N |

## 时间线
[按时间顺序列出关键事件，标注时间戳和耗时]

| 时间 | 事件 | 阶段 | 执行者 | 耗时 | 备注 |
| --- | --- | --- | --- | --- | --- |

## 阶段分析

### Clarify
[该阶段的效率、质量、关键决策]

### Design
[该阶段的效率、质量、关键决策]

### Plan
[该阶段的效率、质量、关键决策]

### Execute
[该阶段的效率、质量、关键决策]

### Review
[该阶段的效率、质量、关键决策]

### Verify
[该阶段的效率、质量、关键决策]

### Finish
[该阶段的效率、质量、关键决策]

## 错误与修复追踪
[每个错误的发生→诊断→修复→验证链条]

## 决策审计
[关键决策点的回顾：当时的选择、依据、实际效果]

## 弱点检测
[本次运行发现的系统性弱点，每个包含严重度、证据、根因分析]

## 改进工单
[本次运行产生的具体改进建议]

## 与历史对比
[与前几次运行的关键指标对比，趋势分析]
```

## Automatic Report Generation Rule

**This is non-negotiable**: Every run that reaches `finish`, `failed`, or `cancelled` MUST produce an inspector report. This is not optional. The orchestrator must trigger it. If the inspector cannot produce a full report (e.g., trace data is incomplete), it must produce a partial report and flag the gap.

The report is written BEFORE the `finish.md` artifact so that `finish.md` can reference it.

## Output Rules

- User-facing prose: Chinese
- Technical terms, metrics, event types: English
- Every claim must reference trace evidence
- Honesty over politeness — bad results should be called out clearly
- The executive summary should be understandable in 30 seconds
