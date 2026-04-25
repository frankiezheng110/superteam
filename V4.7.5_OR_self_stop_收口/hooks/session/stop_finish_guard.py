"""A11.4 / H13 / Gate 7: block Stop when current_stage=finish and inspector report missing.

Also covers A17.3: partial analysis for failed/cancelled runs.
"""
from __future__ import annotations

from ..lib import state
from ..validators import validator_finish, validator_inspector_report, validator_retrospective


def check() -> tuple[bool, str]:
    cr = state.read_current_run()
    cs = cr.get("current_stage", "")
    status = cr.get("status", "")
    slug = state.current_slug()
    if not slug:
        return True, ""

    d = state.inspector_dir()
    if not d:
        return True, ""
    report = d / "reports" / f"{slug}-report.md"

    if cs == "finish" or status == "completed":
        if not report.exists():
            return False, (
                f"不允许 Stop: current_stage=finish 但 inspector 报告 {report} 缺失。"
                f"必须先 spawn superteam:inspector 生成 post-run report 才能结束 session (A11.4 / Gate 7)."
            )
        ok, errs = validator_inspector_report.run()
        if not ok:
            return False, (
                f"不允许 Stop: inspector 报告结构不完整 — {'; '.join(errs[:2])} (Gate 7 check)"
            )

        # A17.1 finish.md acknowledgment
        ok, errs = validator_finish.run()
        if not ok:
            return False, f"不允许 Stop: finish.md 不合格 — {'; '.join(errs[:2])} (A17.1 / Gate 7 check 4)"

        # Gate 7 check 5 / A17.2 retrospective
        ok, errs = validator_retrospective.run()
        if not ok:
            return False, f"不允许 Stop: retrospective.md 不合格 — {'; '.join(errs[:2])} (Gate 7 check 5 / A17.2)"

        # A7.19 rolling artifacts (decision 1 hard block)
        ok, errs = validator_inspector_report.check_health(cr.get("last_updated", ""))
        if not ok:
            return False, f"不允许 Stop: inspector rolling artifact 未更新 — {errs[0]} (A7.19)"
        ok, errs = validator_inspector_report.check_insights(cr.get("last_updated", ""))
        if not ok:
            return False, f"不允许 Stop: insights/improvement-backlog 未更新 — {errs[0]} (A7.20)"

    # A17.3: failed/cancelled 也要 partial analysis
    if status in ("failed", "cancelled"):
        if not report.exists():
            return False, (
                f"不允许 Stop: run status={status} 但未生成 partial inspector report — "
                f"failed/cancelled run 也必须 acknowledge 问题记录 (A17.3)."
            )

    return True, ""
