"""All test cases. Each case has: id, title, purpose, run(ws) -> Result."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from harness import (
    Workspace,
    invoke,
    make_workspace,
    destroy_workspace,
    pre_tool_agent,
    pre_tool_bash,
    pre_tool_edit,
    pre_tool_write,
    post_tool_agent,
    post_tool_bash,
    post_tool_edit,
    session_start,
    stop_event,
)


@dataclass
class CaseResult:
    case_id: str
    title: str
    purpose: str
    passed: bool
    expected: str
    actual: str
    hook_stderr: str = ""
    category: str = ""


@dataclass
class Case:
    id: str
    title: str
    category: str
    purpose: str
    fn: Callable[[Workspace], tuple[bool, str, str, str]]  # passed, expected, actual, stderr


# ---- helpers ----

def _plan_minimal_text(must_items: list[str]) -> str:
    body = """# plan.md

## Delivery Scope

"""
    for item in must_items:
        body += f"- MUST: {item}\n"
    body += """

## Task T1.A

- objective: implement feature F-001
- target files: src/foo.py
- implementation steps: red -> green -> refactor
- verification commands: pytest
- done signal: all tests pass
"""
    return body


def _ui_intent_minimal() -> str:
    return """# ui-intent.md

## Purpose
Test project UI purpose.

## Tone
Minimalist, refined.

## Constraints
Web browsers, modern.

## Differentiation
Distinctive typography choice.

## Aesthetic Direction
Minimalist with serif typography.

## Typography Contract
Primary font: "Satoshi" (Medium, 14-48px)
font-family: 'Satoshi', 'Inter Fallback', sans-serif

## Color Contract
Primary: #0A2540; Accent: #00D4FF.

## Motion Contract
CSS-only transitions 200-400ms ease-out.

## Spatial Contract
8px grid. Asymmetric.

## Visual Detail Contract
Grain overlay 3% opacity.

## Anti-Pattern Exclusions
None declared.
"""


def _install_full_run(ws: Workspace, slug: str = "smoke", **extras: Any) -> None:
    """Helper: set up a run with all artifacts present so gate checks pass."""
    ws.init(slug=slug, **extras)
    rd = f".superteam/runs/{slug}"
    ws.put(
        f"{rd}/project-definition.md",
        """# project-definition.md

## objective
Deliver smoke test.

## constraints
Python 3.11+.

## non-goals
No real Claude calls.

ui_weight: ui-none

## feature scope
- Feature A
""",
    )
    ws.put(
        f"{rd}/activity-trace.md",
        """# activity-trace.md

## Inspector Checkpoint: clarify
- Artifacts present: project-definition.md
- safe-to-advance: YES
- approved_by: user "smoke test approved" 2026-04-24
""",
    )
    ws.put(
        f"{rd}/feature-checklist.md",
        """# feature-checklist.md

- 用户点击按钮后看到欢迎信息 test_type: integration test_tool: pytest
- 用户输入密码错误看到错误提示 test_type: integration test_tool: pytest
""",
    )
    ws.put(
        f"{rd}/plan.md",
        _plan_minimal_text([
            "用户点击按钮后看到欢迎信息",
            "用户输入密码错误看到错误提示",
        ]),
    )


# ============================================================
# CASES
# ============================================================

def c_session_start_injection() -> Case:
    def fn(ws: Workspace):
        ws.init(slug="smoke", current_stage="execute")
        res = invoke("session_start", session_start(), cwd=ws.path)
        context = res.decision.get("hookSpecificOutput", {}).get("additionalContext", "")
        passed = "current_stage=execute" in context or "SuperTeam" in context
        return passed, "SessionStart 注入 current-run 摘要", context[:200] or "(空)", res.stderr
    return Case("H1-session-injection", "SessionStart 注入上轮运行摘要", "H1", "A13.1 / H1", fn)


def c_pre_tool_agent_wrong_stage() -> Case:
    def fn(ws: Workspace):
        ws.init(slug="smoke", current_stage="clarify")
        # 在 clarify 阶段 spawn executor 应该被 block
        res = invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        passed = res.blocked and "execute" in res.reason.lower()
        return passed, "在 clarify 阶段 spawn executor → block", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A4.1-stage-legality", "Agent 跨阶段 spawn 被拦", "A4", "A4.1/A4.9 agent stage legality", fn)


def c_pre_tool_agent_valid_stage() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # add Orchestrator Decision so A5.3 passes
        ws.put(
            ".superteam/runs/smoke/activity-trace.md",
            ws.read(".superteam/runs/smoke/activity-trace.md") + """

## Orchestrator Decision — Task T1.A
Unit id: T1.A
MUST items to deliver:
- 用户点击按钮后看到欢迎信息
- 用户输入密码错误看到错误提示
""",
        )
        res = invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        passed = not res.blocked
        return passed, "stage=execute + Gate 3 + A5.3 decision → allow executor", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A4.1-stage-ok", "合法 stage 下 allow executor", "A4", "A4.1", fn)


def c_gate_commit_no_verification() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="finish")
        res = invoke("pre_tool", pre_tool_bash("git commit -m 'test'"), cwd=ws.path)
        passed = res.blocked and "verification" in res.reason.lower()
        return passed, "verification.md 缺失 → block commit", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A10.1-commit-no-verify", "缺 verification → commit 被拦", "A10", "A10.1 commit gate", fn)


def c_gate_commit_fail_verdict() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="finish")
        ws.put(".superteam/runs/smoke/verification.md", "verdict: FAIL\n## evidence summary\n(empty)\n")
        res = invoke("pre_tool", pre_tool_bash("git commit -am 'x'"), cwd=ws.path)
        passed = res.blocked and ("FAIL" in res.reason or "PASS" in res.reason)
        return passed, "verdict=FAIL → block commit", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A10.1-commit-fail", "verdict=FAIL → commit 被拦", "A10", "A10.1 commit gate", fn)


def c_gate_commit_pass_allow() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="finish")
        ws.put(
            ".superteam/runs/smoke/verification.md",
            """# verification.md
