# SuperTeam V4.7.10 实现计划 · Project 全局进度层

**目标**: 引入 project 层级,解决"phase finish 被误当 project end"的根本 bug。
**触发事件**: 2026-04-26 SMS 项目 phase-4-s3-module(V1.4.0 里程碑)走完整 finish 流程后被误标 `mode.lifecycle=ended` + `ended_by=project_completion`,但实际 SMS 还有 V1.5+ → V2.0.0 多个里程碑待做。
**前置版本**: V4.7.9_anti_dump_stop_guard
**类型**: Feature (架构层新增 project 概念)

---

## 一、根因诊断

### 当前 V4.7.9 状态机粒度

```
project = phase = task slug = `.superteam/runs/<slug>/`
```

`mode.json` + `current-run.json` 只服务一个 phase。`finish` 阶段写完 inspector report + retrospective + finish.md 后,`mode_cli.py end --completion` 直接把 `lifecycle=ended`,等于宣告"整个项目结束"。

### 实际业务粒度

```
project (SMS / 任意客户产品)
├── milestone V1.0.0_foundation       (phase slug: foundation-bootstrap)
├── milestone V1.1.0_s0_module         (phase slug: phase-1-s0-module)
├── milestone V1.2.0_s1_module         (phase slug: phase-2-s1-module)
├── milestone V1.3.0_s2_module         (phase slug: phase-3-s2-module)
├── milestone V1.3.1_s2_fix            (phase slug: phase-3.1-s2-fix)
├── milestone V1.4.0_s3_module         (phase slug: phase-4-s3-module)  ← 当前
├── milestone V1.5.0_desktop           (phase slug: phase-5-desktop)     ← 下一
├── ...
└── milestone V2.0.0_release           (phase slug: phase-N-release)
```

1 个 project 含 N 个 milestone,每个 milestone = 1 个 phase = 1 个 SuperTeam 工作流闭环。

### 缺失能力

1. **全局 project 进度文件**:跨 phase / 跨会话持久化的"项目当前走到哪个 milestone"
2. **phase finish ≠ project end**:phase 完结时只标该 milestone DONE,不 mode end
3. **SessionStart 全局视野注入**:新会话立刻知道整体进度
4. **project complete 显式指令**:全部 milestone DONE 后由 user 显式触发

---

## 二、设计 (V4.7.10 spec)

### 2.1 新 schema: `.superteam/project.md`

位置:**项目根 `.superteam/project.md`**(不在 `runs/<slug>/` 下),与 `state/` 同级。

格式:

```markdown
---
schema_version: 1
project_name: SMS
project_slug: store-management-system
target_release: V2.0.0_release
status: in_progress  # in_progress | complete
current_milestone_slug: phase-5-desktop
created_at: 2026-04-XXTHH:MM:SSZ
last_updated: 2026-04-26TXX:XX:XXZ
---

# Project: SMS (Store Management System)

## Milestones

| # | Version | Phase Slug | Status | Started | Completed | Notes |
|---|---|---|---|---|---|---|
| 1 | V1.0.0_foundation | foundation-bootstrap | DONE | 2026-04-XX | 2026-04-XX | repo init / monorepo skeleton |
| 2 | V1.1.0_s0_module | phase-1-s0-module | DONE | ... | ... | 门店/员工/股东 schema |
| 3 | V1.2.0_s1_module | phase-2-s1-module | DONE | ... | ... | 报账 / 日报 / 工资 |
| 4 | V1.3.0_s2_module | phase-3-s2-module | DONE | ... | ... | 数据获取 / 银行总账 |
| 5 | V1.3.1_s2_fix | phase-3.1-s2-fix | DONE | ... | ... | RC tag 62cbb1b |
| 6 | V1.4.0_s3_module | phase-4-s3-module | DONE | 2026-04-25 | 2026-04-26 | 14 task / 1233→1277 tests |
| 7 | V1.5.0_desktop | phase-5-desktop | PENDING | - | - | Tauri 桌面集成 + D-01~13 |
| 8 | V1.6.0_e2e_real | phase-6-e2e | PENDING | - | - | E2E 实跑激活 + DB seed |
| 9 | V1.7.0_douyin_5-17 | phase-7-douyin-deploy | PENDING | - | - | 抖音真实保活部署 |
| ... | | | | | | |
| N | V2.0.0_release | phase-N-release | PENDING | - | - | 全 V1.x 完成后首发 |

## Decision Log (跨 phase 关键决策)

- 2026-04-XX: 美团官方通道死亡,改月度手工 Excel(memory project_sms_meituan_blocked)
- 2026-04-XX: Tier 2 扩展架构整体废弃(memory project_sms_tier2_abandoned)
- 2026-04-25: V4.7.9 stop hook 漏洞修复(commit 8e3b06c)
- ...

## Pending Cross-Milestone Items

- [HIGH 5-17 deadline] 抖音真实保活部署
- [MED] _pencil-dump-*.md 实物档补录
- [MED] V4.7.10 project 层级生效后 migrate 旧 mode.json
```

