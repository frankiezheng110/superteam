"""V5.0 global progress banner tests · 疏不堵 · OR 物理上每个 turn 必读全局进度。

Run:
    python tests/test_v500_global_progress.py

Covers:

R. global_progress.render_progress_banner() rendering
   - R1 silent when no truth source present
   - R2 milestone layer renders project.md table with marker on current
   - R3 phase/stage layer renders mode + current-run
   - R4 banner contains "你在这里" pointer for current milestone
   - R5 banner contains closing directive about project-complete
   - R6 broken project.md degrades gracefully (no crash, other layers still
        render)

I. SessionStart inject (existing harness)
   - I1 banner is injected via additionalContext when project + mode present
   - I2 corrupt mode.json health alarm overrides global banner

U. UserPromptSubmit inject (NEW — every turn forces banner)
   - U1 each user prompt triggers a fresh banner injection
   - U2 banner appears even when only project.md exists (no mode session)
"""
from __future__ import annotations

import json
import os
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

def write_project_md(ws: Workspace, *, milestones=None, status="in_progress",
                     current_slug="phase-5-desktop", name="SMS",
                     target="V2.0.0") -> None:
    if milestones is None:
        milestones = [
            ("V1.0", "phase-1", "DONE"),
            ("V1.5", "phase-5-desktop", "IN_PROGRESS"),
            ("V2.0", "phase-N-release", "PENDING"),
        ]
    p = ws.superteam / "project.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = (
        "---\n"
        "schema_version: 1\n"
        f"project_name: {name}\n"
        "project_slug: testproject\n"
        f"target_release: {target}\n"
        f"status: {status}\n"
        f"current_milestone_slug: {current_slug}\n"
        "created_at: 2026-04-26T00:00:00+00:00\n"
        "last_updated: 2026-04-26T00:00:00+00:00\n"
        "---\n\n"
        "## Milestones\n\n"
        "| # | Version | Phase Slug | Status | Started | Completed | Notes |\n"
        "|---|---------|------------|--------|---------|-----------|-------|\n"
    )
    rows = "".join(
        f"| {i+1} | {v} | {s} | {st} | - | - | - |\n"
        for i, (v, s, st) in enumerate(milestones)
    )
    p.write_text(fm + rows, encoding="utf-8")


def write_mode(ws: Workspace, *, slug="phase-5-desktop", lifecycle="running",
               mode_val="active") -> None:
    p = ws.superteam / "state" / "mode.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "schema_version": 1, "mode": mode_val,
        "project_lifecycle": lifecycle,
        "active_task_slug": slug,
        "entered_at": "2026-04-26T00:00:00+00:00",
        "last_verified_at": "2026-04-26T00:00:00+00:00",
    }, indent=2), encoding="utf-8")


def write_corrupt_mode(ws: Workspace) -> None:
    p = ws.superteam / "state" / "mode.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{this is not valid json", encoding="utf-8")


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
    for mod in (
        "hooks.lib.state",
        "hooks.lib.mode_state",
        "hooks.lib.project_state",
        "hooks.lib.plan_progress",
        "hooks.lib.global_progress",
    ):
        sys.modules.pop(mod, None)


# ---------- assertion helper ----------

class CaseFail(AssertionError):
    pass


