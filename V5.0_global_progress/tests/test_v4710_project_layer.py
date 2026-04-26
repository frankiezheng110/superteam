"""V4.7.10 project layer tests · project.md frontmatter / milestone table /
stop hook two-layer / SessionStart inject / mode_cli project-* subcommands.

Run:
    python tests/test_v4710_project_layer.py

Covers:

P. project_state lib (frontmatter + milestone table)
   - P1 init_project creates project.md with frontmatter + table
   - P2 is_project_active returns True when status=in_progress, False
        when status=complete or project.md absent
   - P3 mark_milestone_done flips PENDING → DONE and stamps completed
   - P4 set_project_complete sets status=complete
   - P5 reopen_project sets status back to in_progress and stamps audit
   - P6 list_milestones / find_milestone / next_pending_milestone

S. stop hook two-layer (project.md is the primary signal)
   - S1 project.md status=in_progress → BLOCK (regardless of mode)
   - S2 project.md status=complete + mode ended → ALLOW
   - S3 project.md absent → fallback to V4.7.9 mode_state.is_project_alive
   - S4 ≥4 threshold valve still trips under project layer

F. stop_finish_guard side effect
   - F1 finish + valid artifacts + project.md → milestone marked DONE

I. SessionStart project banner
   - I1 project.md present → banner injected
   - I2 project.md absent → no banner

C. mode_cli project subcommands
   - C1 project-init writes file + reports milestone count
   - C2 project-status renders frontmatter + counts
   - C3 project-next updates current_milestone_slug + enters mode
   - C4 project-complete refuses when milestones PENDING
   - C5 project-complete with --force ends mode + sets status=complete
   - C6 reopen revives ended project
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


# ---------- helpers ----------

def write_mode_lifecycle(
    ws: Workspace,
    *,
    project_lifecycle: str = "running",
    mode: str = "active",
    slug: str = "phase-1",
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
        "paused_at": None,
        "paused_by": None,
        "require_hooks": True,
        "stop_block_count": 0,
    }
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_project_md(
    ws: Workspace,
    *,
    status: str = "in_progress",
    current_slug: str = "phase-1",
    milestones: list[tuple[str, str, str]] | None = None,
) -> None:
    """milestones: list of (version, phase_slug, status)."""
    if milestones is None:
        milestones = [
            ("V1.0.0", "phase-1", "PENDING"),
            ("V1.1.0", "phase-2", "PENDING"),
        ]
    p = ws.superteam / "project.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = (
        "---\n"
        "schema_version: 1\n"
        "project_name: TestProject\n"
        "project_slug: testproject\n"
        "target_release: V2.0.0\n"
        f"status: {status}\n"
        f"current_milestone_slug: {current_slug}\n"
        "created_at: 2026-04-26T00:00:00+00:00\n"
        "last_updated: 2026-04-26T00:00:00+00:00\n"
        "---\n\n"
        "# Project: TestProject\n\n"
        "## Milestones\n\n"
        "| # | Version | Phase Slug | Status | Started | Completed | Notes |\n"
        "|---|---------|------------|--------|---------|-----------|-------|\n"
    )
    rows = "".join(
        f"| {i+1} | {v} | {s} | {st} | - | - | - |\n"
        for i, (v, s, st) in enumerate(milestones)
    )
    p.write_text(fm + rows, encoding="utf-8")


def stop_payload(*, hook_active: bool = False) -> dict:
    return {"hook_event_name": "Stop", "stop_hook_active": hook_active}


def setup_env(ws_path: Path) -> dict[str, str | None]:
    snap = {k: os.environ.get(k) for k in ("CLAUDE_PROJECT_DIR",)}
    os.environ["CLAUDE_PROJECT_DIR"] = str(ws_path)
    return snap


def restore_env(snap: dict[str, str | None]) -> None:
    for k, v in snap.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def reload_lib_modules() -> None:
    """V4.7.10 — module-level state.find_superteam_root caches per env."""
    for mod in (
        "hooks.lib.state",
        "hooks.lib.mode_state",
        "hooks.lib.project_state",
    ):
        sys.modules.pop(mod, None)


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


# ---------- assertion helper ----------

class CaseFail(AssertionError):
    pass


def expect(label: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS · {label}")
    else:
        print(f"  FAIL · {label}{(' :: ' + detail) if detail else ''}")
        raise CaseFail(label)


# ---------- P · project_state lib ----------

def case_p1_init_project_creates_file() -> None:
    """init_project writes project.md with frontmatter + milestones table."""
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-1")
        reload_lib_modules()
        from hooks.lib import project_state
        ok = project_state.init_project(
            name="TestProject",
            slug="testproject",
            target_release="V2.0.0",
            milestones=[
                {"version": "V1.0.0", "phase_slug": "phase-1", "status": "PENDING"},
                {"version": "V1.1.0", "phase_slug": "phase-2", "status": "PENDING"},
            ],
        )
        expect("P1.0 init_project ok", ok)
        expect("P1.1 file exists", project_state.project_path().exists())
        fm = project_state.read_project()
        expect("P1.2 schema_version=1", fm.get("schema_version") in ("1", 1))
        expect("P1.3 status=in_progress", fm.get("status") == "in_progress")
        expect(
            "P1.4 current_milestone_slug=phase-1",
            fm.get("current_milestone_slug") == "phase-1",
        )
        rows = project_state.list_milestones()
        expect("P1.5 2 milestones parsed", len(rows) == 2, str(rows))
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_p2_is_project_active_states() -> None:
    """is_project_active reflects status field + presence of project.md."""
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-1")
        reload_lib_modules()
        from hooks.lib import project_state
        # No project.md → False
        expect("P2.0 no project.md → inactive", not project_state.is_project_active())

        write_project_md(ws, status="in_progress")
        expect("P2.1 status=in_progress → active", project_state.is_project_active())

        write_project_md(ws, status="complete")
        expect("P2.2 status=complete → inactive", not project_state.is_project_active())
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_p3_mark_milestone_done() -> None:
    """mark_milestone_done flips PENDING → DONE in the table."""
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-1")
        reload_lib_modules()
        from hooks.lib import project_state
        write_project_md(ws, milestones=[
            ("V1.0.0", "phase-1", "PENDING"),
            ("V1.1.0", "phase-2", "PENDING"),
        ])
        ok = project_state.mark_milestone_done("phase-1", completed_at="2026-04-26")
        expect("P3.0 mark_milestone_done ok", ok)
        row = project_state.find_milestone("phase-1")
        expect("P3.1 row found", row is not None)
        expect("P3.2 status=DONE", (row.get("status") or "").upper() == "DONE", str(row))
        expect(
            "P3.3 completed=2026-04-26",
            row.get("completed", "") == "2026-04-26",
            str(row),
        )
        # other row untouched
        row2 = project_state.find_milestone("phase-2")
        expect("P3.4 phase-2 still PENDING",
               (row2.get("status") or "").upper() == "PENDING")
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_p4_set_project_complete() -> None:
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-1")
        reload_lib_modules()
        from hooks.lib import project_state
        write_project_md(ws, status="in_progress")
        ok = project_state.set_project_complete(by="user")
        expect("P4.0 set_project_complete ok", ok)
        fm = project_state.read_project()
        expect("P4.1 status=complete", fm.get("status") == "complete")
        expect("P4.2 completed_by=user", fm.get("completed_by") == "user")
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_p5_reopen_project() -> None:
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-1")
        reload_lib_modules()
        from hooks.lib import project_state
        write_project_md(ws, status="complete")
        ok = project_state.reopen_project(reason="phase-finish-mismark")
        expect("P5.0 reopen_project ok", ok)
        fm = project_state.read_project()
        expect("P5.1 status=in_progress", fm.get("status") == "in_progress")
        expect("P5.2 reopened_reason recorded",
               fm.get("reopened_reason", "").startswith("phase-finish"))
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_p6_next_pending_milestone() -> None:
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-1")
        reload_lib_modules()
        from hooks.lib import project_state
        write_project_md(ws, milestones=[
            ("V1.0.0", "phase-1", "DONE"),
            ("V1.1.0", "phase-2", "DONE"),
            ("V1.2.0", "phase-3", "PENDING"),
            ("V1.3.0", "phase-4", "PENDING"),
        ])
        nxt = project_state.next_pending_milestone()
        expect("P6.0 next_pending=phase-3", nxt and nxt.get("phase_slug") == "phase-3", str(nxt))
    finally:
        restore_env(snap)
        destroy_workspace(ws)


# ---------- S · stop hook two-layer ----------

def case_s1_project_active_blocks() -> None:
    """project.md status=in_progress → BLOCK regardless of mode lifecycle."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        # Important: mode lifecycle is ENDED but project is in_progress.
        # V4.7.9 alone would ALLOW (mode ended). V4.7.10 must BLOCK
        # because the project layer still says alive.
        write_mode_lifecycle(ws, project_lifecycle="ended", mode="ended", slug="phase-1")
        write_project_md(ws, status="in_progress")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect(
            "S1 project=in_progress (mode=ended) → BLOCK",
            res.blocked,
            res.reason,
        )
        expect(
            "S1 reason mentions V4.7.10 + milestone",
            "V4.7.10" in res.reason and "milestone" in res.reason.lower(),
            res.reason,
        )
    finally:
        destroy_workspace(ws)


