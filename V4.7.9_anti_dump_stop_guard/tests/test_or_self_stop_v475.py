"""V4.7.5 baseline + V4.7.7 lifecycle adaptation.

Run:
    python tests/test_or_self_stop_v475.py

Covers two surfaces, kept here for continuity with the V4.7.5 baseline
report. V4.7.7 stop-hook semantics override the V4.7.5 stage / subagent
checks: project_lifecycle == "running" → BLOCK is the only signal stop
needs. This file's A-section reflects that adaptation; tests that
exercised V4.7.5-only heuristics (clarify-stage allow / subagent-running
allow) were dropped per V4.7.7 plan §9.

A. stop.py::_or_self_stop_check — V4.7.9 binary read
   - mode missing                                    → allow (no project active)
   - project_lifecycle=ended                         → allow (single exit)
   - project_lifecycle=running                       → BLOCK
   - project_lifecycle=paused                        → BLOCK (V4.7.9 — was allow in V4.7.7)
   - stop_hook_active=true under non-ended           → BLOCK (V4.7.9 — was allow)

B. gate_main_session_scope.py state-machine BLOCK list (unchanged)
   - Edit mode.json / active-subagent.json / turn.json /
     spawn-log.jsonl / subagent-stop-log.jsonl /
     gate-violations.jsonl / bypass-log.jsonl        → BLOCK
   - Edit activity-trace.md                          → allow (whitelist)
   - Edit current-run.json                           → allow here
                                                       (gate_stage_advance owns it)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from harness import (  # noqa: E402
    HookResult,
    Workspace,
    destroy_workspace,
    invoke,
    make_workspace,
    pre_tool_edit,
    stop_event,
)


# ---------- helpers ----------

def write_mode(
    ws: Workspace,
    *,
    mode: str = "active",
    slug: str = "smoke-test",
    project_lifecycle: str | None = None,
) -> None:
    """V4.7.7 — writes mode.json including project_lifecycle field.

    Defaults: mode=active → lifecycle=running, mode=ended → lifecycle=ended.
    Pass project_lifecycle="paused"/"ended"/"running" to override.
    """
    p = ws.superteam / "state" / "mode.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    if project_lifecycle is None:
        project_lifecycle = "running" if mode == "active" else "ended"
    data = {
        "schema_version": 1,
        "mode": mode,
        "project_lifecycle": project_lifecycle,
        "entered_at": "2026-04-25T00:00:00+00:00",
        "entered_by": "/superteam:go",
        "active_task_slug": slug,
        "last_verified_at": "2026-04-25T00:00:00+00:00",
        "ended_at": None if mode == "active" else "2026-04-25T01:00:00+00:00",
        "ended_by": None if mode == "active" else "user_command",
        "paused_at": None,
        "paused_by": None,
        "require_hooks": True,
    }
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def mark_subagent_running(ws: Workspace) -> None:
    (ws.superteam / "state" / "active-subagent.json").write_text(
        json.dumps({"subagent_type": "superteam:executor", "started_at": "2026-04-25T00:00:00+00:00"}),
        encoding="utf-8",
    )


def stop_payload(*, hook_active: bool = False) -> dict:
    return {"hook_event_name": "Stop", "stop_hook_active": hook_active}


# ---------- assertion helper ----------

class CaseFail(AssertionError):
    pass


def expect(label: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS · {label}")
    else:
        print(f"  FAIL · {label}{(' :: ' + detail) if detail else ''}")
        raise CaseFail(label)


# ---------- A · stop.py state-machine self-stop tests ----------

def case_a1_mode_not_active() -> None:
    """mode != active → Stop allowed regardless of stage."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")  # stage is exec but mode is missing
        res: HookResult = invoke("stop", stop_payload(), cwd=ws.path)
        expect("A1 mode missing → allow", not res.blocked, res.reason)
    finally:
        destroy_workspace(ws)


def case_a2_mode_ended() -> None:
    """mode=ended → Stop allowed even in exec stage."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, mode="ended", slug="t1")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("A2 mode=ended → allow", not res.blocked, res.reason)
    finally:
        destroy_workspace(ws)


def case_a4_execute_lifecycle_running_blocks() -> None:
    """V4.7.7: stage=execute under lifecycle=running → BLOCK (lifecycle drives, not stage)."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")  # default lifecycle=running
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("A4 stage=execute lifecycle=running → BLOCK", res.blocked, res.reason)
        expect(
            "A4 reason mentions V4.7.9 self-stop block",
            "V4.7.9 self-stop block" in res.reason,
            res.reason,
        )
    finally:
        destroy_workspace(ws)


def case_a5_review_lifecycle_running_blocks() -> None:
    """V4.7.7: stage=review under lifecycle=running → BLOCK."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="review")
        write_mode(ws, slug="t1")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("A5 stage=review lifecycle=running → BLOCK", res.blocked, res.reason)
    finally:
        destroy_workspace(ws)


def case_a6_verify_lifecycle_running_blocks() -> None:
    """V4.7.7: stage=verify under lifecycle=running → BLOCK."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="verify")
        write_mode(ws, slug="t1")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("A6 stage=verify lifecycle=running → BLOCK", res.blocked, res.reason)
    finally:
        destroy_workspace(ws)


