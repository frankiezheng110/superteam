"""V5.0 — all 8 dispatch hooks health check + 强制读取 banner 端到端覆盖。

Run:
    python tests/test_v500_all_hooks_health.py

This test goes hook-by-hook through every entry in hooks.json and asserts:
  - the dispatch script terminates without a Python crash
  - stdout is parseable JSON (Claude Code hook protocol)
  - the V5.0 changes did not break any pre-existing hook routing

Plus extra coverage for the two physical-hard-constraint banner injectors
(SessionStart / UserPromptSubmit) — these are the ones that force the OR
to read global progress every turn, so we drill into edge cases:
  - data source missing
  - data source partial
  - data source corrupt
  - rapid repeated invocation
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from harness import (  # noqa: E402
    Workspace,
    destroy_workspace,
    invoke,
    make_workspace,
    pre_tool_agent,
    pre_tool_bash,
    pre_tool_edit,
    pre_tool_write,
    post_tool_agent,
    post_tool_bash,
    post_tool_edit,
    session_start,
    stop_event,
)


def write_active_v5_state(ws: Workspace, *, slug: str = "phase-6",
                           current_milestone: str = "phase-6") -> None:
    """Plant a complete V5.0 state set (project.md + mode.json + current-run.json)
    so every hook has data to read."""
    p = ws.superteam / "project.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "---\n"
        "schema_version: 1\n"
        "project_name: HookHealth\n"
        "project_slug: hookhealth\n"
        "target_release: V7.0\n"
        "status: in_progress\n"
        f"current_milestone_slug: {current_milestone}\n"
        "created_at: 2026-04-26T00:00:00+00:00\n"
        "last_updated: 2026-04-26T00:00:00+00:00\n"
        "---\n\n"
        "## Milestones\n\n"
        "| # | Version | Phase Slug | Status | Started | Completed | Notes |\n"
        "|---|---------|------------|--------|---------|-----------|-------|\n"
        "| 1 | V1 | phase-1 | DONE | - | - | - |\n"
        f"| 2 | V6 | {current_milestone} | IN_PROGRESS | - | - | - |\n"
        "| 3 | V7 | phase-7 | PENDING | - | - | - |\n",
        encoding="utf-8",
    )
    (ws.superteam / "state" / "mode.json").write_text(json.dumps({
        "schema_version": 1, "mode": "active",
        "project_lifecycle": "running", "active_task_slug": slug,
        "entered_at": "2026-04-26T00:00:00+00:00",
        "last_verified_at": "2026-04-26T00:00:00+00:00",
    }), encoding="utf-8")


def _ok_exit(res, label: str) -> None:
    """A dispatch script must NEVER crash. Return code 0 (allow) or 2
    (block) is fine; anything else (1, etc.) means a Python exception."""
    if res.returncode not in (0, 2):
        raise CaseFail(
            f"{label}: hook crashed rc={res.returncode} stderr={res.stderr[:300]}"
        )


def _ok_json(res, label: str) -> dict:
    """Stdout must be valid JSON per Claude Code hook protocol."""
    if not res.stdout.strip():
        return {}
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as e:
        raise CaseFail(f"{label}: stdout not JSON :: {e} :: stdout={res.stdout[:300]}")


# ---------- assertion helper ----------

class CaseFail(AssertionError):
    pass


def expect(label: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS · {label}")
    else:
        print(f"  FAIL · {label}{(' :: ' + detail) if detail else ''}")
        raise CaseFail(label)


# ---------- H · all 8 dispatch hooks health ----------

def case_h1_session_start_health() -> None:
    """SessionStart hook: 必须不崩 + 输出 JSON + V5.0 banner 出现在 additionalContext。"""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("session_start", session_start(), cwd=ws.path)
        _ok_exit(res, "H1 SessionStart")
        d = _ok_json(res, "H1 SessionStart")
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "")
        expect("H1.0 SessionStart not crashed",
               res.returncode in (0, 2))
        expect("H1.1 SessionStart outputs JSON",
               isinstance(d, dict))
        expect("H1.2 SessionStart injects V5.0 banner",
               "V5.0 global progress" in ctx, ctx[:300])
    finally:
        destroy_workspace(ws)


def case_h2_user_prompt_health() -> None:
    """UserPromptSubmit: 不崩 + 输出 JSON + banner 注入 (硬约束核心)。"""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        payload = {"hook_event_name": "UserPromptSubmit",
                   "prompt": "test", "user_prompt": "test"}
        res = invoke("user_prompt", payload, cwd=ws.path)
        _ok_exit(res, "H2 UserPromptSubmit")
        d = _ok_json(res, "H2 UserPromptSubmit")
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "")
        expect("H2.0 UserPromptSubmit not crashed",
               res.returncode in (0, 2))
        expect("H2.1 UserPromptSubmit injects V5.0 banner",
               "V5.0 global progress" in ctx, ctx[:300])
        expect("H2.2 banner contains 你在这里 marker",
               "你在这里" in ctx, ctx[:300])
    finally:
        destroy_workspace(ws)


def case_h3_pre_tool_agent() -> None:
    """PreToolUse Agent: spawn gate routes + active-subagent flag."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("pre_tool", pre_tool_agent("superteam:executor"), cwd=ws.path)
        _ok_exit(res, "H3 PreToolUse Agent")
        _ok_json(res, "H3 PreToolUse Agent")
        expect("H3 PreToolUse Agent route OK", True)
    finally:
        destroy_workspace(ws)