def expect(label: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS · {label}")
    else:
        print(f"  FAIL · {label}{(' :: ' + detail) if detail else ''}")
        raise CaseFail(label)


# ---------- R · render_progress_banner ----------

def case_r1_silent_when_no_state() -> None:
    """No project / mode / current-run / plan-progress / feature-tdd → return None."""
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-1")
        # Wipe current-run.json that ws.init() wrote so we have truly nothing.
        (ws.superteam / "state" / "current-run.json").unlink()
        reload_lib_modules()
        from hooks.lib import global_progress
        out = global_progress.render_progress_banner()
        expect("R1 banner is None when no source", out is None, repr(out))
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_r2_milestone_layer_renders() -> None:
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-5-desktop")
        write_project_md(ws)
        reload_lib_modules()
        from hooks.lib import global_progress
        out = global_progress.render_progress_banner() or ""
        expect("R2.0 has V5.0 header", "V5.0 global progress" in out, out[:200])
        expect("R2.1 contains project name SMS", "SMS" in out, out[:200])
        expect("R2.2 contains target V2.0.0", "V2.0.0" in out, out[:200])
        expect("R2.3 milestone table 3 rows", out.count("DONE") + out.count("IN_PROGRESS") + out.count("PENDING") >= 3, out)
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_r3_phase_stage_layer() -> None:
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-5-desktop", stage="execute")
        write_project_md(ws)
        write_mode(ws, slug="phase-5-desktop", lifecycle="running")
        reload_lib_modules()
        from hooks.lib import global_progress
        out = global_progress.render_progress_banner() or ""
        expect("R3.0 contains current phase slug", "phase-5-desktop" in out, out[:300])
        expect("R3.1 contains current stage", "execute" in out, out[:300])
        expect("R3.2 contains lifecycle running", "running" in out, out[:300])
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_r4_current_marker_present() -> None:
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-5-desktop")
        write_project_md(ws)
        reload_lib_modules()
        from hooks.lib import global_progress
        out = global_progress.render_progress_banner() or ""
        expect(
            "R4 banner has 你在这里 marker for current milestone",
            "你在这里" in out,
            out[:400],
        )
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_r5_closing_directive() -> None:
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-5-desktop")
        write_project_md(ws)
        reload_lib_modules()
        from hooks.lib import global_progress
        out = global_progress.render_progress_banner() or ""
        expect(
            "R5.0 closing mentions phase finish ≠ project end",
            "phase finish" in out and "milestone DONE" in out,
            out[-300:],
        )
        expect(
            "R5.1 closing mentions /superteam:project-complete",
            "/superteam:project-complete" in out,
            out[-300:],
        )
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_r6_broken_project_md_degrades() -> None:
    """Broken project.md → milestone layer skipped, other layers still render."""
    ws = make_workspace()
    snap = setup_env(ws.path)
    try:
        ws.init(slug="phase-5-desktop", stage="execute")
        # Write garbage (no frontmatter)
        (ws.superteam / "project.md").write_text("just some markdown\n", encoding="utf-8")
        write_mode(ws, slug="phase-5-desktop")
        reload_lib_modules()
        from hooks.lib import global_progress
        out = global_progress.render_progress_banner() or ""
        # phase/stage layer should still appear
        expect(
            "R6 broken project.md does not crash hook; phase/stage still rendered",
            "phase-5-desktop" in out and "execute" in out,
            out[:300],
        )
    finally:
        restore_env(snap)
        destroy_workspace(ws)


# ---------- I · SessionStart ----------

def case_i1_session_start_injects_banner() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="phase-5-desktop", stage="execute")
        write_project_md(ws)
        write_mode(ws, slug="phase-5-desktop")
        res = invoke(
            "session_start",
            {"hook_event_name": "SessionStart", "source": "startup"},
            cwd=ws.path,
        )
        d = res.decision
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "") or d.get("systemMessage", "")
        expect("I1.0 SessionStart injected V5.0 banner",
               "V5.0 global progress" in ctx, ctx[:300])
        expect("I1.1 banner mentions current milestone",
               "phase-5-desktop" in ctx, ctx[:300])
    finally:
        destroy_workspace(ws)


def case_i2_corrupt_mode_alarm_overrides() -> None:
    ws = make_workspace()
    try:
        ws.init(slug="phase-5-desktop")
        write_project_md(ws)
        write_corrupt_mode(ws)
        res = invoke(
            "session_start",
            {"hook_event_name": "SessionStart", "source": "startup"},
            cwd=ws.path,
        )
        d = res.decision
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "") or d.get("systemMessage", "")
        expect("I2 corrupt mode.json triggers warning",
               "状态异常" in ctx and ("corrupt" in ctx or "unknown_schema" in ctx),
               ctx[:400])
    finally:
        destroy_workspace(ws)


