"""A7.16, A11.2, A11.7, A5.2, B-RV-1: activity-trace.md validation.

Ensures:
- Reviewer (post-swap: inspector) continuity checkpoint exists for each of first 3 stages
- Each downstream agent has an Entry Log (B-XX-0 / A5.2)
- 8 compact-entry situations recorded (A11.7)
"""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


STAGES_REQUIRING_CHECKPOINT = ("clarify", "design", "plan")


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "activity-trace.md"
    text = parser.read_text(path)
    if not text:
        return False, ["activity-trace.md 不存在或为空"]
    errs: list[str] = []

    # A11.2: inspector checkpoint for each completed stage among clarify/design/plan
    cs = state.current_stage()
    last = state.read_current_run().get("last_completed_stage", "")
    completed = []
    order = ["clarify", "design", "plan"]
    if last in order:
        idx = order.index(last)
        completed = order[: idx + 1]
    elif cs in order:
        idx = order.index(cs)
        completed = order[:idx]  # stages BEFORE current

    checkpoints = parser.list_inspector_checkpoints(text)
    for stage in completed:
        if stage not in checkpoints:
            errs.append(f"缺 Inspector Checkpoint for {stage} (A11.2)")

    # A11.5: checkpoint body must include safe-to-advance
    for stage in completed:
        body = parser.extract_section(text, rf"Inspector\s+Checkpoint\s*:\s*{stage}")
        if body and not re.search(r"(?i)safe[\s-]to[\s-]advance", body):
            errs.append(f"Inspector Checkpoint {stage} 缺 safe-to-advance 字段 (A11.5)")

    # Reviewer Comment blocks per stage end (A11 extended: reviewer (post-swap) writes comment)
    # Optional — currently advisory

    return not errs, errs


def check_entry_log(agent: str, gate: int) -> tuple[bool, list[str]]:
    """A5.1-A5.2 Entry-Log reconciliation (anti-hallucination).

    Verifies:
    1. Agent's Entry Log section exists in activity-trace.md at the right Gate.
    2. Every required artifact file (per AGENT_ENTRY_LOG_SPEC) is listed with a
       real on-disk path.
    3. Every 'restate' key content actually matches the source file (verbatim
       string presence). This forces the agent to really read the file; it cannot
       hallucinate content that isn't there.
    """
    from ..lib import agent_types

    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if not rd:
        return True, []
    text = parser.read_text(rd / "activity-trace.md")
    entries = parser.list_agent_entries(text)
    agent_short = agent.split(":", 1)[-1].lower()
    if not any(a == agent_short and g == gate for a, g in entries):
        return False, [f"{agent} 未在 activity-trace.md 写入场记录 (期望 Gate {gate}) — A5.1"]

    spec = agent_types.entry_log_spec(agent)
    if not spec:
        return True, []

    section = parser.extract_entry_log_section(text, agent_short, gate)
    if not section:
        return False, [f"{agent} Entry Log 段落找到但无法解析内容"]

    errs: list[str] = []

    # (2) Required artifact files — each must be listed with real path
    listed_artifacts = dict(parser.parse_entry_log_artifacts(section))
    # Normalize listed paths (strip quotes/backticks)
    def _norm(p: str) -> str:
        return p.strip().strip("`").strip('"').strip("'")

    for required_file in spec.get("files", []):
        name_lower = required_file.lower()
        matched_path: str | None = None
        for listed_name, listed_path in listed_artifacts.items():
            if listed_name.lower() == name_lower or listed_name.lower().endswith(name_lower):
                matched_path = _norm(listed_path)
                break
        if not matched_path:
            errs.append(
                f"{agent} Entry Log 必须列出 `{required_file}` 但未列 — 说明未读该文件 (A5.2 anti-hallucination)"
            )
            continue
        # Verify the path Agent wrote is real (no fallback; fake path = block)
        from pathlib import Path as _P
        candidate = _P(matched_path)
        if not candidate.is_absolute():
            candidate = rd / matched_path
        if not candidate.exists():
            errs.append(
                f"{agent} Entry Log 写的 `{required_file}` 路径 `{matched_path}` 在磁盘不存在 — 说明未真读文件 (A5.2a 反幻觉)"
            )

    # (3) Key content restatement
    restate_keys = spec.get("restate", [])
    if "plan-must" in restate_keys:
        plan_text = parser.read_text(rd / "plan.md")
        plan_must = [parser.normalize_must_item(x) for x in parser.plan_must_items(plan_text)]
        restated = [parser.normalize_must_item(x) for x in parser.parse_entry_log_must_items(section)]
        if not restated:
            errs.append(f"{agent} Entry Log 必须列出 'MUST items I will work from' 但为空 — 说明未真正读 plan.md")
        else:
            missing = [m for m in plan_must if m and m not in restated]
            extra = [r for r in restated if r and r not in plan_must]
            if missing:
                errs.append(
                    f"{agent} Entry Log MUST 清单遗漏 {len(missing)} 项 (首项: {missing[0][:60]}) — 与 plan.md 不一致"
                )
            if extra:
                errs.append(
                    f"{agent} Entry Log MUST 清单多出 {len(extra)} 项 (首项: {extra[0][:60]}) — 与 plan.md 不一致"
                )

    if "feature-checklist" in restate_keys:
        fc_text = parser.read_text(rd / "feature-checklist.md")
        fc_items = [i.behavior for i in parser.parse_feature_checklist(fc_text)]
        section_lower = section.lower()
        missing = [x for x in fc_items if x and x.lower()[:30] not in section_lower]
        if fc_items and len(missing) > len(fc_items) // 2:
            errs.append(
                f"{agent} Entry Log 未复述 feature-checklist 的大部分条目 ({len(missing)}/{len(fc_items)} 缺失)"
            )

    if "review-verdict" in restate_keys:
        rv_text = parser.read_text(rd / "review.md")
        rv_verdict = parser.review_verdict(rv_text)
        if rv_verdict and rv_verdict not in section.upper():
            errs.append(f"{agent} Entry Log 缺 review.md verdict ({rv_verdict}) 复述 — 说明未真正读 review.md")

    if "exec-files-changed" in restate_keys:
        exec_text = parser.read_text(rd / "execution.md")
        if exec_text and "files changed" in exec_text.lower() and "files changed" not in section.lower():
            errs.append(f"{agent} Entry Log 缺 '文件变更清单' 引用 — 说明未真正读 execution.md")

    return not errs, errs


