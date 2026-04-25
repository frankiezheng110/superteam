#!/usr/bin/env python3
"""Entry point: run all test cases, emit REPORT.md to tests/.

Usage:
    cd V4.6.0_hook强约束/tests
    python run_tests.py
"""
from __future__ import annotations

import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Make sibling imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_cases import run_all, CaseResult


def group_by_category(results: list[CaseResult]) -> dict[str, list[CaseResult]]:
    groups: dict[str, list[CaseResult]] = {}
    for r in results:
        groups.setdefault(r.category, []).append(r)
    return groups


def render_report(results: list[CaseResult]) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines: list[str] = []
    lines.append("# SuperTeam V4.6.0 · Hook 端到端测试报告")
    lines.append("")
    lines.append(f"**测试时间**: {ts}")
    lines.append(f"**测试方式**: 轻量模拟 — 不调用真实 Claude，直接对每个 dispatch 入口脚本发送 Claude 协议 JSON，断言 stdout 决策与 hook 内部状态变化")
    lines.append("")
    lines.append("## 总结")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 运行用例 | {total} |")
    lines.append(f"| ✅ 通过 | {passed} |")
    lines.append(f"| ❌ 失败 | {failed} |")
    status_emoji = "✅ **全部通过**" if failed == 0 else f"⚠️  **{failed} 个失败**"
    lines.append(f"| 状态 | {status_emoji} |")
    lines.append("")

    # Category coverage
    by_cat = group_by_category(results)
    lines.append("## 分类覆盖")
    lines.append("")
    lines.append("| 分类 | 测试数 | 通过 |")
    lines.append("|------|-------|-----|")
    for cat in sorted(by_cat.keys()):
        cat_results = by_cat[cat]
        cat_total = len(cat_results)
        cat_pass = sum(1 for r in cat_results if r.passed)
        lines.append(f"| {cat} | {cat_total} | {cat_pass}/{cat_total} |")
    lines.append("")

    # Details
    lines.append("## 用例详情")
    lines.append("")
    for cat in sorted(by_cat.keys()):
        lines.append(f"### {cat}")
        lines.append("")
        for r in by_cat[cat]:
            emoji = "✅" if r.passed else "❌"
            lines.append(f"#### {emoji} `{r.case_id}` · {r.title}")
            lines.append("")
            lines.append(f"- **验证点**: {r.purpose}")
            lines.append(f"- **期望行为**: {r.expected}")
            actual_short = r.actual.replace("\n", " · ")[:300]
            lines.append(f"- **实际行为**: {actual_short}")
            if not r.passed and r.hook_stderr.strip():
                stderr_short = r.hook_stderr.replace("\n", " ")[:300]
                lines.append(f"- **Hook stderr**: `{stderr_short}`")
            lines.append("")

    # Failures summary
    if failed:
        lines.append("## ❌ 失败清单（需优化）")
        lines.append("")
        for r in results:
            if not r.passed:
                lines.append(f"- **{r.case_id}** · {r.title}")
                lines.append(f"  - 期望: {r.expected}")
                lines.append(f"  - 实际: {r.actual[:200]}")
                if r.hook_stderr.strip():
                    lines.append(f"  - stderr: `{r.hook_stderr[:200]}`")
                lines.append("")
    else:
        lines.append("## 🎉 无失败项")
        lines.append("")
        lines.append("所有硬约束在模拟环境中表现正确。可进入 Phase 2：GitHub 发布。")
        lines.append("")

    # Recommendations
    lines.append("## 建议")
    lines.append("")
    if failed == 0:
        lines.append("- 模拟层面的硬约束均按设计生效")
        lines.append("- 建议用一个小的真实项目试跑一次（`/superteam:go` + 简单需求）再正式发版")
        lines.append("- GitHub 发布前确认 `.claude-plugin/marketplace.json` 源路径与 GitHub 仓库一致")
    else:
        lines.append("- 优先修失败用例对应的 checker")
        lines.append("- 修完重跑 `python tests/run_tests.py` 确认 0 失败再发版")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    results = run_all()
    report = render_report(results)
    report_path = Path(__file__).resolve().parent / "REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    # Also print short summary to stdout
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    print(f"tests: {passed}/{total} passed, {failed} failed. Report: {report_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
