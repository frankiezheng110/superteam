# SuperTeam V4.5.0

**发布日期**: 2026-03-28

基于 V4.4.0，引入功能清单体系与逐功能 TDD 执行循环。

## 版本定位

V4.5.0 解决的核心问题：
1. 功能清单缺失：plan.md 的 MUST 项粒度停留在阶段/模块级别，executor 和 verifier 不知道具体要做什么、测什么
2. TDD 执行是批量的：executor 把所有任务做完再统一测试，错误积累后返工代价极高
3. 监工报告缺少功能维度：Reviewer 最终报告没有逐功能测试结果的专项记录

## 设计原则

**功能清单是交付合同**：G1 建立初始功能范围，G2 将其锁定为行为级功能清单（`feature-checklist.md`），G3 验证计划完整覆盖清单，G4–G6 全程追溯。

**逐功能 TDD 循环**：executor 每次只做一个功能，完成红绿灯循环并记录证据后，才能开始下一个功能。无法变绿则停下升级 OR，不得跳过。

**监工看得见每个功能的测试结果**：Reviewer 报告新增专项节，逐功能列出 RED/GREEN 证据引用，静默跳过的功能立即暴露。

## 新增内容

### `feature-checklist.md`（运行时产物，G2 锁定）

每个功能项包含：
- 单个可观测的用户行为（不是阶段名/模块名）
- 测试类型（unit / integration / E2E）
- 测试工具

由 orchestrator 在 design 收尾时与用户确认，G2 关闭即锁定，之后只读。

### `framework/stage-gate-enforcement.md`

新增 Agent Entry Log Requirement：每个 agent 启动时在 `activity-trace.md` 写入场记录，记录读取的 Gate 编号和找到的关键产物路径。Reviewer 验证 Gate 编号和路径是否正确。

Gate 1 新增 check 8：`project-definition.md` 包含初始功能范围列表。

Gate 2 新增 checks 10–14：`feature-checklist.md` 存在、每项是单个可观测行为、每项有测试类型和工具、G2 批准记录、Reviewer 检查点。**缺失时 OR 必须问用户，不得由 designer 或 planner 自行补充。**

Gate 3 新增 checks 10–11：plan.md 每个任务可追溯到 feature-checklist.md 某项；plan.md 没有清单外的 MUST 项。

Gate 4 重写为逐功能证据检查（checks 3–8）：
- execution.md 有每个功能的独立章节
- 每个 COMPLETE 功能有真实 RED 输出 + GREEN 输出
- 每个 BLOCKED 功能有升级记录
- 没有功能可以静默缺席

总检查项：**66 个**（V4.4.0 为 59 个）。

## 修改文件

| 文件 | 变更 |
|------|------|
| `agents/executor.md` | 完整重写执行规则：Per-Feature Execution Loop（7 步循环）、Stop Conditions（无法变绿则停）、BLOCKED 升级格式、execution.md 逐功能章节结构 |
| `agents/orchestrator.md` | 新增执行阶段编排职责：executor BLOCKED 时 OR 必须响应（修复方向/推迟/终止），连续 3 个 BLOCKED 必须上报用户 |
| `agents/reviewer.md` | 报告扩展为七节，新增 Section 3：Feature Checklist Test Results（逐功能测试结果表，引用 execution.md 实际输出） |
| `agents/designer.md` | Read First 加入 Gate 1 引用 + 入场记录要求 |
| `agents/planner.md` | Read First 加入 Gate 2 引用 + 入场记录要求 |
| `agents/executor.md` | Read First 加入 Gate 3 引用 + 入场记录要求 |
| `agents/inspector.md` | Read First 加入 Gate 4 引用 + 入场记录要求 |
| `agents/verifier.md` | Read First 加入 Gate 5 引用 + 入场记录要求 |
| `framework/agent-behavior-registry.md` | 每个 agent 新增 B-*-0 入场记录行为；executor B-EX-1~5 完整重写为逐功能证据标准 |
| `framework/stage-gate-enforcement.md` | 新增双重用途说明（出口条件 + 入口导航）；新增 Agent Entry Log Requirement 节；Gate 1/2/3/4 检查项扩展 |

## 删除文件

| 文件 | 原因 |
|------|------|
| `framework/stage-handoff-specs.md` | 设计错误：运行时填写的交接文档有为过门而写的激励结构；门控清单本身已是入口导航，不需要额外交接文档 |

## 继承内容（V4.4.0 保持不变）

- 59 个二进制检查项的基础结构（Gate 1–7）
- 双检机制：OR + Reviewer 并行检查，OR 必须等 Reviewer 报告后才决策
- Reviewer 七节报告结构（Section 1/2/4/5/6/7 不变，新增 Section 3）
- 入场记录格式（Agent Entry Log）
- Designer 设计确认清理协议
- Inspector TDD 非自授权规则
- Verifier 必须运行测试套件

## 安装方式

- marketplace root：`D:\claude code\superteam`
- 当前插件源：`D:\claude code\superteam\V4.5.0_功能清单与逐功能TDD`

## 升级规则

- 新版本使用新目录，旧目录不覆盖
- 更新 marketplace 指向新版本目录后重新加载插件
