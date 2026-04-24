"""A7.1 / Gate 1 checks 3-8: project-definition.md structural validation."""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


REQUIRED_SECTIONS = (
    (r"objective|目标", "objective"),
    (r"constraints|约束", "constraints"),
    (r"non[-\s]?goals?|out[-\s]?of[-\s]?scope|非目标", "non-goals"),
)


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "project-definition.md"
    text = parser.read_text(path)
    if not text:
        return False, ["project-definition.md 不存在或为空"]
    errs: list[str] = []

    for regex, label in REQUIRED_SECTIONS:
        if not parser.has_section(text, regex):
            errs.append(f"缺失必需段: {label}")

    # ui_weight field
    m = re.search(r"(?im)^[-*\s]*ui[_\s-]*weight\s*[:=]\s*(ui-none|ui-standard|ui-critical)", text)
    if not m:
        errs.append("缺失 ui_weight 分类 (必须是 ui-none/ui-standard/ui-critical)")
    else:
        if m.group(1) in ("ui-standard", "ui-critical"):
            # design-thinking seeds
            for seed in (r"purpose", r"tone[_\s-]*seed", r"differentiation[_\s-]*seed"):
                if not re.search(rf"(?im){seed}", text):
                    errs.append(f"ui-standard/critical 项目缺 design thinking seed: {seed}")

    # initial feature scope
    if not parser.has_section(text, r"feature\s+scope|功能范围"):
        errs.append("缺失 feature scope (初始功能范围) 段")

    return not errs, errs
