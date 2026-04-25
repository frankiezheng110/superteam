#!/usr/bin/env python3
"""UserPromptSubmit dispatch.

V4.7.0 responsibilities:
- Re-inject the OR-mode banner on every user message (safety net for compact /
  usage-limit / unexpected session resumes where SessionStart did not fire).
- Refresh mode.json last_verified_at so the main session can detect dead hooks.
- A23 supplement-mode detection ('reopen G1/G2/G3') still applies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, mode_state, state  # noqa: E402


REOPEN_RE = re.compile(
    r"(?i)(reopen|重新打开|补充|supplement)\s*G\s*([123])"
    r"|G\s*([123])\s*(reopen|重开|补充)"
)


def _or_mode_banner() -> str | None:
    if not mode_state.is_or_active():
        return None
    mode_state.bump_last_verified()
    md = mode_state.read_mode()
    slug = md.get("active_task_slug") or "(unset)"
    cr = state.read_current_run()
    cur_stage = (cr.get("current_stage") if cr else "") or "(not yet started)"
    recent = mode_state.read_recent_spawns(limit=3, slug=md.get("active_task_slug"))
    recent_str = (
        ", ".join(f"{r.get('subagent_type','?')}@{(r.get('ts','')[:19])}" for r in recent)
        if recent else "(none)"
    )
    return (
        "【SuperTeam V4.7 mode = active】\n"
        f"task: {slug} · stage: {cur_stage}\n"
        "你（主会话）正在担任 Orchestrator (OR) · 按 framework/main-session-orchestrator.md 七阶段处理任务。\n"
        "禁止直接 Edit/Write 代码 / review.md / verify.md / polish.md / final.md — 必须 spawn 对应 specialist subagent。\n"
        "退出途径只有: /superteam:end · 或 finish 阶段获用户明示确认。\n"
        f"最近 specialist: {recent_str}"
    )


def main() -> None:
    payload = decisions.read_hook_input()
    prompt = payload.get("prompt", "") or payload.get("user_prompt", "")
    m = REOPEN_RE.search(str(prompt))
    if m:
        gate = m.group(2) or m.group(3)
        state.update_current_run(supplement_mode=f"G{gate}-reopen")

    banner = _or_mode_banner()
    if banner:
        decisions.emit_user_prompt_context(banner)
    decisions.emit_allow()


if __name__ == "__main__":
    main()
