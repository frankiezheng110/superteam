# SuperTeam V4.5.0

## 定位

这是 `SuperTeam` 的 Claude Code 兼容说明文件。

SuperTeam 是面向 Claude Code 的七阶段交付插件。

## 核心原则

- 七阶段顺序强制执行：`clarify -> design -> plan -> execute -> review -> verify -> finish`
- 不跳阶段，不绕过 review，不绕过 verify
- 设计和计划批准前不得执行
- 代码变更默认遵守 test-first 规则；做不到时必须升级说明原因
- **TDD is non-optional**：默认执行 `red -> green -> refactor`
- 没有 failing test，不应先写生产实现；若违规，必须升级并按编排决定回退重做或显式例外
- 完成声明必须有新鲜证据，不接受"应该可以"
- 用户边界中文优先，执行内核英文优先
- 前端美学质量是跨阶段契约，不是可选装饰
- **每次运行全程追踪，自动生成团队履职报告，强制改进闭环**
- **第一性原则**：回到问题本质，区分真实约束与历史惯性，优先解决根因而非绕行，对现有架构保持合理质疑
- 三个用户结界点：`G1`、`G2`、`G3`
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
  reviewer/
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
- `reviewer/` 保存运行追踪数据、团队履职报告（HTML + MD）、跨运行洞察、系统健康指标和改进工单
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

`reviewer` 只记录与审计；`review` 阶段的质量门由 `inspector` 负责。

`execute` 与 `review` 之间新增内部整理层：`simplifier`、`doc-polisher`、`release-curator`。

代码任务的默认执行节律：`red -> green -> refactor`。

## 角色

- 6 核心角色：orchestrator、planner、architect、executor、inspector、verifier
- 11 支持角色：analyst、researcher、prd-writer、test-engineer、debugger、designer、writer、reviewer、simplifier、doc-polisher、release-curator

## 质量链

`executor -> polish layer -> inspector -> verifier -> reviewer`