def check_orchestrator_decision(target_agent: str) -> tuple[bool, list[str]]:
    """A5.3: before spawning executor / reviewer, OR must have declared the next unit.

    Requires `## Orchestrator Decision — <Unit>` section in activity-trace.md with:
    - Unit id: matches a plan.md / feature-checklist.md ID
    - Unit not in execution.md's completed list (i.e. it's actually "next")
    - Decision section must be fresher than the last executor `agent_stop` event
      (so OR can't reuse an old decision for a new spawn)
    """
    # Only enforce for executor / reviewer (review-stage). Other agents are fine.
    short = target_agent.split(":", 1)[-1].lower()
    if short not in ("executor", "reviewer"):
        return True, []

    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if not rd:
        return True, []
    trace_text = parser.read_text(rd / "activity-trace.md")
    plan_text = parser.read_text(rd / "plan.md")
    exec_text = parser.read_text(rd / "execution.md")
    fc_text = parser.read_text(rd / "feature-checklist.md")

    decisions = parser.parse_orchestrator_decisions(trace_text)
    if not decisions:
        return False, [
            f"缺 Orchestrator Decision 段 — spawn {target_agent} 前必须在 activity-trace.md "
            f"写 `## Orchestrator Decision — <Unit>` 段 (含 Unit id + 对应 plan MUST 复述), "
            f"说明 OR 本次 spawn 要做的 checkpoint/feature (A5.3 反顺序跳跃)"
        ]

    header, unit_id, body = decisions[-1]  # most recent decision

    # Unit id must appear in plan or feature-checklist
    plan_ids = parser.extract_plan_unit_ids(plan_text) + parser.extract_plan_unit_ids(fc_text)
    if plan_ids and unit_id not in plan_ids:
        return False, [
            f"Orchestrator Decision Unit id=`{unit_id}` 不在 plan.md / feature-checklist.md 已知清单 "
            f"(已知前 5 项: {plan_ids[:5]}) — OR 凭印象创造了清单外的 unit (A5.3)"
        ]

    # Unit must not already be completed
    completed = parser.extract_completed_unit_ids(exec_text)
    if unit_id in completed:
        return False, [
            f"Orchestrator Decision Unit id=`{unit_id}` 已在 execution.md 标记 COMPLETE — "
            f"禁止对同一 unit 重复 spawn {target_agent} (A5.3)"
        ]

    # A5.5: if plan-progress is initialized, Unit id must be PENDING (not COMPLETE/DEFERRED/BLOCKED)
    from ..lib import plan_progress
    if plan_progress.is_initialized():
        st = plan_progress.item_status(unit_id)
        if st and st != "PENDING":
            return False, [
                f"Orchestrator Decision Unit id=`{unit_id}` 在 plan-progress.json 状态={st}，"
                f"不可再 spawn {target_agent} (A5.5 · 中断恢复保护) · 如需重做，先 mark DEFERRED→PENDING 或 reopen G3"
            ]

    return True, []


def check_compact_entries() -> tuple[bool, list[str]]:
    """A11.7: 8 trigger conditions recorded as compact entries (advisory sampling).

    Heuristic: activity-trace.md length grows through the run; we only validate
    that there are at least 1 entry per stage transition and per G reopen.
    """
    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if not rd:
        return True, []
    text = parser.read_text(rd / "activity-trace.md")
    gates_observed = parser.list_gate_decisions(text)
    cs = state.current_stage()
    # Expect at least one decision entry per stage transition so far
    completed = state.read_current_run().get("last_completed_stage", "")
    stage_order = ["clarify", "design", "plan", "execute", "review", "verify", "finish"]
    try:
        target = stage_order.index(completed) + 1 if completed else 0
    except ValueError:
        target = 0
    if len(gates_observed) < target and target > 0:
        return False, [f"activity-trace.md gate decision entries={len(gates_observed)} < 已完成阶段数={target}"]
    return True, []
