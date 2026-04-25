#!/usr/bin/env python3
"""Stop dispatch — Gate 7 inspector check + V4.7.5 state-machine self-stop guard.

Two checks fire on the main-session Stop event:

1. **stop_finish_guard** (V4.6) — Gate 7: when current_stage=finish or
   status=completed, the inspector report must exist and be well-formed.

2. **OR self-stop guard** (V4.7.5) — pure state-machine read. The state
   machine is `mode.json` + `current-run.json` + `active-subagent.json`:
     - mode == "active"                       → OR is on duty
     - current_stage ∈ {execute, review,
       verify}                                → past G3, no user involvement
     - is_subagent_running == False           → nothing is delegated right now
   All three true → BLOCK. The OR cannot end its turn while the state
   machine says it is mid-run.

   `finish` is handled exclusively by stop_finish_guard above — once its
   artifact gates pass, finish *should* stop so the user can confirm exit.

   No timestamps, no verdict scanning, no keyword filters, no spawn-count
   heuristics, no escape-hatch fields. The state machine is the single
   source of truth; preventing tampering with it is the job of
   `gate_main_session_scope.py` (state-machine-file BLOCK list).

   The only legitimate ways out are:
     - subagent currently running           (is_subagent_running)
     - clarify / design / plan stages       (G1/G2/G3 talk to the user)
     - stop_hook_active=true                (Claude Code runtime safety
                                             valve — preserved so the user
                                             can always escape via ESC)
     - /superteam:end                       (user-issued exit command)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, mode_state, state  # noqa: E402
from hooks.session import stop_finish_guard  # noqa: E402


# Stages where the OR must drive forward without user involvement. finish
# is intentionally excluded — its terminal-stop conditions (inspector
# report + finish.md + retrospective.md) are the dedicated job of
# stop_finish_guard.check(), and a properly-completed finish stage *should*
# stop so the user can confirm exit. clarify / design / plan are conversation-
# heavy stages where the OR legitimately produces text and waits on user
# input (G1/G2/G3 approvals).
_EXEC_CLASS_STAGES = {"execute", "review", "verify"}


def _or_self_stop_check(payload: dict[str, Any]) -> tuple[bool, str]:
    """Return (ok, reason). ok=False blocks the Stop event.

    Pure state-machine read. Three signals decide:
        is_or_active             → mode.json says we are on duty
        current_stage ∈ EXEC     → past G3, no user involvement allowed
        is_subagent_running      → some specialist is currently working

    All three true → block. There is no "blocker_summary escape hatch":
    the only legitimate exits are
      (1) a subagent currently running (handled here),
      (2) the runtime safety valve (stop_hook_active=true), or
      (3) the user typing /superteam:end.
    """
    if payload.get("stop_hook_active"):
        return True, ""
    if not mode_state.is_or_active():
        return True, ""
    cs = state.current_stage()
    if cs not in _EXEC_CLASS_STAGES:
        return True, ""
    if mode_state.is_subagent_running():
        return True, ""

    md = mode_state.read_mode()
    slug = md.get("active_task_slug") or "(unset)"
    return False, (
        f"SuperTeam V4.7.5 self-stop block · task={slug} · stage={cs} · "
        "状态机 mode=active && stage∈execute/review/verify && "
        "is_subagent_running=false → 必须 spawn specialist 推进，不允许停下。"
    )


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
