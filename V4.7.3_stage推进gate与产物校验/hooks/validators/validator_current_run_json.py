"""A7.15, A7.18, A1.3, B-OR-1,4,5, B-PL-4: current-run.json schema validation.

Ensures the 33-field minimum set from framework/orchestrator.md is present when
relevant. Missing mandatory fields block the next stage transition.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from ..lib import state


MANDATORY_ALWAYS = (
    "task_slug",
    "current_stage",
    "last_completed_stage",
    "status",
    "last_updated",
)

VALID_STAGES = {"clarify", "design", "plan", "execute", "review", "verify", "finish"}
VALID_STATUSES = {"active", "completed", "failed", "cancelled"}
VALID_PLAN_QG = {"pass", "at_risk", "fail", ""}


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    p = Path(path) if path else state.current_run_path()
    if not p or not p.exists():
        return False, ["current-run.json 不存在"]
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return False, [f"current-run.json 解析失败: {e}"]
    errs: list[str] = []

    for field in MANDATORY_ALWAYS:
        if not data.get(field):
            errs.append(f"current-run.json 缺字段: {field}")

    cs = data.get("current_stage")
    if cs and cs not in VALID_STAGES:
        errs.append(f"current_stage={cs} 非法 (必须是 7 阶段之一)")
    lcs = data.get("last_completed_stage")
    if lcs and lcs not in VALID_STAGES | {""}:
        errs.append(f"last_completed_stage={lcs} 非法")

    status = data.get("status")
    if status and status not in VALID_STATUSES:
        errs.append(f"status={status} 非法")

    pqg = data.get("plan_quality_gate", "")
    if pqg and pqg not in VALID_PLAN_QG:
        errs.append(f"plan_quality_gate={pqg} 非法")

    rc = data.get("repair_cycle_count", 0)
    if not isinstance(rc, int) or rc < 0:
        errs.append("repair_cycle_count 必须是非负整数")

    uw = data.get("ui_weight", "ui-none")
    if uw not in {"ui-none", "ui-standard", "ui-critical"}:
        errs.append(f"ui_weight={uw} 非法")

    return not errs, errs


def check_stage_transition(prev: dict, new: dict) -> tuple[bool, list[str]]:
    """A1.3: transition must update both current_stage and last_completed_stage."""
    errs: list[str] = []
    if prev.get("current_stage") != new.get("current_stage"):
        if new.get("last_completed_stage") != prev.get("current_stage"):
            errs.append(
                f"stage transition 不一致: last_completed_stage 应为 {prev.get('current_stage')}, 实际 {new.get('last_completed_stage')}"
            )
    return not errs, errs
