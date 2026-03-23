# SuperTeam V3.3.0

## 定位

这是 `SuperTeam` 的 Claude Code 兼容说明文件。

SuperTeam 拥有严格的七阶段交付纪律，内置专业级前端设计美学智能，以及全程运行追踪与自动改进的 Reviewer 机制。

## 核心原则

- 七阶段顺序强制执行：`clarify -> design -> plan -> execute -> review -> verify -> finish`
- 不跳阶段，不绕过 review，不绕过 verify
- 设计和计划批准前不得执行
- 代码变更默认遵守 test-first 规则；做不到时必须升级说明原因
- 完成声明必须有新鲜证据，不接受"应该可以"
- 用户边界中文优先，执行内核英文优先
- 前端美学质量是跨阶段契约，不是可选装饰
- **每次运行全程追踪，自动生成团队履职报告，强制改进闭环**
- **第一性原则**：回到问题本质，区分真实约束与历史惯性，优先解决根因而非绕行，对现有架构保持合理质疑

## 命令映射

| 命令 | 含义 |
| --- | --- |
| `/superteam:go` | 全流程入口 |
| `/superteam:clarify` | 澄清阶段 |
| `/superteam:design` | 设计阶段 |
| `/superteam:plan` | 计划阶段 |
| `/superteam:execute` | 执行阶段 |
| `/superteam:review` | 评审阶段 |
| `/superteam:verify` | 验证阶段 |
| `/superteam:finish` | 完成阶段 |
| `/superteam:status` | 查看当前 run 状态 |
| `/superteam:inspect` | 运行分析/系统健康诊断 |
| `/superteam:design-consultation` | UI 美学咨询 |
| `/superteam:team-execute` | 团队并行执行 |
| `/superteam:careful` | 高风险谨慎模式 |
| `/superteam:guard` | 最高安全模式 |
| `/superteam:strategic-compact` | 上下文压缩建议 |
| `/superteam:writing-skills` | 技能创建/编辑 |

## 运行时产物

默认写入目标仓库下的：

```text
.superteam/
  runs/<task-slug>/
  reviewer/
    traces/<task-slug>.jsonl
    reports/<task-slug>-report.html
    reports/<task-slug>-report.md
    insights.md
    health.json
    improvement-backlog.md
  state/current-run.json
```

- `runs/<task-slug>/` 保存阶段文档、handoff、`review.md`、`verification.md`、`scorecard.md`、`finish.md`、`retrospective.md`，以及 `design-system.md`、`ui-intent.md`（含美学契约）
- `reviewer/` 保存运行追踪数据、团队履职报告（HTML + MD）、跨运行洞察、系统健康指标和改进工单
- `state/current-run.json` 保存当前 run 的简明状态

## Reviewer 机制（团队监工）

Reviewer 是系统的行为审计层，在每次运行结束后出具《团队履职报告》：

1. **Trace Layer（被动采集）** — 全程记录阶段转换、agent 调用、命令执行、错误、修复、决策等运行轨迹，从不打断
2. **Analysis Layer（事后分析）** — 运行结束后生成结构化报告，包含数据统计、协作追踪、问题检测
3. **Improvement Loop（强制闭环）** — 发现的问题生成工程化改进指令，必须被 orchestrator 在 finish 中显式处理

**关键规则**：
- 每次运行必须产出团队履职报告（HTML + MD），无例外
- 改进指令必须被 orchestrator 在 finish 中确认（acknowledged / addressed / disputed）
- 同一问题类别连续出现 3 次自动升级为 critical
- Reviewer 不触碰项目交付物质量——那是 Inspector 的职责

详见 `framework/reviewer.md`。

## 美学管线（Frontend Aesthetics Pipeline）

对于 `ui-standard` 和 `ui-critical` 工作，美学意图从 clarify 贯穿到 finish。详见 `framework/frontend-aesthetics.md`。

## 反模式注册表

强制反模式（违反即阻塞）：AP-01 通用字体、AP-02 白底紫渐变、AP-03 对称卡片网格、AP-04 无特征模板组件、AP-05 跨项目收敛美学。

## 角色模型

6 核心角色：orchestrator、planner、architect、executor、inspector、verifier

8 支持角色：analyst、researcher、prd-writer、test-engineer、debugger、designer、writer、reviewer

inspector 内置 5 个专项 profile（critic、security、acceptance、tdd、socratic），按风险按需激活。

## 四层质量体系

1. **executor 自检** — 执行时自我验证
2. **inspector 评审** — 挑战导向的质量门，发现 blocker 立即上报 orchestrator
3. **verifier 验证** — 独立的最终判定
4. **reviewer 分析** — 对团队行为的客观审计与持续改进
