#!/usr/bin/env python3
"""Stop dispatch — Gate 7 inspector check + V4.7.2 OR self-stop guard.

Two checks fire on the main-session Stop event:

1. **stop_finish_guard** (V4.6) — Gate 7: when current_stage=finish or
   status=completed, the inspector report must exist and be well-formed.

2. **OR self-stop guard** (V4.7.2) — when mode.json is active and the
   run is in an execute-class stage (execute / review / verify / finish),
   the main session must have spawned at least one specialist in this
   response turn. If it ends a turn without spawning, the Stop hook
   blocks and tells the OR to delegate the next unit.

   This closes the V4.7.0 / V4.7.1 coverage gap where the OR could
   produce text and quietly end its response without delegating —
   nothing in the existing 4 defenses (SessionStart banner /
   UserPromptSubmit banner / PreToolUse file gate / spawn-log) caught
   that, because none of them watch the conversation-flow layer.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, mode_state, state  # noqa: E402
from hooks.session import stop_finish_guard  # noqa: E402


# Stages where the OR is expected to drive forward without a fresh user
# prompt. clarify / design / plan are conversation-heavy stages where the
# OR legitimately produces text and waits on user input (G1/G2/G3).
_EXEC_CLASS_STAGES = {"execute", "review", "verify", "finish"}


def _or_self_stop_check(payload: dict[str, Any]) -> tuple[bool, str]:
    """Return (ok, reason). ok=False blocks the Stop event."""
    # Avoid infinite block loops — Claude Code sets stop_hook_active=true
    # when the previous Stop was already blocked. Honor that and let the
    # session end if the OR still hasn't spawned.
    if payload.get("stop_hook_active"):
        return True, ""

    if not mode_state.is_or_active():
        return True, ""

    cs = state.current_stage()
    if cs not in _EXEC_CLASS_STAGES:
        # clarify / design / plan stop without spawn is legitimate — the
        # OR is conversing with the user (G1/G2/G3 approval flows).
        return True, ""

    if mode_state.is_subagent_running():
        # A subagent is mid-flight — the response is genuinely waiting,
        # not self-stopping.
        return True, ""

    if mode_state.spawned_in_current_turn():
        return True, ""

    cr = state.read_current_run()
    blocker = cr.get("blocker_summary") or cr.get("blocked_reason")
    if blocker:
        # The run is explicitly stuck and the user must act — let it stop
        # so the user sees the blocker. This avoids fighting Tier C
        # repair-loop terminations.
        return True, ""

    md = mode_state.read_mode()
    slug = md.get("active_task_slug") or "(unset)"
    return False, (
        "SuperTeam V4.7.2 OR self-stop block: 主会话本轮没有 spawn 任何 specialist · "
        f"但 mode=active 且 current_stage={cs} 属于执行类阶段。\n"
        f"task: {slug}\n"
        "下一步必须 spawn 对应 specialist 推进任务（execute → executor; review → reviewer; "
        "verify → verifier; finish → writer/inspector），不要写一段话就结束响应。\n"
        "如确需停下让用户裁决: 写 blocker_summary 到 .superteam/state/current-run.json 后再停。\n"
        "如要退出 OR 模式: 显式 /superteam:end。"
    )


def _escalation_message() -> str | None:
    """V4.7.4 — surface a diagnostic when blocks cluster tightly.

    Three or more gate-violations within 60s suggests one of:
      (1) hook misjudgment on a legitimate write
      (2) the OR is in a confused state (context pressure)
      (3) the user genuinely needs to step in
    Return a non-blocking systemMessage so the OR sees it.
    """
    if not mode_state.is_or_active():
        return None
    recent = mode_state.violations_in_window(seconds=60)
    if len(recent) < 3:
        return None
    sample = "; ".join(
        f"{(r.get('kind') or '?')}@{(r.get('ts','')[:19])}" for r in recent[-3:]
    )
    return (
        f"SuperTeam V4.7.4 escalation: 60s 内已有 {len(recent)} 次 hook block。"
        f"最近: {sample}。可能原因: hook 误判 / 上下文压力 / 真有结构性问题。"
        "建议: /superteam:debug 看完整日志, /superteam:bypass <原因> 一次性放行, 或 /superteam:end 暂停。"
    )


def main() -> None:
    payload = decisions.read_hook_input()

    # Gate 7 finish check first — it concerns terminal correctness.
    ok, reason = stop_finish_guard.check()
    if not ok:
        decisions.emit_block(reason)

    # V4.7.2 — OR self-stop guard.
    ok, reason = _or_self_stop_check(payload)
    if not ok:
        decisions.emit_block(reason)

    # V4.7.4 — escalation diagnostic (non-blocking).
    msg = _escalation_message()
    if msg:
        decisions.emit_system_message(msg, hook_event="Stop")

    decisions.emit_allow()


if __name__ == "__main__":
    main()
