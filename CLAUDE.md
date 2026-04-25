# SuperTeam V4.7.4

## 定位

SuperTeam 是面向 Claude Code 的七阶段交付插件。

## V4.7 架构（重要）

**Orchestrator 角色已从 subagent 迁移到主会话。** Claude Code runtime 物理上禁止 subagent 调 `Agent` 工具 spawn 下级 subagent，pre-V4.7 的 OR subagent 因此无法真正 delegate，只能自代 reviewer/verifier/writer，七阶段流程在物理层面是失效的。

V4.7 起：

- 主会话读 `.superteam/state/mode.json` 自检身份（`mode=active` 即担任 OR）
- 主会话直接用 `Agent` 工具 spawn 各 specialist · 每次 spawn 由 PostToolUse hook 自动写入 `.superteam/runs/<slug>/spawn-log.jsonl`
- 主会话直接 Edit/Write 实质工作文件（代码 / review.md / verify.md / polish.md 等）会被 `gate_main_session_scope.py` 物理 block — 必须 spawn specialist
- 进入 / 退出 OR 模式只有两条合法路径：用户 `/superteam:go` 进、用户 `/superteam:end` 或 finish 阶段用户确认退

详见当前版本目录下的 `framework/main-session-orchestrator.md`。`agents/orchestrator.md` subagent 已 DEPRECATED · 仅为 V4.6 兼容保留。

V4.7.1 是 V4.7.0 的收口修复（active-subagent 仅 superteam:* / corrupt mode.json 显式告警 / 补 `/superteam:bypass` skill / 同步根目录元数据）。

V4.7.2 加两件事：(1) **Stop hook 拦截 OR 自停** — `mode=active` + `current_stage∈{execute,review,verify,finish}` + 本轮无 spawn → block stop + 强制 OR 推进，关闭 V4.7.0/V4.7.1 在对话流层的覆盖盲区；(2) **specialist MCP 工具白名单** — designer/architect/executor/verifier/reviewer/researcher/debugger/test-engineer 加上 pencil/chrome-devtools/playwright/context7/gpt-researcher 白名单，让 specialist 真能用上 MCP server。

V4.7.3 把 PLAN Tier A 三件套补完：(1) **gate_stage_advance** 拦 `.superteam/state/current-run.json` 的违规推进 — execute→review 必须先有 executor spawn + execution.md，review→verify 必须先有 reviewer spawn + review.md，verify→finish 必须先有 verifier spawn + verification.md 且 verdict=PASS；(2) **validator_frontmatter** 校验所有 specialist 产物头部 frontmatter — 缺失则用 active-subagent.json 自动补，伪造（agent_id 不在 spawn-log）则写 gate-violations.jsonl 审计。"理性化绕过"剩余三条路径（自停/跳阶段/伪造产物）全部 hook 化。

V4.7.4 把 PLAN Tier B 收完：(B1+C2) reviewer/verifier/writer/planner/architect/executor 6 个 specialist 加 **Output Discipline** 节，约束输出形式（reviewer 必须 file:line 引用 + 命令输出 / verifier 必须 verdict 三选一 + 配对证据 / writer 七节 final.md 结构 / planner MUST 项原子化 + 类别前缀 等）；(B2) Stop-hook **escalation 诊断** — 60s 内 ≥3 次 gate block 触发 systemMessage 提示用户三个出口；(B3-B5) 三个新 skill `/superteam:debug` `/superteam:repair` `/superteam:doctor` 用于排查 hook 误判 / 修复 mode.json corrupt / 综合健康检查。剩 Tier C1（端到端 pytest 信任链测试套件）是工程基础设施投入，不是 bug。

## 核心原则

V4.6.0 起，规则由 `hooks/` 物理强制，违反即 block（不是警告）。完整约束清单见当前版本目录下的 `framework/hook-enforcement-matrix.md`。

- 七阶段顺序强制执行：`clarify -> design -> plan -> execute -> review -> verify -> finish`
- 设计和计划批准前不得执行；G1 / G2 / G3 三个用户结界点必须用户明确批准
- TDD 红绿灯物理闭环：没有 failing test 不能写生产代码 (`gate_tdd_redgreen.py` 状态机)
- verifier verdict ≠ PASS 不能 git commit (`gate_commit_gate.py`)
- G2 关闭后 `feature-checklist.md` 冻结，G3 关闭后 `plan.md` MUST 项冻结
- inspector（监察者）全程介入 trace · `reviewer`（审查者）owns review 阶段质量门（V4.6.0 reviewer/inspector 语义对调）
- V4.7 起 OR 角色由主会话承担，hook 通过 mode.json + gate_main_session_scope 强制信任链

AI 思维引导原则（无 hook 背书）：

- 用户边界中文优先，执行内核英文优先
- 前端美学质量遵守项目声明的 `ui-intent.md` 契约
- 第一性原则：回到问题本质，区分真实约束与历史惯性，优先解决根因而非绕行
- V4 只保留 plugin 安装方式

## 核心命令

- `/superteam:go [task]`：进入 OR 模式 · 写 mode.json · 引导 clarify
- `/superteam:end`：退出 OR 模式（V4.7 新增）
- `/superteam:status`：看 mode + 七阶段状态 + 最近 spawn + violations
- `/superteam:bypass <reason>`：一次性放行下次违规写（hook 误判时用，V4.7.1 补齐）
- `/superteam:g1` / `/superteam:g2` / `/superteam:g3`：补结界点

## 安装

GitHub marketplace 安装：

```
/plugin marketplace add frankiezheng110/superteam
/plugin install superteam@superteam
/reload-plugins
```

升级：

```
/plugin marketplace update superteam
/plugin update superteam
/reload-plugins
```

当前插件源（marketplace.json `plugins[0].source`）：`./V4.7.4_TierB收口`。

## 运行时产物

```
.superteam/
  state/
    mode.json                 # V4.7 主会话身份开关
    current-run.json          # 七阶段运行状态
    gate-violations.jsonl     # PreToolUse 拦截记录
    bypass-log.jsonl          # /superteam:bypass 审计
    active-subagent.json      # transient · subagent 运行窗口
    feature-tdd-state.json
    *-freeze.lock.json
  runs/<task-slug>/
    project-definition.md, activity-trace.md, solution-options.md,
    solution-landscape.md, design.md, plan.md, execution.md,
    polish.md, review.md, verification.md, finish.md, retrospective.md,
    spawn-log.jsonl           # V4.7 主会话 spawn 审计
    handoffs/01..06-*.md
  inspector/
    traces/<slug>.jsonl
    reports/<slug>-report.{md,html}
    insights.md, health.json, improvement-backlog.md
```

## 立项三阶段

- `clarify / Project Definition`：用户关闭 `G1`
- `design / Development Solutions`：先跑方案循环 · 用户关闭 `G2` 后进入定形
- `plan / Execution Plan`：用户关闭 `G3` 后进入执行

`plan` 审核通过后 · 后续 `execute -> review -> verify -> finish` 默认不再需要用户介入，除非用户主动补充新方向或新约束。

如果用户后续补充了重要新信息，默认重开对应结界点（supplement，不是 rollback）。

## 角色

- 6 核心：orchestrator（V4.7 起由主会话承担）、planner、architect、executor、reviewer、verifier
- 11 支持：analyst、researcher、prd-writer、test-engineer、debugger、designer、writer、inspector、simplifier、doc-polisher、release-curator

## 质量链

`executor -> polish layer (simplifier/doc-polisher/release-curator) -> reviewer -> verifier -> inspector`
