"""A7.9 / Gate 4 check 9: polish.md post-polish fresh checks."""
from __future__ import annotations

from pathlib import Path

from ..lib import parser, state


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "polish.md"
    text = parser.read_text(path)
    if not text:
        return False, ["polish.md 不存在或为空 (execute 后必需)"]
    errs: list[str] = []

    if not parser.has_section(text, r"post[-\s]?polish\s+check|post-polish\s+checks|本地自检"):
        if "behavior-relevant" in text.lower() or "代码变更" in text or "behavior" in text.lower():
            errs.append("polish.md 提到代码变更但缺 post-polish 本地自检记录")

    return not errs, errs
