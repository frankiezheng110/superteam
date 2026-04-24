"""A6.3-A6.6 / B2.1: parse test output and update TDD state machine.

Transitions:
- PENDING + (FAILED in output, non-error) -> RED_LOCKED
- PENDING + (all PASS) -> stays PENDING but records premature-green warning (A6.4)
- RED_LOCKED + (all PASS) -> GREEN_CONFIRMED
- RED_LOCKED + (FAILED) -> increments green_attempts, stays RED_LOCKED
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any

from ..lib import decisions, plan_progress, state, test_runners, trace


def run(tool_input: dict[str, Any], tool_response: dict[str, Any]) -> None:
    cmd = str(tool_input.get("command", ""))
    family, category = test_runners.classify_command(cmd)
    if not family or category != "test":
        return

    stdout = str(tool_response.get("stdout", "") or "")
    stderr = str(tool_response.get("stderr", "") or "")
    combined = stdout + "\n" + stderr

    passed, failed = test_runners.parse_test_output(family, combined)
    is_error = test_runners.looks_like_test_error(combined)

    feature_id, feat = state.get_active_feature()
    if not feature_id:
        return

    st = feat.get("state", "PENDING")
    sha = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]
    now = datetime.now(timezone.utc).isoformat()

    if st == "PENDING":
        if failed > 0 and not is_error:
            state.set_feature_state(
                feature_id,
                state="RED_LOCKED",
                red_evidence={
                    "command": cmd,
                    "family": family,
                    "timestamp": now,
                    "passed": passed,
                    "failed": failed,
                    "stdout_sha256": sha,
                    "output_excerpt": _head(combined, 400),
                },
                green_attempts=0,
            )
            trace.emit("tdd_red_locked", feature_id=feature_id, family=family)
        elif failed == 0 and passed > 0:
            # Premature-green: test passed without a feature yet -> warning
            trace.emit_discrepancy(
                "A6.4",
                f"Feature {feature_id} 测试立即 pass ({passed} passed, 0 failed) — 测试本身可能错了, 先修测试",
                severity="high",
            )
        elif is_error:
            trace.emit_discrepancy("A6.3", f"Feature {feature_id} 测试 error (非 fail), 先修 error")
    elif st == "RED_LOCKED":
        if failed == 0 and passed > 0:
            state.set_feature_state(
                feature_id,
                state="GREEN_CONFIRMED",
                green_evidence={
                    "command": cmd,
                    "family": family,
                    "timestamp": now,
                    "passed": passed,
                    "failed": failed,
                    "stdout_sha256": sha,
                    "output_excerpt": _head(combined, 400),
                },
            )
            trace.emit("tdd_green_confirmed", feature_id=feature_id, family=family, passed=passed)
            # A5.5: mark corresponding MUST item COMPLETE in plan-progress (if registered)
            plan_progress.mark(
                feature_id, "COMPLETE",
                evidence={"tdd_green_sha": sha, "command": cmd},
            )
        elif failed > 0:
            attempts = int(feat.get("green_attempts", 0)) + 1
            state.set_feature_state(feature_id, green_attempts=attempts)
            if attempts >= 3:
                trace.emit_discrepancy(
                    "A6.9",
                    f"Feature {feature_id} 连续 {attempts} 次 GREEN 失败 — 必须写 BLOCKED escalation",
                    severity="high",
                )


def _head(text: str, n: int) -> str:
    if len(text) <= n:
        return text
    return text[:n] + "…"