verdict: PASS
delivery_confidence: high
## evidence summary
pytest all passed
## requirement-by-requirement
- MUST 1: VERIFIED
""",
        )
        ws.put(".superteam/runs/smoke/review.md", "verdict: CLEAR\n")
        ws.put(
            ".superteam/runs/smoke/activity-trace.md",
            ws.read(".superteam/runs/smoke/activity-trace.md") + "\n## Checkpoint smoke-001\ncommit prepared\n",
        )
        res = invoke("pre_tool", pre_tool_bash("git commit -m 'ok'"), cwd=ws.path)
        passed = not res.blocked
        return passed, "verdict=PASS + review=CLEAR + checkpoint 齐全 → allow commit", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A10.1-commit-pass", "所有条件齐全 → allow commit", "A10", "A10.1 commit gate", fn)


def c_gate_commit_override_env() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        os.environ["ALLOW_UNVERIFIED_COMMIT"] = "1"
        try:
            res = invoke("pre_tool", pre_tool_bash("git commit -m 'urgent'"), cwd=ws.path)
        finally:
            os.environ.pop("ALLOW_UNVERIFIED_COMMIT", None)
        passed = not res.blocked
        return passed, "ALLOW_UNVERIFIED_COMMIT=1 → allow (留痕)", f"blocked={res.blocked}", res.stderr
    return Case("A10.4-commit-override", "显式 env 覆盖", "A10", "A10.4 override", fn)


def c_tdd_pending_blocks_prod() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # feature-tdd-state: F-001 at PENDING
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({
                "active_feature_id": "F-001",
                "features": {"F-001": {"state": "PENDING"}},
            }),
        )
        res = invoke("pre_tool", pre_tool_edit("src/foo.py", "def bar(): pass"), cwd=ws.path)
        passed = res.blocked and ("failing test" in res.reason or "RED" in res.reason)
        return passed, "PENDING 状态编辑 src/ → block 要求先 failing test", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A6.1-tdd-pending", "TDD PENDING 禁写生产代码", "A6", "A6.1/A6.2 TDD red first", fn)


def c_tdd_red_locked_allows_prod() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({
                "active_feature_id": "F-001",
                "features": {"F-001": {"state": "RED_LOCKED", "green_attempts": 0}},
            }),
        )
        res = invoke("pre_tool", pre_tool_edit("src/foo.py"), cwd=ws.path)
        passed = not res.blocked
        return passed, "RED_LOCKED 状态编辑 src/ → allow", f"blocked={res.blocked}", res.stderr
    return Case("A6.5-tdd-red-green", "TDD RED_LOCKED 放行生产代码", "A6", "A6.5 green phase", fn)


def c_tdd_test_path_allows() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({
                "active_feature_id": "F-001",
                "features": {"F-001": {"state": "PENDING"}},
            }),
        )
        # 编辑 tests/ 路径 → 应 allow (是测试文件, 不是生产代码)
        res = invoke("pre_tool", pre_tool_edit("tests/test_foo.py"), cwd=ws.path)
        passed = not res.blocked
        return passed, "PENDING 编辑 tests/ → allow (测试文件)", f"blocked={res.blocked}", res.stderr
    return Case("A6.1-test-path", "编辑测试路径不触发 TDD 拦", "A6", "A6.1 test path exempt", fn)


def c_tdd_observer_red_transition() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({
                "active_feature_id": "F-001",
                "features": {"F-001": {"state": "PENDING"}},
            }),
        )
        # 模拟 pytest 输出含 FAILED
        res = invoke(
            "post_tool",
            post_tool_bash("pytest tests/test_foo.py -v", "FAILED tests/test_foo.py::test_add\n1 failed\n"),
            cwd=ws.path,
        )
        state = ws.read_json(".superteam/state/feature-tdd-state.json")
        feat = state.get("features", {}).get("F-001", {})
        passed = feat.get("state") == "RED_LOCKED" and "red_evidence" in feat
        return passed, "pytest FAILED → state 转 RED_LOCKED", f"state={feat.get('state')}", res.stderr
    return Case("A6.3-tdd-observer-red", "Observer 解析 FAILED 转 RED_LOCKED", "A6", "A6.3 observer_test_runner", fn)


def c_tdd_observer_green_transition() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({
                "active_feature_id": "F-001",
                "features": {"F-001": {"state": "RED_LOCKED", "green_attempts": 0}},
            }),
        )
        res = invoke(
            "post_tool",
            post_tool_bash("pytest tests/", "10 passed in 0.5s\n"),
            cwd=ws.path,
        )
        state = ws.read_json(".superteam/state/feature-tdd-state.json")
        feat = state.get("features", {}).get("F-001", {})
        passed = feat.get("state") == "GREEN_CONFIRMED" and "green_evidence" in feat
        return passed, "pytest 全 pass → state 转 GREEN_CONFIRMED", f"state={feat.get('state')}", res.stderr
    return Case("A6.6-tdd-observer-green", "Observer 解析全 PASS 转 GREEN_CONFIRMED", "A6", "A6.6 observer_test_runner", fn)


def c_gate_file_scope_clarify() -> Case:
    def fn(ws: Workspace):
        ws.init(slug="smoke", current_stage="clarify")
        # clarify 阶段禁写 plan.md
        res = invoke("pre_tool", pre_tool_edit(f"{ws.path}/.superteam/runs/smoke/plan.md"), cwd=ws.path)
        passed = res.blocked and "plan" in res.reason.lower()
        return passed, "clarify 阶段写 plan.md → block", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A9.1-file-scope-clarify", "文件阶段权限拦截", "A9", "A9.1 file stage scope", fn)


def c_gate_file_scope_execute_prod() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # execute 阶段写 src/foo.py (非 .superteam/runs/) → 应 allow (除了 TDD gate 考虑)
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({
                "active_feature_id": "F-001",
                "features": {"F-001": {"state": "RED_LOCKED"}},
            }),
        )
        res = invoke("pre_tool", pre_tool_edit("src/foo.py"), cwd=ws.path)
        passed = not res.blocked
        return passed, "execute 阶段 RED_LOCKED 下写 src/ → allow", f"blocked={res.blocked}", res.stderr
    return Case("A9.4-file-scope-execute", "execute 阶段可写生产代码", "A9", "A9.4", fn)


def c_entry_log_missing_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        from pathlib import Path as _P
        sys_path_saved = list(os.sys.path)
        hooks_root = str(_P(__file__).resolve().parents[1])
        os.sys.path.insert(0, hooks_root)
        old_cwd = os.getcwd()
        os.chdir(str(ws.path))
        try:
            from hooks.validators import validator_activity_trace
            ok, errs = validator_activity_trace.check_entry_log("superteam:executor", 3)
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        passed = (not ok) and any(("Entry" in e) or ("场记录" in e) or ("A5.1" in e) for e in errs)
        return passed, "executor 未写 Entry Log → discrepancy", f"ok={ok}, errs={errs[:1]}", ""
    return Case("A5.1-entry-missing", "Entry Log 缺失被捕获", "A5", "A5.1 entry log required", fn)


def c_entry_log_wrong_path_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # executor Entry Log 里写了一个假路径 (文件不存在)
        ws.put(
            ".superteam/runs/smoke/activity-trace.md",
            ws.read(".superteam/runs/smoke/activity-trace.md") + """

