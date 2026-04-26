"""A6.13 / V1 / I5: flag build-only commands so they cannot pose as test evidence.

Emits a trace discrepancy when reviewer/verifier stage sees a Bash exec that
is build-only (cargo check / tsc --noEmit / flutter analyze / etc.).
validator_verification.py separately refuses to accept these as test evidence.
"""
from __future__ import annotations

from typing import Any

from ..lib import state, test_runners, trace


def run(tool_input: dict[str, Any], tool_response: dict[str, Any]) -> None:
    cmd = str(tool_input.get("command", ""))
    family, category = test_runners.classify_command(cmd)
    if category != "build":
        return
    cs = state.current_stage()
    if cs in ("review", "verify"):
        trace.emit_discrepancy(
            "A6.13",
            f"{cs} stage 执行了 build-only 命令 {family} — 不可作为测试证据 (需跑真实 test suite)",
            severity="medium",
        )