def case_a8_stop_hook_active_single_repeat_blocks() -> None:
    """V4.7.9: single stop_hook_active=true under lifecycle=running → BLOCK.

    V4.7.5/V4.7.7 let the flag through on first repeat (1-strike pass).
    V4.7.9 raises threshold to >=4 consecutive blocks. A single repeat is
    still BLOCK; only sustained looping (4+ in same cycle) trips the valve.
    """
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")  # lifecycle=running
        # First call sets counter=1
        invoke("stop", stop_payload(hook_active=False), cwd=ws.path)
        # Second call (hook_active=true) -> counter=2, still BLOCK
        res = invoke("stop", stop_payload(hook_active=True), cwd=ws.path)
        expect(
            "A8 first repeat (count=2) BLOCK (V4.7.9 threshold=4)",
            res.blocked,
            res.reason,
        )
    finally:
        destroy_workspace(ws)


def case_a9_finish_completed_lifecycle_ended_allows() -> None:
    """V4.7.7: finish-completed projects have lifecycle=ended → stop allowed.

    stop_finish_guard may still block when its artifact gates fail; this
    test asserts only that the V4.7.7 self-stop guard itself does not add
    a new block when lifecycle is ended.
    """
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="finish", status="completed")
        # Simulate phase-7 finish auto-completion path: lifecycle=ended.
        write_mode(ws, slug="t1", project_lifecycle="ended")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect(
            "A9 lifecycle=ended → no self-stop block",
            "V4.7.7 self-stop block" not in res.reason,
            res.reason,
        )
    finally:
        destroy_workspace(ws)


# ---------- B · gate_main_session_scope state-machine BLOCK tests ----------

# Note: pre_tool dispatches PreToolUse; gate_main_session_scope is one of
# many gates wired in. We assert blocked status; the state-machine gate's
# block message contains "state-machine block".

def _expect_state_machine_block(ws: Workspace, file_path: str, label: str) -> None:
    res = invoke("pre_tool", pre_tool_edit(file_path), cwd=ws.path)
    expect(f"{label}: blocked", res.blocked, res.reason)
    expect(
        f"{label}: reason from state-machine gate",
        "状态机" in res.reason or "state-machine" in res.reason.lower() or "state_machine" in res.reason.lower(),
        res.reason,
    )


def _expect_allow(ws: Workspace, file_path: str, label: str) -> None:
    res = invoke("pre_tool", pre_tool_edit(file_path), cwd=ws.path)
    expect(f"{label}: allowed", not res.blocked, res.reason)


def case_b1_block_mode_json() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")
        _expect_state_machine_block(ws, ".superteam/state/mode.json", "B1 mode.json")
    finally:
        destroy_workspace(ws)


def case_b2_block_active_subagent_json() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")
        _expect_state_machine_block(
            ws, ".superteam/state/active-subagent.json", "B2 active-subagent.json"
        )
    finally:
        destroy_workspace(ws)


def case_b3_block_turn_json() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")
        _expect_state_machine_block(ws, ".superteam/state/turn.json", "B3 turn.json")
    finally:
        destroy_workspace(ws)


def case_b4_block_spawn_log() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")
        _expect_state_machine_block(
            ws, ".superteam/runs/t1/spawn-log.jsonl", "B4 spawn-log.jsonl"
        )
    finally:
        destroy_workspace(ws)


def case_b5_block_subagent_stop_log() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")
        _expect_state_machine_block(
            ws, ".superteam/state/subagent-stop-log.jsonl", "B5 subagent-stop-log.jsonl"
        )
    finally:
        destroy_workspace(ws)


def case_b6_block_gate_violations() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")
        _expect_state_machine_block(
            ws, ".superteam/state/gate-violations.jsonl", "B6 gate-violations.jsonl"
        )
    finally:
        destroy_workspace(ws)


def case_b7_block_bypass_log() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")
        _expect_state_machine_block(
            ws, ".superteam/state/bypass-log.jsonl", "B7 bypass-log.jsonl"
        )
    finally:
        destroy_workspace(ws)


def case_b8_allow_activity_trace() -> None:
    """activity-trace.md is the OR's coordination log — allowed."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode(ws, slug="t1")
        _expect_allow(
            ws, ".superteam/runs/t1/activity-trace.md", "B8 activity-trace.md"
        )
    finally:
        destroy_workspace(ws)


# ---------- runner ----------

CASES = [
    ("A1", case_a1_mode_not_active),
    ("A2", case_a2_mode_ended),
    # A3 (stage=clarify allow) / A7 (subagent-running allow) deleted in V4.7.7
    # — V4.7.7 stop hook reads only project_lifecycle; stage and subagent
    # presence are not part of the decision (see PLAN-V4.7.7 §9).
    ("A4", case_a4_execute_lifecycle_running_blocks),
    ("A5", case_a5_review_lifecycle_running_blocks),
    ("A6", case_a6_verify_lifecycle_running_blocks),
    ("A8", case_a8_stop_hook_active_single_repeat_blocks),
    ("A9", case_a9_finish_completed_lifecycle_ended_allows),
    ("B1", case_b1_block_mode_json),
    ("B2", case_b2_block_active_subagent_json),
    ("B3", case_b3_block_turn_json),
    ("B4", case_b4_block_spawn_log),
    ("B5", case_b5_block_subagent_stop_log),
    ("B6", case_b6_block_gate_violations),
    ("B7", case_b7_block_bypass_log),
    ("B8", case_b8_allow_activity_trace),
]


def main() -> int:
    failures: list[str] = []
    for label, fn in CASES:
        print(f"\n[{label}] {fn.__name__}")
        try:
            fn()
        except CaseFail as e:
            failures.append(f"{label}: {e}")
        except Exception as e:  # pragma: no cover
            failures.append(f"{label} ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    print("\n========================================")
    if failures:
        print(f"FAIL · {len(failures)}/{len(CASES)} cases failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS · all {len(CASES)} cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