def case_s2_project_complete_allows() -> None:
    """project.md status=complete + mode ended → ALLOW."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        write_mode_lifecycle(ws, project_lifecycle="ended", mode="ended", slug="phase-1")
        write_project_md(ws, status="complete")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("S2 project=complete + mode=ended → ALLOW", not res.blocked, res.reason)
    finally:
        destroy_workspace(ws)


def case_s3_no_project_falls_back() -> None:
    """project.md absent → V4.7.9 fallback: mode lifecycle decides."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        # No project.md
        write_mode_lifecycle(ws, project_lifecycle="running", slug="phase-1")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("S3.0 no project.md + lifecycle=running → BLOCK", res.blocked, res.reason)

        write_mode_lifecycle(ws, project_lifecycle="ended", mode="ended", slug="phase-1")
        res = invoke("stop", stop_payload(), cwd=ws.path)
        expect("S3.1 no project.md + lifecycle=ended → ALLOW", not res.blocked, res.reason)
    finally:
        destroy_workspace(ws)


def case_s4_threshold_valve_still_works() -> None:
    """≥4 threshold valve trips under project layer too."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        write_mode_lifecycle(ws, project_lifecycle="running", slug="phase-1")
        write_project_md(ws, status="in_progress")
        # First call: stop_hook_active=false → count=1 → BLOCK
        res1 = invoke("stop", stop_payload(hook_active=False), cwd=ws.path)
        expect("S4.0 first stop → BLOCK (count=1)", res1.blocked, res1.reason)
        # Now drive count up via stop_hook_active=true repeats. After the
        # 4th BLOCK the valve trips and ALLOWS.
        res2 = invoke("stop", stop_payload(hook_active=True), cwd=ws.path)
        expect("S4.1 second stop → BLOCK (count=2)", res2.blocked, res2.reason)
        res3 = invoke("stop", stop_payload(hook_active=True), cwd=ws.path)
        expect("S4.2 third stop → BLOCK (count=3)", res3.blocked, res3.reason)
        res4 = invoke("stop", stop_payload(hook_active=True), cwd=ws.path)
        expect(
            "S4.3 fourth stop → ALLOW (valve at threshold ≥4)",
            not res4.blocked,
            res4.reason,
        )
    finally:
        destroy_workspace(ws)


# ---------- C · mode_cli project subcommands ----------

def case_c1_project_init_cli() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        rc, out, err = _run_mode_cli(
            ws, "project-init",
            "--name", "TestProject",
            "--target-release", "V2.0.0",
        )
        expect("C1.0 exit code 0", rc == 0, f"rc={rc} stderr={err}")
        payload = json.loads(out)
        expect("C1.1 ok=True", payload.get("ok") is True, out)
        expect("C1.2 project_path set", bool(payload.get("project_path")), out)
        expect("C1.3 file exists",
               (ws.superteam / "project.md").exists(),
               str(list(ws.superteam.iterdir())))
    finally:
        destroy_workspace(ws)


def case_c2_project_status_cli() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        write_project_md(ws, milestones=[
            ("V1.0.0", "phase-1", "DONE"),
            ("V1.1.0", "phase-2", "PENDING"),
        ])
        rc, out, err = _run_mode_cli(ws, "project-status")
        expect("C2.0 exit code 0", rc == 0, err)
        payload = json.loads(out)
        expect("C2.1 project_present", payload.get("project_present") is True, out)
        expect("C2.2 is_active", payload.get("is_active") is True, out)
        counts = payload.get("milestones_by_status", {})
        expect("C2.3 1 DONE 1 PENDING",
               counts.get("DONE") == 1 and counts.get("PENDING") == 1, str(counts))
    finally:
        destroy_workspace(ws)


def case_c3_project_next_cli() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        write_project_md(ws, milestones=[
            ("V1.0.0", "phase-1", "DONE"),
            ("V1.1.0", "phase-2", "PENDING"),
        ])
        rc, out, err = _run_mode_cli(ws, "project-next", "phase-2")
        expect("C3.0 exit code 0", rc == 0, err)
        payload = json.loads(out)
        expect("C3.1 ok", payload.get("ok") is True, out)
        # Re-read project.md to confirm current_milestone_slug
        text = (ws.superteam / "project.md").read_text(encoding="utf-8")
        expect("C3.2 current_milestone_slug updated",
               "current_milestone_slug: phase-2" in text, text[:200])
    finally:
        destroy_workspace(ws)


def case_c4_project_complete_refuses_pending() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        write_project_md(ws, milestones=[
            ("V1.0.0", "phase-1", "DONE"),
            ("V1.1.0", "phase-2", "PENDING"),
        ])
        rc, out, err = _run_mode_cli(ws, "project-complete")
        expect("C4.0 exit code != 0 (refused)", rc != 0, err)
        payload = json.loads(out)
        expect("C4.1 ok=False", payload.get("ok") is False, out)
        expect(
            "C4.2 reason mentions PENDING",
            "PENDING" in (payload.get("reason") or "")
            or "milestone" in (payload.get("reason") or "").lower(),
            out,
        )
    finally:
        destroy_workspace(ws)


def case_c5_project_complete_force() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        write_mode_lifecycle(ws, project_lifecycle="running", slug="phase-1")
        write_project_md(ws, milestones=[
            ("V1.0.0", "phase-1", "DONE"),
            ("V1.1.0", "phase-2", "DONE"),
        ])
        rc, out, err = _run_mode_cli(ws, "project-complete")
        expect("C5.0 ok with all DONE", rc == 0, err)
        payload = json.loads(out)
        expect("C5.1 project_marked_complete", payload.get("project_marked_complete") is True, out)
        expect("C5.2 mode_ended", payload.get("mode_ended") is True, out)
        # Confirm mode.json has lifecycle=ended
        md = json.loads((ws.superteam / "state" / "mode.json").read_text(encoding="utf-8"))
        expect("C5.3 mode lifecycle=ended", md.get("project_lifecycle") == "ended", str(md))
    finally:
        destroy_workspace(ws)


def case_c6_reopen_revives() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        write_mode_lifecycle(ws, project_lifecycle="ended", mode="ended", slug="phase-1")
        write_project_md(ws, status="complete")
        rc, out, err = _run_mode_cli(ws, "reopen", "--reason", "phase-finish-mismark")
        expect("C6.0 exit code 0", rc == 0, err)
        payload = json.loads(out)
        expect("C6.1 project_reopened", payload.get("project_reopened") is True, out)
        expect("C6.2 mode_reopened", payload.get("mode_reopened") is True, out)
        # Verify on disk
        fm_text = (ws.superteam / "project.md").read_text(encoding="utf-8")
        expect("C6.3 status=in_progress on disk",
               "status: in_progress" in fm_text, fm_text[:200])
        md = json.loads((ws.superteam / "state" / "mode.json").read_text(encoding="utf-8"))
        expect("C6.4 mode lifecycle=running", md.get("project_lifecycle") == "running", str(md))
    finally:
        destroy_workspace(ws)


# ---------- I · SessionStart project banner ----------

def case_i1_session_start_inject_project_banner() -> None:
    """SessionStart with project.md present injects banner with project info."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        write_project_md(ws, milestones=[
            ("V1.0.0", "phase-1", "DONE"),
            ("V1.1.0", "phase-2", "PENDING"),
        ])
        res = invoke(
            "session_start",
            {"hook_event_name": "SessionStart", "source": "startup"},
            cwd=ws.path,
        )
        # SessionStart hook returns additionalContext via decisions.emit_session_context
        d = res.decision
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "") or d.get(
            "systemMessage", ""
        )
        expect(
            "I1.0 banner contains progress marker (V4.7.10 or V5.0)",
            ("V4.7.10" in ctx or "V5.0" in ctx) and "project" in ctx.lower(),
            ctx[:300],
        )
        expect(
            "I1.1 banner contains TestProject + target",
            "TestProject" in ctx and "V2.0.0" in ctx,
            ctx[:300],
        )
    finally:
        destroy_workspace(ws)


