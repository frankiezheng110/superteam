"""A17.1 / Gate 7 check 4: finish.md must acknowledge every inspector problem record.

finish.md structural + acknowledgment rules:
- contains 'reviewer_report_acknowledged' / '已确认监察报告' flag
- every F-xxx / P-xxx problem in inspector report is acknowledged with one of
  {acknowledged, addressed, disputed} + rationale
"""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


PROBLEM_ID_RE = re.compile(r"(?m)^#{3,4}\s+(?P<pid>(?:F|P)-\d+)")
ACK_LINE_RE = re.compile(
    r"(?P<pid>(?:F|P)-\d+)\s*[:\-—]?\s*(?P<verdict>acknowledged|addressed|disputed|已确认|已处理|已反驳)",
    re.IGNORECASE,
)


def run() -> tuple[bool, list[str]]:
    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if not rd:
        return True, []

    finish = rd / "finish.md"
    if not finish.exists():
        return False, ["finish.md 不存在 — Gate 7 禁止 finish 关闭"]

    text = parser.read_text(finish)
    errs: list[str] = []

    # 1) acknowledgement flag
    has_ack_flag = bool(
        re.search(
            r"(?i)(reviewer|inspector)_report_acknowledged\s*[:=]\s*(true|YES|已确认)",
            text,
        )
    )
    if not has_ack_flag:
        errs.append(
            "finish.md 缺 `reviewer_report_acknowledged: true` (或 `inspector_report_acknowledged: true` / "
            "`已确认监察报告`) 标记 — Gate 7 check 4"
        )

    # 2) for each problem in inspector report, acknowledgment entry must exist
    d = state.inspector_dir()
    if d:
        report = d / "reports" / f"{slug}-report.md"
        if report.exists():
            report_text = parser.read_text(report)
            problem_ids = {m.group("pid") for m in PROBLEM_ID_RE.finditer(report_text)}
            ack_ids = {m.group("pid") for m in ACK_LINE_RE.finditer(text)}
            missing = problem_ids - ack_ids
            if missing:
                sample = sorted(missing)[:3]
                errs.append(
                    f"finish.md 未 acknowledge {len(missing)} 条 inspector problem (首项: {sample}) — A17.1"
                )

    return not errs, errs
