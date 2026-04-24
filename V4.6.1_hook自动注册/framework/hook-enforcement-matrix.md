# SuperTeam V4.6.0 · Hook Enforcement Matrix

> **本文件性质**: SuperTeam 所有 "应当 / 禁止 / 必须 / 不得" 规则的**唯一事实源**。任何规则要在 V4.6.0 里 enforce，必须在本矩阵中登记并绑定一个 hook checker 或明确标记为 `.md-only`（仅作为 AI 思维引导）。
>
> **设计立场**: 用户（SuperTeam 作者）明确表态不再信任 "AI 自觉执行 .md 规则"。V4.5.0 实物证据（SMS V1.3 phase-3 silent skip 事件）显示 OR 绕过 reviewer/verifier/inspector 三层独立监察零代价。V4.6.0 的破局点在 Claude Code harness 的 hook 机制 —— **hook 执行不在 AI 决策链里**，物理上免疫模型合理化。
>
> **分层原则**:
> - **框架级规则 (A)**: 对所有用 SuperTeam 的项目一致的规则（七阶段 / TDD 红绿灯 / Gate 门控 / 冻结锁 / commit 闸 / inspector 连续性等）→ **全局 hook 硬拦截**
> - **项目级规则 (B)**: 品味 / 具体技术栈 / 业务领域相关的规则（字体选择 / 色板 / 测试框架等）→ hook 读项目自己的 artifact (`ui-intent.md` / `feature-checklist.md` 等) 间接强制，**禁止 hardcode 全局清单**
> - **.md-only 规则 (C)**: 无法机械校验的规则（第一性原则思考 / 最小实现偏好 / 审美判断等）→ 保留在 agent.md 作为思维引导，矩阵明确标注 "无 hook 背书"，读者知道这是建议不是约束
> - **删除规则 (D)**: V4.5.0 .md 中 "已由 hook 完美覆盖" 的规则 → 从 .md 中删除，避免冗余叙述
>
> **保证**: V4.6.0 安装脚本包含 `matrix_selfcheck.py`：读本矩阵，对每条 A / B 分类断言对应 checker 存在且可 import；对每条 D 分类断言源 .md 确实已删除对应段落；任一不成立 → 安装失败。规则与 hook 不可能脱钩。

---

## Terminology · Reviewer vs Inspector (防混淆)

SuperTeam 里有两个字面容易混的角色，本矩阵严格区分：

| 中文 | English | 域 | 写的文件 | 权力 | 本矩阵 validator |
|------|---------|----|--------|------|-----------------|
| **审查者** | `reviewer` | 代码/交付物质量 (correctness / plan fidelity / security / TDD / UI) | `review.md` (verdict: CLEAR / CLEAR_WITH_CONCERNS / BLOCK) | 有 BLOCK 权（立即上报 OR）；**无** final verdict | `validator_review.py` |
| **监察者** | `inspector` | 团队行为 & 流程 (collaboration / trace completeness / gate honesty) | `activity-trace.md` continuity checkpoints + `.superteam/inspector/reports/<slug>-report.md` | **零**中断权，静默记录；post-run 才出报告 | `validator_inspector_report.py` |

**权力边界**（来自 `framework/role-contracts.md` L191）：

> "The inspector never touches deliverable quality. The reviewer never touches team behavior metrics."

所有 A7.10 / A6.12 / A16.* 等涉及 `review.md` 的条目属 **审查者 (reviewer)** 域。
所有 A7.12 / A11.* 等涉及 `inspector/reports/` 或 `activity-trace.md continuity checkpoint` 的条目属 **监察者 (inspector)** 域。
禁止将两者的职责放入同一 checker。

## 本矩阵如何使用

1. **开发者 review**: 逐条看规则分类是否合理、hook 方案是否覆盖、是否漏了未列的约束
2. **写 hook 代码时**: 对照矩阵实施，每完成一个 checker 勾选一项
3. **新增规则时**: 先登记矩阵，再实现；禁止"先写代码后补矩阵"
4. **发布前**: `matrix_selfcheck.py` 扫一遍，100% 通过才能 release

## 总体统计 (final · 2026-04-24)

| 分类 | 数量 | 说明 |
|------|------|------|
| **A · 框架级 (hook 硬拦截)** | 73 条 | 对所有项目一致，全局 hook (A8 冻结锁 3 条撤除，A5 对账加强 1 条) |
| **B · 项目级 (读 artifact)** | 15 条 | 读项目自声明的 artifact 间接校验 |
| **C · .md-only (思维引导)** | 29 条 | 无法机械校验，保留在 .md |
| **D · 删除 (已由 hook 覆盖)** | 18 条 | 从 V4.5.0 .md 删除 |
| **合计** | **135 条** | 对应 V4.5.0 全部 "应当 / 禁止 / 必须 / 不得" |

**补读来源**: 在 draft-0 (107 条) 基础上，补读 `framework/frontend-aesthetics.md` / `verification-and-fix.md` / `role-contracts.md` / `framework/orchestrator.md` / `framework/reviewer.md` / `framework/inspector.md` 后新增 30 条。

Hook checker 总数：**30 个**（14 validators + 7 gates + 4 observers + 3 post-agent + 2 session） · 不增加，每个 checker 覆盖更多矩阵条目

---

## Part A · 框架级规则 (全局 hook 硬拦截)

### A1 · 七阶段顺序与 stage transition

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A1.1 | stage-model.md L3, CLAUDE.md L10 | 七阶段 `clarify→design→plan→execute→review→verify→finish` 不可跳 | `gate_agent_spawn.py` | PreToolUse(Agent): 当前 stage 与 agent 对应 stage 不符 → block | **删除**（冗余） |
| A1.2 | stage-model.md L106-110 | 每阶段必须留对应 artifact | `validator_*.py` (14 个) | PostToolUse 触发对应 validator；gate 推进前再扫一次 | 保留（现状描述） |
| A1.3 | orchestrator.md L34, stage-model.md L111 | 每个 stage transition 同步更新 `current-run.json` (`current_stage`, `last_completed_stage`) | `validator_current_run_json.py` + `post_agent_trace_writer.py` | current-run.json 字段缺失或与 activity-trace.md 不一致 → block 下一阶段 agent spawn | **删除** |
| A1.4 | stage-model.md L116-127 | Bounded Fix Loop: `execute→review→verify→execute` 最多 3 次 | `gate_agent_spawn.py::check_repair_cycle` | `repair_cycle_count >= 3` 且尝试 spawn executor → block，强制 escalate | **删除** |

### A2 · 用户结界 G1 / G2 / G3

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A2.1 | B-OR-3, Gate 1 check 9, stage-model.md L62 | G1 必须用户明确批准 | `gate_agent_spawn.py::check_user_approval` | 批准记录是"approved by orchestrator"等 AI 自签 → block designer spawn | **删除** |
| A2.2 | B-OR-3, Gate 2 check 13 | G2 必须用户明确批准 | 同上 | block planner spawn | **删除** |
| A2.3 | B-OR-3, Gate 3 check 14 | G3 必须用户明确批准 | 同上 | block executor spawn | **删除** |
| A2.4 | Gate 2 check 10, stage-gate-enforcement.md L201 | `feature-checklist.md` 必须用户确认，不可 AI 自生成 | `validator_feature_checklist.py` + `gate_agent_spawn.py` | activity-trace.md 无用户确认原文 (≥10 char 引用) → block planner | **保留精简** |
| A2.5 | G3 关闭后 MUST 项冻结 | `gate_freeze_locks.py::plan_must_lock` | PreToolUse(Edit) plan.md MUST 段哈希变化 → block | 新增说明 |
| A2.6 | G2 关闭后 feature-checklist.md 冻结 | `gate_freeze_locks.py::feature_scope_lock` | PreToolUse(Edit) feature-checklist.md 哈希变化 → block | 新增说明 |
| A2.7 | stage-model.md L76-82 | G 重入默认 supplement 不 rollback | `dispatch/user_prompt.py::detect_supplement` | 无 block，仅设 `supplement_mode=true` 放松下游冻结 | 保留 |

