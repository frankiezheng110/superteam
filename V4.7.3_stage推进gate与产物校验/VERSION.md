# SuperTeam V4.7.3 — PLAN Tier A 收口 · stage 推进 gate + 产物 frontmatter 校验

**发布日期**: 2026-04-25
**前置版本**: V4.7.2_Stop_hook与MCP工具白名单
**类型**: Patch（PLAN Tier A 三件套最后两件）

## V4.7.3 修复

把 PLAN-V4.7.0 第十一节 P1 的 Tier A 三件套补完。V4.7.2 已经实现 Tier A1（Stop hook 拦自停），V4.7.3 实现剩下两件：

### A2 · gate_stage_advance — 拦 current-run.json 违规推进

`hooks/gates/gate_stage_advance.py` 拦截 PreToolUse Edit/Write/MultiEdit `.superteam/state/current-run.json`：

- diff 出 `current_stage` 字段从 X 变为 Y
- 校验 Y 的进入条件（spawn-log + 产物 + verdict）
- 不满足 → block + 提示需要 spawn 哪个 specialist + 提供 `/superteam:bypass` 出口

| 推进 | 准入条件 |
|---|---|
| execute → review | spawn-log 含 `superteam:executor` + `execution.md` 存在 |
| review → verify | spawn-log 含 `superteam:reviewer` + `review.md` 存在 |
| verify → finish | spawn-log 含 `superteam:verifier` + `verification.md` 存在 + 含 `verdict: PASS` |

只覆盖 G3 关闭后的执行链（review/verify/finish）— design/plan/execute 进入仍由 V4.6 既有 G1/G2/G3 用户审批门处理。