### 2.2 新 lib API: `hooks/lib/project_state.py`

```python
# hooks/lib/project_state.py (V4.7.10 新增)
"""V4.7.10 — project layer state machine.

A project is a multi-milestone delivery; each milestone is a phase
(SuperTeam workflow run). project.md schema lives at .superteam/project.md
and persists across sessions and phases.

Stop hook now consults project.md.status (not mode.json.lifecycle alone)
to decide whether OR can self-stop. Phase finish marks one milestone DONE
in project.md but does NOT terminate the project.
"""
from __future__ import annotations
import re
import yaml  # or use simple frontmatter parser
from pathlib import Path
from . import state

PROJECT_FILE_NAME = "project.md"

def project_path() -> Path | None:
    d = state.superteam_dir()
    return d / PROJECT_FILE_NAME if d else None

def read_project() -> dict:
    """Parse frontmatter; return {} if missing or corrupt."""
    p = project_path()
    if not p or not p.exists():
        return {}
    try:
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            return {}
        return yaml.safe_load(m.group(1)) or {}
    except Exception:  # noqa: BLE001
        return {}

def project_status() -> str:
    """Returns 'in_progress' | 'complete' | '' (no project.md)."""
    return read_project().get("status", "")

def is_project_active() -> bool:
    """V4.7.10 — replaces is_project_alive() in stop hook.

    True ⇔ project.md exists AND status != 'complete'.
    False ⇔ project.md missing (no project loaded) OR status='complete'.
    """
    s = project_status()
    return s != "" and s != "complete"

def current_milestone() -> str:
    return read_project().get("current_milestone_slug", "")

def mark_milestone_done(slug: str, completed_at: str | None = None) -> bool:
    """Update project.md milestone table: status PENDING → DONE."""
    # Implementation: read text, locate row by phase_slug, update status + completed_at
    # Atomic write via temp file
    ...

def set_project_complete(by: str = "user") -> bool:
    """Set status=complete in frontmatter."""
    ...
```

### 2.3 stop.py 改造

```python
# hooks/dispatch/stop.py (V4.7.10)
def _or_self_stop_check(payload):
    # V4.7.10: prefer project_state if project.md present;
    # fall back to mode_state for legacy projects
    from ..lib import project_state, mode_state
    
    if project_state.read_project():
        # Project layer active
        if project_state.is_project_active():
            # threshold valve unchanged from V4.7.9
            is_repeat = bool(payload.get("stop_hook_active"))
            count = mode_state.bump_stop_block_count(reset_to_one=not is_repeat)
            if count >= mode_state._STOP_BLOCK_THRESHOLD:
                mode_state.reset_stop_block_count()
                return True, ""
            return False, REASON_PROJECT_ACTIVE
        return True, ""  # project complete
    
    # Legacy: no project.md → fall back to mode_state.is_project_alive
    if mode_state.is_project_alive():
        # ... same threshold valve logic ...
    return True, ""
```

新 reason 文本:
```
SuperTeam V4.7.10 self-stop block · 项目仍在交付中 · current_milestone=<slug>
读 project.md 查看整体进度,推进当前 milestone 或启动下一个。
唯一退出: /superteam:project-complete (全部 milestone DONE 后)。
```

### 2.4 finish 流程改造

`hooks/session/stop_finish_guard.py` 新增:

```python
# 当 current_stage=finish 且当前 milestone 在 project.md 中:
# 1. 标该 milestone DONE
# 2. 不调用 mode end --completion (除非 user 显式 /superteam:project-complete)
# 3. 提示 next_milestone (如有 PENDING) 或 prompt user 触发 project-complete
```

`mode_cli.py` 新增子命令:

```bash
python mode_cli.py project-init <name> --target-release <ver> --milestones-file <path>
python mode_cli.py project-status
python mode_cli.py project-next <milestone-slug>  # phase finish 后切下一 phase
python mode_cli.py project-complete --by user
```

### 2.5 SessionStart hook 注入

`hooks/session/session_injection.py` 新增:

```python
def inject_project_context(payload):
    """V4.7.10 — at session start, inject project.md content into OR context."""
    p = project_state.project_path()
    if not p or not p.exists():
        return  # no project, skip
    text = p.read_text(encoding="utf-8")
    payload["additional_context"] = (
        payload.get("additional_context", "")
        + "\n\n## 全局 Project 进度 (来自 .superteam/project.md)\n"
        + text
    )
```

### 2.6 新 slash commands

