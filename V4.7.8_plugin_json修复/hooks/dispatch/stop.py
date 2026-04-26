#!/usr/bin/env python3
"""Stop dispatch — Gate 7 inspector check + V4.7.7 single-field self-stop guard.

Two checks fire on the main-session Stop event:

1. **stop_finish_guard** (V4.6) — Gate 7: when current_stage=finish or
   status=completed, the inspector report must exist and be well-formed.

2. **OR self-stop guard** (V4.7.7) — single-field state-machine read.
   The state machine is `mode.json.project_lifecycle` ∈ {running, paused,
   ended}. project_lifecycle == "running" → BLOCK; everything else → ALLOW.

   No stage check, no is_subagent_running check, no timestamps, no verdict
   scanning, no keyword filters, no spawn-count heuristics, no escape-hatch
   fields. Stage and subagent presence describe in-flight progress, not
   project lifecycle — they do not belong in the stop-hook decision.

   The legitimate ways out (everything except 'running'):
     - /superteam:pause                  (project_lifecycle=paused)
     - /superteam:end                    (project_lifecycle=ended)
     - phase7 finish auto-completion     (project_lifecycle=ended)
     - stop_hook_active=true             (Claude Code runtime safety valve)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, mode_state  # noqa: E402
from hooks.session import stop_finish_guard  # noqa: E402


def _or_self_stop_check(payload: dict[str, Any]) -> tuple[bool, str]:
    """Return (ok, reason). ok=False blocks the Stop event.

    V4.7.7 single-field state-machine: project_lifecycle == "running" → BLOCK.
    The AST purity test (tests/test_v477_stop_purity.py) enforces that this
    function references no transient-progress symbols (stage, subagent flag,
    turn id, timestamps, etc.) — anything not on the project_lifecycle axis.
    """
    if payload.get("stop_hook_active"):
        return True, ""
    if mode_state.project_lifecycle() == "running":
        return False, (
            "SuperTeam V4.7.7 self-stop block · "
            "project_lifecycle=running · OR 不允许自停 · "
            "用 /superteam:pause 暂停 / /superteam:end 结束"
        )
    return True, ""


def main() -> None:
    payload = decisions.read_hook_input()

    ok, reason = stop_finish_guard.check()
    if not ok:
        decisions.emit_block(reason)

    ok, reason = _or_self_stop_check(payload)
    if not ok:
        decisions.emit_block(reason)

    decisions.emit_allow()


if __name__ == "__main__":
    main()