## executor Entry — Gate 3
Gate read: Gate 3 (plan -> execute)
Key artifacts confirmed from gate checks:
- plan.md: /nonexistent/fake/plan.md
- feature-checklist.md: /also/fake/fc.md

MUST items I will work from:
- 用户点击按钮后看到欢迎信息
- 用户输入密码错误看到错误提示
""",
        )
        sys_path_saved = list(os.sys.path)
        from pathlib import Path as _P
        hooks_root = str(_P(__file__).resolve().parents[1])
        os.sys.path.insert(0, hooks_root)
        old_cwd = os.getcwd()
        os.chdir(ws.path)
        try:
            from hooks.validators import validator_activity_trace
            # Force reload-free: the lib caches cwd via find_superteam_root per-call, not module import
            ok, errs = validator_activity_trace.check_entry_log("superteam:executor", 3)
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        # Path doesn't exist on disk → fail
        passed = (not ok) and any("磁盘不存在" in e or "路径" in e for e in errs)
        return passed, "Entry Log 写假路径 → block (anti-hallucination)", f"ok={ok}, errs={[e[:80] for e in errs[:2]]}", ""
    return Case("A5.2a-entry-fake-path", "假路径说明未真读文件", "A5", "A5.2a path reality check", fn)


def c_entry_log_must_mismatch_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # Entry Log 列出的 MUST 与 plan.md 不一致
        rd = ws.path / ".superteam/runs/smoke"
        ws.put(
            ".superteam/runs/smoke/activity-trace.md",
            ws.read(".superteam/runs/smoke/activity-trace.md") + f"""

## executor Entry — Gate 3
Gate read: Gate 3 (plan -> execute)
Key artifacts confirmed from gate checks:
- plan.md: {rd}/plan.md
- feature-checklist.md: {rd}/feature-checklist.md

MUST items I will work from:
- 一个和 plan.md 不匹配的项目
""",
        )
        sys_path_saved = list(os.sys.path)
        from pathlib import Path as _P
        hooks_root = str(_P(__file__).resolve().parents[1])
        os.sys.path.insert(0, hooks_root)
        old_cwd = os.getcwd()
        os.chdir(ws.path)
        try:
            from hooks.validators import validator_activity_trace
            # Force reload-free: the lib caches cwd via find_superteam_root per-call, not module import
            ok, errs = validator_activity_trace.check_entry_log("superteam:executor", 3)
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        passed = (not ok) and any("MUST" in e for e in errs)
        return passed, "MUST 清单与 plan.md 不一致 → block", f"ok={ok}, errs={[e[:80] for e in errs[:2]]}", ""
    return Case("A5.2b-entry-must-mismatch", "MUST 清单不一致说明凭印象做事", "A5", "A5.2b MUST reconciliation", fn)


def c_plan_must_multi_category_parse() -> Case:
    def fn(ws: Workspace):
        plan = """# plan.md

## Delivery Scope

### 功能 (来源: feature-checklist.md)
- MUST [F-001]: 用户点击登录看到欢迎页
- MUST [F-002]: 密码错误显示提示

### API endpoint
- MUST [API-matrix]: GET /api/transactions/matrix
- MUST [API-drill]: GET /drill-down

### Migration
- MUST [MIG-010]: bank_transactions 扩展
"""
        from pathlib import Path as _P
        sys_path_saved = list(os.sys.path)
        os.sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
        try:
            from hooks.lib import parser as _parser
            items = _parser.plan_must_items_structured(plan)
            cats = _parser.plan_must_categories(plan)
        finally:
            os.sys.path[:] = sys_path_saved
        has_feat = any(it.must_id == "F-001" and "功能" in it.category for it in items)
        has_api = any(it.must_id == "API-matrix" for it in items)
        has_mig = any(it.must_id == "MIG-010" for it in items)
        passed = has_feat and has_api and has_mig and len(items) == 5
        return passed, "多类 MUST 正确解析为 5 项 3 类", f"items={len(items)}, cats={list(cats.keys())}", ""
    return Case("A5.4-parse-multi", "多类 MUST 解析", "A5", "A5.4 multi-category parsing", fn)


def c_exec_missing_must_id_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # 写多类 plan
        ws.put(".superteam/runs/smoke/plan.md", """# plan.md

## Delivery Scope

### 功能
- MUST [F-001]: 用户点击按钮后看到欢迎信息
- MUST [F-002]: 用户输入密码错误看到错误提示

