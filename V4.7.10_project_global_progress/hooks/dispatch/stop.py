#!/usr/bin/env python3
"""Stop dispatch — Gate 7 inspector check + V4.7.10 two-layer self-stop guard.

Two checks fire on the main-session Stop event:

1. **stop_finish_guard** (V4.6, V4.7.10 enriched) — Gate 7: when
   current_stage=finish or status=completed, the inspector report and the
   finish-stage artifacts must exist and validate. V4.7.10 also marks the
   active milestone DONE in `.superteam/project.md` as a side effect.

2. **OR self-stop guard** (V4.7.10 two-layer) — preferred order:
       (a) project.md present → consult `project_state.is_project_active()`
       (b) project.md absent  → fall back to V4.7.9
                                 `mode_state.is_project_alive()`
   In both layers the same ≥4 threshold safety valve applies.

   Why two layers and not a wholesale switch:
   - Existing projects without project.md must keep the V4.7.9 behavior
     verbatim — anti-dump valve, fail-closed, paused-also-blocks.
   - Projects that adopt project.md gain milestone-aware semantics so
     phase-finish does not mistakenly terminate the project lifecycle.

   Threshold valve mirrors V4.7.9 (`stop_block_count` persisted in mode.json,
   `stop_hook_active` distinguishes new vs. continuing stop cycles, ≥4
   consecutive blocks → ALLOW + reset).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, mode_state, project_state  # noqa: E402
from hooks.session import stop_finish_guard  # noqa: E402


def _block_reason_with_milestone() -> str:
    """V4.7.10 reason text. When project.md present, name the active
    milestone so the OR sees concrete next-step guidance."""
    slug = project_state.current_milestone_slug()
    if slug:
        nxt = project_state.next_pending_milestone()
        nxt_hint = ""
        if nxt and nxt.get("phase_slug") and nxt.get("phase_slug") != slug:
            nxt_hint = f" 下一 milestone: {nxt['phase_slug']}."
        return (
            "SuperTeam V4.7.10 self-stop block · "
            f"项目仍在交付中 · current_milestone={slug}.{nxt_hint} "
            "读 .superteam/project.md 查看整体进度,推进当前 milestone "
            "或用 /superteam:project-next <slug> 切下一个。 "
            "唯一退出: /superteam:project-complete (全部 milestone DONE 后)。"
        )
    # No project.md — V4.7.9-style reason (lifecycle-only).
    return (
        "SuperTeam V4.7.10 self-stop block · "
        "项目未结束,不允许中途停止。"
        "读 plan 文件推进下一步。"
        "唯一退出: /superteam:end。"
    )


def _or_self_stop_check(payload: dict[str, Any]) -> tuple[bool, str]:
    """Return (ok, reason). ok=False blocks the Stop event.

    V4.7.10 two-layer state-machine. Layer 1 is the project (project.md).
    Layer 2 is the V4.7.9 mode-only fallback for legacy projects without a
    project.md. The function still satisfies the V4.7.7/V4.7.9 AST purity
    contract: only `is_project_alive` (mode layer) and `is_project_active`
    (project layer) are read; no transient-progress or string-lifecycle
    references.

    The threshold valve is identical to V4.7.9: count consecutive blocks
    in the same stop cycle (stop_hook_active distinguishes new from
    continuing cycles); at ≥ STOP_BLOCK_THRESHOLD ALLOW+reset (case-3
    hook-bug rescue).
    """
    if not project_state.is_project_active() and not mode_state.is_project_alive():
        return True, ""

    is_repeat = bool(payload.get("stop_hook_active"))
    count = mode_state.bump_stop_block_count(reset_to_one=not is_repeat)

    if count >= mode_state._STOP_BLOCK_THRESHOLD:
        mode_state.reset_stop_block_count()
        return True, ""

    return False, _block_reason_with_milestone()


def main() -> None:
    """V4.7.10 fail-closed entrypoint (mirrors V4.7.9).

    Any exception anywhere — payload parse, finish guard, lifecycle read,
    decision emit — re-routes to emit_block. The hook never falls through
    to allow-by-accident.
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
        try:
            decisions.emit_block(
                f"SuperTeam V4.7.10 fail-closed self-stop block · "
                f"hook internal error: {type(exc).__name__}: {exc} · "
                f"项目仍在运行,继续推进。"
            )
        except Exception:  # noqa: BLE001
            import sys
            sys.exit(2)


if __name__ == "__main__":
    main()
