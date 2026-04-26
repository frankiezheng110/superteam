"""A7.6 / Gate 2 checks 10-12 / A2.4: feature-checklist.md — behavior-level items.

B-PL-1b guarantee: every item is a single observable behavior + test_type + test_tool.
Gate 2 close also requires a user-confirmation line in activity-trace.md.
"""
from __future__ import annotations

from pathlib import Path

from ..lib import parser, state


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "feature-checklist.md"
    text = parser.read_text(path)
    if not text:
        return False, ["feature-checklist.md 不存在或为空"]
    errs: list[str] = []

    items = parser.parse_feature_checklist(text)
    if not items:
        errs.append("feature-checklist.md 没有任何功能条目")
        return False, errs

    for item in items:
        if not item.is_behavior:
            errs.append(
                f"{item.id} 看起来是阶段/模块/分类名而非单一可观察行为: {item.behavior[:60]}"
            )
        if not item.test_type:
            errs.append(f"{item.id} 缺 test_type (必须是 unit/integration/E2E)")
        if not item.test_tool:
            errs.append(f"{item.id} 缺 test_tool (例如 pytest/jest/cargo-test)")

    # A2.4 user confirmation (read activity-trace)
    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if rd:
        trace_text = parser.read_text(rd / "activity-trace.md")
        if (
            "feature-checklist" in trace_text.lower() or "功能清单" in trace_text
        ) and not parser.has_user_approval(trace_text):
            errs.append("feature-checklist.md 缺用户确认记录 (activity-trace 中无 approved_by: user)")

    return not errs, errs