### API
- MUST [API-matrix]: GET /api/transactions/matrix

## Task T1.A
- objective: implement all
- target files: src/
- implementation steps: red -> green
- verification commands: pytest
- done signal: tests pass
""")
        # execution.md 只做了 F-001, 漏 F-002 和 API-matrix
        ws.put(".superteam/runs/smoke/execution.md", """# execution.md

## Feature F-001 用户点击按钮后看到欢迎信息
Status: COMPLETE

### RED evidence
FAILED

### GREEN evidence
passed

## Execution Summary
Features completed: 1 of 1
TDD exception in effect: NO
""")
        from pathlib import Path as _P
        sys_path_saved = list(os.sys.path)
        os.sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
        old_cwd = os.getcwd()
        os.chdir(str(ws.path))
        try:
            from hooks.validators import validator_execution
            ok, errs = validator_execution.run()
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        # Should complain about missing F-002 and API-matrix
        passed = (not ok) and any("F-002" in e or "API-matrix" in e for e in errs)
        return passed, "execution.md 缺 F-002/API-matrix section → discrepancy", f"ok={ok}, errs={[e[:80] for e in errs[:3]]}", ""
    return Case("A5.4-exec-missing-id", "execution 漏某类 MUST → 发现", "A5", "A5.4 execution ID reconciliation", fn)


def c_plan_must_no_id_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="design")
        ws.put(".superteam/runs/smoke/plan.md", """# plan.md

## Delivery Scope

- MUST: 项 1
- MUST: 项 2
- MUST: 项 3
- MUST: 项 4
- MUST: 项 5

## Task T1.A
- objective: x
- target files: src/a.py
- implementation steps: red -> green
- verification commands: pytest
- done signal: tests pass
""")
        from pathlib import Path as _P
        sys_path_saved = list(os.sys.path)
        os.sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
        old_cwd = os.getcwd()
        os.chdir(str(ws.path))
        try:
            from hooks.validators import validator_plan
            ok, errs = validator_plan.run()
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        # Legacy all-auto-id plan should pass soft (all auto-id is OK)
        # but plan without feature-checklist traceback + has MUST that don't match → still flag
        # Here feature-checklist has 2 items ('用户点击按钮后...' etc) — none of '项 X' match so errs will have fc tracing issues
        passed = not ok
        return passed, "全部自由文本 MUST + 与 fc 无关 → validator_plan 报错", f"ok={ok}, err_count={len(errs)}", ""
    return Case("A5.4-plan-no-id", "plan MUST 全自由文本且与 fc 无关 → 报错", "A5", "A5.4 plan ID requirement", fn)


def c_orch_decision_missing_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # No Orchestrator Decision section in activity-trace → spawn executor should block
        res = invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        passed = res.blocked and "Decision" in res.reason
        return passed, "缺 Orchestrator Decision → block spawn executor", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A5.3-decision-missing", "缺 OR decision log → block", "A5", "A5.3 orchestrator decision log", fn)


def c_orch_decision_unknown_unit_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # Plan has C00..C15; pretend OR declares bogus C99
        ws.put(".superteam/runs/smoke/plan.md", """# plan.md

## Checkpoint Table

| Checkpoint | Theme |
|---|---|
| C00 | scout |
| C01 | impl |
| C02 | review |

## Task T1.A
- objective: x
- target files: src/a.py
- implementation steps: red -> green
- verification commands: pytest
- done signal: tests pass
""")
        ws.put(".superteam/runs/smoke/activity-trace.md",
               ws.read(".superteam/runs/smoke/activity-trace.md") + """

## Orchestrator Decision — Fake checkpoint
Unit id: C99
MUST items to deliver:
- 瞎猜的项目
""")
        res = invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        passed = res.blocked and "C99" in res.reason
        return passed, "Decision 的 Unit id 不在 plan → block", f"blocked={res.blocked}, reason={res.reason[:150]}", res.stderr
    return Case("A5.3-decision-unknown", "OR 瞎创造 unit → block", "A5", "A5.3 unit must come from plan", fn)


def c_orch_decision_valid_allow() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(".superteam/runs/smoke/plan.md", """# plan.md

## Checkpoint Table

| Checkpoint | Theme |
|---|---|
| C00 | scout |
| C01 | impl |

## Task T1.A
- objective: implement F-001
- target files: src/a.py
- implementation steps: red -> green -> refactor
- verification commands: pytest
- done signal: tests pass

Delivery scope:
- MUST: 用户点击按钮后看到欢迎信息
- MUST: 用户输入密码错误看到错误提示
""")
        rd = ws.path / ".superteam/runs/smoke"
        ws.put(".superteam/runs/smoke/activity-trace.md",
               ws.read(".superteam/runs/smoke/activity-trace.md") + f"""

## Orchestrator Decision — Checkpoint C01 impl
Unit id: C01
Plan section: plan.md § Checkpoint C01
MUST items to deliver:
- 用户点击按钮后看到欢迎信息
- 用户输入密码错误看到错误提示
Justification: C00 已完成 scout, C01 是下一个 checkpoint

## executor Entry — Gate 3
Gate read: Gate 3 (plan -> execute)
Key artifacts confirmed from gate checks:
- plan.md: {rd}/plan.md
- feature-checklist.md: {rd}/feature-checklist.md

MUST items I will work from:
- 用户点击按钮后看到欢迎信息
- 用户输入密码错误看到错误提示

TDD exception in effect: NO
""")
        res = invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        passed = not res.blocked
        return passed, "合法 Decision + Entry Log → allow", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A5.3-decision-valid", "合法 OR decision → allow", "A5", "A5.3 happy path", fn)


def c_entry_log_complete_allow() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        rd = ws.path / ".superteam/runs/smoke"
        ws.put(
            ".superteam/runs/smoke/activity-trace.md",
            ws.read(".superteam/runs/smoke/activity-trace.md") + f"""