副作用：V4.6 既有的 `gate_file_scope.py` 第 62 行硬拦 `.superteam/state/` 任何写入。V4.7.3 让 OR 模式下主会话能写 `current-run.json`（其他 state/* 文件继续拦），把 stage 推进的合法性校验交给 `gate_stage_advance` 处理。

### A3 · validator_frontmatter — 校验 specialist 产物来源

`hooks/validators/validator_frontmatter.py` 在 PostToolUse Edit/Write 后校验受监控的 specialist 产物：

| 文件 | 期望 agent_type |
|---|---|
| review.md | reviewer |
| verify.md / verification.md | verifier |
| polish.md | simplifier / doc-polisher / release-curator |
| final.md / finish.md | writer |
| retrospective.md | writer / inspector |
| execution.md | executor |
| test-plan.md | test-engineer / planner |

校验内容：
1. 文件头部必须含 YAML frontmatter，包含 `agent_type` / `agent_id` / `task_slug`
2. `agent_id` 必须能在 `spawn-log.jsonl` 找到
3. `agent_type` 必须与文件类型匹配
4. `task_slug` 必须与当前 active run 一致

行为分两层：

- **缺 frontmatter**：用 `active-subagent.json` 推断当前 specialist + 从 spawn-log 找最近一条匹配的 `agent_id`，**自动补**到文件头。不破坏 specialist 内容（方案 C — 优先保住工作而非删文件）。
- **frontmatter 伪造**（agent_id 不在 spawn-log / agent_type 不匹配 / slug 不一致）：写 `gate-violations.jsonl` 审计记录。**V4.7.3 不删文件** — 检测即足以让 finish 阶段审计 + `/superteam:status` 暴露问题。删文件作为后续 strict-mode opt-in 留给 V4.8。

### 9 个 specialist 加 frontmatter 输出指南

reviewer / verifier / writer / executor / simplifier / doc-polisher / release-curator / test-engineer / inspector 的 `agents/<role>.md` 末尾追加 "Output Frontmatter (V4.7.3 trust-chain requirement)" 节，让 specialist 主动写 frontmatter（避免依赖 hook 自动补）。

## V4.7 PLAN Tier A 完整状态

| 项 | 版本 | 状态 |
|---|---|---|
| A1 · Stop hook 拦自停 | V4.7.2 | ✓ |
| A2 · stage 推进 gate | V4.7.3 | ✓ |
| A3 · 产物 frontmatter 校验 | V4.7.3 | ✓ |

"理性化绕过"的三条剩余路径——**自停 / 跳阶段 / 伪造产物**——全部 hook 化。AI 自律边界压缩到只剩 Tier D（语义判断、用户决策），那才是 AI 该做主观判断的地方。

## 不变的部分

- V4.6 + V4.7.0/.1/.2 的所有 hook、gate、validator、observer 全部保留
- 七阶段决策规则（framework/orchestrator.md）不变
- specialist tools MCP 白名单（V4.7.2）不变
- mode.json 状态机（V4.7.0）/ corrupt 检测（V4.7.1）不变

## 后续

PLAN 第十一节 P2 / Tier B/C 留给 V4.8+：
- Reviewer prompt 硬模板（必须引用文件+行号+命令输出）
- Block escalation 阈值机制
- `/superteam:debug` / `/superteam:repair` / `/superteam:doctor`
- 完整信任链测试套件
- frontmatter 伪造的 strict-mode（删文件，作为 opt-in）

---

# SuperTeam V4.7.2 — Stop hook 拦截 OR 自停 · specialist MCP 工具白名单

**发布日期**: 2026-04-25
**前置版本**: V4.7.1_主会话OR收口修复
**类型**: Patch（V4.7 对话流层硬约束 + 工具集补齐）

## V4.7.2 修复

### 1. Stop hook 拦截主会话 OR 自停（PLAN Tier A1）

V4.7.0/V4.7.1 的 4 层防线（SessionStart banner / UserPromptSubmit banner / PreToolUse 文件拦截 / spawn-log）都在**工具/事件**层 — 主会话"输出文本就结束响应"不触发任何 hook，因此可以理性化绕过流程。

V4.7.2 在 `hooks/dispatch/stop.py` 加 OR 自停 guard：

| 条件 | 行为 |
|---|---|
| `mode=active` + `current_stage ∈ {execute, review, verify, finish}` + 本轮无 spawn + 无 active subagent + 无 blocker_summary | **block stop** + 注入"必须 spawn specialist 推进任务" |
| `stop_hook_active=true`（前一次已被 block） | 放行（避免无限循环） |
| `current_stage ∈ {clarify, design, plan}` | 放行（这些阶段对话流是合法的，等用户审批） |
| `mode != active` | 放行（普通会话） |

实现细节：
- `hooks/lib/mode_state.py` 加 `begin_turn()` / `current_turn_id()` / `last_spawn_turn_id()` / `spawned_in_current_turn()`
- `hooks/dispatch/user_prompt.py` 在 OR 模式下每条用户消息生成新 `turn_id`，写入 `.superteam/state/turn.json`
- `append_spawn_log` 在每条 spawn 记录里追加 `turn_id` 字段
- Stop hook 比较 `last_spawn_turn_id() == current_turn_id()` 判断本轮是否有 spawn

### 2. specialist 工具集加 MCP 白名单（用户痛点 #2）

V4.7.0/V4.7.1 的 specialist `tools` frontmatter 都是基础工具（Read/Write/Edit/Bash/Grep/Glob），**不含 MCP 工具**。Claude Code subagent 的 tools 字段一旦显式列出就会限制成只能用列出的，因此 specialist 实际拿不到 MCP，主会话只能自己用 MCP（再被 gate_main_session_scope 拦着不能写 UI 文件 → 死锁）。

V4.7.2 给 8 个 specialist 加 MCP 工具白名单（通配符）：

| Specialist | 新增 MCP |
|---|---|
| designer | pencil + chrome-devtools + playwright |
| architect | context7 + WebFetch + WebSearch |
| executor | pencil + chrome-devtools + playwright + context7 |
| verifier | chrome-devtools + playwright |
| reviewer | chrome-devtools + playwright |
| researcher | context7 + gpt-researcher + WebFetch + WebSearch |
| debugger | chrome-devtools + playwright |
| test-engineer | playwright + chrome-devtools |

不变的 specialist（不需要 MCP）：analyst / planner / prd-writer / writer / doc-polisher / release-curator / simplifier / inspector。

**注意 MCP server 命名**：通配符按当前广泛使用的 server 名（`mcp__pencil__*` / `mcp__chrome-devtools-mcp__*` / `mcp__plugin_playwright_playwright__*` / `mcp__context7__*` / `mcp__gpt-researcher__*`）。若用户安装的 MCP server 命名不同（比如 `mcp__chrome_devtools__*` 没连字符），通配符不匹配，等于 specialist 没拿到 MCP — fallback 到只能用基础工具。用户可在自己的 plugin 副本里调整 frontmatter 替换为实际 server 名。

## 不变的部分

- V4.6.4 / V4.7.0 / V4.7.1 的所有 hook、gate、validator、observer 全部保留
- Stop hook 既有的 Gate 7 (stop_finish_guard) 检查继续运行 — 在 OR 自停 guard 之前
- 七阶段决策规则（framework/orchestrator.md）不变

## 与 PLAN Tier A 的关系

PLAN-V4.7.0 第十一节 P1 列了三件套：
1. ✅ Stop hook 拦自停 — 本版本完成
2. ⏳ stage 推进 gate — 留待 V4.7.3
3. ⏳ 产物 frontmatter 校验 — 留待 V4.7.3

V4.7.2 选择 Tier A1 + MCP 白名单一起做，因为这两件事都直接影响当前 SMS 接力可用性（自停拦截避免接力中断；MCP 白名单让 designer/executor 能用 pencil 完成 UI 任务）。

---

# SuperTeam V4.7.1 — V4.7 主会话即 OR · 收口修复

**发布日期**: 2026-04-25
**前置版本**: V4.7.0_主会话即OR_信任链重建
**类型**: Hotfix（V4.7.0 自身的四项收口修复）

## V4.7.1 修复（一句话清单）

1. **active-subagent 窗口收紧**：`pre_tool.py` 改为只有 `agent.startswith("superteam:")` 才打开 active-subagent flag。V4.7.0 是任意非空 agent 都打开 — 主会话调用 general-purpose / Explore 等非 SuperTeam subagent 期间，主会话自身的 Edit/Write 会被错误放行。
2. **`/superteam:bypass` skill 补齐**：V4.7.0 在 `framework/main-session-orchestrator.md` 第 2.3 节和 `gate_main_session_scope.py` 错误信息里都引用了它，但漏建 SKILL.md。CLI (`mode_cli.py bypass`) 已经支持，本版本只是把 skill 文件补上。
3. **坏 mode.json 不再静默退化**：`mode_state.py` 新增 `mode_health()` 返回 `missing | corrupt | unknown_schema | active | ended`。`session_injection` 和 `user_prompt` 在 corrupt/unknown_schema 时输出**显式警告**而不是静默假装"非 OR 项目"。`mode_cli.py status` 同步加 `health` 字段。
4. **GitHub 根目录元数据同步到 V4.7**：根 `CLAUDE.md`、`README.md`、`VERSION.md` 此前还停留在 V4.5.0/V4.6.0，与新 V4.7 目录不一致；本版本更新顶部段落与版本号字段（直接 git clone 安装路径不再读到老内容）。

## 为什么是 V4.7.1 而不是补丁 V4.7.0

V4.7.0 已经 push 到 GitHub main 并被用户通过 marketplace 装到本地，按版本管理铁律"旧版本不动"，V4.7.0 留作含上述缺陷的初版历史。

---

# SuperTeam V4.7.0 — 主会话即 Orchestrator · 信任链重建

**发布日期**: 2026-04-25
**前置版本**: V4.6.4_tdd初始化修复
**类型**: 架构层（不是功能增量 · 主版本号 +1 因 OR 角色物理迁移）

## 一句话

把 Orchestrator 角色从 subagent 搬到主会话 · 用 hook + 磁盘状态机硬执行信任链 · 不再依赖 AI 自律。

## 触发原因

V4.6 及之前所有 SuperTeam 项目的"七阶段流程"在物理层面**从未真正存在过**：

- `superteam:orchestrator` 是 subagent
- Claude Code runtime 硬限制：subagent 不能调 `Agent` 工具 spawn 下级 subagent（这条限制 V4.6.4 VERSION.md 末尾"未覆盖项"已点出但未处理）
- 结果 OR subagent 被迫一肩挑（自代 reviewer/verifier/writer/executor）
- 七阶段沦为单 agent 换帽子表演 · 所有质量 gate 退化成"自审自"

V1.3.1 attempt-2 接力时第一个 OR subagent 在 review.md 头部诚实披露了这一点：
"Reviewer: orchestrator 代理执行(当前 session 无 Task/Agent 工具)"。

V4.7 的本质：把设计意图迁移到能兑现的物理层（主会话）。

## 核心变更

### 1. mode.json 状态机（新增）

新增 `.superteam/state/mode.json` · 主会话身份的**单一开关**（`active` / `ended`）·
schema_version 防漂移 · last_verified_at 心跳 · entered_by + ended_by 审计源。

写入入口仅四个：`/superteam:go`、`/superteam:end`、finish 阶段用户确认、hook 心跳刷 last_verified_at。
原子写（temp + os.replace）防写入半文件。

### 2. 主会话即 OR

- 新增 `framework/main-session-orchestrator.md` — 主会话 OR 行为契约
- `agents/orchestrator.md` 头部加 **DEPRECATED** 警告 · 向后兼容保留但新 run 不再 spawn
- 主会话每个响应开头读 mode.json 自检身份

### 3. Hook 注入 OR 系统提示

- `hooks/dispatch/session_start.py` — 新会话启动时注入主会话 OR 身份提示
- `hooks/dispatch/user_prompt.py` — 每条用户消息注入（兜底 auto-compact / usage-limit / 崩溃续接）
- 注入内容含：active_task_slug、current_stage、最近 specialist 日志、退出途径

### 4. PreToolUse 拦截主会话写工作文件

新增 `hooks/gates/gate_main_session_scope.py`：

- OR 模式下 + 没有 active subagent 时，主会话直接 Edit/Write 实质工作文件 → **block**
- 实质文件：`*.{ts,tsx,vue,py,go,...}`、`review.md` / `verify.md` / `polish.md` / `final.md` / `test-plan.md` / `plan.md` / 等
- 白名单（OR 协调职能）：`.superteam/state/*`、`activity-trace.md`、`task-list.md`、`decision-log.md`
- 主会话试图绕过 → 写入 `.superteam/state/gate-violations.jsonl` 审计

### 5. PostToolUse 写 spawn-log.jsonl

`hooks/dispatch/post_tool.py`：每次主会话调 `Agent` 工具，自动追加一条记录到 `.superteam/runs/<slug>/spawn-log.jsonl`：

```json
{"ts":"...","subagent_type":"reviewer","agent_id":"...","task_slug":"..."}
```

主会话**无法伪造**这个日志 — hook 拦的是真实 Agent tool call 事件。是后续所有信任链 gate 的唯一真相源。

### 6. Slash Commands

- `/superteam:go [task]` — 改造 skill：进入流程前先调用 mode_cli.py 写 mode.json
- `/superteam:end` — 新增 skill：立即 mode=ended，退出 OR
- `/superteam:status` — 改造 skill：先输出 mode + 最近 spawn + 最近 violations 再读 current-run.json

底层 CLI：`commands/cli/mode_cli.py`（enter / end / status / bypass）。slash command 与 hook 共用同一段原子写代码。

### 7. Active Subagent Window

新增 `.superteam/state/active-subagent.json` transient flag：

- PreToolUse Agent 时设置 → 期间 subagent 内的 Edit/Write 不被 main_session_scope gate 误判
- PostToolUse Agent 或 SubagentStop 时清除（双闸关闭）

## 不变的部分

V4.6.4 的所有 hook（gate_tdd_redgreen、gate_commit_gate、gate_freeze_locks、validators、observers、PostToolUse 自动 trace 等）全部保留并继续工作。
V4.7 只是在 OR 身份维度上加了一层物理强制。

`framework/orchestrator.md` 的七阶段决策规则不变。变的只是"谁来执行" — 从 subagent 搬到主会话。

## 升级路径（已有项目）

1. `/plugin marketplace update superteam` + `/plugin update superteam`
2. 已有 V4.6 项目的 `.superteam/state/current-run.json` 仍然有效，但没有 mode.json
3. 主会话识别策略：mode.json 不存在 → 普通 Claude Code 模式（不自动迁移）
4. 用户主动 `/superteam:go <slug>` 进入 V4.7 OR 模式时才创建 mode.json

## 文件改动清单

### 新增
- `framework/main-session-orchestrator.md`
- `hooks/lib/mode_state.py`
- `hooks/gates/gate_main_session_scope.py`
- `commands/cli/mode_cli.py`
- `skills/end/SKILL.md`

### 改动
- `.claude-plugin/plugin.json` — version 4.6.4 → 4.7.0 + 新描述
- `agents/orchestrator.md` — 头部加 DEPRECATED 警告
- `hooks/lib/decisions.py` — 加 `emit_user_prompt_context`
- `hooks/dispatch/pre_tool.py` — 接入 gate_main_session_scope · spawn 时设置 active subagent
- `hooks/dispatch/post_tool.py` — 写 spawn-log.jsonl · 清 active subagent
- `hooks/dispatch/user_prompt.py` — 注入 OR 身份 banner
- `hooks/dispatch/subagent_stop.py` — 清 active subagent
- `hooks/session/session_injection.py` — SessionStart 加 OR banner
- `skills/go/SKILL.md` — V4.7 First Action：先调 mode_cli.py enter
- `skills/status/SKILL.md` — V4.7 First Step：先调 mode_cli.py status

### 不变
- `framework/orchestrator.md`、`framework/stage-model.md` 等七阶段决策契约
- 所有 specialist agents（executor/reviewer/verifier/writer/...）
- 所有 V4.6 已有 hook（gate_tdd_redgreen、validator_*、observer_* 等）

---

# SuperTeam V4.6.4

**发布日期**: 2026-04-24
**类型**: Hotfix（关键 Bug 修复）

## V4.6.4 变更

**核心修复**：消除 V4.6.0 引入的 TDD 状态机初始化死锁。

### V4.6.3 死锁症状

`execute` 阶段任何新 run 的首次生产代码 Edit/Write 都被 `gate_tdd_redgreen.py` 硬拦截并返回：

> 未识别到 active feature (execution.md 未添加对应 ## Feature 段或未更新 feature-tdd-state.json) — 先创建 feature section 再编辑生产代码 (A6.8 violation)

### 调用链（死锁闭合）

- gate 要求 `feature-tdd-state.json` 里 `active_feature_id` 非空
- `set_feature_state()` 是唯一会写 `active_feature_id` 的通道
- `set_feature_state()` 的所有调用点都在 `observer_test_runner.run()`，而该 observer 第一件事就是 `get_active_feature() == None → return` —— **无起点，永远进不去**

V4.6.0 把 TDD "应当" 规则硬化为 hook 拦截时，未实现"从 execution.md 的 `## Feature <name>` section 自动 init active_feature_id"的机制。

### V4.6.4 补丁

在 `hooks/dispatch/post_tool.py` 的 Edit/Write/MultiEdit 分支新增 `_maybe_init_active_feature(file_path)`：

- 触发条件：`basename(file_path) == "execution.md"` 且 `current_stage() == "execute"`
- 行为：读 execution.md → `parser.parse_execution_features()` → 找最后一个 `status` 不在 `{COMPLETE, BLOCKED, DEFERRED}` 的 section → 用 `section.name` 作为 `feature_id`
- 写入策略：
  - 已有 feature 记录且 `active_feature_id == fid` → 跳过（让 observer 驱动状态转换）
  - 已有 feature 记录但 active 指向别处 → 仅切换 active 指针（保留已有 RED_LOCKED / GREEN_CONFIRMED）
  - 新 feature → `set_feature_state(fid, state="PENDING")`

修复后正确流程：executor 写 `## Feature X` → active=X, state=PENDING → 写 failing test → 跑 pytest FAILED → observer 转 RED_LOCKED → 写生产代码 → gate 放行。

### 影响面

- 涉及单文件：`hooks/dispatch/post_tool.py`（+42 行）
- 新增单测：`c_tdd_init_from_execution_md()`（test_cases.py）
- 测试套件：45/45 passed（V4.6.3 基线 44/44 + 新 case 1）
- 无破坏性变更：只在 execute 阶段 + execution.md 被写入时才触发，不影响其他阶段和其他文件

### 未覆盖项

诊断文档第 127-133 行提到的"orchestrator Agent 工具能否 spawn superteam:* sub-agent"设计局限，本版本未处理。留作后续版本澄清。

---

# SuperTeam V4.6.3

**发布日期**: 2026-04-24
**类型**: Hotfix（关键 Bug 修复）

## V4.6.3 变更

**核心修复**：hook 项目根解析从 `os.getcwd()` 改为 `$CLAUDE_PROJECT_DIR`，解决 hook 在无关 session 中误触发的致命问题。

### 暴露的致命 Bug

V4.6.2 hook 激活后，在**任何** Claude Code session 里都可能被 Stop hook 拦截——即使该 session 与 SuperTeam 完全无关。

根因在 `hooks/lib/state.py` 的 `find_superteam_root()`：

```python
# V4.6.2 及之前
p = Path(start or os.getcwd()).resolve()
```

`os.getcwd()` 反映的是 hook 进程 spawn 时的 cwd，而 Claude Code 的 Bash 工具可能把 cwd 留在任意临时目录（如 git clone 目录、workspace 以外的路径）。只要父链上有 `.superteam/` 目录（例如 SuperTeam 自己的仓库 clone），hook 就会错误地以为那里是当前项目，触发全套 Gate 检查——典型表现是在无关 session 里无法 Stop，因为 clone 里的 sample run 永远闭不了环。

### 修复

```python
# V4.6.3
if start is None:
    start = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
p = Path(start).resolve()
```

`$CLAUDE_PROJECT_DIR` 是 Claude Code 原生传递给 hook 的环境变量，准确表示 session 的项目根。只在没有该环境变量时才 fallback 到 `os.getcwd()`（保证向后兼容 / 非 Claude Code 环境）。

### 影响面

- 全部 8 个 dispatch hook 都经由 `state.py` 解析 `.superteam/`，这一个单点修复覆盖所有事件
- 无破坏性变更：对实际 SuperTeam 项目（`$CLAUDE_PROJECT_DIR/.superteam/` 存在）行为完全不变
- 修复只在"当前 session 不是 SuperTeam 项目但父路径有 `.superteam/`"时生效——从误拦截变为正确放行

---

# SuperTeam V4.6.2

**发布日期**: 2026-04-24
**类型**: Hotfix

## V4.6.2 变更

**核心修复**：`hooks.json` 位置从 `.claude-plugin/hooks.json` 改到 `hooks/hooks.json`。

V4.6.1 把 `hooks.json` 放在 `.claude-plugin/` 下，但 Claude Code 官方文档（https://code.claude.com/docs/en/hooks.md 的 File Locations 表格）规定的 plugin 原生 hook 声明位置是 **`<plugin-root>/hooks/hooks.json`**，不是 `.claude-plugin/hooks.json`。V4.6.1 因此读不到 hook，`/reload-plugins` 仍报 `0 hooks`，"hook 强约束"依旧不生效。

**V4.6.2 修复**：把 `hooks.json` 从 `.claude-plugin/` 搬到 `hooks/`，其他内容不变。文件格式保持 `{"hooks": {"SessionStart": [...], ...}}`，`${CLAUDE_PLUGIN_ROOT}` 变量和 8 个 dispatch 脚本引用全部保留。

**破坏性**：无。纯路径修正。

---

# SuperTeam V4.6.1

**发布日期**: 2026-04-24
**类型**: Hotfix

## V4.6.1 变更

**核心修复**：hook 改为 Claude Code 原生自动注册。

V4.6.0 发布后发现：从 plugin marketplace 安装时 hook 全部失活（`/reload-plugins` 显示 `0 hooks`），V4.6.0 宣称的"hook 强约束"实际不生效。根因：hook 注册依赖用户手动运行 `install.ps1` / `install.sh` 把 `hooks_settings_template.json` 合并到 `~/.claude/settings.json`，而 Claude Code 从 GitHub marketplace 安装 plugin 时只做 `git clone`，不会执行 install 脚本。

**V4.6.1 修复方案**：新增 `.claude-plugin/hooks.json`（Claude Code plugin 原生 hook 声明位置），把 8 个事件 hook 直接声明在这里。Claude Code 加载 plugin 时自动注册，不再依赖 install 脚本。

**保留项**：`install.ps1` / `install.sh` / `hooks_settings_template.json` 保留给直接 `git clone` 使用的老用户（他们不走 plugin marketplace 流程）。新走 plugin marketplace 的用户什么都不用做，hook 自动生效。

**破坏性**：无。纯补丁。

---

# SuperTeam V4.6.0 (开发中)

**目标发布日期**: 2026-05 (待 hook 实施完成)
**当前状态**: Hook Enforcement Matrix final · 等待 30 个 hook checker 实施

## V4.6.0 核心目标

把 SuperTeam 所有 "应当 / 禁止 / 必须" 规则从 "AI 自觉执行" 升级为 **plugin-level hook 硬约束**。诊断依据见 `DIAGNOSIS-V4.5.0-self-enforce-flaw.md`；执行清单见 `framework/hook-enforcement-matrix.md` (137 条规则 × 30 个 checker)。

## V4.6.0 已完成的变更

### 1. Hook Enforcement Matrix (唯一事实源)

- 新增 `framework/hook-enforcement-matrix.md`：逐条登记 V4.5.0 的 137 条规则 × 对应 hook checker
- 分层: A 框架级硬拦截 (75) / B 项目级读 artifact (15) / C .md-only 思维引导 (29) / D 建议删除 (18)
- B6 节 UI anti-pattern 明确**不做 hook**（交由 reviewer 人眼审查），避免把 SuperTeam 品味硬塞给所有项目

### 2. Role 语义正名 · reviewer ↔ inspector 对调

V4.5.0 及之前版本 `reviewer` 做团队行为监察、`inspector` 做代码质量审查，**与英文字面相反**（review 应对应审查，inspect 应对应监察）。V4.6.0 彻底修正：

| V4.5.0 | V4.6.0 (对调后) | 职责 |
|--------|----------------|------|
| `inspector` 做 review 阶段质量门 + BLOCK 权 | `reviewer` 做 review 阶段质量门 + BLOCK 权 | 代码/交付物审查，产出 `review.md` |
| `reviewer` 做团队行为监察 + 零中断 | `inspector` 做团队行为监察 + 零中断 | 流程监察，产出 `.superteam/inspector/reports/*` |

**改名不改职责**，英文 / 中文 / Stage 语义完全对齐：
- 中文"审查者" = English `reviewer` = review 阶段质量门 (BLOCK 权)
- 中文"监察者" = English `inspector` = 全程流程监察 (零中断)

数据路径对调: `.superteam/reviewer/` → `.superteam/inspector/`

**破坏性变更**: V4.5.0 及之前项目的 `.superteam/reviewer/` 目录在 V4.6.0 下需迁移 (install 脚本会做兼容迁移)。

---

## V4.6.0 待完成

- hooks/dispatch/ 8 个事件入口脚本
- hooks/validators/ 14 个产物 validator
- hooks/gates/ 7 个 tool 拦截 checker
- hooks/observers/ 4 个 Bash 输出解析器
- hooks/post_agent/ 3 个 agent 结束后巡检
- hooks/session/ 2 个 session checker
- `matrix_selfcheck.py` 自检工具
- `install.ps1` / `install.sh` 合并 hooks 到 `.claude/settings.json`
- tests/ 单测 + SMS V1.3 C07 回归 fixture
- 精简 agents/ + framework/ 删除 18 条 D 类规则 (hook 已覆盖)

---

## 历史继承 (来自 V4.5.0 · 2026-03-28)

V4.5.0 基于 V4.4.0，引入功能清单体系与逐功能 TDD 执行循环。

## 版本定位

V4.5.0 解决的核心问题：
1. 功能清单缺失：plan.md 的 MUST 项粒度停留在阶段/模块级别，executor 和 verifier 不知道具体要做什么、测什么
2. TDD 执行是批量的：executor 把所有任务做完再统一测试，错误积累后返工代价极高
3. 监工报告缺少功能维度：Inspector 最终报告没有逐功能测试结果的专项记录

## 设计原则

**功能清单是交付合同**：G1 建立初始功能范围，G2 将其锁定为行为级功能清单（`feature-checklist.md`），G3 验证计划完整覆盖清单，G4–G6 全程追溯。

**逐功能 TDD 循环**：executor 每次只做一个功能，完成红绿灯循环并记录证据后，才能开始下一个功能。无法变绿则停下升级 OR，不得跳过。

**监工看得见每个功能的测试结果**：Inspector 报告新增专项节，逐功能列出 RED/GREEN 证据引用，静默跳过的功能立即暴露。

## 新增内容

### `feature-checklist.md`（运行时产物，G2 锁定）

每个功能项包含：
- 单个可观测的用户行为（不是阶段名/模块名）
- 测试类型（unit / integration / E2E）
- 测试工具

由 orchestrator 在 design 收尾时与用户确认，G2 关闭即锁定，之后只读。

### `framework/stage-gate-enforcement.md`

新增 Agent Entry Log Requirement：每个 agent 启动时在 `activity-trace.md` 写入场记录，记录读取的 Gate 编号和找到的关键产物路径。Inspector 验证 Gate 编号和路径是否正确。

Gate 1 新增 check 8：`project-definition.md` 包含初始功能范围列表。

Gate 2 新增 checks 10–14：`feature-checklist.md` 存在、每项是单个可观测行为、每项有测试类型和工具、G2 批准记录、Inspector 检查点。**缺失时 OR 必须问用户，不得由 designer 或 planner 自行补充。**

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
| `agents/inspector.md` | 报告扩展为七节，新增 Section 3：Feature Checklist Test Results（逐功能测试结果表，引用 execution.md 实际输出） |
| `agents/designer.md` | Read First 加入 Gate 1 引用 + 入场记录要求 |
| `agents/planner.md` | Read First 加入 Gate 2 引用 + 入场记录要求 |
| `agents/executor.md` | Read First 加入 Gate 3 引用 + 入场记录要求 |
| `agents/reviewer.md` | Read First 加入 Gate 4 引用 + 入场记录要求 |
| `agents/verifier.md` | Read First 加入 Gate 5 引用 + 入场记录要求 |
| `framework/agent-behavior-registry.md` | 每个 agent 新增 B-*-0 入场记录行为；executor B-EX-1~5 完整重写为逐功能证据标准 |
| `framework/stage-gate-enforcement.md` | 新增双重用途说明（出口条件 + 入口导航）；新增 Agent Entry Log Requirement 节；Gate 1/2/3/4 检查项扩展 |

## 删除文件

| 文件 | 原因 |
|------|------|
| `framework/stage-handoff-specs.md` | 设计错误：运行时填写的交接文档有为过门而写的激励结构；门控清单本身已是入口导航，不需要额外交接文档 |

## 继承内容（V4.4.0 保持不变）

- 59 个二进制检查项的基础结构（Gate 1–7）
- 双检机制：OR + Inspector 并行检查，OR 必须等 Inspector 报告后才决策
- Inspector 七节报告结构（Section 1/2/4/5/6/7 不变，新增 Section 3）
- 入场记录格式（Agent Entry Log）
- Designer 设计确认清理协议
- Reviewer TDD 非自授权规则
- Verifier 必须运行测试套件

## 安装方式

- marketplace root：`D:\claude code\superteam`
- 当前插件源：`D:\claude code\superteam\V4.5.0_功能清单与逐功能TDD`

## 升级规则

- 新版本使用新目录，旧目录不覆盖
- 更新 marketplace 指向新版本目录后重新加载插件
