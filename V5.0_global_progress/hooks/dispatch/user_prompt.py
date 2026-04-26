#!/usr/bin/env python3
"""UserPromptSubmit dispatch.

V5.0 responsibilities:
- Inject the global progress banner on every user prompt — physical
  hard-constraint that the OR reads where it is in the project →
  milestone → phase → stage → MUST → feature hierarchy before deciding
  the next move. Hook fires in the input stream, not as an optional
  tool call; the OR cannot skip reading.
- Refresh mode.json last_verified_at so the main session can detect
  dead hooks.
- A23 supplement-mode detection ('reopen G1/G2/G3') still applies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, global_progress, mode_state, state  # noqa: E402


REOPEN_RE = re.compile(
    r"(?i)(reopen|重新打开|补充|supplement)\s*G\s*([123])"
    r"|G\s*([123])\s*(reopen|重开|补充)"
)


def _banner() -> str | None:
    """V5.0 — unified global progress banner with health-alarm priority."""
    health = mode_state.mode_health()
    if health in (mode_state.MODE_HEALTH_CORRUPT, mode_state.MODE_HEALTH_UNKNOWN_SCHEMA):
        return (
            "【SuperTeam V5.0 警告：mode.json 状态异常】\n"
            f"health: {health}\n"
            "主会话**不应**继续担任 OR 角色。请先用 `/superteam:end` 显式退出，"
            "再用 `/superteam:go <slug>` 重新进入；或直接打开 `.superteam/state/mode.json` 检查并修复。"
        )
    if health == mode_state.MODE_HEALTH_ACTIVE:
        mode_state.bump_last_verified()
    # Always try the global progress banner — project.md may exist even when
    # mode.json is missing/ended (e.g. between phases the user has not run
    # /superteam:project-next yet, or pre-OR clarify stage).
    return global_progress.render_progress_banner()


def main() -> None:
    payload = decisions.read_hook_input()
    prompt = payload.get("prompt", "") or payload.get("user_prompt", "")
    m = REOPEN_RE.search(str(prompt))
    if m:
        gate = m.group(2) or m.group(3)
        state.update_current_run(supplement_mode=f"G{gate}-reopen")

    # V4.7.2 — open a new turn so the Stop hook can detect "main session
    # produced text but did not spawn anything in this turn".
    if mode_state.is_or_active():
        mode_state.begin_turn()

    banner = _banner()
    if banner:
        decisions.emit_user_prompt_context(banner)
    decisions.emit_allow()


if __name__ == "__main__":
    main()
