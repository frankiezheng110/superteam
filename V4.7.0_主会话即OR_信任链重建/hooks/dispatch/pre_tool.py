#!/usr/bin/env python3
"""PreToolUse dispatch — routes to gates/ by tool name + context.

Order matters: we short-circuit on the first block-returning checker.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, mode_state, trace  # noqa: E402
from hooks.gates import (  # noqa: E402
    gate_agent_spawn,
    gate_commit_gate,
    gate_file_scope,
    gate_freeze_locks,
    gate_main_session_scope,
    gate_subjective_language,
    gate_tdd_redgreen,
    gate_ui_contract,
)


def main() -> None:
    payload = decisions.read_hook_input()
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    if tool == "Agent":
        # A22/B-RV-1 minimum coverage: emit spawn event
        agent = str(tool_input.get("subagent_type", ""))
        if agent.startswith("superteam:"):
            trace.emit_agent_spawn(agent, spawner="orchestrator")
        ok, reason = gate_agent_spawn.check(tool_input)
        if not ok:
            decisions.emit_block(reason)
        # V4.7.0 — open the subagent-running window so writes done inside the
        # spawned subagent are not mis-attributed to the main session.
        if mode_state.is_or_active() and agent:
            mode_state.mark_subagent_started(agent)

    elif tool in ("Edit", "Write", "MultiEdit"):
        # V4.7.0 main-session-scope gate runs first: cheapest, highest priority.
        ok, reason = gate_main_session_scope.check(tool_input)
        if not ok:
            decisions.emit_block(reason)
        # Run all Edit/Write gates in order; first block wins
        for mod in (
            gate_file_scope,
            gate_freeze_locks,
            gate_ui_contract,
            gate_subjective_language,
            gate_tdd_redgreen,
        ):
            ok, reason = mod.check(tool_input)
            if not ok:
                decisions.emit_block(reason)

    elif tool == "Bash":
        ok, reason = gate_commit_gate.check(tool_input)
        if not ok:
            decisions.emit_block(reason)

    decisions.emit_allow()


if __name__ == "__main__":
    main()
