"""A13.1 / H1 / A11.9: SessionStart injects last-run report summary + handles retention.

- Inject <=500 tokens: last inspector report path + discrepancy count + open problems
- Rotate traces/reports keeping only 5 most recent (A11.9)
- Initialize compat cutover; migrate legacy .superteam/reviewer/ to inspector/
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from ..lib import compat, decisions, mode_state, plan_progress, state


def _latest_report_summary() -> str | None:
    d = state.inspector_dir()
    if not d or not (d / "reports").exists():
        return None
    reports = sorted((d / "reports").glob("*-report.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        return None
    p = reports[0]
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return None
    # Extract Improvement Findings count + Gate discrepancies count
    findings = len(re.findall(r"(?m)^#{3,4}\s+F-\d+", text))
    discrepancies = len(re.findall(r"discrepancy:\s*(YES|true)", text, re.IGNORECASE))
    rel = str(p).replace("\\", "/")
    return (
        f"上轮 inspector 报告: {rel}\n"
        f"- Improvement findings: {findings}\n"
        f"- Gate discrepancies: {discrepancies}\n"
        f"(完整内容见文件；若存在 critical 问题，本次 run 的 orchestrator 必须在 finish 阶段 acknowledge)"
    )


def _resume_directive(current_stage: str, pending_items: list[dict], repair_cycle: int, status: str) -> str | None:
    """Produce an explicit 'what to do next on resume' directive so Claude doesn't hesitate.

    G4-G7 are designed to run fully automatically after G3 close. Whenever a session
    resumes (new session after compact / session end), we tell Claude exactly what's
    next — no user confirmation needed.
    """
    if status in ("completed", "cancelled", "failed"):
        return None  # terminal — don't auto-resume
    if not current_stage or current_stage == "clarify":
        return None  # G1 needs user anyway
    if current_stage == "design":
        return "Resume 指令 (G2 阶段): 继续 design 循环 (solution options + ui-intent), G2 关闭需用户批准。"
    if current_stage == "plan":
        return "Resume 指令 (G3 阶段): 继续 plan 起草 (读 design/ui-intent), G3 关闭需用户批准 plan.md MUST 清单。"
    if current_stage == "execute":
        next_id = (pending_items[0].get("id") if pending_items else None) or "(no PENDING)"
        return (
            f"Resume 指令 (G4 自动化阶段): 下一 PENDING Unit = [{next_id}]. "
            f"直接写 `## Orchestrator Decision — {next_id}` 到 activity-trace.md, "
            f"然后 spawn superteam:executor. 无需用户确认 — hook 已校验好所有前置条件."
        )
    if current_stage == "review":
        return (
            "Resume 指令 (G5 自动化阶段): 读 review.md verdict. "
            "CLEAR/CLEAR_WITH_CONCERNS → 直接 spawn superteam:verifier. "
            "BLOCK → 自动 re-spawn executor 修 blockers (repair_cycle 自增). "
            "无需用户确认."
        )
    if current_stage == "verify":
        return (
            "Resume 指令 (G6 自动化阶段): 读 verification.md verdict. "
            "PASS → 进 finish 阶段 spawn superteam:inspector 出 post-run report. "
            "FAIL → 自动 re-spawn executor 修 (repair_cycle cap=3). "
            "INCOMPLETE → 补 evidence 或 re-plan. 无需用户确认."
        )
    if current_stage == "finish":
        return (
            "Resume 指令 (G7 自动化阶段): 若 inspector report 未生成 → spawn superteam:inspector. "
            "若已生成 → 写 finish.md (acknowledge 每条 problem record) + retrospective.md "
            "(improvement_action 非空) + 更新 health.json/insights.md/improvement-backlog.md. "
            "Stop 事件会自动放行. 无需用户确认."
        )
    return None


def _rotate(dir_: Path, pattern: str, keep: int = 5) -> None:
    if not dir_.exists():
        return
    files = sorted(dir_.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    archive = dir_.parent / f"{dir_.name}_archive"
    for old in files[keep:]:
        try:
            archive.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old), archive / old.name)
        except OSError:
            pass


def _or_mode_banner() -> str | None:
    """V4.7.1 — banner output is gated by mode_health(), not just is_or_active().

    - missing/ended → return None (silent — non-OR or already exited).
    - active → standard OR banner.
    - corrupt/unknown_schema → loud warning so the main session refuses to
      act as OR until the user repairs mode.json (per PLAN 4.6).
    """
    health = mode_state.mode_health()
    if health in (mode_state.MODE_HEALTH_MISSING, mode_state.MODE_HEALTH_ENDED):
        return None
    if health in (mode_state.MODE_HEALTH_CORRUPT, mode_state.MODE_HEALTH_UNKNOWN_SCHEMA):
        return (
            "【SuperTeam V4.7 警告：mode.json 状态异常】\n"
            f"health: {health}\n"
            "主会话**不应**继续担任 OR 角色。请先用 `/superteam:end` 显式退出，"
            "再用 `/superteam:go <slug>` 重新进入；或直接打开 `.superteam/state/mode.json` 检查并修复。\n"
            "在状态机修好之前，按普通 Claude Code 处理用户请求，不要执行七阶段流程。"
        )
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


def run() -> str:
    """Return additionalContext string (<=1500 chars). Empty if nothing to say."""
    # Cutover + migration
    compat.initialize_cutover()
    if compat.legacy_reviewer_dir_exists():
        compat.migrate_reviewer_to_inspector()

    # Rotate retention (A11.9)
    d = state.inspector_dir()
    if d:
        _rotate(d / "traces", "*.jsonl", keep=5)
        _rotate(d / "reports", "*-report.md", keep=5)
        _rotate(d / "reports", "*-report.html", keep=5)

    # Inject last-run summary
    bits: list[str] = []
    or_banner = _or_mode_banner()
    if or_banner:
        bits.append(or_banner)
    cr = state.read_current_run()
    if cr:
        bits.append(
            f"SuperTeam 运行状态: current_stage={cr.get('current_stage','?')}, "
            f"status={cr.get('status','?')}, repair_cycle={cr.get('repair_cycle_count',0)}"
        )
    summary = _latest_report_summary()
    if summary:
        bits.append(summary)

    # A5.5 inject plan-progress summary (remaining PENDING items)
    pp_summary = plan_progress.summary_for_injection()
    if pp_summary:
        bits.append(pp_summary)
    if plan_progress.plan_changed_since_init():
        bits.append(
            "⚠️ plan.md MUST 清单自上次初始化后已改动 — 可能需要 reopen G3 并重初始化 plan-progress"
        )

    # A5.7 explicit resume directive (G4-G7 must be fully automated after G3)
    directive = _resume_directive(
        current_stage=cr.get("current_stage", "") if cr else "",
        pending_items=plan_progress.pending_items(),
        repair_cycle=int(cr.get("repair_cycle_count", 0)) if cr else 0,
        status=cr.get("status", "") if cr else "",
    )
    if directive:
        bits.append(directive)
    # Also echo current-run.json's next_action if OR persisted one
    if cr and cr.get("next_action"):
        bits.append(f"上次 OR 记录的 next_action: {cr['next_action']}")
    if compat.in_tolerant_window():
        bits.append(
            "⚠️ 迁移窗口: 本项目尚未登记 V4.6.0 cutover, commit-gate 处于宽容模式。"
            "运行 `/superteam:migrate` (待实施) 完成追溯审计后恢复严格模式。"
        )
    return "\n\n".join(bits)
