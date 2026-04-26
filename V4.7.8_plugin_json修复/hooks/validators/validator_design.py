"""A7.4 / Gate 2 check 5,6: design.md — selected direction + rejected alternatives."""
from __future__ import annotations

from pathlib import Path

from ..lib import parser, state


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "design.md"
    text = parser.read_text(path)
    if not text:
        return False, ["design.md 不存在或为空"]
    errs: list[str] = []

    if not parser.has_section(text, r"selected\s+(direction|solution)|选中(方向|方案)"):
        errs.append("缺失选中方向段 (必须有 Selected Direction 或 选中方案)")
    if not parser.has_section(text, r"rejected\s+(alternatives|options)|被拒方案|已否决"):
        errs.append("缺失被拒方案段 (必须列出 Rejected Alternatives 及理由)")

    return not errs, errs
