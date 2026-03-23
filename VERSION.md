# SuperTeam V3.3.0

**发布日期**: 2026-03-23

## 更新内容

本版本对 Inspector 与 Reviewer 角色进行语义正名与完整职责重构，并新增团队履职报告规范、数据保留策略及框架健康检查机制。

### 核心重构：Inspector / Reviewer 角色对调

原有角色语义与直觉相反，本版本彻底修正：

- **Inspector**（新）= 项目质量检查员，负责 review 阶段，主动评估交付物 8 个维度，发现 blocker 立即上报 orchestrator，产出 `review.md`（CLEAR / CLEAR_WITH_CONCERNS / BLOCKED）
- **Reviewer**（新）= 团队行为审计员，全程被动观察，从不打断，run 结束后出具《团队履职报告》（HTML + MD）

涉及文件：
- **`framework/inspector.md`** — 重写为项目质量检查规范（8 个检查维度、blocker 上报规则、5 个专家侧写）
- **`framework/reviewer.md`** — 重写为团队行为审计规范（数据统计、协作追踪、问题检测）
- **`framework/orchestrator.md`** — 更新阶段负责人表、Reviewer trace 路径、状态字段
- **`framework/role-contracts.md`** — 更新核心角色表、职责边界、路由规则
- **`CLAUDE.md`** — 修正角色模型、四层质量体系、存储路径、机制说明

### 新增：团队履职报告规范

- 每次 run 结束生成两份报告：HTML（用户可视，深色主题）+ Markdown（机器追踪）
- 报告结构：运行概况 → 各 Agent 履职表 → 错误记录 → 协作链路 → 问题清单 → 审计总结
- **改进方向格式约束**：工程化指令 `<owner>: [条件,] <动作>`，可直接提交系统执行

### 新增：数据保留策略

- Trace 文件 + Run artifacts 保留最近 5 次，超出后删除
- `insights.md` 永久保留作为长期蒸馏摘要
- improvement-backlog 定期清理已解决超过 10 run 的条目
- Reviewer 在每次事后分析时负责执行清理

### 新增：框架健康检查（按需触发）

触发条件（任一满足）：improvement-backlog ≥5 条 high/critical 未解决 / 同一问题类别连续出现 3 次 / 任意 `framework/*.md` 超过 300 行 / 用户主动要求

检查内容：死规则、冲突规则、重复规则、无上限列表，结果供用户审核后决定是否裁减。

### 全局版本管理规则更新

- **`~/.claude/CLAUDE.md`** — 新增「每个版本必须是可发布的完整状态」约束

### 产物规模

- 14 个 agents（6 核心 + 8 支持）
- 16 个 skills
- 12 个 framework 文档（新增 reviewer.md）
- 总文件数 91