## executor Entry — Gate 3
Gate read: Gate 3 (plan -> execute)
Key artifacts confirmed from gate checks:
- plan.md: {rd}/plan.md
- feature-checklist.md: {rd}/feature-checklist.md

MUST items I will work from:
- 用户点击按钮后看到欢迎信息
- 用户输入密码错误看到错误提示

TDD exception in effect: NO
""",
        )
        sys_path_saved = list(os.sys.path)
        from pathlib import Path as _P
        hooks_root = str(_P(__file__).resolve().parents[1])
        os.sys.path.insert(0, hooks_root)
        old_cwd = os.getcwd()
        os.chdir(ws.path)
        try:
            from hooks.validators import validator_activity_trace
            # Force reload-free: the lib caches cwd via find_superteam_root per-call, not module import
            ok, errs = validator_activity_trace.check_entry_log("superteam:executor", 3)
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        passed = ok
        return passed, "完整 Entry Log + 正确路径 + MUST 对账 → pass", f"ok={ok}, errs={errs}", ""
    return Case("A5.2-entry-complete", "完整 Entry Log 通过", "A5", "A5.2 happy path", fn)


def c_subjective_words_review() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="review")
        bad = "verdict: CLEAR_WITH_CONCERNS\nThe implementation probably works but looks fine overall."
        res = invoke("pre_tool", {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"{ws.path}/.superteam/runs/smoke/review.md",
                "content": bad,
            },
        }, cwd=ws.path)
        passed = res.blocked and "appears" in res.reason.lower() or "seems" in res.reason.lower() or "probably" in res.reason.lower() or "looks" in res.reason.lower()
        return passed, "review.md 含 probably/looks fine → block", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A18.1-subjective", "review.md 主观词拦截", "A18", "A18.1 subjective language", fn)


def c_subjective_words_backtick_exempt() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="review")
        ok = "verdict: CLEAR\nexecution.md line 42: `should pass` (user-reported language)"
        res = invoke("pre_tool", {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"{ws.path}/.superteam/runs/smoke/review.md",
                "content": ok,
            },
        }, cwd=ws.path)
        passed = not res.blocked
        return passed, "`should pass` backtick 引用 → allow", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A18.1-backtick-exempt", "backtick 引用豁免", "A18", "A18.1 exempt", fn)


def c_ui_contract_not_declared_inactive() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute", ui_weight="ui-standard")
        # 没有 ui-intent.md → hook 不激活
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({"active_feature_id": "F-001", "features": {"F-001": {"state": "RED_LOCKED"}}}),
        )
        css = 'body { font-family: Inter, sans-serif; }'
        res = invoke("pre_tool", pre_tool_write("src/styles.css", css), cwd=ws.path)
        # 没有 ui-intent → 不拦字体
        passed = not res.blocked
        return passed, "ui-intent.md 未声明 → hook 不激活 (决策 2 核心)", f"blocked={res.blocked}", res.stderr
    return Case("B1.1-ui-inactive", "项目未声明契约时 hook 不干预", "B1", "B1.1 inactive default", fn)


def c_ui_contract_violation() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute", ui_weight="ui-standard")
        ws.put(".superteam/runs/smoke/ui-intent.md", _ui_intent_minimal())
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({"active_feature_id": "F-001", "features": {"F-001": {"state": "RED_LOCKED"}}}),
        )
        css = 'body { font-family: "Comic Sans MS", cursive; }'
        res = invoke("pre_tool", pre_tool_write("src/styles.css", css), cwd=ws.path)
        lr = res.reason.lower()
        passed = res.blocked and ("font" in lr or "字体" in res.reason or "typography" in lr)
        return passed, "字体不在 ui-intent 白名单 → block", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("B1.1-ui-violation", "违反项目声明字体契约 → block", "B1", "B1.1 typography contract", fn)


def c_ui_contract_respect_whitelist() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute", ui_weight="ui-standard")
        ws.put(".superteam/runs/smoke/ui-intent.md", _ui_intent_minimal())
        ws.put(
            ".superteam/state/feature-tdd-state.json",
            json.dumps({"active_feature_id": "F-001", "features": {"F-001": {"state": "RED_LOCKED"}}}),
        )
        css = 'body { font-family: "Satoshi", sans-serif; }'
        res = invoke("pre_tool", pre_tool_write("src/styles.css", css), cwd=ws.path)
        passed = not res.blocked
        return passed, "使用 ui-intent 声明的字体 → allow", f"blocked={res.blocked}", res.stderr
    return Case("B1.1-ui-allow", "符合项目字体契约 → allow", "B1", "B1.1 typography contract", fn)


def c_repair_cycle_cap() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute", repair_cycle_count=3)
        res = invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        passed = res.blocked and "repair" in res.reason.lower()
        return passed, "repair_cycle_count=3 → block executor spawn", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A4.3-repair-cap", "repair 循环上限触发升级", "A4", "A4.3 repair cap", fn)


def c_stop_finish_no_report() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="finish")
        # 没有 inspector report → Stop 应 block
        res = invoke("stop", stop_event(), cwd=ws.path)
        passed = res.blocked and ("report" in res.reason.lower() or "inspector" in res.reason.lower())
        return passed, "finish 无 inspector report → block Stop", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A11.4-stop-no-report", "Stop 硬闸要求 reviewer/inspector report", "A11", "A11.4 / Gate 7", fn)


def _write_full_finish_artifacts(ws: Workspace, slug: str) -> None:
    """Helper: write inspector report + finish.md + retrospective.md + rolling artifacts for Gate 7 pass."""
    sections = [
        "## Run Summary", "## Gate Enforcement Quality",
        "## Feature Checklist Test Results", "## Agent Behavior Compliance",
        "## Stage Continuity Record", "## Gate Checklist Coverage",
        "## Improvement Findings",
    ]
    content = "# Inspector Post-Run Report\n\n" + "\n\n(content)\n\n".join(sections) + "\n\n(content)\n"
    ws.put(f".superteam/inspector/reports/{slug}-report.md", content)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    ws.put(".superteam/inspector/health.json", json.dumps({"last_updated": now, "ok": True}))
    ws.put(".superteam/inspector/insights.md", f"# Insights\n\nrun slug={slug}\n- F-001 observed")
    ws.put(".superteam/inspector/improvement-backlog.md", f"# Backlog\n\nrun slug={slug}\n- (none)")
    ws.put(f".superteam/runs/{slug}/finish.md", f"""# finish.md

