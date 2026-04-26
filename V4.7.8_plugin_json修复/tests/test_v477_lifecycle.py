"""V4.7.7 lifecycle behavior tests · stop hook + pause/resume CLI + migration.

Run:
    python tests/test_v477_lifecycle.py

Covers:

L. stop hook lifecycle decision (single-field state machine)
   - L1 project_lifecycle=running                    → BLOCK
   - L2 project_lifecycle=paused                     → ALLOW
   - L3 project_lifecycle=ended                      → ALLOW
   - L4 stop_hook_active=true under any lifecycle    → ALLOW (safety valve)

C. /superteam:pause CLI command
   - C1 pause writes project_lifecycle=paused, sets paused_at + paused_by

M. SessionStart legacy migration
   - M1 mode.json without project_lifecycle + mode==active → backfilled "running"
   - M2 mode.json without project_lifecycle + ended_at set → backfilled "ended"
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from harness import (  # noqa: E402
    Workspace,
    destroy_workspace,
    invoke,
    make_workspace,
)


def write_mode_lifecycle(
    ws: Workspace,
    *,
    project_lifecycle: str,
    mode: str = "active",
    slug: str = "smoke-test",
) -> None:
    p = ws.superteam / "state" / "mode.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 1,
        "mode": mode,
        "project_lifecycle": project_lifecycle,
        "entered_at": "2026-04-26T00:00:00+00:00",
        "entered_by": "/superteam:go",
        "active_task_slug": slug,
        "last_verified_at": "2026-04-26T00:00:00+00:00",
        "ended_at": None if mode == "active" else "2026-04-26T01:00:00+00:00",
        "ended_by": None if mode == "active" else "user_command",
        "paused_at": "2026-04-26T00:30:00+00:00" if project_lifecycle == "paused" else None,
        "paused_by": "user" if project_lifecycle == "paused" else None,
        "require_hooks": True,
    }
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_legacy_mode(ws: Workspace, *, mode: str, ended_at: str | None = None) -> None:
    """V4.7.6 mode.json — no project_lifecycle field (simulates pre-V4.7.7 file)."""
    p = ws.superteam / "state" / "mode.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 1,
        "mode": mode,
        "entered_at": "2026-04-25T00:00:00+00:00",
        "entered_by": "/superteam:go",
        "active_task_slug": "legacy",
        "last_verified_at": "2026-04-25T00:00:00+00:00",
        "ended_at": ended_at,
        "ended_by": "user_command" if ended_at else None,
        "require_hooks": True,
    }
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def stop_payload(*, hook_active: bool = False) -> dict:
    return {"hook_event_name": "Stop", "stop_hook_active": hook_active}


class CaseFail(AssertionError):
    pass


def expect(label: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS · {label}")
    else:
        print(f"  FAIL · {label}{(' :: ' + detail) if detail else ''}")
        raise CaseFail(label)


# ---------- L · stop hook lifecycle decision ----------

def case_l1_running_blocks() -> None:
    """project_lifecycle=running → stop hook BLOCK."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode_lifecycle(ws, project_lifecycle="running", slug="t1")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("L1 lifecycle=running → BLOCK", res.blocked, res.reason)
        expect(
            "L1 reason mentions V4.7.7 lifecycle",
            "project_lifecycle=running" in res.reason,
            res.reason,
        )
    finally:
        destroy_workspace(ws)


def case_l2_paused_allows() -> None:
    """project_lifecycle=paused → stop hook ALLOW (user explicitly paused)."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode_lifecycle(ws, project_lifecycle="paused", slug="t1")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("L2 lifecycle=paused → ALLOW", not res.blocked, res.reason)
    finally:
        destroy_workspace(ws)


def case_l3_ended_allows() -> None:
    """project_lifecycle=ended → stop hook ALLOW (project closed)."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode_lifecycle(ws, project_lifecycle="ended", mode="ended", slug="t1")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("L3 lifecycle=ended → ALLOW", not res.blocked, res.reason)
    finally:
        destroy_workspace(ws)