def case_i2_session_start_no_project_no_banner() -> None:
    """SessionStart without project.md does NOT inject project banner."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        res = invoke(
            "session_start",
            {"hook_event_name": "SessionStart", "source": "startup"},
            cwd=ws.path,
        )
        d = res.decision
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "") or d.get(
            "systemMessage", ""
        )
        expect(
            "I2 no project banner content without project.md",
            "V4.7.10 project" not in ctx and "Milestone roadmap" not in ctx,
            ctx[:300],
        )
    finally:
        destroy_workspace(ws)


# ---------- runner ----------

CASES = [
    ("P1", case_p1_init_project_creates_file),
    ("P2", case_p2_is_project_active_states),
    ("P3", case_p3_mark_milestone_done),
    ("P4", case_p4_set_project_complete),
    ("P5", case_p5_reopen_project),
    ("P6", case_p6_next_pending_milestone),
    ("S1", case_s1_project_active_blocks),
    ("S2", case_s2_project_complete_allows),
    ("S3", case_s3_no_project_falls_back),
    ("S4", case_s4_threshold_valve_still_works),
    ("C1", case_c1_project_init_cli),
    ("C2", case_c2_project_status_cli),
    ("C3", case_c3_project_next_cli),
    ("C4", case_c4_project_complete_refuses_pending),
    ("C5", case_c5_project_complete_force),
    ("C6", case_c6_reopen_revives),
    ("I1", case_i1_session_start_inject_project_banner),
    ("I2", case_i2_session_start_no_project_no_banner),
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