### A3 · Gate 门控 (7 gates × 66 checks)

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A3.1 | stage-gate-enforcement.md Gate 1 (10 checks) | clarify→design 门控 | `gate_1_clarify_to_design.py` (聚合 14 个 validator 结果) | 任一 mandatory check FAIL 且无 override record → block | **精简**（stage-gate-enforcement.md 保留 check 清单，删除"OR 负责执行"叙述） |
| A3.2 | Gate 2 (14 checks) | design→plan | `gate_2_design_to_plan.py` | 同上 | **精简** |
| A3.3 | Gate 3 (15 checks) | plan→execute | `gate_3_plan_to_execute.py` | 同上 | **精简** |
| A3.4 | Gate 4 (9 checks) | execute→review | `gate_4_execute_to_review.py` | 同上 | **精简** |
| A3.5 | Gate 5 (7 checks) | review→verify | `gate_5_review_to_verify.py` | 同上 | **精简** |
| A3.6 | Gate 6 (6 checks) | verify→finish | `gate_6_verify_to_finish.py` | 同上 | **精简** |
| A3.7 | Gate 7 (6 checks) | finish 完成检查 | `gate_7_finish.py` + `stop_finish_guard.py` | inspector report 缺失 → block Stop | **精简** |
| A3.8 | stage-gate-enforcement.md L14-84 | Dual-Check: OR + Inspector 双独立检查 | `post_agent_trace_writer.py` hook 自己写 `gate_check_report` 事件 | hook 层保证 trace 事件齐全，不依赖 inspector agent 自己写 | **删除** OR-dual-check 叙述（hook 自动化了） |

### A4 · Agent 调用范围与顺序

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A4.1 | 各 agent.md frontmatter | 每个 agent 仅在对应 stage spawn | `gate_agent_spawn.py::check_agent_stage` | 表 `{agent: valid_stages}` 不匹配 → block | **删除** 各 agent 的 stage 叙述（保留 frontmatter） |
| A4.2 | Gate 3 check 2 | `plan_quality_gate=fail` 不得 spawn executor | `gate_agent_spawn.py::check_plan_quality` | current-run.json `plan_quality_gate=fail` → block executor | **删除** |
| A4.3 | orchestrator.md L115, stage-model.md L127 | `repair_cycle > 3` 必须 escalate 用户 | `gate_agent_spawn.py::check_repair_cycle` | 第 4 次 executor spawn → block + Notification | **删除** |
| A4.4 | orchestrator.md L116 | 连续 3 BLOCKED feature 必须上报用户 | `validator_execution.py::check_consecutive_blocked` | execution.md 最近 3 feature 全 BLOCKED → block 下一 feature 继续 | **删除** |
| A4.5 | reviewer.md L62-63 | Reviewer 必须读 polish.md / execution.md / plan.md 后才能判断 | `gate_agent_spawn.py::check_preread` | 前置 artifact 缺失 → block reviewer spawn | **删除** |
| A4.6 | verifier.md L28 | Verifier 读 review.md 但不得替代 review | `gate_agent_spawn.py::check_review_verdict` | review.md verdict=BLOCK 而直接 spawn verifier → block | **删除** |
| A4.7 | verifier.md L93 | Verifier 不得验证自己写的实现 | `gate_agent_spawn.py::check_self_verify` | 同一 session 内 verifier 不得 spawn if executor 在同 session 由 verifier 扮演 (基于 subagent_type 追踪) | **保留精简**（基本不会发生，有 hook 兜底） |
| A4.8 | role-contracts.md L13-14 | Workers 不得 spawn 下游 subagent (仅 orchestrator 可路由) | `gate_agent_spawn.py::check_spawner_is_orchestrator` | Agent 调用的上游 caller (根据 trace 追踪) 不是 orchestrator 或用户自己 → block | 新增 |
| A4.9 | role-contracts.md L17-40 | 专业 agent (analyst/researcher/prd-writer/test-engineer/debugger/writer/simplifier/doc-polisher/release-curator) 各自的 valid stages | `gate_agent_spawn.py::check_agent_stage` (表扩展) | 表 `{specialist: [valid_stages]}` 不匹配 → block；如 test-engineer 在 clarify 阶段被 spawn → block | **保留精简**（role-contracts 表保留，但 "Primary use" 叙述删除冗余） |
| A4.10 | framework/orchestrator.md L230, reviewer.md L33 | Reviewer 发现 blocker 必须立即上报 OR (trace event `escalation`)，不得等 stage 结束批处理 | `post_agent_trace_writer.py::check_immediate_escalation` | reviewer 产出 review.md 含 BLOCK finding 但 trace 缺对应 `escalation` event → discrepancy；下次 gate 前未补 → block | **精简** |

### A5 · Agent Entry Log 对账 (核心反幻觉机制)

**V4.6.0 最重要的反幻觉设计**。每个下游 agent 启动时，hook 强制它写 Entry Log，并校验 Entry Log 内容与源文件一致 —— agent 如果没真读文件，写不出正确内容，hook 下次 gate 即 block。

每个 agent 声明"必读文件清单 + 需复述的关键内容"，见 `hooks/lib/agent_types.py::AGENT_ENTRY_LOG_SPEC`，覆盖全部 16 个 agent (analyst / researcher / prd-writer / architect / designer / planner / executor / debugger / test-engineer / simplifier / doc-polisher / release-curator / reviewer / verifier / inspector / writer)。

| # | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|-------------|-----------|----------------|
| A5.1 | 每个下游 agent 必须写 Entry Log `## [agent] Entry — Gate [N]` | `post_agent_entry_log.py` → `validator_activity_trace.check_entry_log` | 无段落 → discrepancy + 下次 gate block | **删除**各 agent "Before doing any work, write entry log" 叙述 |
| A5.2a | Entry Log 必须列出 `AGENT_ENTRY_LOG_SPEC.files` 声明的每个必读文件及其**真实磁盘路径** | 同上 | 必需 artifact 未列 / 路径在磁盘不存在 → block (agent 写错路径说明没真打开文件) | 新增 |
| A5.2b | executor / reviewer / verifier 必须在 Entry Log 逐条列出 plan.md 当前 MUST 清单 | 同上 | MUST 清单与 plan.md 不一致 (遗漏/多出/改写) → block | 新增 |
| A5.2c | planner 复述 feature-checklist 条目；verifier 复述 review.md verdict；simplifier 引用 execution.md 文件变更清单 | 同上 | 对应复述缺失 → discrepancy | 新增 |
| A5.3 | spawn executor / reviewer 前，orchestrator 必须在 activity-trace.md 写 `## Orchestrator Decision — <Unit>` 段（含 Unit id + 对应 plan MUST 复述） | `gate_agent_spawn.py::check_orchestrator_decision` + `validator_activity_trace.check_orchestrator_decision` | 无 Decision 段 / Unit id 不在 plan / Unit 已 COMPLETE → block (防止 OR 顺序跳跃 / 重复 spawn) | 新增 — SMS V1.3 C07 "做了 T1.G 而非 T1.H" 类事件直接防住 |
| A5.4 | plan.md 的 MUST 项支持 **多类 + 显式 [ID]** (如 `- MUST [F-001]: 用户看到欢迎页` / `- MUST [API-matrix]: GET /api/...` / `- MUST [UI-HFrSG]: 数据获取页`) · 按 `### 分类` 分组 · execution.md 每条 MUST [ID] 必须有 `## <Category> [ID]` section + Status | `validator_plan.py` (要求 ID 格式) + `validator_execution.py` (逐 [ID] 对账) | 有 >50% MUST 缺显式 [ID] → block plan；MUST [ID] 在 execution.md 无对应 section / 无 Status → block Gate 4 | 新增 — 防止 "5 个 endpoint + 3 张表" 被缩水为"做了 1 个 endpoint" 类事件 |
| A5.5 | `plan-progress.json` 追踪每条 MUST 的 PENDING / COMPLETE / BLOCKED / DEFERRED 状态 · G3 关闭时初始化 · feature GREEN_CONFIRMED 时自动标 COMPLETE · SessionStart 注入剩余 PENDING 摘要 · Orchestrator Decision Log 的 Unit id 必须是 PENDING 状态 · PreCompact 时进 snapshot 保护 · plan.md MUST 清单变动 → 提示 reopen G3 | `hooks/lib/plan_progress.py` (新增) + `gate_agent_spawn.py` (首次 spawn 自动 init) + `observer_test_runner.py` (GREEN 时 mark) + `validator_activity_trace.check_orchestrator_decision` (Unit id 必 PENDING) + `session_injection.py` (注入摘要) + `pre_compact.py` (snapshot 包含) | Decision 的 Unit id 状态 ∈ {COMPLETE, DEFERRED, BLOCKED} → block；plan 改动导致 sha256 变化 → 注入警告提示重初始化 | 新增 — 中断恢复 · 上下文 compact 后不丢状态 · OR 不会重做已完成项 |
| A5.7 | **G4-G7 全自动化引导** · `post_executor_chain.py` 对 executor/polish/reviewer/verifier/inspector 每阶段完成都注入明确 Next action systemMessage，包含"no user confirmation needed"字样 · SessionStart `_resume_directive` 根据 current_stage 注入具体下一步（execute: spawn executor with PENDING Unit；review: spawn verifier if CLEAR；verify: enter finish；finish: write finish.md + retrospective）· current-run.json 的 `next_action` 字段被一并回显 | `hooks/post_agent/post_executor_chain.py` + `hooks/session/session_injection.py::_resume_directive` | 非 block 约束（仅注入系统消息指导 Claude） — 目的: 压缩/中断后恢复 session 时 Claude 知道下一步做什么，不再问用户 | 新增 — 用户关切 "G4-G7 中间必须完整自动化，压缩或其他原因导致的中断之后仍要自动化" |