reviewer_report_acknowledged: true

## Acknowledgments
- F-001: acknowledged — Source: inspector report
""")
    ws.put(f".superteam/runs/{slug}/retrospective.md", f"""# retrospective.md

improvement_action: 继续优化 plan 覆盖率
""")


def c_stop_finish_with_report() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="finish")
        _write_full_finish_artifacts(ws, "smoke")
        res = invoke("stop", stop_event(), cwd=ws.path)
        passed = not res.blocked
        return passed, "所有 Gate 7 产物齐全 → allow Stop", f"blocked={res.blocked}, reason={res.reason[:120]}", res.stderr
    return Case("A11.4-stop-ok", "完整 Gate 7 产物允许 Stop", "A11", "A11.4 / Gate 7 happy", fn)


def c_finish_no_acknowledge_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="finish")
        _write_full_finish_artifacts(ws, "smoke")
        # 重写 finish.md 去掉 acknowledgment flag
        ws.put(".superteam/runs/smoke/finish.md", "# finish.md\n\n(空壳，没 acknowledge)\n")
        res = invoke("stop", stop_event(), cwd=ws.path)
        passed = res.blocked and "acknowledge" in res.reason.lower()
        return passed, "finish.md 无 acknowledgment → block Stop", f"blocked={res.blocked}, reason={res.reason[:150]}", res.stderr
    return Case("A17.1-finish-no-ack", "finish.md 空壳不 acknowledge → block", "A17", "A17.1 finish acknowledge", fn)


def c_retrospective_blank_improvement_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="finish")
        _write_full_finish_artifacts(ws, "smoke")
        ws.put(".superteam/runs/smoke/retrospective.md", "# retrospective.md\n\nimprovement_action: TBD\n")
        res = invoke("stop", stop_event(), cwd=ws.path)
        passed = res.blocked and ("improvement" in res.reason.lower() or "retrospective" in res.reason.lower())
        return passed, "retrospective improvement_action 为 TBD → block Stop", f"blocked={res.blocked}, reason={res.reason[:150]}", res.stderr
    return Case("Gate7-retro-blank", "retrospective 空白 improvement_action → block", "A17", "Gate 7 check 5", fn)


def c_rolling_artifacts_missing_block() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="finish")
        _write_full_finish_artifacts(ws, "smoke")
        # 删除 insights.md 模拟未更新
        (ws.path / ".superteam/inspector/insights.md").unlink()
        res = invoke("stop", stop_event(), cwd=ws.path)
        passed = res.blocked and ("insights" in res.reason.lower() or "rolling" in res.reason.lower())
        return passed, "insights.md 缺失 → block Stop (A7.20)", f"blocked={res.blocked}, reason={res.reason[:150]}", res.stderr
    return Case("A7.20-rolling-missing", "rolling artifact 未更新 → block (决策 1)", "A7", "A7.20 rolling artifacts", fn)


def c_post_executor_chain_hint() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(".superteam/runs/smoke/execution.md", "## Feature: 用户点击按钮后看到欢迎信息\nStatus: COMPLETE\n### RED evidence\nFAILED\n### GREEN evidence\npassed\n")
        res = invoke("post_tool", post_tool_agent("superteam:executor"), cwd=ws.path)
        msg = res.decision.get("systemMessage", "") or res.reason
        passed = "simplifier" in msg.lower() or "polish" in msg.lower()
        return passed, "executor 结束 → 引导 spawn simplifier/polish", f"msg={msg[:120]}", res.stderr
    return Case("A14.1-chain-hint", "executor 结束引导 polish 链", "A14", "A14.1 polish chain", fn)


def c_trace_auto_emit() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        # 模拟 spawn 前 pre_tool emit agent_spawn, spawn 后 post_tool emit agent_stop
        invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        invoke("post_tool", post_tool_agent("superteam:executor"), cwd=ws.path)
        trace_path = ws.path / ".superteam/inspector/traces/smoke.jsonl"
        events: list[dict[str, Any]] = []
        if trace_path.exists():
            for line in trace_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
        has_spawn = any(e.get("event_type") == "agent_spawn" for e in events)
        has_stop = any(e.get("event_type") == "agent_stop" for e in events)
        passed = has_spawn and has_stop
        return passed, "hook 自动写 agent_spawn + agent_stop 到 inspector trace", f"spawn={has_spawn}, stop={has_stop}, events={len(events)}", ""
    return Case("A11.3-trace-auto", "Inspector trace 由 hook 自动写", "A11", "A11.3/A11.8", fn)


def c_validator_execution_missing_red() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(".superteam/runs/smoke/execution.md", "## Feature: 用户点击按钮后看到欢迎信息\nStatus: COMPLETE\n")
        # 触发 PostToolUse Edit 的 validator
        res = invoke(
            "post_tool",
            post_tool_edit(f"{ws.path}/.superteam/runs/smoke/execution.md"),
            cwd=ws.path,
        )
        # 检查 trace 中是否记了 discrepancy
        trace_path = ws.path / ".superteam/inspector/traces/smoke.jsonl"
        found_disc = False
        if trace_path.exists():
            for line in trace_path.read_text(encoding="utf-8").splitlines():
                if "RED" in line or "GREEN" in line or "evidence" in line or "discrepancy" in line.lower():
                    found_disc = True
                    break
        passed = found_disc
        return passed, "execution.md COMPLETE 缺 RED → 写 discrepancy", f"discrepancy 记录={found_disc}", res.stderr
    return Case("A7.8-execution-validator", "execution.md 自动校验发现缺 RED", "A7", "A7.8 / B-EX-2", fn)


def c_plan_progress_initialize() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(".superteam/runs/smoke/plan.md", """# plan.md
## Delivery Scope

