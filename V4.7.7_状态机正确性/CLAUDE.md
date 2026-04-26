# SuperTeam V4.7.4

## 定位

这是 `SuperTeam` 的 Claude Code 兼容说明文件。

SuperTeam 是面向 Claude Code 的七阶段交付插件。

## V4.7 架构变更（重要）

**Orchestrator 角色已从 subagent 迁移到主会话。** Claude Code runtime 物理上禁止 subagent 调 `Agent` 工具 spawn 下级 subagent，pre-V4.7 的 OR subagent 因此无法真正 delegate，只能自代 reviewer/verifier/writer，七阶段流程在物理层面是失效的。

V4.7.0 起：

- 主会话读 `.superteam/state/mode.json` 自检身份（`mode=active` 即担任 OR）
- 主会话直接用 `Agent` 工具 spawn 各 specialist · 每次 spawn 由 PostToolUse hook 自动写入 `.superteam/runs/<slug>/spawn-log.jsonl`
- 主会话直接 Edit/Write 实质工作文件（代码 / review.md / verify.md / polish.md 等）会被 `gate_main_session_scope.py` 物理 block — 必须 spawn specialist
- 进入 / 退出 OR 模式只有两条合法路径：用户 `/superteam:go` 进、用户 `/superteam:end` 或 finish 阶段用户确认退

详见 `framework/main-session-orchestrator.md`。`agents/orchestrator.md` subagent 已 DEPRECATED · 仅为 V4.6 兼容保留。

## 核心原则

**V4.6.0 起，以下规则由 `hooks/` 物理强制，违反即 block（不是警告）**。完整约束清单与 hook 映射见 `framework/hook-enforcement-matrix.md` (137 条规则 × 30 个 checker)。

- 七阶段顺序强制执行：`clarify -> design -> plan -> execute -> review -> verify -> finish`
- 设计和计划批准前不得执行；G1 / G2 / G3 三个用户结界点必须用户明确批准
- TDD 红绿灯物理闭环：没有 failing test 不能写生产代码 (`gate_tdd_redgreen.py` 状态机)
- verifier verdict ≠ PASS 不能 git commit (`gate_commit_gate.py`)
- G2 关闭后 `feature-checklist.md` 冻结，G3 关闭后 `plan.md` MUST 项冻结
- inspector (监察者) 全程介入，trace 由 hook 自动写

**以下原则是 AI 思维引导（无 hook 背书，记录在 `.md-only` 类别）**：

- 用户边界中文优先，执行内核英文优先
- 前端美学质量遵守项目声明的 `ui-intent.md` 契约；反模式由 reviewer (审查者) 人眼审查
- **第一性原则**：回到问题本质，区分真实约束与历史惯性，优先解决根因而非绕行
- V4 只保留 plugin 安装方式

## 核心命令

- `/superteam:go`：主入口
- `/superteam:status`：看状态
- `/superteam:g1`：补项目定义
- `/superteam:g2`：补方案讨论
- `/superteam:g3`：补执行计划

高级命令保留，但不作为首屏入口。

## 安装

本地正式安装：

```text
/plugin marketplace add "D:\opencode项目\superteam"
/plugin install superteam@superteam
/reload-plugins
```

GitHub 安装：

```text
/plugin marketplace add <owner>/<repo>
/plugin install superteam@superteam
/reload-plugins
```

升级：

```text
/plugin marketplace update superteam
/reload-plugins
```

根目录是 marketplace，`V4.5.0_功能清单与逐功能TDD` 是当前插件源。

## 运行时产物

默认写入目标仓库下的：

```text
.superteam/
  runs/<task-slug>/
    polish.md
  inspector/
    traces/<task-slug>.jsonl
    reports/<task-slug>-report.html
    reports/<task-slug>-report.md
    insights.md
    health.json
    improvement-backlog.md
  state/current-run.json
```

- `runs/<task-slug>/` 保存阶段文档与 handoff
- 关键文件：`project-definition.md`、`activity-trace.md`、`solution-options.md`、`solution-landscape.md`、`design.md`、`plan.md`、`execution.md`、`polish.md`、`review.md`、`verification.md`
- `inspector/` 保存运行追踪数据、团队履职报告（HTML + MD）、跨运行洞察、系统健康指标和改进工单
- `state/current-run.json` 保存当前 run 的简明状态

## 立项三阶段

- `clarify / Project Definition`：用户关闭 `G1`
- `design / Development Solutions`：先跑方案循环，用户关闭 `G2` 后进入定形
- `plan / Execution Plan`：用户关闭 `G3` 后进入执行

第二阶段外部搜索默认按“需求锚点驱动”执行：先用关键词做 Web 搜索（Google 或等价搜索引擎）和 GitHub 搜索找成熟方案与实现，再用官方文档校验依赖约束，并补社区信号与失败信号。

`plan` 审核通过后，后续 `execute -> review -> verify -> finish` 默认不再需要用户介入，除非用户主动补充新方向或新约束。

如果用户后续补充了重要新信息，默认重开对应结界点：

- `G1`：补项目定义
- `G2`：补方案讨论
- `G3`：补执行计划

默认是 supplement，不是 rollback。

`inspector` 只记录与审计；`review` 阶段的质量门由 `reviewer` 负责。

`execute` 与 `review` 之间新增内部整理层：`simplifier`、`doc-polisher`、`release-curator`。

代码任务的默认执行节律：`red -> green -> refactor`。

## 角色

- 6 核心角色：orchestrator、planner、architect、executor、reviewer、verifier
- 11 支持角色：analyst、researcher、prd-writer、test-engineer、debugger、designer、writer、inspector、simplifier、doc-polisher、release-curator

## 质量链

`executor -> polish layer -> reviewer -> verifier -> inspector`
