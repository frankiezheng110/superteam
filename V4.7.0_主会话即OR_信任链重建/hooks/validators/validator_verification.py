"""A7.11 / Gate 6 / B-VR-*: verification.md validation.

V1-V14 covered; A15.3 ui-critical + missing aesthetic evidence = INCOMPLETE;
A12.3 fix package required on FAIL.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


FIX_PACKAGE_FIELDS = (
    r"failed\s+requirement|失败需求",
    r"evidence\s+of\s+failure|失败证据",
    r"suspected\s+scope|可疑范围",
    r"(recommended\s+)?task\s+list|任务列表",
    r"re-?verification\s+command|重新验证命令",
)


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "verification.md"
    text = parser.read_text(path)
    if not text:
        return False, ["verification.md 不存在或为空"]
    errs: list[str] = []

    verdict = parser.verification_verdict(text)
    if verdict not in ("PASS", "FAIL", "INCOMPLETE"):
        errs.append("verification.md verdict 非 PASS/FAIL/INCOMPLETE")

    # Evidence summary / test run output
    if not parser.has_section(text, r"evidence\s+summary|证据摘要"):
        errs.append("缺 Evidence Summary 段")

    # Per-requirement status table
    if not re.search(r"(?i)requirement\s*[-_\s]*by\s*[-_\s]*requirement|逐需求状态|per[_\s-]*requirement", text):
        errs.append("缺逐需求状态表 (per-requirement status)")

    # delivery_confidence
    if not parser.verification_confidence(text):
        errs.append("缺 delivery_confidence (必须是 high/medium/low)")

    # Test execution evidence (not just compile)
    has_test_cmd = bool(re.search(
        r"(?i)\b(pytest|jest|vitest|cargo\s+test|go\s+test|npm\s+test|yarn\s+test|mvn\s+test|gradle\s+test|dotnet\s+test|rspec|phpunit|cypress\s+run|playwright\s+test|flutter\s+test)\b",
        text,
    ))
    has_compile_only = bool(re.search(r"(?i)\b(cargo\s+check|tsc\s+--noEmit|flutter\s+analyze)\b", text))
    if has_compile_only and not has_test_cmd:
        errs.append("证据仅引用编译命令 (cargo check / tsc --noEmit 等), 非 test 执行 (A6.13 V1 violation)")

    # A15.3 ui-critical + missing aesthetic evidence -> INCOMPLETE required
    uw = state.ui_weight()
    if uw == "ui-critical":
        has_aesth = bool(re.search(
            r"(?i)aesthetic\s+contract|anti[-\s]?pattern\s+gate|ui\s+intent\s+preservation", text
        ))
        if not has_aesth and verdict == "PASS":
            errs.append("ui-critical 缺审美证据, verdict 必须为 INCOMPLETE 而非 PASS (A15.3)")

    # A12.3 fix package on FAIL
    if verdict == "FAIL":
        fix_body = parser.extract_section(text, r"fix\s+package|修复包")
        if not fix_body:
            errs.append("verdict=FAIL 但缺 Fix Package 段 (A12.3)")
        else:
            for field in FIX_PACKAGE_FIELDS:
                if not re.search(rf"(?im){field}", fix_body):
                    errs.append(f"Fix Package 缺字段: {field.split('|')[0]}")

    return not errs, errs