### 功能
- MUST [F-001]: 用户点击按钮后看到欢迎信息
- MUST [F-002]: 密码错误

### API
- MUST [API-1]: GET /api/x

## Task T1.A
- objective: x
- target files: src/
- steps: red -> green
- verification: pytest
- done: tests pass
""")
        from pathlib import Path as _P
        sys_path_saved = list(os.sys.path)
        os.sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
        old_cwd = os.getcwd()
        os.chdir(str(ws.path))
        try:
            from hooks.lib import plan_progress
            data = plan_progress.initialize()
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        items = data.get("items", {})
        passed = (
            "F-001" in items and items["F-001"]["status"] == "PENDING"
            and "API-1" in items and items["API-1"]["category"] == "API"
            and bool(data.get("plan_sha256"))
        )
        return passed, "G3 关闭后 plan-progress 正确初始化", f"items={list(items.keys())}", ""
    return Case("A5.5-init", "plan-progress 初始化", "A5", "A5.5 G3 close init", fn)


def c_plan_progress_block_completed_unit() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(".superteam/runs/smoke/plan.md", """# plan.md
## Delivery Scope

### 功能
- MUST [F-001]: 用户点击按钮后看到欢迎信息
- MUST [F-002]: 用户输入密码错误看到错误提示

## Task T1.A
- objective: x
- target files: src/
- steps: red -> green
- verification: pytest
- done: tests pass
""")
        # Pre-mark F-001 as COMPLETE in plan-progress
        from pathlib import Path as _P
        sys_path_saved = list(os.sys.path)
        os.sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
        old_cwd = os.getcwd()
        os.chdir(str(ws.path))
        try:
            from hooks.lib import plan_progress
            plan_progress.initialize()
            plan_progress.mark("F-001", "COMPLETE", evidence={"note": "already done"})
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        # OR writes Decision pointing to F-001 (which is already COMPLETE)
        ws.put(".superteam/runs/smoke/activity-trace.md",
               ws.read(".superteam/runs/smoke/activity-trace.md") + """

## Orchestrator Decision — 重做已完成 F-001
Unit id: F-001
MUST items to deliver:
- 用户点击按钮后看到欢迎信息
- 用户输入密码错误看到错误提示
""")
        res = invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        passed = res.blocked and ("F-001" in res.reason and "COMPLETE" in res.reason)
        return passed, "OR 尝试重做 COMPLETE 的 F-001 → block", f"blocked={res.blocked}, reason={res.reason[:150]}", res.stderr
    return Case("A5.5-block-complete", "progress=COMPLETE 的 Unit 不可重 spawn", "A5", "A5.5 resumption guard", fn)


def c_resume_directive_per_stage() -> Case:
    def fn(ws: Workspace):
        import json as _json
        stages_expected = [
            ("execute", "G4"),
            ("review", "G5"),
            ("verify", "G6"),
            ("finish", "G7"),
        ]
        missing: list[str] = []
        for stage, expected_marker in stages_expected:
            _install_full_run(ws, slug="smoke", current_stage=stage)
            # Ensure status=active
            cr = ws.read_json(".superteam/state/current-run.json")
            cr["status"] = "active"
            ws.put(".superteam/state/current-run.json", _json.dumps(cr))
            res = invoke("session_start", session_start(), cwd=ws.path)
            ctx = res.decision.get("hookSpecificOutput", {}).get("additionalContext", "")
            if expected_marker not in ctx:
                missing.append(f"{stage}->{expected_marker}")
            if "无需用户确认" not in ctx and "no user confirmation" not in ctx.lower():
                missing.append(f"{stage}-no-user-confirmation-missing")
        passed = not missing
        return passed, "G4-G7 resume directive 每阶段明确下一步 + 不需用户确认", f"missing={missing}", ""
    return Case("A5.7-resume-directive", "G4-G7 自动化 resume 指令", "A5", "A5.7 auto-resume per stage", fn)


def c_plan_progress_session_injection() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(".superteam/runs/smoke/plan.md", """# plan.md
## Delivery Scope

### 功能
- MUST [F-001]: 用户点击按钮后看到欢迎信息
- MUST [F-002]: 密码错误显示提示

### API
- MUST [API-1]: GET /api/x
""")
        from pathlib import Path as _P
        sys_path_saved = list(os.sys.path)
        os.sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
        old_cwd = os.getcwd()
        os.chdir(str(ws.path))
        try:
            from hooks.lib import plan_progress
            plan_progress.initialize()
            plan_progress.mark("F-001", "COMPLETE")
        finally:
            os.chdir(old_cwd)
            os.sys.path[:] = sys_path_saved
        res = invoke("session_start", session_start(), cwd=ws.path)
        context = res.decision.get("hookSpecificOutput", {}).get("additionalContext", "")
        passed = (
            "PENDING" in context and "F-002" in context
            and "COMPLETE" in context and "F-001" in context
        )
        return passed, "SessionStart 注入含 PENDING + COMPLETE 摘要", f"context[:200]={context[:200]}", res.stderr
    return Case("A5.5-session-injection", "中断恢复 session 注入剩余清单", "A5", "A5.5 SessionStart inject", fn)


def c_plan_progress_observer_auto_mark() -> Case:
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(".superteam/runs/smoke/plan.md", """# plan.md
## Delivery Scope