# ---------- U · UserPromptSubmit (the hard-constraint inject) ----------

def case_u1_user_prompt_injects_banner() -> None:
    """Each user prompt triggers fresh banner — physical hard-constraint."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-5-desktop", stage="execute")
        write_project_md(ws)
        write_mode(ws, slug="phase-5-desktop")
        res = invoke(
            "user_prompt",
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "what next",
                "user_prompt": "what next",
            },
            cwd=ws.path,
        )
        d = res.decision
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "")
        expect("U1.0 UserPromptSubmit injects V5.0 banner",
               "V5.0 global progress" in ctx, ctx[:400])
        expect("U1.1 banner contains 你在这里 marker",
               "你在这里" in ctx, ctx[:400])
    finally:
        destroy_workspace(ws)


def case_u2_banner_renders_with_only_project_md() -> None:
    """Even without mode.json, project.md alone is enough to surface progress."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-5-desktop")
        # Wipe mode.json (ws.init only writes current-run.json)
        write_project_md(ws)
        # Don't write mode.json at all
        res = invoke(
            "user_prompt",
            {"hook_event_name": "UserPromptSubmit", "prompt": "x", "user_prompt": "x"},
            cwd=ws.path,
        )
        d = res.decision
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "")
        expect("U2 banner renders milestone layer with no mode.json",
               "V5.0 global progress" in ctx and "SMS" in ctx, ctx[:300])
    finally:
        destroy_workspace(ws)


# ---------- N · 套娃场景端到端 (用户原话场景) ----------

def case_n1_v1_to_v7_at_v6_session_resume() -> None:
    """V1-V7 项目, 走到 V6 execute, 会话异常断, 新会话 SessionStart 第一眼:
    banner 必须同时含 V6 IN_PROGRESS + V7 PENDING 否则 OR 会误把 V6 当整体。"""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6-V6-feature", stage="execute")
        write_project_md(ws,
            name="BigProject", target="V7.0_final",
            current_slug="phase-6-V6-feature",
            milestones=[
                ("V1.0", "phase-1-init",       "DONE"),
                ("V2.0", "phase-2-auth",       "DONE"),
                ("V3.0", "phase-3-api",        "DONE"),
                ("V4.0", "phase-4-ui",         "DONE"),
                ("V5.0", "phase-5-deploy",     "DONE"),
                ("V6.0", "phase-6-V6-feature", "IN_PROGRESS"),
                ("V7.0", "phase-7-V7-final",   "PENDING"),
            ],
        )
        write_mode(ws, slug="phase-6-V6-feature")
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
            "N1.0 V1-V5 全部 DONE 在 banner 中可见",
            all(v in ctx for v in ["V1.0", "V2.0", "V3.0", "V4.0", "V5.0"]),
            ctx[:600],
        )
        expect(
            "N1.1 V6 行同时含 IN_PROGRESS 和 你在这里",
            "V6.0" in ctx and "IN_PROGRESS" in ctx and "你在这里" in ctx,
            ctx[:600],
        )
        expect(
            "N1.2 V7 行同时含 V7.0 标识 + PENDING (防 OR 把 V6 当终点)",
            "V7.0" in ctx and "PENDING" in ctx,
            ctx[:600],
        )
        expect(
            "N1.3 closing 警告 phase finish ≠ project end",
            "phase finish" in ctx and "milestone DONE" in ctx
            and "/superteam:project-complete" in ctx,
            ctx[-400:],
        )
        expect(
            "N1.4 进度条 5/7 可见",
            "5/7" in ctx,
            ctx[:600],
        )
    finally:
        destroy_workspace(ws)


