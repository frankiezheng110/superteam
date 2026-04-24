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
