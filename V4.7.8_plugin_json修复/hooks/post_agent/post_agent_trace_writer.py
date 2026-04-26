"""A11.1, A11.3, A11.8, A12.1: hook auto-emits inspector trace events.

This is the key V4.6.0 guarantee: trace minimum-coverage doesn't rely on
inspector agent self-writing. Hook observes agent spawn/stop and writes the
trace itself. This physically closes the 'inspector zero-call' loophole.
"""
from __future__ import annotations

import re
from typing import Any

from ..lib import parser, state, trace


def run(tool_input: dict[str, Any], tool_response: dict[str, Any]) -> None:
    agent = str(tool_input.get("subagent_type", ""))
    if not agent.startswith("superteam:"):
        return

    # agent_stop event (spawn event was emitted in pre_tool dispatcher)
    trace.emit_agent_stop(agent)

    # If this was a stage-transition-owning agent, emit gate_check_report on hook's behalf
    # so the trace has the minimum-coverage even when inspector wasn't spawned.
    short = agent.split(":", 1)[-1]
    gate_map = {
        "designer": 1, "architect": 1, "researcher": 1, "planner": 2,
        "executor": 3, "reviewer": 4, "verifier": 5,
    }
    g = gate_map.get(short)
    if g:
        trace.emit(
            "gate_check_report",
            gate=f"gate_{g}",
            source="hook",
            note=f"hook-auto-emit after {short} completion",
        )

    # A12.1: detect OR override in activity-trace without JSON record -> discrepancy
    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if rd:
        at = rd / "activity-trace.md"
        if at.exists():
            text = parser.read_text(at)
            if re.search(r"(?i)override", text):
                cr = state.read_current_run()
                if not cr.get("override"):
                    trace.emit_discrepancy(
                        "A12.1", "activity-trace.md 提到 override 但 current-run.json 缺 JSON record"
                    )