- `/superteam:project init <name>` → 创建 project.md
- `/superteam:project status` → 输出 project.md 渲染表格
- `/superteam:project next <slug>` → phase finish 后切下一 milestone (mode_cli enter <slug>)
- `/superteam:project complete` → 全部 milestone DONE 后真 mode end

每个 slash command 写到 `commands/cli/project_cli.py` 子命令分发。

---

## 三、文件清单

V4.7.10 复制 V4.7.9 → V4.7.10_project_global_progress,改动:

| 路径 | 操作 |
|---|---|
| `hooks/lib/project_state.py` | **NEW** |
| `hooks/dispatch/stop.py` | MODIFY (加 project_state 优先判定) |
| `hooks/session/stop_finish_guard.py` | MODIFY (phase finish 标 milestone DONE 不 mode end) |
| `hooks/session/session_injection.py` | MODIFY (SessionStart inject project.md) |
| `hooks/dispatch/session_start.py` | MODIFY (调用 inject_project_context) |
| `commands/cli/mode_cli.py` | MODIFY (新增 project-init / status / next / complete 子命令) |
| `framework/main-session-orchestrator.md` | MODIFY (加 project layer 章节) |
| `framework/state-and-resume.md` | MODIFY (project.md 在 resume 中的地位) |
| `tests/test_v4710_project_layer.py` | **NEW** (P1-P10 case: project init / milestone done / next / complete / stop hook 双层判定 / SessionStart inject 等) |
| `tests/test_v477_stop_purity.py` | MODIFY (ALLOWED_NAMES 加 is_project_active / project_state) |
| `tests/test_v477_lifecycle.py` | MODIFY (新增 P 系列 case: project complete → ALLOW / project in_progress → BLOCK 即使 mode lifecycle ended) |
| `tests/test_or_self_stop_v475.py` | MODIFY (legacy fallback 路径仍验证) |
| `.claude-plugin/plugin.json` | version 4.7.9 → 4.7.10 + description |
| `VERSION.md` | **NEW** (按 V4.7.9 模板写完整 spec) |

---

## 四、实现顺序(给新会话执行用)

1. 复制 V4.7.9 → V4.7.10_project_global_progress 目录
2. 写 `hooks/lib/project_state.py`(read_project / is_project_active / mark_milestone_done / set_project_complete)
3. 改 stop.py 加 project_state 双层判定 + legacy fallback
4. 改 session_injection.py 加 inject_project_context
5. 改 mode_cli.py 加 4 个 project- 子命令
6. 写新测试 `test_v4710_project_layer.py`
7. 改老测试反转/补 case
8. 跑全测试,绿
9. 更新 VERSION.md / plugin.json description
10. clone superteam-fix repo + cp + marketplace.json + git commit + push

预计:300-500 行新代码 + 10-15 个新 test cases + 4-6 个测试改动。复杂度约为 V4.7.9 patch 的 2-3 倍。

---

## 五、Migration 路径(已部署 V4.7.9 的 SMS 项目)

V4.7.10 部署后,SMS 项目需要:

1. 用户在 SMS 项目根创建 `.superteam/project.md`(用 `/superteam:project init SMS --target-release V2.0.0_release`,然后 user 编辑 milestone 表格补 V1.0~V1.4 历史 + V1.5+ 计划)
2. 把当前 `mode.json.lifecycle=ended`(被误标的)切回 `running`(用 `mode_cli.py force-resume` 或编辑 mode.json) — V4.7.10 应提供合法工具:`mode_cli.py reopen --reason "误标 ended,实为 phase finish 非 project end"`
3. SessionStart hook 自动 inject project.md → 新会话立刻看到全局视野

旧项目无 project.md → V4.7.10 fallback 走 V4.7.9 行为(legacy mode_state),完全向后兼容。

---

## 六、不变的

- V4.7.9 ≥4 阈值 valve (case-3 hook bug 救命)
- V4.7.9 fail-closed try/except
- V4.7.9 5 要素强引导 reason (但语义升级:不再说"项目未结束",改说"milestone 未完结")
- V4.7.9 paused 也 BLOCK
- V4.7.5 状态机文件 BLOCK 列表(project.md 加入 BLOCK 列表,只能通过 mode_cli 修改)
- V4.7.6 兼容层

---

## 七、新会话开工指令

下次开新会话时,user 输入:

```
读 D:\claude code\superteam\PLAN-V4.7.10-project-global-progress.md
按文件 §四 实现顺序逐步落地 V4.7.10
不要走 SuperTeam 工作流(V4.7.9 风险:把 V4.7.10 patch 跑成另一个 phase)
直接由 main session 主导:复制目录 / 写代码 / 跑测试 / push GitHub
完成后告诉我 commit hash + 升级路径,我手动 /plugin marketplace update
```