def case_l4_stop_hook_active_allows_under_running() -> None:
    """stop_hook_active=true under lifecycle=running → ALLOW (runtime safety valve)."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode_lifecycle(ws, project_lifecycle="running", slug="t1")
        res = invoke("stop", stop_payload(hook_active=True), cwd=ws.path)
        expect(
            "L4 stop_hook_active overrides lifecycle=running",
            not res.blocked,
            res.reason,
        )
    finally:
        destroy_workspace(ws)


# ---------- C · /superteam:pause CLI ----------

def _run_mode_cli(ws: Workspace, *args: str) -> tuple[int, str, str]:
    cli = ROOT / "commands" / "cli" / "mode_cli.py"
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(ws.path)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, str(cli), *args],
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(ws.path), env=env, timeout=20,
    )
    return proc.returncode, proc.stdout, proc.stderr


def case_c1_pause_command_writes_paused() -> None:
    """mode_cli.py pause writes lifecycle=paused + paused_at + paused_by."""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_mode_lifecycle(ws, project_lifecycle="running", slug="t1")
        rc, out, err = _run_mode_cli(ws, "pause")
        expect("C1 pause exit code 0", rc == 0, f"rc={rc} stderr={err}")
        try:
            payload = json.loads(out)
        except json.JSONDecodeError:
            payload = {}
        expect("C1 pause stdout JSON ok", payload.get("ok") is True, out)
        expect(
            "C1 stdout reports paused",
            payload.get("project_lifecycle") == "paused",
            out,
        )
        md = json.loads((ws.superteam / "state" / "mode.json").read_text(encoding="utf-8"))
        expect("C1 mode.json lifecycle=paused", md.get("project_lifecycle") == "paused", str(md))
        expect("C1 mode.json paused_at recorded", bool(md.get("paused_at")), str(md))
        expect("C1 mode.json paused_by=user", md.get("paused_by") == "user", str(md))
    finally:
        destroy_workspace(ws)


# ---------- M · SessionStart legacy migration ----------

def case_m1_legacy_active_migrates_to_running() -> None:
    """老 mode.json 含 mode=active 且无 project_lifecycle → SessionStart 后变 running。"""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="execute")
        write_legacy_mode(ws, mode="active")
        # Trigger SessionStart hook (which runs the migration)
        invoke("session_start", {"hook_event_name": "SessionStart", "source": "startup"}, cwd=ws.path)
        md = json.loads((ws.superteam / "state" / "mode.json").read_text(encoding="utf-8"))
        expect(
            "M1 legacy mode=active 自动迁移为 lifecycle=running",
            md.get("project_lifecycle") == "running",
            str(md),
        )
    finally:
        destroy_workspace(ws)


def case_m2_legacy_ended_migrates_to_ended() -> None:
    """老 mode.json 含 ended_at → SessionStart 后 lifecycle=ended。"""
    ws = make_workspace()
    try:
        ws.init(slug="t1", stage="finish")
        write_legacy_mode(ws, mode="ended", ended_at="2026-04-25T05:00:00+00:00")
        invoke("session_start", {"hook_event_name": "SessionStart", "source": "startup"}, cwd=ws.path)
        md = json.loads((ws.superteam / "state" / "mode.json").read_text(encoding="utf-8"))
        expect(
            "M2 legacy ended → lifecycle=ended",
            md.get("project_lifecycle") == "ended",
            str(md),
        )
    finally:
        destroy_workspace(ws)


CASES = [
    ("L1", case_l1_running_blocks),
    ("L2", case_l2_paused_allows),
    ("L3", case_l3_ended_allows),
    ("L4", case_l4_stop_hook_active_allows_under_running),
    ("C1", case_c1_pause_command_writes_paused),
    ("M1", case_m1_legacy_active_migrates_to_running),
    ("M2", case_m2_legacy_ended_migrates_to_ended),
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