def case_n2_v6_just_finished_v7_still_visible() -> None:
    """V6 刚 finish 标 DONE,新会话起来,banner 必须仍显示 V7 PENDING
    防 OR 看见 V6=DONE 就误判 project=complete。"""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6-V6-feature", stage="finish")
        write_project_md(ws,
            name="BigProject", target="V7.0_final",
            current_slug="phase-6-V6-feature",
            milestones=[
                ("V1.0", "phase-1-init",       "DONE"),
                ("V2.0", "phase-2-auth",       "DONE"),
                ("V3.0", "phase-3-api",        "DONE"),
                ("V4.0", "phase-4-ui",         "DONE"),
                ("V5.0", "phase-5-deploy",     "DONE"),
                ("V6.0", "phase-6-V6-feature", "DONE"),  # 刚标 DONE
                ("V7.0", "phase-7-V7-final",   "PENDING"),
            ],
        )
        write_mode(ws, slug="phase-6-V6-feature")
        res = invoke(
            "user_prompt",
            {"hook_event_name": "UserPromptSubmit",
             "prompt": "下一步", "user_prompt": "下一步"},
            cwd=ws.path,
        )
        d = res.decision
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "")
        expect(
            "N2.0 V6 显示 DONE",
            "V6.0" in ctx and "DONE" in ctx,
            ctx[:600],
        )
        expect(
            "N2.1 V7 PENDING 仍清晰可见 (套娃防御核心)",
            "V7.0" in ctx and "PENDING" in ctx,
            ctx[:600],
        )
        expect(
            "N2.2 进度条仍显 6/7 不是 7/7",
            "6/7" in ctx,
            ctx[:600],
        )
    finally:
        destroy_workspace(ws)


def case_n3_user_prompt_each_turn_reinjects() -> None:
    """每个 user prompt 都重新注入 banner — 物理硬约束 OR 必读。
    模拟 OR 在 turn N 想偷懒不读, turn N+1 hook 强制再注一遍。"""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6-V6-feature", stage="execute")
        write_project_md(ws, name="BigProject", target="V7.0",
                         current_slug="phase-6-V6-feature",
                         milestones=[
                             ("V1.0", "phase-1", "DONE"),
                             ("V6.0", "phase-6-V6-feature", "IN_PROGRESS"),
                             ("V7.0", "phase-7", "PENDING"),
                         ])
        write_mode(ws, slug="phase-6-V6-feature")
        # Three consecutive user prompts
        seen_v7 = []
        for i in range(3):
            res = invoke(
                "user_prompt",
                {"hook_event_name": "UserPromptSubmit",
                 "prompt": f"prompt {i}", "user_prompt": f"prompt {i}"},
                cwd=ws.path,
            )
            ctx = (res.decision.get("hookSpecificOutput", {}) or {}).get("additionalContext", "")
            seen_v7.append("V7.0" in ctx and "PENDING" in ctx)
        expect(
            "N3 每个 turn 都注入 V7 PENDING (3 turn 全部命中)",
            all(seen_v7),
            f"per-turn V7-PENDING seen={seen_v7}",
        )
    finally:
        destroy_workspace(ws)


# ---------- runner ----------

CASES = [
    ("R1", case_r1_silent_when_no_state),
    ("R2", case_r2_milestone_layer_renders),
    ("R3", case_r3_phase_stage_layer),
    ("R4", case_r4_current_marker_present),
    ("R5", case_r5_closing_directive),
    ("R6", case_r6_broken_project_md_degrades),
    ("I1", case_i1_session_start_injects_banner),
    ("I2", case_i2_corrupt_mode_alarm_overrides),
    ("U1", case_u1_user_prompt_injects_banner),
    ("U2", case_u2_banner_renders_with_only_project_md),
    # 套娃端到端场景 (用户实物诉求)
    ("N1", case_n1_v1_to_v7_at_v6_session_resume),
    ("N2", case_n2_v6_just_finished_v7_still_visible),
    ("N3", case_n3_user_prompt_each_turn_reinjects),
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