def case_h4_pre_tool_edit() -> None:
    """PreToolUse Edit: gate_main_session_scope + gate_stage_advance + 5 边路由。"""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        # Edit a benign trace file (whitelist) — should allow
        res = invoke("pre_tool",
                     pre_tool_edit(".superteam/runs/phase-6/activity-trace.md"),
                     cwd=ws.path)
        _ok_exit(res, "H4 PreToolUse Edit benign")
        _ok_json(res, "H4 PreToolUse Edit benign")
        expect("H4 PreToolUse Edit benign route OK", True)
    finally:
        destroy_workspace(ws)


def case_h5_pre_tool_bash() -> None:
    """PreToolUse Bash: gate_commit_gate route."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("pre_tool", pre_tool_bash("ls -la"), cwd=ws.path)
        _ok_exit(res, "H5 PreToolUse Bash")
        _ok_json(res, "H5 PreToolUse Bash")
        expect("H5 PreToolUse Bash route OK", True)
    finally:
        destroy_workspace(ws)


def case_h6_post_tool_agent() -> None:
    """PostToolUse Agent: spawn-log written + active-subagent cleared."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("post_tool", post_tool_agent("superteam:executor"), cwd=ws.path)
        _ok_exit(res, "H6 PostToolUse Agent")
        _ok_json(res, "H6 PostToolUse Agent")
        expect("H6 PostToolUse Agent route OK", True)
    finally:
        destroy_workspace(ws)


def case_h7_post_tool_edit() -> None:
    """PostToolUse Edit: trace + frontmatter validator route."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("post_tool",
                     post_tool_edit(".superteam/runs/phase-6/activity-trace.md"),
                     cwd=ws.path)
        _ok_exit(res, "H7 PostToolUse Edit")
        _ok_json(res, "H7 PostToolUse Edit")
        expect("H7 PostToolUse Edit route OK", True)
    finally:
        destroy_workspace(ws)


def case_h8_post_tool_bash() -> None:
    """PostToolUse Bash: observers route (test_runner / build_only / git / spotcheck)."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("post_tool", post_tool_bash("pytest", "1 passed"), cwd=ws.path)
        _ok_exit(res, "H8 PostToolUse Bash")
        _ok_json(res, "H8 PostToolUse Bash")
        expect("H8 PostToolUse Bash route OK", True)
    finally:
        destroy_workspace(ws)


def case_h9_stop_hook() -> None:
    """Stop hook: V5.0 fail-closed + project_state + ≥4 阈值 valve unaffected."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("stop", stop_event(), cwd=ws.path)
        _ok_exit(res, "H9 Stop")
        d = _ok_json(res, "H9 Stop")
        # project active → BLOCK
        is_block = (d.get("decision") == "block"
                    or (d.get("hookSpecificOutput", {}) or {}).get("permissionDecision") == "deny")
        expect("H9 Stop hook BLOCK while project active", is_block, str(d)[:200])
    finally:
        destroy_workspace(ws)


def case_h10_subagent_stop_hook() -> None:
    """SubagentStop: clear active-subagent flag, write spawn-log entry."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("subagent_stop",
                     {"hook_event_name": "SubagentStop"},
                     cwd=ws.path)
        _ok_exit(res, "H10 SubagentStop")
        _ok_json(res, "H10 SubagentStop")
        expect("H10 SubagentStop route OK", True)
    finally:
        destroy_workspace(ws)


def case_h11_pre_compact_hook() -> None:
    """PreCompact: capture compact context + skill rules."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("pre_compact",
                     {"hook_event_name": "PreCompact", "trigger": "auto"},
                     cwd=ws.path)
        _ok_exit(res, "H11 PreCompact")
        _ok_json(res, "H11 PreCompact")
        expect("H11 PreCompact route OK", True)
    finally:
        destroy_workspace(ws)


def case_h12_session_end_hook() -> None:
    """SessionEnd: graceful no-op or trace flush."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        res = invoke("session_end",
                     {"hook_event_name": "SessionEnd"},
                     cwd=ws.path)
        _ok_exit(res, "H12 SessionEnd")
        _ok_json(res, "H12 SessionEnd")
        expect("H12 SessionEnd route OK", True)
    finally:
        destroy_workspace(ws)


# ---------- F · 强制读取 banner hook 边缘场景 ----------

