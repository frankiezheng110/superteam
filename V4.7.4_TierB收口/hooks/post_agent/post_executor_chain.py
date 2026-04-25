"""A14.1-3 / H7/H8/H9: executor -> polish -> reviewer -> verifier auto chain.

After executor stops, validate execution.md per-feature evidence and inject
a systemMessage telling main session to spawn the next agent (simplifier /
doc-polisher / reviewer / verifier). We don't physically spawn — Claude Code
hook can't — but repeated pre_tool gate will block any attempt to skip.
"""
from __future__ import annotations

from typing import Any

from ..lib import decisions, state, trace
from ..validators import validator_execution, validator_polish, validator_review


def run(tool_input: dict[str, Any], tool_response: dict[str, Any]) -> str | None:
    """Return a systemMessage string to inject into main session (or None)."""
    agent = str(tool_input.get("subagent_type", ""))
    if not agent.startswith("superteam:"):
        return None

    short = agent.split(":", 1)[-1]

    # G4-G7 (execute → review → verify → finish) are FULLY AUTOMATED after G3 close.
    # Every "Next action" below must be actionable without user confirmation.

    if short == "executor":
        ok, errs = validator_execution.run()
        if not ok:
            trace.emit_discrepancy("A7.8", "; ".join(errs[:3]), severity="high")
        return (
            "Next action (G4, no user confirmation needed): spawn superteam:simplifier for code-polish "
            "(also doc-polisher if docs changed). Skipping polish is blocked at next Agent spawn."
        )

    if short in ("simplifier", "doc-polisher", "release-curator"):
        ok, _ = validator_polish.run()
        if ok:
            return "Next action (G4→G5, no user confirmation needed): spawn superteam:reviewer for review-stage quality gate."
        return "Next action (G4, no user confirmation needed): finalize polish.md with post-polish checks, then spawn reviewer."

    if short == "reviewer":
        ok, _errs = validator_review.run()
        from ..lib import parser as _parser
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if rd:
            verdict = _parser.review_verdict(_parser.read_text(rd / "review.md"))
            if verdict == "BLOCK":
                return (
                    "review.md verdict=BLOCK (G5 fail) — auto-return to execute: re-spawn superteam:executor "
                    "with the fix scope derived from review.md blockers. No user confirmation needed; "
                    "repair_cycle_count auto-increments (cap=3)."
                )
            if verdict in ("CLEAR", "CLEAR_WITH_CONCERNS"):
                return "Next action (G5→G6, no user confirmation needed): spawn superteam:verifier for independent PASS/FAIL/INCOMPLETE verdict."

    if short == "verifier":
        from ..lib import parser as _parser, locks as _locks
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if rd:
            vtext = _parser.read_text(rd / "verification.md")
            verdict = _parser.verification_verdict(vtext)
            if verdict:
                _locks.sign_verdict(slug, vtext)
            if verdict == "PASS":
                return (
                    "Next action (G6→G7, no user confirmation needed): enter finish stage — "
                    "spawn superteam:inspector for post-run analysis (writes reports/<slug>-report.md + "
                    "health.json + insights.md + improvement-backlog.md). After inspector returns, OR writes "
                    "finish.md (acknowledge each inspector problem) + retrospective.md (improvement_action). "
                    "Then Stop auto-passes."
                )
            if verdict == "FAIL":
                return (
                    "verification FAIL (G6) — auto-repair loop: re-spawn superteam:executor with the fix "
                    "package from verification.md. No user confirmation needed (repair_cycle cap=3, "
                    "exceeding triggers escalation)."
                )
            if verdict == "INCOMPLETE":
                return (
                    "verification INCOMPLETE (G6) — re-spawn executor to produce missing evidence, OR "
                    "re-spawn planner if plan itself is weak. No user confirmation needed unless repair_cycle > 3."
                )

    if short == "inspector":
        # Inspector post-run analysis finished; OR finalizes finish artifacts
        return (
            "Next action (G7, no user confirmation needed): OR writes finish.md with "
            "`reviewer_report_acknowledged: true` + per-problem acknowledgment, writes retrospective.md "
            "with non-empty `improvement_action`, ensures health.json/insights.md/improvement-backlog.md "
            "are updated for this run. Once artifacts are present, Stop event auto-passes."
        )

    return None
