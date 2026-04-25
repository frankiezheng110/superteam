"""Gate 7 check 5 / A17.2: retrospective.md must have non-empty improvement_action
and surface every critical inspector problem.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


CRITICAL_PROBLEM_RE = re.compile(
    r"(?m)^#{3,4}\s+(?P<pid>(?:F|P)-\d+).*?(?=^#{3,4}|\Z)",
    re.DOTALL,
)


def run() -> tuple[bool, list[str]]:
    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if not rd:
        return True, []

    retro = rd / "retrospective.md"
    if not retro.exists():
        return False, ["retrospective.md 不存在 — Gate 7 禁止 finish 关闭"]

    text = parser.read_text(retro)
    errs: list[str] = []

    # 1) improvement_action non-empty
    m = re.search(r"(?im)^\s*[-*]?\s*improvement_action\s*[:=]\s*(?P<val>.+?)$", text)
    if not m:
        errs.append(
            "retrospective.md 缺 `improvement_action` 字段 — Gate 7 check 5 (必须至少声明 'no improvement actions identified this run')"
        )
    else:
        val = m.group("val").strip().strip("\"'`").lower()
        if not val or val in ("none", "null", "tbd", "待定"):
            errs.append(
                f"retrospective.md improvement_action 值为空/待定 ({val!r}) — Gate 7 要求显式非空"
            )

    # 2) critical inspector problems must be surfaced
    d = state.inspector_dir()
    if d:
        report = d / "reports" / f"{slug}-report.md"
        if report.exists():
            report_text = parser.read_text(report)
            critical_ids: list[str] = []
            for m in CRITICAL_PROBLEM_RE.finditer(report_text):
                body = m.group(0)
                if re.search(r"(?i)severity\s*[:=]\s*critical|critical\s+problem", body):
                    critical_ids.append(m.group("pid"))
            missing_in_retro = [pid for pid in critical_ids if pid not in text]
            if missing_in_retro:
                errs.append(
                    f"retrospective.md 未提及 inspector 报告中的 critical problem: {missing_in_retro[:3]} — A17.2"
                )

    return not errs, errs
