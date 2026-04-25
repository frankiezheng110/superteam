"""A7.12, A7.19, A7.20 / Gate 7 / A18.3: inspector (监察者) post-run outputs.

After swap, inspector (continuity/team-audit) writes:
- .superteam/inspector/reports/<slug>-report.md (7 sections)
- .superteam/inspector/health.json
- .superteam/inspector/insights.md (rolling, incremental)
- .superteam/inspector/improvement-backlog.md (rolling, incremental)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from ..lib import parser, state


SEVEN_SECTIONS = (
    r"Run\s+Summary|运行概况",
    r"Gate\s+Enforcement\s+Quality|门控执行质量",
    r"Feature\s+Checklist\s+Test\s+Results|功能清单测试结果",
    r"Agent\s+Behavior\s+Compliance|Agent\s+行为合规",
    r"Stage\s+Continuity\s+Record|阶段连续性记录",
    r"Gate\s+Checklist\s+Coverage|门控清单覆盖",
    r"Improvement\s+Findings|改进发现",
)


def _inspector_reports_dir() -> Path | None:
    d = state.inspector_dir()
    return d / "reports" if d else None


def run() -> tuple[bool, list[str]]:
    slug = state.current_slug()
    if not slug:
        return True, []
    d = state.inspector_dir()
    if not d:
        return True, []

    errs: list[str] = []

    # A7.12 report.md 7 sections
    reports = d / "reports" / f"{slug}-report.md"
    if not reports.exists():
        return False, ["inspector 报告 .superteam/inspector/reports/<slug>-report.md 不存在"]
    text = parser.read_text(reports)
    for sect in SEVEN_SECTIONS:
        if not parser.has_section(text, sect):
            errs.append(f"inspector report 缺 section: {sect.split('|')[0]}")

    return not errs, errs


def check_health(run_start_iso: str | None = None) -> tuple[bool, list[str]]:
    """A7.19 health.json must be updated for the current run."""
    d = state.inspector_dir()
    if not d:
        return True, []
    p = d / "health.json"
    errs: list[str] = []
    if not p.exists():
        return False, ["health.json 缺失 (inspector 每次 run 必须更新)"]
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return False, [f"health.json 解析失败: {e}"]
    if run_start_iso and data.get("last_updated", "") < run_start_iso:
        errs.append(f"health.json last_updated={data.get('last_updated')} 早于本 run 开始时间")
    return not errs, errs


def check_insights(run_start_iso: str | None = None) -> tuple[bool, list[str]]:
    """A7.20 insights.md / improvement-backlog.md must have an entry for this run."""
    d = state.inspector_dir()
    if not d:
        return True, []
    errs: list[str] = []
    slug = state.current_slug()
    for name in ("insights.md", "improvement-backlog.md"):
        p = d / name
        if not p.exists():
            errs.append(f"{name} 缺失")
            continue
        content = parser.read_text(p)
        if slug and slug not in content:
            errs.append(f"{name} 未提及本 run slug={slug} (未做增量更新)")
    return not errs, errs


def check_citations() -> tuple[bool, list[str]]:
    """A18.3 report 每条结论须 cite trace event 或 artifact location."""
    slug = state.current_slug()
    if not slug:
        return True, []
    d = state.inspector_dir()
    if not d:
        return True, []
    reports = d / "reports" / f"{slug}-report.md"
    text = parser.read_text(reports)
    errs: list[str] = []
    # Heuristic: count "finding" / "F-XXX" / blockquote lines lacking citations
    findings = re.findall(r"(?m)^#{3,4}\s+F-\d+.*?(?=^#{3,4}\s|\Z)", text, re.DOTALL)
    missing_cite = 0
    for f in findings:
        has_source = re.search(r"(?i)Source:|Evidence:|timestamp|line\s+\d|activity-trace\.md|\.jsonl", f)
        if not has_source:
            missing_cite += 1
    if missing_cite > 3:
        errs.append(f"inspector report {missing_cite} 条 finding 缺 Source/Evidence 引用 (A18.3)")
    return not errs, errs
