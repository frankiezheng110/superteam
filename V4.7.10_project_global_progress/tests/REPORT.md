# SuperTeam V4.6.0 · Hook 端到端测试报告

**测试时间**: 2026-04-26 15:37:33 UTC
**测试方式**: 轻量模拟 — 不调用真实 Claude，直接对每个 dispatch 入口脚本发送 Claude 协议 JSON，断言 stdout 决策与 hook 内部状态变化

## 总结

| 指标 | 值 |
|------|-----|
| 运行用例 | 45 |
| ✅ 通过 | 45 |
| ❌ 失败 | 0 |
| 状态 | ✅ **全部通过** |

## 分类覆盖

| 分类 | 测试数 | 通过 |
|------|-------|-----|
| A10 | 4 | 4/4 |
| A11 | 3 | 3/3 |
| A14 | 1 | 1/1 |
| A17 | 2 | 2/2 |
| A18 | 2 | 2/2 |
| A4 | 3 | 3/3 |
| A5 | 15 | 15/15 |
| A6 | 6 | 6/6 |
| A7 | 2 | 2/2 |
| A9 | 2 | 2/2 |
| B1 | 3 | 3/3 |
| H1 | 1 | 1/1 |
| SC | 1 | 1/1 |

## 用例详情

### A10

#### ✅ `A10.1-commit-no-verify` · 缺 verification → commit 被拦

- **验证点**: A10.1 commit gate
- **期望行为**: verification.md 缺失 → block commit
- **实际行为**: blocked=True, reason=verification.md 不存在 — 必须先 verify PASS 才能 git commit/tag/push (A10.1)

#### ✅ `A10.1-commit-fail` · verdict=FAIL → commit 被拦

- **验证点**: A10.1 commit gate
- **期望行为**: verdict=FAIL → block commit
- **实际行为**: blocked=True, reason=verification.md verdict=FAIL — 必须先达成 PASS 才能 git commit (A10.1). 紧急情况可 ALLOW_UNVERIFIED_COMMIT=1 显式覆盖 (留痕)

#### ✅ `A10.1-commit-pass` · 所有条件齐全 → allow commit

- **验证点**: A10.1 commit gate
- **期望行为**: verdict=PASS + review=CLEAR + checkpoint 齐全 → allow commit
- **实际行为**: blocked=False, reason=

#### ✅ `A10.4-commit-override` · 显式 env 覆盖

- **验证点**: A10.4 override
- **期望行为**: ALLOW_UNVERIFIED_COMMIT=1 → allow (留痕)
- **实际行为**: blocked=False

### A11

#### ✅ `A11.4-stop-no-report` · Stop 硬闸要求 reviewer/inspector report

- **验证点**: A11.4 / Gate 7
- **期望行为**: finish 无 inspector report → block Stop
- **实际行为**: blocked=True, reason=不允许 Stop: current_stage=finish 但 inspector 报告 C:\Users\frankie\AppData\Local\Temp\st_test_ty7qfpsp\.superteam\inspector\

#### ✅ `A11.4-stop-ok` · 完整 Gate 7 产物允许 Stop

- **验证点**: A11.4 / Gate 7 happy
- **期望行为**: 所有 Gate 7 产物齐全 → allow Stop
- **实际行为**: blocked=False, reason=

#### ✅ `A11.3-trace-auto` · Inspector trace 由 hook 自动写

- **验证点**: A11.3/A11.8
- **期望行为**: hook 自动写 agent_spawn + agent_stop 到 inspector trace
- **实际行为**: spawn=True, stop=True, events=6

### A14

#### ✅ `A14.1-chain-hint` · executor 结束引导 polish 链

