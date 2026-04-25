"""A5.1-2 / H5 / B-XX-0: each downstream agent must leave Entry Log in activity-trace.md.

After agent returns, verify the Entry Log is present with correct Gate number.
Missing log => trace.emit_discrepancy; not a hard block (the agent already ran),
but next agent spawn will pick it up via gate_agent_spawn dependency check.
"""
from __future__ import annotations

from typing import Any

from ..lib import agent_types, trace
from ..validators import validator_activity_trace


def run(tool_input: dict[str, Any], tool_response: dict[str, Any]) -> None:
    agent = str(tool_input.get("subagent_type", ""))
    if not agent.startswith("superteam:"):
        return
    # Only agents that need Entry Log
    gate = agent_types.entry_gate(agent)
    if not gate:
        return
    ok, errs = validator_activity_trace.check_entry_log(agent, gate)
    if not ok:
        for e in errs:
            trace.emit_discrepancy(f"A5.1-{agent}", e, severity="medium")