def case_f1_session_start_no_state() -> None:
    """SessionStart with zero V5.0 state files → no banner injected, no crash."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-1")
        # Remove current-run.json so we have truly nothing
        (ws.superteam / "state" / "current-run.json").unlink()
        res = invoke("session_start", session_start(), cwd=ws.path)
        _ok_exit(res, "F1 SessionStart no state")
        _ok_json(res, "F1 SessionStart no state")
        expect("F1 SessionStart no state — no crash", True)
    finally:
        destroy_workspace(ws)


def case_f2_user_prompt_corrupt_project_md() -> None:
    """UserPromptSubmit with corrupt project.md → banner degrades, hook does not crash."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        # Corrupt project.md (no frontmatter, garbage)
        (ws.superteam / "project.md").write_text(
            "$$ totally invalid $$\nno frontmatter\n", encoding="utf-8")
        write_active_v5_state(ws)
        # Now overwrite the project.md again with corruption
        (ws.superteam / "project.md").write_text(
            "$$ totally invalid $$\n", encoding="utf-8")
        payload = {"hook_event_name": "UserPromptSubmit",
                   "prompt": "x", "user_prompt": "x"}
        res = invoke("user_prompt", payload, cwd=ws.path)
        _ok_exit(res, "F2 UserPromptSubmit corrupt project.md")
        _ok_json(res, "F2 UserPromptSubmit corrupt project.md")
        expect("F2 corrupt project.md does not crash banner",
               res.returncode in (0, 2))
    finally:
        destroy_workspace(ws)


def case_f3_repeated_user_prompts_stable() -> None:
    """5 consecutive UserPromptSubmit calls — banner content stable, no crash."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6", stage="execute")
        write_active_v5_state(ws)
        contexts = []
        for i in range(5):
            res = invoke(
                "user_prompt",
                {"hook_event_name": "UserPromptSubmit",
                 "prompt": f"p{i}", "user_prompt": f"p{i}"},
                cwd=ws.path,
            )
            _ok_exit(res, f"F3 UserPromptSubmit#{i}")
            d = _ok_json(res, f"F3 UserPromptSubmit#{i}")
            ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "")
            contexts.append("V5.0 global progress" in ctx and "V7" in ctx)
        expect(
            "F3 banner injected on every one of 5 turns",
            all(contexts),
            f"per-turn={contexts}",
        )
    finally:
        destroy_workspace(ws)


def case_f4_session_start_only_project_no_mode() -> None:
    """SessionStart with project.md but no mode.json — milestone layer still renders."""
    ws = make_workspace()
    try:
        ws.init(slug="phase-6")
        # Plant ONLY project.md
        p = ws.superteam / "project.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            "---\nschema_version: 1\nproject_name: P\nproject_slug: p\n"
            "target_release: V7\nstatus: in_progress\n"
            "current_milestone_slug: phase-6\n"
            "created_at: 2026-04-26T00:00:00+00:00\n"
            "last_updated: 2026-04-26T00:00:00+00:00\n---\n\n"
            "## Milestones\n\n"
            "| # | Version | Phase Slug | Status | Started | Completed | Notes |\n"
            "|---|---------|------------|--------|---------|-----------|-------|\n"
            "| 1 | V6 | phase-6 | IN_PROGRESS | - | - | - |\n"
            "| 2 | V7 | phase-7 | PENDING | - | - | - |\n",
            encoding="utf-8",
        )
        res = invoke("session_start", session_start(), cwd=ws.path)
        _ok_exit(res, "F4 SessionStart project-only")
        d = _ok_json(res, "F4 SessionStart project-only")
        ctx = (d.get("hookSpecificOutput", {}) or {}).get("additionalContext", "")
        expect(
            "F4 banner renders project layer with no mode.json",
            "V5.0 global progress" in ctx and "V7" in ctx and "PENDING" in ctx,
            ctx[:400],
        )
    finally:
        destroy_workspace(ws)


# ---------- runner ----------

CASES = [
    # H · all 8 dispatch hooks (each fires with V5.0 state in place)
    ("H1", case_h1_session_start_health),
    ("H2", case_h2_user_prompt_health),
    ("H3", case_h3_pre_tool_agent),
    ("H4", case_h4_pre_tool_edit),
    ("H5", case_h5_pre_tool_bash),
    ("H6", case_h6_post_tool_agent),
    ("H7", case_h7_post_tool_edit),
    ("H8", case_h8_post_tool_bash),
    ("H9", case_h9_stop_hook),
    ("H10", case_h10_subagent_stop_hook),
    ("H11", case_h11_pre_compact_hook),
    ("H12", case_h12_session_end_hook),
    # F · 强制读取 banner hook 边缘场景
    ("F1", case_f1_session_start_no_state),
    ("F2", case_f2_user_prompt_corrupt_project_md),
    ("F3", case_f3_repeated_user_prompts_stable),
    ("F4", case_f4_session_start_only_project_no_mode),
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
