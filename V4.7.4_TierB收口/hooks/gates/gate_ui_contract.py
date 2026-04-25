"""B1.* UI contract enforcement. Reads project's ui-intent.md; does NOT hardcode.

If project declared Typography/Color/Motion Contract, hook checks edits against
that declaration. If no declaration -> hook inactive for that dimension.
B6 (AP predefined blacklist) intentionally NOT implemented (作者决策 2026-04-24).
"""
from __future__ import annotations

from typing import Any

from ..lib import state, ui_grep


def check(tool_input: dict[str, Any]) -> tuple[bool, str]:
    if state.ui_weight() not in ("ui-standard", "ui-critical"):
        return True, ""

    fp = str(tool_input.get("file_path", ""))
    if not fp or not ui_grep.is_ui_file(fp):
        return True, ""

    new_content = tool_input.get("new_string") or tool_input.get("content") or ""
    if not new_content:
        return True, ""

    offender = ui_grep.check_typography_violation(new_content, fp)
    if offender:
        return False, (
            f"字体 '{offender}' 不在项目 ui-intent.md § Typography Contract 声明的白名单内。"
            f"要使用此字体，请先更新 ui-intent.md (B1.1)"
        )

    return True, ""