- **验证点**: A14.1 polish chain
- **期望行为**: executor 结束 → 引导 spawn simplifier/polish
- **实际行为**: msg=Next action (G4, no user confirmation needed): spawn superteam:simplifier for code-polish (also doc-polisher if docs cha

### A17

#### ✅ `A17.1-finish-no-ack` · finish.md 空壳不 acknowledge → block

- **验证点**: A17.1 finish acknowledge
- **期望行为**: finish.md 无 acknowledgment → block Stop
- **实际行为**: blocked=True, reason=不允许 Stop: finish.md 不合格 — finish.md 缺 `reviewer_report_acknowledged: true` (或 `inspector_report_acknowledged: true` / `已确认监察报告`) 标记 — Gate 7 check 4 (

#### ✅ `Gate7-retro-blank` · retrospective 空白 improvement_action → block

- **验证点**: Gate 7 check 5
- **期望行为**: retrospective improvement_action 为 TBD → block Stop
- **实际行为**: blocked=True, reason=不允许 Stop: retrospective.md 不合格 — retrospective.md improvement_action 值为空/待定 ('tbd') — Gate 7 要求显式非空 (Gate 7 check 5 / A17.2)

### A18

#### ✅ `A18.1-subjective` · review.md 主观词拦截

- **验证点**: A18.1 subjective language
- **期望行为**: review.md 含 probably/looks fine → block
- **实际行为**: blocked=True, reason=检测到主观词 probably, looks fine 出现在 review.md. review/verification/inspector report 禁止主观证据语言 (A18.1). 改写为具体证据引用 (file:line /

#### ✅ `A18.1-backtick-exempt` · backtick 引用豁免

- **验证点**: A18.1 exempt
- **期望行为**: `should pass` backtick 引用 → allow
- **实际行为**: blocked=False, reason=

### A4

#### ✅ `A4.1-stage-legality` · Agent 跨阶段 spawn 被拦

- **验证点**: A4.1/A4.9 agent stage legality
- **期望行为**: 在 clarify 阶段 spawn executor → block
- **实际行为**: blocked=True, reason=superteam:executor 仅允许在 ['execute'] 阶段 spawn，当前 stage=clarify

#### ✅ `A4.1-stage-ok` · 合法 stage 下 allow executor

- **验证点**: A4.1
- **期望行为**: stage=execute + Gate 3 + A5.3 decision → allow executor
- **实际行为**: blocked=False, reason=

#### ✅ `A4.3-repair-cap` · repair 循环上限触发升级

- **验证点**: A4.3 repair cap
- **期望行为**: repair_cycle_count=3 → block executor spawn
- **实际行为**: blocked=True, reason=repair_cycle_count >= 3 — 必须升级用户 (re-plan / reduce scope / terminate)

### A5

#### ✅ `A5.1-entry-missing` · Entry Log 缺失被捕获

- **验证点**: A5.1 entry log required
- **期望行为**: executor 未写 Entry Log → discrepancy
- **实际行为**: ok=False, errs=['superteam:executor 未在 activity-trace.md 写入场记录 (期望 Gate 3) — A5.1']

#### ✅ `A5.2a-entry-fake-path` · 假路径说明未真读文件

- **验证点**: A5.2a path reality check
- **期望行为**: Entry Log 写假路径 → block (anti-hallucination)
- **实际行为**: ok=False, errs=['superteam:executor Entry Log 写的 `plan.md` 路径 `/nonexistent/fake/plan.md` 在磁盘不存在 ', 'superteam:executor Entry Log 写的 `feature-checklist.md` 路径 `/also/fake/fc.md` 在磁盘']

#### ✅ `A5.2b-entry-must-mismatch` · MUST 清单不一致说明凭印象做事

- **验证点**: A5.2b MUST reconciliation
- **期望行为**: MUST 清单与 plan.md 不一致 → block
- **实际行为**: ok=False, errs=['superteam:executor Entry Log MUST 清单遗漏 2 项 (首项: 用户点击按钮后看到欢迎信息) — 与 plan.md 不一致', 'superteam:executor Entry Log MUST 清单多出 1 项 (首项: 一个和 plan.md 不匹配的项目) — 与 plan.md ']

#### ✅ `A5.2-entry-complete` · 完整 Entry Log 通过

- **验证点**: A5.2 happy path
- **期望行为**: 完整 Entry Log + 正确路径 + MUST 对账 → pass
- **实际行为**: ok=True, errs=[]

#### ✅ `A5.3-decision-missing` · 缺 OR decision log → block

- **验证点**: A5.3 orchestrator decision log
- **期望行为**: 缺 Orchestrator Decision → block spawn executor
- **实际行为**: blocked=True, reason=缺 Orchestrator Decision 段 — spawn superteam:executor 前必须在 activity-trace.md 写 `## Orchestrator Decision — <Unit>` 段 (含 U

#### ✅ `A5.3-decision-unknown` · OR 瞎创造 unit → block

- **验证点**: A5.3 unit must come from plan
- **期望行为**: Decision 的 Unit id 不在 plan → block
- **实际行为**: blocked=True, reason=Orchestrator Decision Unit id=`C99` 不在 plan.md / feature-checklist.md 已知清单 (已知前 5 项: ['C00', 'C01', 'C02', 'T1.A']) — OR 凭印象创造了清单外的 unit (A5.3)

#### ✅ `A5.3-decision-valid` · 合法 OR decision → allow

- **验证点**: A5.3 happy path
- **期望行为**: 合法 Decision + Entry Log → allow
- **实际行为**: blocked=False, reason=

#### ✅ `A5.4-parse-multi` · 多类 MUST 解析

- **验证点**: A5.4 multi-category parsing
- **期望行为**: 多类 MUST 正确解析为 5 项 3 类
- **实际行为**: items=5, cats=['功能', 'API endpoint', 'Migration']

#### ✅ `A5.4-exec-missing-id` · execution 漏某类 MUST → 发现

- **验证点**: A5.4 execution ID reconciliation
- **期望行为**: execution.md 缺 F-002/API-matrix section → discrepancy
- **实际行为**: ok=False, errs=['execution.md 仅 1 个 feature section, feature-checklist 有 2 项 (有功能被静默跳过)', 'Execution Summary 未声明 tdd_exception (YES/NO)', 'MUST [F-002] (功能) 在 execution.md 无对应 section — 该交付项未被处理 (A5.4)']

#### ✅ `A5.4-plan-no-id` · plan MUST 全自由文本且与 fc 无关 → 报错

- **验证点**: A5.4 plan ID requirement
- **期望行为**: 全部自由文本 MUST + 与 fc 无关 → validator_plan 报错
- **实际行为**: ok=False, err_count=5

#### ✅ `A5.5-init` · plan-progress 初始化

- **验证点**: A5.5 G3 close init
- **期望行为**: G3 关闭后 plan-progress 正确初始化
- **实际行为**: items=['F-001', 'F-002', 'API-1']

#### ✅ `A5.5-block-complete` · progress=COMPLETE 的 Unit 不可重 spawn

- **验证点**: A5.5 resumption guard
- **期望行为**: OR 尝试重做 COMPLETE 的 F-001 → block
- **实际行为**: blocked=True, reason=Orchestrator Decision Unit id=`F-001` 在 plan-progress.json 状态=COMPLETE，不可再 spawn superteam:executor (A5.5 · 中断恢复保护) · 如需重做，先 mark DEFERRED→PENDING 或 r

#### ✅ `A5.5-session-injection` · 中断恢复 session 注入剩余清单

- **验证点**: A5.5 SessionStart inject
- **期望行为**: SessionStart 注入含 PENDING + COMPLETE 摘要
- **实际行为**: context[:200]=SuperTeam 运行状态: current_stage=execute, status=active, repair_cycle=0 ·  · Plan Progress (3 items, plan_sha=7f78b90d) ·   PENDING (2): ·     - [F-002] : 密码错误显示提示 ·     - [API-1] : GET /api/x ·   COMPLETE (1): ·     

#### ✅ `A5.5-auto-mark` · Observer 自动更新 progress

- **验证点**: A5.5 green auto-mark
- **期望行为**: feature GREEN → plan-progress 自动 mark COMPLETE
- **实际行为**: F-001 status=COMPLETE

#### ✅ `A5.7-resume-directive` · G4-G7 自动化 resume 指令

- **验证点**: A5.7 auto-resume per stage
- **期望行为**: G4-G7 resume directive 每阶段明确下一步 + 不需用户确认
- **实际行为**: missing=[]

### A6

#### ✅ `A6.1-tdd-pending` · TDD PENDING 禁写生产代码

- **验证点**: A6.1/A6.2 TDD red first
- **期望行为**: PENDING 状态编辑 src/ → block 要求先 failing test
- **实际行为**: blocked=True, reason=Feature F-001 state=PENDING — 必须先写 failing test 并跑出 RED 证据 才能编辑生产代码 src/foo.py. (A6.1/A6.2 violation)

#### ✅ `A6.5-tdd-red-green` · TDD RED_LOCKED 放行生产代码

- **验证点**: A6.5 green phase
- **期望行为**: RED_LOCKED 状态编辑 src/ → allow
- **实际行为**: blocked=False

#### ✅ `A6.1-test-path` · 编辑测试路径不触发 TDD 拦

- **验证点**: A6.1 test path exempt
- **期望行为**: PENDING 编辑 tests/ → allow (测试文件)
- **实际行为**: blocked=False

#### ✅ `A6.3-tdd-observer-red` · Observer 解析 FAILED 转 RED_LOCKED

- **验证点**: A6.3 observer_test_runner
- **期望行为**: pytest FAILED → state 转 RED_LOCKED
- **实际行为**: state=RED_LOCKED

#### ✅ `A6.6-tdd-observer-green` · Observer 解析全 PASS 转 GREEN_CONFIRMED

- **验证点**: A6.6 observer_test_runner
- **期望行为**: pytest 全 pass → state 转 GREEN_CONFIRMED
- **实际行为**: state=GREEN_CONFIRMED

#### ✅ `A6.8-tdd-init-from-exec` · V4.6.4 PostToolUse 自动 init active_feature_id

- **验证点**: A6.8 V4.6.4 init deadlock fix
- **期望行为**: Edit execution.md → active_feature_id=welcome-banner, state=PENDING
- **实际行为**: fid='welcome-banner', state='PENDING'

### A7

#### ✅ `A7.20-rolling-missing` · rolling artifact 未更新 → block (决策 1)

- **验证点**: A7.20 rolling artifacts
- **期望行为**: insights.md 缺失 → block Stop (A7.20)
- **实际行为**: blocked=True, reason=不允许 Stop: insights/improvement-backlog 未更新 — insights.md 缺失 (A7.20)

#### ✅ `A7.8-execution-validator` · execution.md 自动校验发现缺 RED

- **验证点**: A7.8 / B-EX-2
- **期望行为**: execution.md COMPLETE 缺 RED → 写 discrepancy
- **实际行为**: discrepancy 记录=True

### A9

#### ✅ `A9.1-file-scope-clarify` · 文件阶段权限拦截

- **验证点**: A9.1 file stage scope
- **期望行为**: clarify 阶段写 plan.md → block
- **实际行为**: blocked=True, reason=当前 stage=clarify 禁止写入 plan.md (允许的文件: ['activity-trace.md', 'project-definition.md']) — A9 violation

#### ✅ `A9.4-file-scope-execute` · execute 阶段可写生产代码

- **验证点**: A9.4
- **期望行为**: execute 阶段 RED_LOCKED 下写 src/ → allow
- **实际行为**: blocked=False

### B1

#### ✅ `B1.1-ui-inactive` · 项目未声明契约时 hook 不干预

- **验证点**: B1.1 inactive default
- **期望行为**: ui-intent.md 未声明 → hook 不激活 (决策 2 核心)
- **实际行为**: blocked=False

#### ✅ `B1.1-ui-violation` · 违反项目声明字体契约 → block

- **验证点**: B1.1 typography contract
- **期望行为**: 字体不在 ui-intent 白名单 → block
- **实际行为**: blocked=True, reason=字体 'comic sans ms' 不在项目 ui-intent.md § Typography Contract 声明的白名单内。要使用此字体，请先更新 ui-intent.md (B1.1)

#### ✅ `B1.1-ui-allow` · 符合项目字体契约 → allow

- **验证点**: B1.1 typography contract
- **期望行为**: 使用 ui-intent 声明的字体 → allow
- **实际行为**: blocked=False

### H1

#### ✅ `H1-session-injection` · SessionStart 注入上轮运行摘要

- **验证点**: A13.1 / H1
- **期望行为**: SessionStart 注入 current-run 摘要
- **实际行为**: SuperTeam 运行状态: current_stage=execute, status=active, repair_cycle=0 ·  · Resume 指令 (G4 自动化阶段): 下一 PENDING Unit = [(no PENDING)]. 直接写 `## Orchestrator Decision — (no PENDING)` 到 activity-trace.md, 然后 spaw

### SC

#### ✅ `SC-matrix-ok` · Matrix self-check

- **验证点**: Matrix sync
- **期望行为**: matrix_selfcheck 30 个 checker 全找到且可 import
- **实际行为**: MATRIX OK · 34 checkers resolved and importable

## 🎉 无失败项

所有硬约束在模拟环境中表现正确。可进入 Phase 2：GitHub 发布。

## 建议

- 模拟层面的硬约束均按设计生效
- 建议用一个小的真实项目试跑一次（`/superteam:go` + 简单需求）再正式发版
- GitHub 发布前确认 `.claude-plugin/marketplace.json` 源路径与 GitHub 仓库一致
