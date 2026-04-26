"""A7.2 / Gate 2 check 2, 7: solution-options.md structural validation."""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "solution-options.md"
    text = parser.read_text(path)
    if not text:
        return False, ["solution-options.md 不存在或为空"]
    errs: list[str] = []

    # At least 2 options (heading count or bullet count)
    option_heads = re.findall(r"(?im)^#{2,3}\s+Option\s+\d|^(?im)#{2,3}\s+方案\s*\d", text)
    bullet_options = re.findall(r"(?m)^\s*[-*]\s+(?:Option|方案)\s*\d", text)
    total_options = len(option_heads) + len(bullet_options)
    if total_options < 2:
        errs.append(f"选项数 {total_options} < 2 (必须至少提供 2 个候选方案让用户做选择)")

    # User decision recorded
    if not re.search(r"(?im)(user\s+decision|用户决策|decided|approved_by\s*:\s*user)", text):
        errs.append("未记录用户决策 (缺 user_decision / 用户决策 / approved_by: user 段)")

    return not errs, errs
