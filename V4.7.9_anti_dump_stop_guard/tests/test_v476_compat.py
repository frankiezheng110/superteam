"""V4.7.6 — three regression-fix compatibility tests.

Run:
    python tests/test_v476_compat.py

Covers:

A. validator_plan.run() — multi-file plan/ directory compatibility
   - A1 plan/*.md aggregated and validated
   - A2 empty plan/ dir → block with explicit message
   - A3 plan.md present → take precedence over plan/

B. state.current_slug() — mode.json preferred over current-run.json
   - B1 mode.json.active_task_slug present → returned
   - B2 mode.json missing or empty → fallback to current-run.json.task_slug

C. gate_stage_advance — finish accepts verify.md and verification.md
   - C1 verify.md with verdict=PASS → finish transition allowed
   - C2 verification.md with verdict=PASS → finish transition allowed
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ---------- workspace helpers ----------

def make_workspace() -> Path:
    return Path(tempfile.mkdtemp(prefix="st_v476_test_"))


def destroy_workspace(d: Path) -> None:
    shutil.rmtree(d, ignore_errors=True)


def write_mode(ws: Path, *, mode: str = "active", slug: str | None = "smoke-test") -> None:
    """Write mode.json; pass slug=None to omit active_task_slug."""
    p = ws / ".superteam" / "state" / "mode.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 1,
        "mode": mode,
        "entered_at": "2026-04-25T00:00:00+00:00",
        "entered_by": "/superteam:go",
        "active_task_slug": slug,
        "last_verified_at": "2026-04-25T00:00:00+00:00",
        "ended_at": None if mode == "active" else "2026-04-25T01:00:00+00:00",
        "ended_by": None if mode == "active" else "user_command",
        "require_hooks": True,
    }
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_current_run(ws: Path, *, slug: str = "", stage: str = "execute", **extras) -> None:
    p = ws / ".superteam" / "state" / "current-run.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    cr = {
        "task_slug": slug,
        "current_stage": stage,
        "last_completed_stage": "",
        "status": "active",
        "repair_cycle_count": 0,
        "plan_quality_gate": "pass",
        "ui_weight": "ui-none",
        "tdd_exception": "YES",
        "last_updated": "2026-04-25T00:00:00+00:00",
        **extras,
    }
    p.write_text(json.dumps(cr, indent=2), encoding="utf-8")


def write_spawn_log(ws: Path, slug: str, subagent_short: str) -> None:
    """Append a single spawn-log record so gate_stage_advance sees the predecessor."""
    p = ws / ".superteam" / "runs" / slug / "spawn-log.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": "2026-04-25T00:00:00+00:00",
        "subagent_type": f"superteam:{subagent_short}",
        "agent_id": "test-agent",
        "task_slug": slug,
        "turn_id": "testturn",
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


MIN_PLAN_BODY = (
    "# Plan\n\n"
    "## Delivery Scope\n\n"
    "- MUST: 任务 A\n\n"
    "## Task A: 测试任务\n\n"
    "- objective: 测\n"
    "- target: 通过\n"
    "- steps: 1. 跑\n"
    "- verification: 检查\n"
    "- done: ok\n"
)


def setup_env(ws: Path) -> dict[str, str]:
    """Snapshot env, set CLAUDE_PROJECT_DIR; caller must restore_env after."""
    snap = {k: os.environ.get(k) for k in ("CLAUDE_PROJECT_DIR",)}
    os.environ["CLAUDE_PROJECT_DIR"] = str(ws)
    return snap


def restore_env(snap: dict[str, str | None]) -> None:
    for k, v in snap.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


# ---------- assertion helper ----------

class CaseFail(AssertionError):
    pass


def expect(label: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS · {label}")
    else:
        print(f"  FAIL · {label}{(' :: ' + detail) if detail else ''}")
        raise CaseFail(label)


# ---------- A · validator_plan multi-file plan/ ----------

def case_a1_multifile_plan_dir_passes() -> None:
    """V4.6 多文件 plan/ 结构应被识别为合法 plan."""
    ws = make_workspace()
    snap = setup_env(ws)
    try:
        slug = "test-multi"
        rd = ws / ".superteam" / "runs" / slug
        plan_dir = rd / "plan"
        plan_dir.mkdir(parents=True)
        (plan_dir / "01-features.md").write_text(MIN_PLAN_BODY, encoding="utf-8")
        write_current_run(ws, slug=slug)
        write_mode(ws, slug=slug)

        from hooks.validators import validator_plan
        ok, errs = validator_plan.run()
        expect("A1 多文件 plan/ → validator OK", ok, "errs=" + str(errs))
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_a2_empty_plan_dir_blocks() -> None:
    """plan/ 目录存在但无 .md 文件应明确报错."""
    ws = make_workspace()
    snap = setup_env(ws)
    try:
        slug = "test-empty"
        rd = ws / ".superteam" / "runs" / slug
        (rd / "plan").mkdir(parents=True)
        write_current_run(ws, slug=slug)
        write_mode(ws, slug=slug)

        from hooks.validators import validator_plan
        ok, errs = validator_plan.run()
        expect("A2 空 plan/ → block", not ok)
        expect(
            "A2 错误信息含 '无 .md 文件'",
            any("无 .md 文件" in e for e in errs),
            "errs=" + str(errs),
        )
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_a3_plan_md_takes_precedence() -> None:
    """plan.md 单文件优先于 plan/ 目录 (V4.7 项目场景)."""
    ws = make_workspace()
    snap = setup_env(ws)
    try:
        slug = "test-precedence"
        rd = ws / ".superteam" / "runs" / slug
        rd.mkdir(parents=True)
        (rd / "plan.md").write_text(MIN_PLAN_BODY, encoding="utf-8")
        # plan/ 目录里塞垃圾 — 若 validator 误读 plan/ 会因解析不到 Task 报错
        (rd / "plan").mkdir()
        (rd / "plan" / "garbage.md").write_text("not a valid plan\n", encoding="utf-8")
        write_current_run(ws, slug=slug)
        write_mode(ws, slug=slug)

        from hooks.validators import validator_plan
        ok, errs = validator_plan.run()
        expect("A3 plan.md 优先 → validator OK", ok, "errs=" + str(errs))
    finally:
        restore_env(snap)
        destroy_workspace(ws)


# ---------- B · current_slug() 双源优先级 ----------

def case_b1_current_slug_prefers_mode_json() -> None:
    """mode.json.active_task_slug 应优先于 current-run.json.task_slug."""
    ws = make_workspace()
    snap = setup_env(ws)
    try:
        # 漂移场景: mode.json 是 phase-4-s3-module, current-run.json 是 store-management-system
        write_mode(ws, slug="phase-4-s3-module")
        write_current_run(ws, slug="store-management-system")

        # 强制重新 import 以避免缓存的旧 mode_state state
        for mod in ("hooks.lib.state", "hooks.lib.mode_state"):
            sys.modules.pop(mod, None)
        from hooks.lib import state
        got = state.current_slug()
        expect("B1 mode.json 优先", got == "phase-4-s3-module", f"got={got!r}")
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_b2_current_slug_falls_back_when_mode_empty() -> None:
    """mode.json 不存在 active_task_slug 时回退 current-run.json."""
    ws = make_workspace()
    snap = setup_env(ws)
    try:
        # mode.json 没有 active_task_slug
        write_mode(ws, slug=None)
        write_current_run(ws, slug="legacy-slug")

        for mod in ("hooks.lib.state", "hooks.lib.mode_state"):
            sys.modules.pop(mod, None)
        from hooks.lib import state
        got = state.current_slug()
        expect("B2 fallback 到 current-run.json", got == "legacy-slug", f"got={got!r}")
    finally:
        restore_env(snap)
        destroy_workspace(ws)


# ---------- C · gate_stage_advance verify.md / verification.md ----------

def _build_finish_transition_payload() -> dict:
    return {
        "file_path": ".superteam/state/current-run.json",
        "new_string": '"current_stage": "finish"',
    }


def case_c1_finish_accepts_verify_md() -> None:
    """verify→finish 接受 verify.md 命名 (V4.7 framework 标准)."""
    ws = make_workspace()
    snap = setup_env(ws)
    try:
        slug = "test-c1"
        rd = ws / ".superteam" / "runs" / slug
        rd.mkdir(parents=True)
        (rd / "verify.md").write_text("verdict: PASS\n", encoding="utf-8")
        write_mode(ws, slug=slug)
        write_current_run(ws, slug=slug, stage="verify")
        write_spawn_log(ws, slug, "verifier")

        for mod in ("hooks.lib.state", "hooks.lib.mode_state",
                    "hooks.gates.gate_stage_advance"):
            sys.modules.pop(mod, None)
        from hooks.gates import gate_stage_advance
        ok, reason = gate_stage_advance.check(_build_finish_transition_payload())
        expect("C1 verify.md → 允许 finish 推进", ok, f"reason={reason}")
    finally:
        restore_env(snap)
        destroy_workspace(ws)


def case_c2_finish_accepts_verification_md() -> None:
    """verify→finish 也接受 verification.md 命名 (V4.7.5 旧标准 · 向后兼容)."""
    ws = make_workspace()
    snap = setup_env(ws)
    try:
        slug = "test-c2"
        rd = ws / ".superteam" / "runs" / slug
        rd.mkdir(parents=True)
        (rd / "verification.md").write_text("verdict: PASS\n", encoding="utf-8")
        write_mode(ws, slug=slug)
        write_current_run(ws, slug=slug, stage="verify")
        write_spawn_log(ws, slug, "verifier")

        for mod in ("hooks.lib.state", "hooks.lib.mode_state",
                    "hooks.gates.gate_stage_advance"):
            sys.modules.pop(mod, None)
        from hooks.gates import gate_stage_advance
        ok, reason = gate_stage_advance.check(_build_finish_transition_payload())
        expect("C2 verification.md → 允许 finish 推进", ok, f"reason={reason}")
    finally:
        restore_env(snap)
        destroy_workspace(ws)


# ---------- runner ----------

CASES = [
    ("A1", case_a1_multifile_plan_dir_passes),
    ("A2", case_a2_empty_plan_dir_blocks),
    ("A3", case_a3_plan_md_takes_precedence),
    ("B1", case_b1_current_slug_prefers_mode_json),
    ("B2", case_b2_current_slug_falls_back_when_mode_empty),
    ("C1", case_c1_finish_accepts_verify_md),
    ("C2", case_c2_finish_accepts_verification_md),
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