**设计哲学**：hook 不做哈希冻结（作者决策 2026-04-24：OR 不是对抗者，不会主动篡改文件）。每次 agent 启动都被强制"现读现复述"，OR 改 plan.md 后必须在 Entry Log 同步改，两边一致即放行 —— 既消灭"凭印象做事"的幻觉，又不过度设计。

### A6 · TDD 红绿灯 (核心)

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A6.1 | executor.md L43-53, CLAUDE.md L15 | 每 feature 必须 RED→GREEN→REFACTOR | `gate_tdd_redgreen.py` + `observer_test_runner.py` | 见下方状态机 | **删除** |
| A6.2 | executor.md L43 | Step 1 RED: 先写测试 (目标路径在 tests/** 或 `feature-checklist.md` 声明的 test file) | `gate_tdd_redgreen.py::check_red_first` | feature state=PENDING 且 Edit/Write 目标是生产代码路径 → block reason: "Feature F-X 必须先有 failing test" | **删除** |
| A6.3 | executor.md L44 | Step 2 验证 RED: 测试必须 FAILED (非 error) | `observer_test_runner.py::parse_red` | Bash 运行 pytest 等, stdout 包含 FAILED + 指向新测试名 → state PENDING→RED_LOCKED；若仅 error (ImportError/SyntaxError) → state 不转移 (仍 PENDING) | **删除** |
| A6.4 | executor.md L45 | Step 2 测试立即 pass = 测试错 → 先修测试 | `observer_test_runner.py::check_premature_green` | state=PENDING 且测试运行全 PASS → warning 注入 "测试本身没测到新行为，先修测试" (不 block，记 discrepancy) | **删除** |
| A6.5 | executor.md L46-47 | Step 3 GREEN: 最小实现 | `gate_tdd_redgreen.py::check_green_allowed` | state=RED_LOCKED 时允许 Edit 生产代码；state=PENDING → block；state=GREEN_CONFIRMED → block | **删除** |
| A6.6 | executor.md L48 | Step 4 验证 GREEN: 测试 pass + 全套不 regression | `observer_test_runner.py::parse_green` | state=RED_LOCKED 且全套 PASS → state→GREEN_CONFIRMED + 记 green_evidence | **删除** |
| A6.7 | executor.md L50 | Step 5 REFACTOR 只能 green 状态下 | `gate_tdd_redgreen.py::check_refactor_phase` | state≠GREEN_CONFIRMED 时声明 refactor 段落 → block | **保留精简** |
| A6.8 | executor.md L51-52 | Step 6-7 记录 evidence 后才能下一 feature | `gate_tdd_redgreen.py::check_feature_switch` | execution.md 新增 feature section 但上一 feature state≠GREEN_CONFIRMED 也无 BLOCKED escalation → block | **删除** |
| A6.9 | executor.md L57 | 连续 3 次 GREEN 失败必须 escalate | `gate_tdd_redgreen.py::check_green_attempts` | state=RED_LOCKED 且 observer 累计 attempt_count>=3 仍未转 GREEN → block 下一次 Edit 生产代码，强制写 BLOCKED escalation block | **删除** |
| A6.10 | executor.md L46 | Step 3 GREEN 是最小实现 | `.md-only` (C 类) | 无法机械判断"最小" | 保留作为引导 |
| A6.11 | orchestrator.md L112, plan-quality.md | TDD 豁免只能 orchestrator 签发 | `validator_plan.py::check_tdd_exception_format` | current-run.json `tdd_exception=YES` 需伴随 `reason` 字段 + plan.md 对应段落 | **删除** |
| A6.12 | reviewer.md L66-75 | Reviewer 不得自签 TDD N/A | `validator_review.py::check_tdd_gate` | review.md TDD gate 段落 "N/A" 无引用 `tdd_exception` 记录 → block → review verdict=invalid | **删除** |
| A6.13 | reviewer.md L93, verifier.md L97 | 禁用 `cargo check` / `tsc --noEmit` 代替测试 | `observer_build_only.py` | Bash 命令匹配 `^(cargo check|tsc --noEmit|.*--dry-run)` 后若在 verify/review 阶段 → 记 "not-a-test"；verification.md 引用此命令作证据 → validator_verification 判 V1 FAIL | **删除** |
| A6.14 | verification-and-fix.md L22-26 | 实现前无 failing test = TDD violation，默认返工除非 orchestrator 明文 exception | `gate_tdd_redgreen.py::check_production_first` | PostToolUse(Edit) 生产代码后若 feature state 从未进入过 RED_LOCKED 且无 tdd_exception → 回溯标记违规 + block 下一 feature | **删除** |
| A6.15 | framework/orchestrator.md L223, verification-and-fix.md L185 | review verdict=BLOCK 必须返回 execute 再 verify (禁止直接 verify) | `gate_agent_spawn.py::check_review_verdict_before_verify` | current-run.json review_verdict=BLOCK 且尝试 spawn verifier → block | **删除** |

### A7 · 产物文件完整性

| # | 监视文件 | Validator | Block 条件 (任一) |
|---|---------|-----------|------------------|
| A7.1 | `project-definition.md` | `validator_project_definition.py` | 缺 `objective` / `constraints` / `non-goals` / `ui_weight` / 初始功能范围；字段空 |
| A7.2 | `solution-options.md` | `validator_solution_options.py` | 选项数 <2；无用户决策记录 |
| A7.3 | `solution-landscape.md` | `validator_solution_landscape.py` | 无外部搜索证据 (URL + 日期)；无依赖验证 |
| A7.4 | `design.md` | `validator_design.py` | 无选中方向 + 理由；无被拒方案 |
| A7.5 | `ui-intent.md` | `validator_ui_intent.py` | 7 节任一缺失或内容空 (Aesthetic/Typography/Color/Motion/Spatial/Visual Detail/Anti-Pattern Exclusions) |
| A7.6 | `feature-checklist.md` | `validator_feature_checklist.py` | 有"阶段名/模块名/分类名"而非单一可观察行为；缺 test_type 或 test_tool |
| A7.7 | `plan.md` | `validator_plan.py` | 任一 task 缺 5 字段 (objective/target files/steps/verification/done)；MUST 项无 test case；MUST/DEFERRED 标签缺失；MUST 未覆盖 feature-checklist |
| A7.8 | `execution.md` | `validator_execution.py` | feature section 数 < feature-checklist.md；COMPLETE 功能缺 RED/GREEN evidence；BLOCKED 功能缺 escalation；summary 缺 TDD exception 声明 |
| A7.9 | `polish.md` | `validator_polish.py` | polish 层运行后此文件缺失；polish 改了行为相关文件但无 post-polish checks |
| A7.10 | `review.md` | `validator_review.py` | verdict 非 CLEAR/CLEAR_WITH_CONCERNS/BLOCK；缺 delivery scope check；缺 TDD gate；MUST 缺失但记为 MINOR 非 BLOCK |
| A7.11 | `verification.md` | `validator_verification.py` | verdict 非 PASS/FAIL/INCOMPLETE；缺测试套件 evidence；缺逐 MUST 状态；缺 delivery_confidence |
| A7.12 | `reports/<slug>-report.md` | `validator_inspector_report.py` | 7 section 任一缺失；引用的 trace event 不存在；含"appears/seems/probably"关键词 |
| A7.13 | `finish.md` | Gate 7 | 无 inspector_report_acknowledged |
| A7.14 | `retrospective.md` | Gate 7 | 无 improvement_action |
| A7.15 | `current-run.json` | `validator_current_run_json.py` | schema 不符；字段缺失；stage transition 跳阶；repair_cycle_count 与 activity-trace 不一致 |
| A7.16 | `activity-trace.md` | `validator_activity_trace.py` | 缺任一 stage 的 inspector checkpoint；缺任一 agent 的 entry log；缺 gate decision record |
| A7.17 | `scorecard.md` | `validator_scorecard.py` (新增 validator, 合并进 validator_current_run_json.py) | 存在 plan 后不维护 → discrepancy；不 block 但 Gate 7 硬 check |
| A7.18 | `current-run.json` 扩展字段 | `validator_current_run_json.py::check_full_fields` | framework/orchestrator.md L303-340 列出 33 个字段（current_stage / last_completed_stage / repair_cycle_count / plan_quality_gate / ui_weight / aesthetic_direction / anti_pattern_gate_status / inspector_trace_path / inspector_report_status 等）；每次 stage transition 必须字段齐全 → 缺失 → block 下一 stage |
| A7.19 | `.superteam/inspector/health.json` | `validator_inspector_report.py::check_health` | 完成 run **必须**更新 health.json；缺失或 mtime 早于本 run 开始时间 → **block Gate 7**（不允许 finish 关闭） |
| A7.20 | `.superteam/inspector/insights.md` / `improvement-backlog.md` | `validator_inspector_report.py::check_insights` | 完成 run **必须**对这两个文件做增量更新（至少追加一段本 run 的条目，含 `run_slug` + 时间戳）；未更新 → **block Gate 7** |

### A8 · ~~冻结锁~~ (已删除 · 作者决策 2026-04-24)

V4.6.0 初期设计包含对 feature-checklist.md / plan.md MUST / verification.md verdict 的 SHA256 冻结。**已删除**。理由：OR 不是对抗者，不会主动篡改文件；真正的问题是"凭印象做事"，由 A5 Entry Log 对账机制覆盖（agent 必须现读现复述）。`gate_freeze_locks.py` 保留为 no-op stub 避免 install 失败，可在 V4.7.0 清理。

原 A8.1 / A8.2 / A8.3 规则内容 → 被 A5.2b (plan MUST) + A5.2a (artifact 路径) 实质替代。

### A9 · 文件阶段写入权限 (File Stage Scope)

| # | 阶段 | 允许写入的文件 | Hook Checker |
|---|------|--------------|-------------|
| A9.1 | clarify | `project-definition.md`, `activity-trace.md`, `handoffs/01-*`, `current-run.json`(hook 限字段) | `gate_file_scope.py::check_clarify` |
| A9.2 | design | `solution-options.md`, `solution-landscape.md`, `design.md`, `ui-intent.md`, `feature-checklist.md`, `activity-trace.md`, `handoffs/02-*` | `gate_file_scope.py::check_design` |
| A9.3 | plan | `plan.md`, `activity-trace.md`, `handoffs/03-*` | `gate_file_scope.py::check_plan` |
| A9.4 | execute | `execution.md`, 生产代码, 测试代码, `activity-trace.md`, `handoffs/04-*` (polish 层写 `polish.md`) | `gate_file_scope.py::check_execute` |
| A9.5 | review | `review.md` (仅 reviewer caller), `activity-trace.md`, `handoffs/05-*` | `gate_file_scope.py::check_review` |
| A9.6 | verify | `verification.md` (仅 verifier caller), `activity-trace.md`, `handoffs/06-*` | `gate_file_scope.py::check_verify` |
| A9.7 | finish | `finish.md`, `retrospective.md`, `reports/*` (仅 inspector caller), `activity-trace.md` | `gate_file_scope.py::check_finish` |

**Block 条件**：跨 stage 写入 → block reason 指明 "当前 stage=X，禁写 Y，参考 framework/hook-enforcement-matrix.md §A9"

### A10 · Git Commit / Tag / Push 硬闸

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A10.1 | 诊断文件 Hook 2 | commit 前对应 checkpoint 必须 `verification.md verdict=PASS` | `gate_commit_gate.py::check_verdict` | 最近 verification.md verdict≠PASS 或缺失 → block | 新增 |
| A10.2 | 诊断文件 Hook 2 | commit 前 review.md verdict≠BLOCK | `gate_commit_gate.py::check_review` | review.md verdict=BLOCK → block | 新增 |
| A10.3 | 诊断文件 H11 | commit 对应的 checkpoint 必须在 activity-trace.md 有段落 | `gate_commit_gate.py::check_trace_continuity` | 本次 commit 无对应 `## Checkpoint <id>` 段 → block | 新增 |
| A10.4 | 显式 override | `ALLOW_UNVERIFIED_COMMIT=1` 环境变量允许 bypass | `gate_commit_gate.py::check_override` | bypass 时写 `.superteam/state/unverified-commits.jsonl` 留痕 | 新增 |

### A11 · Inspector 全程介入

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A11.1 | inspector.md L60-90, stage-gate-enforcement.md L14-84 | 每 gate 推进前必须有 `gate_check_report` trace 事件 | `post_agent_trace_writer.py` (hook 自写) + `gate_agent_spawn.py::check_inspector_trace` | jsonl 当前 stage 无 `gate_check_report` 事件 → block 下一 stage agent spawn | **删除**（hook 自动化） |
| A11.2 | inspector.md L27-55, B-RV-1 | clarify/design/plan 每 stage 必须有 continuity checkpoint | `validator_activity_trace.py::check_inspector_checkpoint` | activity-trace.md 缺 `## Inspector Checkpoint: <stage>` 段 → block 下一 stage | **保留精简** |
| A11.3 | inspector.md L113-145 | 每 agent 调用前后必须记 `agent_spawn` / `agent_stop` trace 事件 | `post_agent_trace_writer.py` | hook 自动写，不依赖 inspector agent 自觉；缺失即 hook bug | **删除** |
| A11.4 | 诊断文件 Hook 3 | finish 前必须有 `<slug>-report.md` | `stop_finish_guard.py` | current_stage=finish 且 reports/<slug>-report.md 不存在 → block Stop 事件 | **删除** |
| A11.5 | inspector.md L43-52 | Inspector checkpoint 含 "safe-to-advance: YES/NO" | `validator_activity_trace.py::check_checkpoint_content` | checkpoint 段无此字段 → discrepancy | 保留精简 |
| A11.6 | inspector.md L293-297, R7 | Inspector 报告禁用 "appears/seems/probably" 主观词 (**见 A18 跨角色写作纪律**，此条仅限 inspector 产出) | `gate_subjective_language.py::check_inspector_report` | PreToolUse(Edit) 目标是 `inspector/reports/**` 时 content 含禁用关键词 → block | **删除** |
| A11.7 | framework/orchestrator.md L342-351 | activity-trace.md 在 8 种情境必须追加 compact entry (新问题/design mode 选定/G 重入/solution option 引入-拒-选/search checkpoint/inspector continuity 更新/plan 呈现 review) | `validator_activity_trace.py::check_compact_entries` | 对应事件发生 (由 hook 自己识别) 但 trace 段无对应条目 → discrepancy | **精简** |
| A11.8 | framework/inspector.md L42-50, framework/orchestrator.md L353-367 | Inspector trace 最小事件覆盖 7 类 (stage_enter/stage_exit/decision_made/specialist_inject/gate_check/repair_cycle/user_intervention) | `post_agent_trace_writer.py::ensure_minimum_events` (hook 自写) | hook 自动 emit，不依赖 agent 自觉；任一 stage 转换事件缺失即 hook bug | **删除** |
| A11.9 | framework/inspector.md L79-82 | Retention: 保留最近 5 个 traces + 5 个 reports，老的归档 | `session/session_injection.py::rotate_retention` | SessionStart 时扫 `.superteam/inspector/traces/` 和 `reports/`，超 5 归档到 `traces_archive/` 和 `reports_archive/`；不 block | **保留精简** |

### A12 · Override 记录

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A12.1 | stage-gate-enforcement.md L439-460 | 任何 gate override 必须写 JSON record 到 current-run.json + activity-trace.md | `post_agent_trace_writer.py::check_override_record` | activity-trace 出现 "override" 字样无配对 current-run.json override block → discrepancy | **精简** |
| A12.2 | stage-gate-enforcement.md L462-469 | Override 禁用场景: 缺 G 批准 / 缺 artifact / 缺 inspector report / 未决 BLOCK / FAIL verdict | `gate_agent_spawn.py::check_override_scope` | 上述场景尝试 override → block (override 被拒) | **精简** |
| A12.3 | verification-and-fix.md L138-153 | Fix Package 必须含 5 字段 (failed requirement / evidence of failure / suspected scope / minimal recommended task list / re-verification command set) | `validator_verification.py::check_fix_package` | verdict=FAIL 但 verification.md 缺 fix package section 或任一字段缺失 → block 返回 execute | 新增 |
| A12.4 | verification-and-fix.md L160-165 | Return Paths 严格路由: FAIL→execute；INCOMPLETE(plan weak)→plan；INCOMPLETE(missing context)→escalate；repeated systemic failure→terminate | `gate_agent_spawn.py::check_return_path` | verifier verdict + 建议 return target 与实际 spawn 的下游 agent 不符 → block | **精简** |

### A13 · Session 连续性与压缩保护

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A13.1 | 诊断文件 Hook 4 | SessionStart 注入上轮 discrepancy 摘要 + report 路径 | `session_injection.py` | SessionStart 时若 current-run.json 存在且 reports/ 下有报告 → 注入 ≤500 tokens 摘要；无 block | 新增 |
| A13.2 | 新增 | PreCompact 前快照 current-run.json / feature-tdd-state / plan-freeze / 最新 trace 事件 | `dispatch/pre_compact.py` | 无 block，快照到 `.superteam/state/snapshots/<ts>.json` | 新增 |
| A13.3 | SessionEnd | 轻量收尾：current-run.json last_updated 写入 | `dispatch/session_end.py` | 无 block | 新增 |

### A14 · Polish 层强制链

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A14.1 | orchestrator.md L204-207 | executor 结束后代码/文档变更 → 自动引导 simplifier / doc-polisher | `post_executor_chain.py` | executor 结束后无 polish.md 或 polish.md 未更新 → PostToolUse 注入 systemMessage "必须 spawn simplifier" | **删除** |
| A14.2 | stage-model.md L96-103 | polish 结束后 reviewer 必被 spawn | `post_executor_chain.py::check_reviewer_next` | polish.md 完成但未 spawn reviewer → systemMessage 引导；下次 PreToolUse(Agent≠reviewer) 前检查仍缺 → block | **删除** |
| A14.3 | 新增 | reviewer verdict=CLEAR 后 verifier 必被 spawn | `post_executor_chain.py::check_verifier_next` | review.md verdict=CLEAR 但未 spawn verifier → systemMessage 引导；后续再 spawn 其他 agent → block | 新增 |

### A15 · Feature 顺序与切换

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A15.1 | executor.md L78 | Feature 按 plan.md 顺序执行，不得重排 | `gate_tdd_redgreen.py::check_feature_order` | execution.md 新增 feature section 与 plan.md 下一项不符 → block | **删除** |
| A15.2 | executor.md L51-53 | 下一 feature 开始前必须记录 evidence | `gate_tdd_redgreen.py::check_feature_switch` | 见 A6.8 | **删除** |
| A15.3 | verification-and-fix.md L99, frontend-aesthetics.md stage-model | ui-critical 缺审美证据 → verifier verdict 必须 INCOMPLETE 不得 PASS | `validator_verification.py::check_ui_critical_evidence` | ui_weight=ui-critical 且 verification.md 缺 aesthetic contract evidence + anti-pattern gate 段落但 verdict=PASS → block 判 verdict invalid | **删除** |

### A16 · Reviewer Responsibility Checklist (审查者 8+1 维度)

来源 `framework/role-contracts.md` L92-164: reviewer 必须对每次 review 覆盖以下 8+1 维度，review.md 的 Checklist Coverage 节要逐项标注 checked/not-checked + result。

| # | 维度 | Hook 校验 |
|---|------|----------|
| A16.1 | Functional Correctness | `validator_review.py::check_checklist_functional` review.md Checklist Coverage 节缺此维度 → block |
| A16.2 | Plan Fidelity | 同上 (check_plan_fidelity) |
| A16.3 | Code and Design Quality | 同上 (check_code_quality) |
| A16.4 | Security | 同上 (check_security) |
| A16.5 | Artifact Completeness | 同上 (check_artifact_completeness) |
| A16.6 | Error and Fix Quality | 同上 (check_fix_quality) |
| A16.7 | TDD And Test Coverage (code-changing work) | 见 A6.12 |
| A16.8 | UI Quality (ui-standard/ui-critical) | 见 B1 (读 ui-intent.md) |
| A16.9 | Immediate Blocker Reporting | 见 A4.10 (立即上报 OR) |

**Block 条件通用**: review.md Checklist Coverage 节任一维度缺失或标为 "skipped without reason" → block；UI 维度在 ui-weight=ui-none 时可标 N/A。

### A17 · Finish 阶段 Inspector Problem Acknowledgment

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A17.1 | framework/orchestrator.md L374-380 | finish.md 必须 acknowledge 每条 inspector report 的 problem record (`acknowledged` / `addressed` / `disputed`) | `gate_7_finish.py::check_problem_acknowledgment` | reports/<slug>-report.md 每条 problem 在 finish.md 无对应 acknowledgment → block finish 关闭 | **删除** |
| A17.2 | framework/orchestrator.md L380 | inspector critical problem 必须出现在 retrospective.md 显要位置 | `gate_7_finish.py::check_critical_in_retro` | critical problem 未在 retrospective.md 出现 → block | **精简** |
| A17.3 | framework/orchestrator.md L381 | failed / cancelled 运行也要部分 inspector analysis + acknowledgment | `stop_finish_guard.py::check_partial_analysis_on_terminal` | current-run.json status=failed/cancelled 但无 partial report → systemMessage 引导 + 下次 Stop 前仍缺 → block | **精简** |

### A18 · 跨角色写作纪律 (reviewer / verifier / inspector 共同)

| # | 来源 | 规则 | Hook Checker | Block 条件 | V4.5.0 .md 处理 |
|---|------|------|-------------|-----------|----------------|
| A18.1 | reviewer.md L92, verifier.md L89, inspector.md R7 | 禁用主观词 "appears/seems/probably/should/looks fine" 作为最终证据 | `gate_subjective_language.py::check_all_review_artifacts` | PreToolUse(Edit/Write) 目标 ∈ `{review.md, verification.md, reports/**}` 且 content diff 新增行含禁用关键词 → block；用户明确引用或引述除外（quoted in backticks 豁免） | **精简**（保留总方针，删除三份重复叙述） |
| A18.2 | reviewer.md L92 | 禁止 blocker 藏在软措辞 | 部分 hook（A18.1 关键词拦截覆盖大半）；语义层面转为 C10 `.md-only` | 同上 | 保留总方针 |
| A18.3 | inspector.md R6, verifier.md L86-87 | 每条 claim 必须 cite artifact location 或 trace event | `validator_inspector_report.py::check_citations` + `validator_verification.py::check_evidence_citations` | report/verification.md 结论句无邻近 file:line 或 trace event timestamp → discrepancy；Gate 7 时累计 discrepancy>3 → block finish | **精简** |

---

## Part B · 项目级规则 (读项目 artifact 间接强制)

> 这些规则的**内容**因项目而异（品味、技术栈、业务域），但**"必须遵守"这个行为**是框架级的。Hook 读项目自己的 artifact，不 hardcode 全局清单。

### B1 · UI 审美契约遵守 (仅 ui-standard / ui-critical)

| # | 来源 | 项目声明位置 | Hook 校验方式 | V4.5.0 .md 处理 |
|---|------|-------------|--------------|----------------|
| B1.1 | executor.md L91-97 | `ui-intent.md` § Typography Contract | `gate_ui_contract.py::check_typography`：提取声明的字体白名单；PreToolUse(Edit) CSS/HTML 若 `font-family` 出现不在白名单内字体 → block | **删除** V4.5.0 硬编码的 "never Inter/Roboto/Arial" |
| B1.2 | executor.md L99-103 | `ui-intent.md` § Color Contract | `gate_ui_contract.py::check_color`：提取声明的 hex/rgb 调色板；PreToolUse(Edit) CSS 若出现 palette 外颜色 → block；若声明了 "禁用紫色渐变" 硬匹配拦截 | **删除** 硬编码 "never purple gradient on white" |
| B1.3 | executor.md L105-111 | `ui-intent.md` § Motion Contract | `gate_ui_contract.py::check_motion`：提取声明的动效技术 (CSS-only/Motion/GSAP)；PreToolUse(Edit) 若引入非声明技术 → block | **删除** 硬编码 "never animate indiscriminately" |
| B1.4 | executor.md L113-117 | `ui-intent.md` § Spatial Contract | `gate_ui_contract.py::check_spatial`：项目若声明 "禁止对称卡片网格" 则 grep CSS 禁用 pattern；项目未声明则放行 | **删除** 硬编码 "never symmetric card grid" |
| B1.5 | executor.md L119-123 | `ui-intent.md` § Visual Detail Contract | `gate_ui_contract.py::check_visual_detail` | **删除** 硬编码 "never flat solid background" |
| B1.6 | executor.md L125-128 | `ui-intent.md` § Anti-Pattern Exclusions | `gate_ui_contract.py::check_antipattern`：项目声明的 AP-01..AP-N 清单 → PreToolUse(Edit) grep 拦截 | **删除** V4.5.0 硬编码 AP-01..AP-05 |
| B1.7 | executor.md L130-135 | `ui-intent.md` § Aesthetic Direction (maximalist/minimalist) | `.md-only` (C 类)：代码复杂度匹配审美的判断无法机械化 | 保留在 .md |

**项目自主**：如果某项目就想用 Inter，它在 ui-intent.md § Typography 写 "Inter (Medium, 14-48px)" 即可，hook 允许。**全局 hook 不做字体黑名单**。

### B2 · 测试命令识别

| # | 项目声明位置 | Hook 校验方式 |
|---|-------------|--------------|
| B2.1 | `feature-checklist.md` 每项 test_tool 字段 + `.superteam/config/test-commands.json` (可选) | `observer_test_runner.py` 读 feature-checklist.md 得出本 feature 应跑命令；Bash 输出用对应 parser (pytest/jest/cargo/...) 解析 PASSED/FAILED |
| B2.2 | `.superteam/config/test-commands.json` | 项目可自定义正则扩展 (如 Rust nextest / deno test) |

### B3 · Test-First 执行路径

| # | 项目声明 | Hook 校验 |
|---|---------|----------|
| B3.1 | `feature-checklist.md` 每项 test_type (unit/integration/E2E) 决定 RED→GREEN 的"测试文件路径推断" | `gate_tdd_redgreen.py::infer_test_path` 从 test_type 推断目录前缀 (`tests/unit/` vs `tests/integration/` vs `tests/e2e/`)；项目可在 `.superteam/config/test-paths.json` 自定义映射 |

### B4 · Team 执行模式

| # | 项目声明 | Hook 校验 |
|---|---------|----------|
| B4.1 | `plan.md` 声明 `execution_mode=team` + `conflict_domain` + `merge_owner` | `gate_file_scope.py::check_team_boundary`：executor spawn 时若 team 模式，Edit 目标在 touched_files 外 → block；非 team 模式不触发 |

### B5 · Design Thinking Framework 4 Pillars (ui-standard / ui-critical)

| # | 来源 | 项目声明位置 | Hook 校验方式 |
|---|------|-------------|--------------|
| B5.1 | frontend-aesthetics.md L9-52 | `project-definition.md` 新增 `design_thinking_seeds` 段（clarify 阶段）+ `ui-intent.md` 完整 4 pillar 段（design 阶段） | `validator_project_definition.py::check_design_seeds` 要求有 purpose / tone seed / differentiation seed 三段；`validator_ui_intent.py::check_4_pillars` 要求 Purpose / Tone / Constraints / Differentiation 四节非空 |

### B6 · UI Anti-Pattern · **不做 hook** (作者决策 2026-04-24)

**设计决策**: V4.5.0 `framework/frontend-aesthetics.md` Mandatory Anti-Patterns (AP-01..AP-05: 禁 Inter/Roboto、禁紫渐变、禁对称卡片等) 是 SuperTeam 框架作者的品味偏好，不属于"对所有项目一致的客观规则"。**hook 不对 AP 做任何预设拦截**。

**理由**:
- 某些项目的 brand system 正当使用 Inter / Roboto → 预设黑名单会误伤合法需求
- "紫渐变 + 白底" 的视觉判断有语境依赖 → hook grep 拦截不够智能，容易假阳性
- 即使采用"默认严厉 + 项目豁免"方案，hook 代码里仍然嵌入了品味清单 → 违背 "不把个别品味做成全局 hook" 的立场

**V4.6.0 处理**:
- `framework/frontend-aesthetics.md` 原 Mandatory / Advisory Anti-Patterns 两节**全文保留**作为 **设计时参考资料 / 审查者 (reviewer) 人眼检查清单**
- 但**不生成** `gate_ui_contract.py::check_antipattern` 函数
- `hooks/config/antipattern-defaults.json` **不创建**
- 审查者 (reviewer) 在 review.md Checklist Coverage § UI Quality 维度可引用这些 AP 作为主观质量评估依据，但不属于 hook 硬拦截

**与 B1.1-B1.6 的边界**:
- B1.* 是"项目主动声明"的硬契约：项目在 `ui-intent.md` 显式写 "字体只用 Satoshi" → hook 读这个白名单去拦 → **保留**
- B6 是"框架预设黑名单"：SuperTeam 替所有项目预先禁用某些 pattern → **删除**
- 区别：hook 只执行项目自己签的字，从不替项目做品味判断

### B1 补充说明 · 项目未声明时 hook 不激活

当 `ui-intent.md` § Typography Contract 未声明字体白名单（或整个 Typography Contract 段落不存在）时，`gate_ui_contract.py::check_typography` **不激活** —— 不默认禁止任何字体。Color / Motion / Spatial / Visual Detail Contract 同理。

项目主动声明 → hook 按声明拦。项目没声明 → hook 什么都不管。**SuperTeam 框架不替项目做品味判断。**

---

## Part C · 保留在 .md 作为思维引导 (无 hook 背书)

> 这些规则**无法机械校验**或**校验成本远高于价值**，保留在 agent.md 作为 AI 思维引导。矩阵明确标注它们是建议不是约束，读者知晓。

| # | 来源 | 规则 | 为何不 hook 化 |
|---|------|------|---------------|
| C1 | orchestrator.md L46-55 | First Principles Decision-Making (挑战继承假设、追溯核心目标、结构洞察升级) | 机械无法判断"真限制 vs 历史惯性" |
| C2 | orchestrator.md L47 | "Challenge inherited assumptions" | 同上 |
| C3 | orchestrator.md L50 | "Trace back to core objective" | 同上 |
| C4 | orchestrator.md L52 | "Prefer root-cause over workaround" | 同上 |
| C5 | executor.md L79 | "prefer smallest implementation" | 无法量化"最小" |
| C6 | executor.md L80 | "refactor only while tests stay green — not a license to add behavior" | 部分可校验 (A6.7)，"不得 add behavior" 语义无法机械判断 |
| C7 | executor.md L81-82 | "if task package is wrong, escalate instead of improvise" | 无法机械判断"即兴" |
| C8 | executor.md L84 | "call out plan drift explicitly" | 无法自动识别"drift" |
| C9 | reviewer.md L59 | "emit concrete blocker findings quickly" | "quickly"无法量化 |
| C10 | reviewer.md L92 | "hide blockers inside soft wording" | 语义判断 |
| C11 | verifier.md L88 | "prefer command output over narrative claims" | 主观 |
| C12 | verifier.md L89 | "cite what was checked and what remains missing" | 部分可校验（A7.11），质量无法机械判断 |
| C13 | inspector.md L55 | "solution-options.md has no rejected alternatives" 可观察 vs "team seems rushed" 不可观察 | 部分 hook，部分保留作为 inspector 写作纪律 |
| C14 | stage-gate-enforcement.md L111 | "An agent that copies paths without reading them will produce incorrect work" | 语义判断 |
| C15 | frontend-aesthetics.md (待读) | "bold aesthetic direction" / "avoid generic" | 审美判断无法机械化 |
| C16 | designer.md (待读) | Multiple design options rationale quality | 理由质量是语义 |
| C17 | designer.md | 审美方向"bold" vs "generic" 区分 | 同 C15 |
| C18 | skills/careful, skills/guard | "slow down, restate risky action" | 语义 |
| C19 | frontend-aesthetics.md L21-40 | 选 "bold, intentional" 审美方向 vs 陈词滥调 | "bold"无法机械化 |
| C20 | frontend-aesthetics.md L58 | typography "distinctive + characterful" | 审美判断 |
| C21 | frontend-aesthetics.md L110-139 | motion "high-impact moments" vs "animate everything" | 部分可 hook (动画数量上限)，核心判断是审美 |
| C22 | frontend-aesthetics.md L211-233 | Implementation Complexity Matching (maximalist 需繁密代码 / minimalist 需精简代码) | 机械无法判断"复杂度匹配" |
| C23 | frontend-aesthetics.md L201-209 | Advisory Anti-Patterns AP-06..AP-10 (非阻塞，review 标记) | 部分语义 (如 "identical timing on all elements") 无法机械 |
| C24 | frontend-aesthetics.md L274-280 | 每项目必须 distinctive，跨项目 convergence 本身是 anti-pattern | 跨 run 判断需人工，hook 范围外 |
| C25 | framework/orchestrator.md L170-246 | Specialist Injection Rules "when risk justifies" (add researcher when source evidence missing / add debugger when repeated attempts fail / ...) | "risk justifies" 本身是判断 |
| C26 | role-contracts.md L197-204 | Reviewer 5 Specialist Profiles (critic/tdd/acceptance/socratic/security) 何时激活 | profile 内部策略，hook 范围外 |
| C27 | framework/orchestrator.md L45 | Convention vs Rule 区分 (哪些是 non-negotiable rule 哪些是可挑战的 convention) | 元层面判断 |
| C28 | framework/inspector.md L84-91 | Health Check Triggers (high-severity 重复 / cross-run 模式 / framework files 过大) | 跨 run 触发，由人驱动 |
| C29 | framework/role-contracts.md L218-221 | Language Policy user-facing 中文 / execution-facing 英文 | 语义无法机械判断"user-facing" |

---

## Part D · 建议删除 (已由 hook 完美覆盖)

> V4.5.0 .md 中这些规则在 V4.6.0 由对应 hook 物理强制，.md 保留反而冗余。删除动作由 V4.6.0 的 agent.md / framework 精简 PR 执行。

| # | V4.5.0 出处 | 原文摘要 | 由谁覆盖 |
|---|------------|---------|---------|
| D1 | orchestrator.md L58-65 | "never skip review/verify/user approval/..." | A1.1 + A2.1-3 + A3.* + A4.* (hook 物理不可能跳过) |
| D2 | orchestrator.md L66-91 | Stage Gate Enforcement Protocol 整段 Step 1-7 | A3.* (hook 自动执行 7 步) |
| D3 | orchestrator.md L94-96 | "after every stage transition, update status file" | A1.3 |
| D4 | orchestrator.md L117 | "make inspector write continuity checkpoints" | A11.2 |
| D5 | executor.md L18 | "Before doing any implementation work, write an executor entry log" | A5.1 |
| D6 | executor.md L36-53 | Per-Feature Execution Loop 七步描述 | A6.1-A6.8 |
| D7 | executor.md L56-61 | Stop conditions | A6.9 + A4.4 |
| D8 | executor.md L91-135 | Frontend Aesthetics Execution Rules 硬编码字体/颜色/动效/布局 | B1.* (改成读 ui-intent.md) |
| D9 | reviewer.md L34-36 | "Before doing any review work, write reviewer entry log" | A5.1 |
| D10 | reviewer.md L66-75 | TDD Waiver Rule — Reviewer Cannot Self-Authorize 叙述 | A6.12 + A6.11 |
| D11 | verifier.md L14-18 | "Before doing any verification work, write verifier entry log" | A5.1 |
| D12 | verifier.md L37-51 | Functional Verification Requirement 叙述 | A6.13 + A7.11 |
| D13 | stage-gate-enforcement.md L12-84 | Dual-Check Mechanism 所有"OR must receive inspector report before advance"叙述 | A11.1 + A11.3 (hook 自动写 trace + 自动 block spawn) |
| D14 | stage-gate-enforcement.md L88-110 | Agent Entry Log Requirement 全节 | A5.* |
| D15 | stage-model.md L111 | "orchestrator must keep stage state synchronized" | A1.3 |
| D16 | CLAUDE.md L12-17 | "不跳阶段，不绕过 review/verify, 设计和计划批准前不得执行，TDD is non-optional..." | A1.* + A2.* + A3.* + A6.* |
| D17 | framework/orchestrator.md L50-60 | "Must Not Do" 整段 (skip stages / replace verdict / hide blockers / ...) | A1.* + A3.* + A11.* + A12.* |
| D18 | framework/verification-and-fix.md L18-26 | TDD Core Contract 整段叙述 | A6.* |
| D19 | framework/orchestrator.md L303-340 | Status Update Rule 33 个字段列举叙述 | A7.18 |
| D20 | framework/orchestrator.md L353-367 | Inspector Trace Emission Rule 7 类事件叙述 (hook 自动 emit 后该叙述对 AI 已无指导价值) | A11.8 |
| D21 | framework/reviewer.md L29-34 | Blocker Rule "escalate immediately / do not wait" 叙述 | A4.10 |
| D22 | framework/inspector.md L93-98 | "Must Never" 四条 (interrupt workflow / downgrade reviewer / fabricate trace / ...) | A11.* + A18.3 |

**删除工作量**: 约 V4.5.0 agent.md / framework 的 30-40% 正文，**但产物质量提升**：读者知道哪些是 hook 强制的约束，哪些只是引导，不再混淆。

---

## Part E · Hook Checker 总表 (30 个)

| 类别 | Checker 文件 | 覆盖矩阵条目 | 触发事件 |
|------|-------------|-------------|---------|
| Validator (14) | `validator_project_definition.py` | A7.1 | PostToolUse(Edit/Write), Gate 1 |
| | `validator_solution_options.py` | A7.2 | PostToolUse, Gate 2 |
| | `validator_solution_landscape.py` | A7.3 | PostToolUse, Gate 2 |
| | `validator_design.py` | A7.4 | PostToolUse, Gate 2 |
| | `validator_ui_intent.py` | A7.5 | PostToolUse, Gate 2 |
| | `validator_feature_checklist.py` | A7.6, A2.4 | PostToolUse, Gate 2 |
| | `validator_plan.py` | A7.7, A6.11 | PostToolUse, Gate 3 |
| | `validator_execution.py` | A7.8, A4.4 | PostToolUse, Gate 4 |
| | `validator_polish.py` | A7.9 | PostToolUse, Gate 4 |
| | `validator_review.py` | A7.10, A6.12 | PostToolUse, Gate 5 |
| | `validator_verification.py` | A7.11 | PostToolUse, Gate 6 |
| | `validator_inspector_report.py` | A7.12, A7.19, A7.20 | Gate 7 / Stop |
| | `validator_finish.py` | A17.1, Gate 7 check 4 | Gate 7 / Stop |
| | `validator_retrospective.py` | A17.2, Gate 7 check 5 | Gate 7 / Stop |
| | `validator_current_run_json.py` | A7.15, A1.3 | PostToolUse Edit current-run.json |
| | `validator_activity_trace.py` | A7.16, A5.2, A11.2, A11.5 | PostToolUse Edit activity-trace.md |
| Gate (7) | `gate_agent_spawn.py` | A1.1, A2.1-3, A4.1-7, A11.1, A12.2 | PreToolUse(Agent) |
| | `gate_file_scope.py` | A9.*, B4.1 | PreToolUse(Edit/Write) |
| | `gate_freeze_locks.py` | A8.1-3, A2.5-6 | PreToolUse(Edit) |
| | `gate_tdd_redgreen.py` | A6.1-A6.9, A15.* | PreToolUse(Edit/Write) |
| | `gate_ui_contract.py` | B1.1-6 | PreToolUse(Edit/Write) |
| | `gate_commit_gate.py` | A10.* | PreToolUse(Bash) |
| | `gate_subjective_language.py` | A11.6 | PreToolUse(Edit/Write on review/verification/reports) |
| Observer (4) | `observer_test_runner.py` | A6.3-A6.6, B2.1 | PostToolUse(Bash) |
| | `observer_build_only.py` | A6.13 | PostToolUse(Bash) |
| | `observer_git_activity.py` | A10.3 | PostToolUse(Bash) |
| | `observer_feature_spotcheck.py` | V3 | PostToolUse(Bash during verify) |
| Post-Agent (3) | `post_agent_entry_log.py` | A5.1-2 | PostToolUse(Agent) |
| | `post_agent_trace_writer.py` | A11.1, A11.3, A12.1 | PostToolUse(Agent) |
| | `post_executor_chain.py` | A14.1-3 | PostToolUse(Agent=executor/polish) |
| Session (2) | `session_injection.py` | A13.1 | SessionStart |
| | `stop_finish_guard.py` | A11.4, Gate 7 | Stop |

---

## 矩阵自检脚本

**文件**: `hooks/matrix_selfcheck.py`

**职责**: 安装时 (install.ps1/install.sh 调用) + release 前 (CI) 跑：

1. 解析本矩阵，提取所有 Part A / B 条目和其声明的 Hook Checker 文件名
2. 对每个声明的 checker 文件：
   - 断言 `hooks/validators/<name>.py` / `hooks/gates/<name>.py` 等路径存在
   - 断言可 `import` 且暴露 `run()` 入口
3. 对 Part D 每条"建议删除"：
   - 读取源 .md 文件，grep 对应行号的原文摘要
   - 断言**已不存在**（已被 V4.6.0 精简掉）
4. 全部通过输出 `MATRIX OK`；任一失败输出具体失败项并 exit 1

**意义**: 保证规则与 hook 不可能脱钩。开发者改了 agent.md 加一条新"应当"但没加 hook，selfcheck 失败，release 被阻止。

---

## 变更日志 (本矩阵)

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-24 | draft-0 | 初稿。基于 V4.5.0 agents/ + framework/stage-gate-enforcement.md + framework/agent-behavior-registry.md 挖掘 107 条约束。Part A/B/C/D 分层结构确立。 |
| 2026-04-24 | final-draft | 补读 framework/frontend-aesthetics.md + verification-and-fix.md + role-contracts.md + framework/orchestrator.md + framework/reviewer.md + framework/inspector.md，新增 30 条到 137 条。新增 Terminology 节 (防 reviewer/inspector 混淆)。新增 A15.3 / A16 (Reviewer 8+1 Checklist) / A17 (Finish Acknowledgment) / A18 (跨角色写作纪律) 节；扩展 A4.8-10 / A6.14-15 / A7.17-20 / A11.7-9 / A12.3-4；新增 B5 (Design Thinking 4 Pillars) / B6 (UI Anti-Pattern 项目声明); 扩充 C19-29；新增 D17-22。 |
| 2026-04-24 | **final** | 采纳作者决策修正 3 项：(1) A7.19/A7.20 rolling artifacts 缺失改为**硬 block Gate 7** (放松会次次跳过)；(2) B6 节 UI anti-pattern 整个**不做 hook**（品味不应硬塞，交由 reviewer 人眼审查；B1.* 项目主动声明契约保留）；(3) **reviewer ↔ inspector 对调**修正反语义：现在 `reviewer`=审查者(质量门+BLOCK 权, 写 review.md) / `inspector`=监察者(行为监察+零中断, 写 .superteam/inspector/reports/*)。matrix 所有 validator 命名 / path 引用 / Terminology 全部翻转；agents/ + framework/ 两对文件名互换；内容全局替换 (41 文件)。 |

---

## Appendix · 已解决与仍待确认

### ✅ 已解决（原 draft-0 待补项全部补完）

- `framework/frontend-aesthetics.md` 已读 → B1 / B5 / B6 / C19-24
- `framework/verification-and-fix.md` 已读 → A6.14-15 / A12.3-4 / A15.3
- `framework/role-contracts.md` 已读 → A4.8-10 / A16 / C25-26 / C29
- `framework/orchestrator.md` 已读 → A7.17-18 / A11.7-9 / A17 / C25 / C27 / D17-22
- `framework/reviewer.md` 已读 → A4.10 / A16 (与 agents/reviewer.md 大量重复已去重)
- `framework/inspector.md` 已读 → A11.9 / A7.19-20 / C28 / D22

### 仍需作者拍板的设计决策

1. **A7.19/A7.20 (inspector 的 health.json / insights.md / improvement-backlog.md)** 缺失是否要 block Gate 7？当前设计是 **discrepancy 不 block**，因为这些是 rolling long-term artifacts，单次 run 缺失不致命。同意否？
2. **A18.1 禁用主观词清单** 当前是 `appears / seems / probably / should / looks fine`，是否要扩展？（如 "might" / "could be" / "perhaps"）或缩小（"should" 在一些语境如 "test suite should pass" 是正确用法）？建议保持当前 5 词，被 quoted backtick 引用时豁免。
3. **B6.1 AP-01..AP-05 默认状态**：V4.6.0 默认 `hooks/config/antipattern-defaults.json` 提供什么 baseline？两种选项：
   - 选项 A: baseline 空，每个项目自己声明禁用 pattern（最自由，对新项目最宽松，但容易疏忽）
   - 选项 B: baseline 继承 V4.5.0 的 AP-01..AP-05 (禁 Inter/Roboto/purple gradient 等)，项目可显式 override（默认严厉，需要主动豁免）
   - **推荐选项 B**，因为项目品味默认倾向保守而非激进。需作者确认。
4. **C8 "call out plan drift explicitly"** 和 C13 "solution-options.md has no rejected alternatives" 的判断：前者纯语义，后者可部分 hook (checker 验"rejected alternatives" 节存在 + 有内容)。C13 可升级为 A 类，需作者确认。

### 不在本矩阵范围（显式边界）

- `skills/*/SKILL.md` 流程引导文本不登记矩阵（其约束力全部追溯到 agent.md / framework）
- `docs/` 目录文档（改动不影响 enforcement）
- `plan/` 目录（SuperTeam 自身开发文档，不影响用户运行时）
