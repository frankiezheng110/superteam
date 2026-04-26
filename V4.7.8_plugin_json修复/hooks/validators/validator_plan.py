"""A7.7 / Gate 3 / B-PL-*: plan.md validation.

Checks:
- Every task has 5 critical fields (objective/target/steps/verification/done)
- Every delivery scope item has MUST or DEFERRED tier label
- Every MUST item maps to feature-checklist.md
- plan_quality_gate in current-run.json is not 'fail'
- TDD exception record consistency (A6.11)
"""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


REQUIRED_FIELDS = ("objective", "target", "steps", "verification", "done")


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        # V4.7.6 兼容多文件 plan/ 目录 (V4.6 历史结构)
        plan_md = rd / "plan.md"
        plan_dir = rd / "plan"
        if plan_md.exists():
            path = plan_md
            text = parser.read_text(path)
        elif plan_dir.is_dir():
            md_files = sorted(plan_dir.glob("*.md"))
            if not md_files:
                return False, [f"plan/ 目录存在但无 .md 文件 (path={plan_dir})"]
            text = "\n\n".join(parser.read_text(p) for p in md_files)
            path = plan_dir  # parent==rd, feature-checklist.md 查找仍正确
        else:
            return False, [
                f"plan.md 不存在且 plan/ 目录无内容 "
                f"(检查 {plan_md} 或 {plan_dir}/*.md)"
            ]
    else:
        text = parser.read_text(path)
    if not text:
        return False, ["plan 内容为空"]
    errs: list[str] = []

    # Field completeness
    tasks = parser.parse_plan_tasks(text)
    if not tasks:
        errs.append("plan.md 未解析到任何 Task (检查 ## Task 标题格式)")
    for t in tasks:
        missing = [f for f in REQUIRED_FIELDS if not t.has(f)]
        if missing:
            errs.append(f"{t.heading.strip()} 缺字段: {','.join(missing)}")

    # Tier labels
    must_items = parser.plan_must_items(text)
    deferred_items = parser.plan_deferred_items(text)
    scope_section = parser.extract_section(text, r"delivery\s+scope|交付范围")
    if scope_section:
        bullets = re.findall(r"(?m)^[\s\-*]+\s*(.+)$", scope_section)
        untiered = [
            b for b in bullets
            if b.strip() and not re.match(r"(?i)(MUST|DEFERRED|✅)", b.strip())
        ]
        # ✅ without tier is the silent-ship trap (Gate 3 check 8)
        if untiered:
            errs.append(f"交付范围 {len(untiered)} 项未标 MUST/DEFERRED 分层")

    # MUST -> feature-checklist coverage (only category=功能/Feature requires fc mapping)
    rd = Path(path).parent
    fc = rd / "feature-checklist.md"
    fc_items = parser.parse_feature_checklist(parser.read_text(fc)) if fc.exists() else []
    fc_behaviors = {i.behavior.lower()[:60] for i in fc_items}

    structured = parser.plan_must_items_structured(text)
    feature_cats = {"uncategorized", "功能", "Feature", "feature", "功能清单"}
    for item in structured:
        if item.category in feature_cats:
            desc = item.desc.lower()[:60]
            matches = any(desc in b or b in desc for b in fc_behaviors)
            if not matches and fc_behaviors:
                errs.append(f"功能类 MUST {item.must_id} 未回溯到 feature-checklist: {item.desc[:80]}")

    # A5.4 MUST 必须有显式 [ID] (防止纯自由文本 MUST 无法对账)
    non_id_count = sum(1 for i in structured if not i.has_explicit_id)
    if structured and non_id_count == len(structured):
        # All auto-id; soft warning (legacy plans without ID prefix still pass)
        pass
    elif non_id_count > 0 and non_id_count > len(structured) // 2:
        errs.append(
            f"{non_id_count}/{len(structured)} 条 MUST 缺显式 [ID] 前缀 — 无法做多类对账 (A5.4)"
        )

    # plan_quality_gate field
    pqg = state.plan_quality_gate()
    if pqg == "fail":
        errs.append("plan_quality_gate=fail -- 必须先修复 critical 字段才能 advance")

    # TDD: each code task must have red->green->refactor or cite tdd_exception
    cr = state.read_current_run()
    tdd_exc = cr.get("tdd_exception", "")
    for t in tasks:
        if re.search(r"\.(py|js|ts|rs|go|java|rb|cs|php|swift|kt)\b", t.body):
            has_tdd = re.search(r"(?i)red\s*->\s*green|red\s+green\s+refactor|failing\s+test", t.body)
            if not has_tdd and tdd_exc != "YES":
                errs.append(f"{t.heading.strip()} 是代码任务但缺 TDD 步骤且未登记 tdd_exception")

    return not errs, errs
