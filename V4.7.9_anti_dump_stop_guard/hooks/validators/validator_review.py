"""A7.10 / Gate 5 / B-IN-1..5 / A16 (Reviewer 8+1 Checklist): review.md validation.

Post-swap: reviewer (中文 审查者) writes review.md with verdict CLEAR / CLEAR_WITH_CONCERNS / BLOCK.
A6.12: cannot declare TDD "N/A" without orchestrator-issued waiver.
A18: subjective-language discipline enforced separately by gate_subjective_language.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


CHECKLIST_DIMENSIONS = (
    r"Functional\s+Correctness|功能正确性",
    r"Plan\s+Fidelity|计划保真",
    r"Code\s+(and|&)\s+Design\s+Quality|代码质量|设计质量",
    r"Security|安全",
    r"Artifact\s+Completeness|产物完整",
    r"Error\s+(and|&)\s+Fix\s+Quality|修复质量",
    r"TDD\s+(And|&)?\s*Test\s+Coverage|TDD|测试覆盖",
    r"UI\s+Quality|UI\s+质量",
    r"Immediate\s+Blocker\s+Reporting|立即上报",
)


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "review.md"
    text = parser.read_text(path)
    if not text:
        return False, ["review.md 不存在或为空"]
    errs: list[str] = []

    # Verdict
    verdict = parser.review_verdict(text)
    if verdict not in ("CLEAR", "CLEAR_WITH_CONCERNS", "BLOCK"):
        errs.append("review.md verdict 非 CLEAR/CLEAR_WITH_CONCERNS/BLOCK (或缺失)")

    # Delivery Scope Check
    if not parser.has_section(text, r"delivery\s+scope\s+check|交付范围检查"):
        errs.append("缺 Delivery Scope Check 段 (逐 MUST 项状态)")

    # TDD Gate section
    tdd_section = parser.extract_section(text, r"TDD\s+gate|TDD\s+门控")
    if not tdd_section:
        errs.append("缺 TDD Gate 段")
    else:
        # A6.12: cannot declare N/A without citing orchestrator waiver
        if re.search(r"(?i)\bN/A\b|not\s+applicable", tdd_section):
            cr = state.read_current_run()
            has_waiver = cr.get("tdd_exception") == "YES" or re.search(
                r"(?i)tdd[_\s-]*exception|orchestrator[_\s-]*waiver", tdd_section
            )
            if not has_waiver:
                errs.append("TDD Gate 写 N/A 但无 orchestrator 签发的 tdd_exception 引用 (A6.12 violation)")

    # MUST missing should be BLOCK not MINOR
    scope_body = parser.extract_section(text, r"delivery\s+scope\s+check|交付范围检查")
    if scope_body:
        if re.search(r"(?i)(MISSING|未交付)", scope_body):
            if not re.search(r"(?i)\bBLOCK\b", scope_body):
                errs.append("交付范围有 MISSING 项但未标 BLOCK (不得降为 MINOR/CONCERN)")

    # UI quality gate (if ui-standard/critical)
    uw = state.ui_weight()
    if uw in ("ui-standard", "ui-critical"):
        if not parser.has_section(text, r"UI\s+Quality\s+Gate|UI\s+质量门"):
            errs.append(f"ui_weight={uw} 缺 UI Quality Gate 段")

    # Checklist coverage (A16.* - 8+1 dimensions)
    cov = parser.extract_section(text, r"Checklist\s+Coverage|清单覆盖")
    if not cov:
        errs.append("缺 Checklist Coverage 段 (8+1 dimensions)")
    else:
        missing_dims: list[str] = []
        for dim in CHECKLIST_DIMENSIONS:
            if not re.search(rf"(?im){dim}", cov):
                missing_dims.append(dim.split("|")[0])
        if missing_dims:
            errs.append(f"Checklist Coverage 缺维度: {', '.join(missing_dims[:3])}{'...' if len(missing_dims)>3 else ''}")

    return not errs, errs
