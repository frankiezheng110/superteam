"""A7.8 / Gate 4 / B-EX-*: execution.md — per-feature RED/GREEN evidence.

Covers:
- A7.8, A15.1 (feature order vs plan), A15.2 (feature switch discipline)
- A4.4 (consecutive blocked threshold)
- B-EX-1..5 behaviors
"""
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
        path = rd / "execution.md"
    text = parser.read_text(path)
    if not text:
        return False, ["execution.md 不存在或为空"]
    errs: list[str] = []

    rd = Path(path).parent
    fc = rd / "feature-checklist.md"
    fc_text = parser.read_text(fc) if fc.exists() else ""
    fc_items = parser.parse_feature_checklist(fc_text)
    fc_count = len(fc_items)

    sections = parser.parse_execution_features(text)
    if not sections:
        errs.append("execution.md 未解析到任何 Feature section (检查 ## Feature 标题)")
    if fc_count and len(sections) < fc_count:
        errs.append(f"execution.md 仅 {len(sections)} 个 feature section, feature-checklist 有 {fc_count} 项 (有功能被静默跳过)")

    # Per-feature RED/GREEN
    blocked_tail = 0
    last_three_status: list[str] = []
    for sect in sections:
        status = (sect.status or "").upper()
        last_three_status.append(status)
        if status == "COMPLETE":
            if not sect.has_red:
                errs.append(f"Feature {sect.name}: COMPLETE 但缺 RED evidence")
            if not sect.has_green:
                errs.append(f"Feature {sect.name}: COMPLETE 但缺 GREEN evidence")
        elif status == "BLOCKED":
            if "attempt" not in sect.body.lower() and "needs from or" not in sect.body.lower():
                errs.append(f"Feature {sect.name}: BLOCKED 但缺 escalation block (需 attempts/Needs from OR)")
        elif status == "DEFERRED":
            if "deferred by or" not in sect.body.lower():
                errs.append(f"Feature {sect.name}: DEFERRED 但缺 OR decision (必须有 'Deferred by OR — reason: ...')")
        elif not status:
            errs.append(f"Feature {sect.name}: 状态缺失 (必须是 COMPLETE/BLOCKED/DEFERRED)")

    # A4.4 consecutive BLOCKED threshold
    if len(last_three_status) >= 3 and all(s == "BLOCKED" for s in last_three_status[-3:]):
        errs.append("连续 3 个 feature BLOCKED - 必须升级到用户 (禁止继续)")

    # Summary section
    if not parser.has_section(text, r"Execution\s+Summary|执行总结"):
        errs.append("缺 Execution Summary 段")
    else:
        summary = parser.extract_section(text, r"Execution\s+Summary|执行总结")
        if not re.search(r"(?i)tdd[_\s-]*exception[\s:]*\s*(YES|NO)", summary):
            errs.append("Execution Summary 未声明 tdd_exception (YES/NO)")

    # A5.4 Multi-category MUST ID reconciliation
    plan_path = rd / "plan.md"
    if plan_path.exists():
        plan_text = parser.read_text(plan_path)
        must_items = parser.plan_must_items_structured(plan_text)
        explicit_ids = [it for it in must_items if it.has_explicit_id]
        # Only enforce when plan uses explicit [ID] pattern
        if explicit_ids:
            for it in explicit_ids:
                # Execution.md should reference this ID somewhere marked COMPLETE/DEFERRED/BLOCKED
                id_pattern = re.escape(it.must_id)
                section_re = re.compile(
                    rf"(?ms)^##\s+[^\n]*?{id_pattern}[^\n]*?\n(?P<body>.*?)(?=^##\s|\Z)"
                )
                m = section_re.search(text)
                if not m:
                    errs.append(
                        f"MUST [{it.must_id}] ({it.category}) 在 execution.md 无对应 section — 该交付项未被处理 (A5.4)"
                    )
                    continue
                body = m.group("body")
                if not re.search(r"(?im)^\s*Status\s*:\s*(COMPLETE|BLOCKED|DEFERRED)", body):
                    errs.append(
                        f"MUST [{it.must_id}] section 存在但无 Status COMPLETE/BLOCKED/DEFERRED 标记 (A5.4)"
                    )

    return not errs, errs
