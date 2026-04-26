"""A6.1-A6.9, A15.1-2: TDD red→green state machine enforcement.

States per feature: PENDING -> RED_LOCKED -> GREEN_CONFIRMED.

PreToolUse(Edit/Write) on production code paths:
- feature state=PENDING -> BLOCK (must write failing test first)
- state=RED_LOCKED -> ALLOW (green phase, write production code)
- state=GREEN_CONFIRMED -> BLOCK (feature complete, switch feature)

tdd_exception=YES in current-run.json downgrades to warning only.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..lib import parser, state


# Production-code path heuristics
PROD_CODE_EXT = re.compile(r"\.(py|js|jsx|ts|tsx|rs|go|java|rb|cs|php|swift|kt|kts|cpp|c|h|hpp|vue|svelte)$", re.IGNORECASE)
TEST_PATH_HINT = re.compile(
    r"(?i)(^|[/\\])(tests?|__tests?__|spec|specs|test)[/\\]|"
    r"\.(test|spec)\.[a-zA-Z0-9]+$|_test\.[a-zA-Z0-9]+$|_spec\.[a-zA-Z0-9]+$"
)


def is_production_code(path: str) -> bool:
    if not PROD_CODE_EXT.search(path):
        return False
    if TEST_PATH_HINT.search(path):
        return False
    return True


def check(tool_input: dict[str, Any]) -> tuple[bool, str]:
    # Only active during execute stage
    if state.current_stage() != "execute":
        return True, ""

    # tdd_exception short-circuit
    cr = state.read_current_run()
    if cr.get("tdd_exception") == "YES":
        return True, ""

    fp = str(tool_input.get("file_path", ""))
    if not fp or not is_production_code(fp):
        return True, ""

    feature_id, feat = state.get_active_feature()
    if not feature_id:
        return False, (
            "未识别到 active feature (execution.md 未添加对应 ## Feature 段或未更新 "
            "feature-tdd-state.json) — 先创建 feature section 再编辑生产代码 (A6.8 violation)"
        )

    st = feat.get("state", "PENDING")
    if st == "PENDING":
        return False, (
            f"Feature {feature_id} state=PENDING — 必须先写 failing test 并跑出 RED 证据 "
            f"才能编辑生产代码 {fp}. (A6.1/A6.2 violation)"
        )
    if st == "GREEN_CONFIRMED":
        return False, (
            f"Feature {feature_id} 已 GREEN_CONFIRMED — 要改动请切换新 feature "
            f"(在 execution.md 新增 ## Feature 段). 当前禁止再改 (A15.2)"
        )
    if st == "RED_LOCKED":
        attempts = int(feat.get("green_attempts", 0))
        if attempts >= 3:
            return False, (
                f"Feature {feature_id} 已失败 3 次转 GREEN — 必须停止并写 BLOCKED escalation (A6.9)"
            )
        return True, ""
    # Unknown state: allow but warn
    return True, ""