### 功能
- MUST [F-001]: 用户点击按钮后看到欢迎信息
- MUST [F-002]: 密码错误
""")
        from pathlib import Path as _P
        sys_path_saved = list(os.sys.path)
        os.sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
        os.chdir(str(ws.path))
        try:
            from hooks.lib import plan_progress
            plan_progress.initialize()
        finally:
            os.sys.path[:] = sys_path_saved
        # Set active feature F-001 at RED_LOCKED and simulate pytest all-pass
        ws.put(".superteam/state/feature-tdd-state.json", json.dumps({
            "active_feature_id": "F-001",
            "features": {"F-001": {"state": "RED_LOCKED", "green_attempts": 0}},
        }))
        res = invoke(
            "post_tool",
            post_tool_bash("pytest", "10 passed in 0.5s\n"),
            cwd=ws.path,
        )
        # Read plan-progress
        pp = ws.read_json(".superteam/state/plan-progress.json")
        status = pp.get("items", {}).get("F-001", {}).get("status", "")
        passed = status == "COMPLETE"
        os.chdir(os.path.dirname(str(ws.path)))
        return passed, "feature GREEN → plan-progress 自动 mark COMPLETE", f"F-001 status={status}", res.stderr
    return Case("A5.5-auto-mark", "Observer 自动更新 progress", "A5", "A5.5 green auto-mark", fn)


def c_matrix_selfcheck_passes() -> Case:
    def fn(ws: Workspace):
        import subprocess, sys, os as _os
        from pathlib import Path
        script = Path(__file__).resolve().parents[1] / "hooks" / "matrix_selfcheck.py"
        env = _os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
        )
        stdout = proc.stdout or ""
        passed = proc.returncode == 0 and "MATRIX OK" in stdout
        return passed, "matrix_selfcheck 30 个 checker 全找到且可 import", stdout.strip()[:200], proc.stderr or ""
    return Case("SC-matrix-ok", "Matrix self-check", "SC", "Matrix sync", fn)


def c_tdd_init_from_execution_md() -> Case:
    """V4.6.4: PostToolUse(Edit execution.md) auto-inits active_feature_id.

    Guards against the V4.6.3 init deadlock — without this hook, every new run
    entering execute stage would hit gate_tdd_redgreen with no active feature
    and no way to set one.
    """
    def fn(ws: Workspace):
        _install_full_run(ws, slug="smoke", current_stage="execute")
        ws.put(
            ".superteam/runs/smoke/execution.md",
            """# execution.md

## Feature: welcome-banner
Status:

### RED evidence
(pending)
""",
        )
        # No feature-tdd-state.json seeded — mirrors a fresh execute stage.
        exec_path = ws.path / ".superteam" / "runs" / "smoke" / "execution.md"
        res = invoke("post_tool", post_tool_edit(str(exec_path)), cwd=ws.path)
        tdd = ws.read_json(".superteam/state/feature-tdd-state.json")
        fid = tdd.get("active_feature_id")
        feat_state = (tdd.get("features", {}).get(fid or "") or {}).get("state")
        passed = fid == "welcome-banner" and feat_state == "PENDING"
        return passed, "Edit execution.md → active_feature_id=welcome-banner, state=PENDING", f"fid={fid!r}, state={feat_state!r}", res.stderr
    return Case("A6.8-tdd-init-from-exec", "V4.6.4 PostToolUse 自动 init active_feature_id", "A6", "A6.8 V4.6.4 init deadlock fix", fn)


ALL_CASES: list[Case] = [
    c_matrix_selfcheck_passes(),
    c_session_start_injection(),
    c_pre_tool_agent_wrong_stage(),
    c_pre_tool_agent_valid_stage(),
    c_gate_commit_no_verification(),
    c_gate_commit_fail_verdict(),
    c_gate_commit_pass_allow(),
    c_gate_commit_override_env(),
    c_tdd_pending_blocks_prod(),
    c_tdd_red_locked_allows_prod(),
    c_tdd_test_path_allows(),
    c_tdd_observer_red_transition(),
    c_tdd_observer_green_transition(),
    c_tdd_init_from_execution_md(),
    c_gate_file_scope_clarify(),
    c_gate_file_scope_execute_prod(),
    c_entry_log_missing_block(),
    c_entry_log_wrong_path_block(),
    c_entry_log_must_mismatch_block(),
    c_entry_log_complete_allow(),
    c_orch_decision_missing_block(),
    c_orch_decision_unknown_unit_block(),
    c_orch_decision_valid_allow(),
    c_plan_must_multi_category_parse(),
    c_exec_missing_must_id_block(),
    c_plan_must_no_id_block(),
    c_plan_progress_initialize(),
    c_plan_progress_block_completed_unit(),
    c_plan_progress_session_injection(),
    c_plan_progress_observer_auto_mark(),
    c_resume_directive_per_stage(),
    c_subjective_words_review(),
    c_subjective_words_backtick_exempt(),
    c_ui_contract_not_declared_inactive(),
    c_ui_contract_violation(),
    c_ui_contract_respect_whitelist(),
    c_repair_cycle_cap(),
    c_stop_finish_no_report(),
    c_stop_finish_with_report(),
    c_finish_no_acknowledge_block(),
    c_retrospective_blank_improvement_block(),
    c_rolling_artifacts_missing_block(),
    c_post_executor_chain_hint(),
    c_trace_auto_emit(),
    c_validator_execution_missing_red(),
]


def run_all() -> list[CaseResult]:
    results: list[CaseResult] = []
    for case in ALL_CASES:
        ws = make_workspace()
        try:
            passed, expected, actual, stderr = case.fn(ws)
            results.append(
                CaseResult(
                    case_id=case.id,
                    title=case.title,
                    purpose=case.purpose,
                    passed=bool(passed),
                    expected=expected,
                    actual=actual,
                    hook_stderr=stderr,
                    category=case.category,
                )
            )
        except Exception as e:
            results.append(
                CaseResult(
                    case_id=case.id,
                    title=case.title,
                    purpose=case.purpose,
                    passed=False,
                    expected="(运行不抛异常)",
                    actual=f"EXCEPTION: {type(e).__name__}: {e}",
                    hook_stderr="",
                    category=case.category,
                )
            )
        finally:
            destroy_workspace(ws)
    return results
