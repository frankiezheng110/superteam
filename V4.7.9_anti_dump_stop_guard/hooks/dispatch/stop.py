#!/usr/bin/env python3
"""Stop dispatch — Gate 7 inspector check + V4.7.9 binary self-stop guard.

Two checks fire on the main-session Stop event:

1. **stop_finish_guard** (V4.6) — Gate 7: when current_stage=finish or
   status=completed, the inspector report must exist and be well-formed.

2. **OR self-stop guard** (V4.7.9) — lifecycle bit + ≥4 threshold valve.

   Lifecycle judgment (primary):
   - `running` / `paused` / any non-ended → BLOCK
   - `ended` → ALLOW (the single legitimate exit)
   - mode.json missing → ALLOW (project not loaded; OR concept N/A)

   Threshold valve (case-3 hook-bug rescue):
   - count consecutive BLOCKs in the same stop cycle
   - `stop_hook_active=false` → new cycle, count=1
   - `stop_hook_active=true`  → same cycle, count++
   - count >= STOP_BLOCK_THRESHOLD (=4) → ALLOW + reset

   Why threshold ≥4 instead of V4.7.7's 1-strike pass:
   - V4.7.7 transcripts: ~89% of valve triggers were case-2 (OR text-
     dumping), only ~0% were genuine hook bugs
   - The strong-guidance reason text ("读 plan 推进下一步") directs the
     model to break out of case-2 within the first 1-3 blocks
   - 4th consecutive block = the model is structurally stuck despite
     clear directives → probable hook bug → trip the valve

   Why count-based instead of timeout-based:
   - Claude Code's 60s hook timeout would be a tempting fallback, but
     it conflates real hook bugs with network/IO latency. A slow disk
     or slow file system call should not be misread as a death loop.
     Loop count is a deterministic behavioral signal; wall-clock time
     is not.

   User mandate (2026-04-26):
   - "项目没有结束 = 永远不能停下"  (lifecycle judgment)
   - "哪怕无限循环一亿次也不允许停"  (later softened: "气话")
   - "阈值设置成 ≥4"                (final: structural-bug detector)
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

    V4.7.9 binary state-machine: ONLY project_lifecycle == "ended" allows
    OR to stop. Anything else (running / paused / any non-ended value) →
    BLOCK.

    Rationale (user mandate, 2026-04-26): "项目没有结束 = 状态机 true =
    永远不能停下". Project-end is a single explicit event triggered by
    /superteam:end (or finish-stage auto-completion). All other lifecycle
    states are "project still alive" and OR must keep working — including
    `paused`, which V4.7.7 mistakenly treated as a legitimate stop. There
    is exactly one exit door, no half-doors.

    The AST purity test (tests/test_v477_stop_purity.py) enforces that this
    function references no transient-progress symbols and no runtime-bypass
    flags (e.g. stop_hook_active).
    """
    # V4.7.9 — threshold safety valve. The Claude Code runtime sets
    # `stop_hook_active=true` after a single prior block, which is far
    # too eager to be a hook-bug detector. We replace it with a counter:
    # only after >= STOP_BLOCK_THRESHOLD consecutive blocks in the same
    # stop cycle do we treat it as a probable hook bug and ALLOW (case-3
    # rescue). The strong-guidance reason text below directs the model
    # to break out of case-2 dumping within the first 1-3 blocks, so the
    # valve trips only when the model's behavior is structurally stuck —
    # the legitimate "hook bug locks the session" scenario.
    if not mode_state.is_project_alive():
        return True, ""

    is_repeat = bool(payload.get("stop_hook_active"))
    count = mode_state.bump_stop_block_count(reset_to_one=not is_repeat)

    if count >= mode_state._STOP_BLOCK_THRESHOLD:
        # case-3 rescue: hook has BLOCKed (THRESHOLD-1) times this cycle
        # and the model is still re-trying without progress. Probably a
        # genuine hook-bug loop. ALLOW + reset so the next cycle starts
        # fresh.
        mode_state.reset_stop_block_count()
        return True, ""

    return False, (
        "SuperTeam V4.7.9 self-stop block · "
        "项目未结束,不允许中途停止。"
        "读 plan 文件推进下一步。"
        "唯一退出: /superteam:end。"
    )


def main() -> None:
    """V4.7.9 fail-closed entrypoint.

    Any exception anywhere — payload parse, finish guard, lifecycle read,
    decision emit — re-routes to emit_block. The hook never falls through
    to allow-by-accident. User mandate: 哪怕无限循环一亿次,也不允许中途
    停止。
    """
    try:
        payload = decisions.read_hook_input()

        ok, reason = stop_finish_guard.check()
        if not ok:
            decisions.emit_block(reason)  # noreturn (sys.exit inside)

        ok, reason = _or_self_stop_check(payload)
        if not ok:
            decisions.emit_block(reason)  # noreturn

        decisions.emit_allow()  # noreturn
    except Exception as exc:  # noqa: BLE001 — fail-closed for real bugs only
        # SystemExit / KeyboardInterrupt deliberately NOT caught — emit_*
        # use sys.exit() and we must not swallow that. Real exceptions
        # (parse error, lifecycle read crash, etc.) re-route to BLOCK.
        try:
            decisions.emit_block(
                f"SuperTeam V4.7.9 fail-closed self-stop block · "
                f"hook internal error: {type(exc).__name__}: {exc} · "
                f"项目仍在运行,继续推进。"
            )
        except Exception:  # noqa: BLE001
            import sys
            sys.exit(2)


if __name__ == "__main__":
    main()
