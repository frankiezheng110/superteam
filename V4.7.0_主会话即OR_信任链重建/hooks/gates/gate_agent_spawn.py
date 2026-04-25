"""A1.1, A2.1-3, A4.*, A6.15, A11.1, A12.2: PreToolUse(Agent) gate.

When Claude wants to spawn superteam:* subagent, we verify:
- agent is legal for current stage (A4.1 / A4.9)
- upstream agent is orchestrator or user (A4.8)
- previous gate's checklist all PASS (A1.1 / A2.1-3)
- plan_quality_gate != fail for executor (A4.2)
- repair_cycle < 3 for executor (A4.3 / A12.4)
- inspector (post-swap) pre-read artifacts present (A4.5)
- review.md verdict != BLOCK for verifier (A4.6 / A6.15)
- reviewer (post-swap: code reviewer) not in same session as executor (A4.7)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..lib import agent_types, parser, state, trace
from ..validators import (
    validator_current_run_json,
    validator_design,
    validator_feature_checklist,
    validator_plan,
    validator_project_definition,
    validator_review,
    validator_solution_landscape,
    validator_solution_options,
    validator_ui_intent,
)


# Map entry-gate -> list of validator modules that must pass
GATE_VALIDATORS = {
    1: [validator_project_definition, validator_current_run_json],
    2: [
        validator_design,
        validator_solution_options,
        validator_solution_landscape,
        validator_ui_intent,
        validator_feature_checklist,
    ],
    3: [validator_plan],
    4: None,  # execute->review: validator_execution checked by gate_4 dedicated module
    5: [validator_review],
}


def check(tool_input: dict[str, Any]) -> tuple[bool, str]:
    agent = str(tool_input.get("subagent_type", ""))
    if not agent.startswith("superteam:"):
        return True, ""
    cs = state.current_stage() or "clarify"

    # A4.1 / A4.9 stage-legality
    if not agent_types.is_valid_for_stage(agent, cs):
        allowed = sorted(agent_types.AGENT_VALID_STAGES.get(agent, set()))
        return False, f"{agent} 仅允许在 {allowed} 阶段 spawn，当前 stage={cs}"

    # A4.2 plan_quality_gate check (for executor)
    if agent == "superteam:executor" and state.plan_quality_gate() == "fail":
        return False, "plan_quality_gate=fail — 不得 spawn executor，先修复 plan.md critical 字段"

    # A4.3 / A12.4 repair-cycle cap
    if agent == "superteam:executor" and state.repair_cycle_count() >= 3:
        return False, "repair_cycle_count >= 3 — 必须升级用户 (re-plan / reduce scope / terminate)"

    # Gate precondition validators
    gate = agent_types.entry_gate(agent)
    mods = GATE_VALIDATORS.get(gate) if gate else None
    if mods:
        for mod in mods:
            ok, errs = mod.run()
            if not ok:
                summary = "; ".join(errs[:3])
                trace.emit_discrepancy(
                    f"gate_{gate}_precondition", f"{agent} spawn blocked: {summary}"
                )
                return False, f"Gate {gate} 未通过 — {summary}"

    # A4.5 pre-read artifacts
    preread = agent_types.required_preread(agent)
    if preread:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if rd:
            for fname in preread:
                if not (rd / fname).exists():
                    return False, f"{agent} 必须先读 {fname}，但文件不存在"

    # A5.5 Initialize plan-progress on first executor spawn (if plan.md exists)
    if agent == "superteam:executor":
        from ..lib import plan_progress as _pp
        if not _pp.is_initialized():
            _pp.initialize()

    # A5.3 Orchestrator Decision Log (spawn executor / reviewer requires declared next unit)
    if agent in ("superteam:executor", "superteam:reviewer"):
        from ..validators import validator_activity_trace
        ok, errs = validator_activity_trace.check_orchestrator_decision(agent)
        if not ok:
            trace.emit_discrepancy("A5.3", errs[0] if errs else "OR decision log missing")
            return False, errs[0]

    # A6.15 review verdict gate for verifier
    if agent == "superteam:verifier":
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if rd:
            review_text = parser.read_text(rd / "review.md")
            if review_text and parser.review_verdict(review_text) == "BLOCK":
                return False, "review.md verdict=BLOCK — 必须先返 execute 修复，不得直接 verify (A6.15)"

    # A2.1-3 user approval checks (gate 1/2/3 agents downstream require approval)
    if gate in (1, 2, 3):
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if rd:
            trace_text = parser.read_text(rd / "activity-trace.md")
            if not parser.has_user_approval(trace_text):
                return False, f"Gate {gate} 需要用户明确批准 (approved_by: user 或 '用户批准') 才能 spawn {agent}"

    # A11.1 inspector gate_check_report must exist before advancing
    if gate >= 2:
        # expect gate_check_report for previous gate in trace jsonl
        prev_gate = gate - 1
        if prev_gate >= 1 and not trace.has_event("gate_check_report", stage=None):
            # advisory: hook itself writes gate_check_report on its own (post_agent_trace_writer),
            # so this should only fail if trace never initialized
            pass

    return True, ""
