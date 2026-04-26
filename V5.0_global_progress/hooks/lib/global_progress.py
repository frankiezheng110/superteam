"""V5.0 — global progress banner aggregator.

Reads the five existing truth sources (project.md / mode.json /
current-run.json / plan-progress.json / feature-tdd-state.json) and
renders one unified banner that names where the OR is in the full
project → milestone → phase → stage → MUST → feature hierarchy.

Design philosophy: 疏不堵. The banner is injected by SessionStart and
UserPromptSubmit hooks into the OR's input stream every turn. The OR
cannot skip reading it — the banner is part of the prompt, not an
optional tool call. When the OR sees the full hierarchy, it
structurally cannot mistake one milestone for the whole project.

This module is read-only on top of the existing state libs. It does
not migrate, write, or own any state file. All sources fail-soft —
a single broken file degrades the banner, never crashes the hook.
"""
from __future__ import annotations

from typing import Any

from . import mode_state, plan_progress, project_state, state


# ---------- visual helpers ----------

def _progress_bar(done: int, total: int, width: int = 14) -> str:
    if total <= 0:
        return "[" + " " * width + "]"
    filled = int(round(width * done / total))
    filled = max(0, min(width, filled))
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def _safe(getter, default: Any = None) -> Any:
    """Call getter() catching every exception. Truth-source failures must
    degrade the banner, never break the hook."""
    try:
        return getter()
    except Exception:  # noqa: BLE001
        return default


# ---------- per-layer render ----------

def _render_milestone_layer() -> list[str] | None:
    fm = _safe(project_state.read_project, {}) or {}
    if not fm:
        return None
    rows = _safe(project_state.list_milestones, []) or []
    if not rows:
        # frontmatter exists but no milestone table — still useful summary.
        name = fm.get("project_name") or fm.get("project_slug") or "(unset)"
        target = fm.get("target_release") or "(unset)"
        status = fm.get("status") or "(unset)"
        return [
            f"SuperTeam project: {name} / target {target} / status {status}",
            "(milestone table empty — fill .superteam/project.md)",
        ]

    name = fm.get("project_name") or fm.get("project_slug") or "(unset)"
    target = fm.get("target_release") or "(unset)"
    status = fm.get("status") or "(unset)"
    cur_slug = fm.get("current_milestone_slug") or ""

    done_count = sum(1 for r in rows if (r.get("status") or "").upper() == "DONE")
    total = len(rows)
    pending = total - done_count
    bar = _progress_bar(done_count, total)

    lines: list[str] = []
    lines.append(f"SuperTeam project: {name} / target {target} / status {status}")
    lines.append(
        f"{bar} {done_count}/{total} milestones DONE · {pending} remaining"
    )
    lines.append("")
    lines.append("Milestone roadmap:")
    for r in rows:
        slug = r.get("phase_slug", "")
        version = r.get("version", "")
        st = (r.get("status") or "").upper()
        marker = "  ✓" if st == "DONE" else ("  ▶" if slug == cur_slug else "   ")
        tail = ""
        if slug == cur_slug:
            tail = "  ← 你在这里"
        lines.append(f"{marker} {version:<24} {slug:<28} {st:<11}{tail}")
    return lines


def _render_phase_stage_layer() -> list[str] | None:
    md = _safe(mode_state.read_mode, {}) or {}
    cr = _safe(state.read_current_run, {}) or {}
    if not md and not cr:
        return None
    slug = md.get("active_task_slug") or cr.get("task_slug") or "(unset)"
    cur_stage = cr.get("current_stage") or "(not started)"
    repair = cr.get("repair_cycle_count", 0)
    status = cr.get("status", "active")
    lifecycle = md.get("project_lifecycle", "running")
    lines = [
        f"Current phase: {slug} · stage: {cur_stage} · status: {status}"
        f" · lifecycle: {lifecycle}"
        + (f" · repair_cycle: {repair}" if repair else ""),
    ]
    return lines


def _render_must_progress_layer() -> list[str] | None:
    data = _safe(plan_progress.read_progress, {}) or {}
    items = data.get("items") or {}
    if not items:
        return None
    by_status: dict[str, int] = {}
    for v in items.values():
        st = (v.get("status") or "?").upper()
        by_status[st] = by_status.get(st, 0) + 1
    total = len(items)
    done = by_status.get("COMPLETE", 0)
    pending = by_status.get("PENDING", 0)
    blocked = by_status.get("BLOCKED", 0)
    deferred = by_status.get("DEFERRED", 0)
    bar = _progress_bar(done, total, width=10)
    breakdown = (
        f"COMPLETE {done} · PENDING {pending}"
        + (f" · BLOCKED {blocked}" if blocked else "")
        + (f" · DEFERRED {deferred}" if deferred else "")
    )
    lines = [f"MUST progress: {bar} {done}/{total}  ({breakdown})"]

    # Surface up to 3 PENDING ids (next concrete work) and up to 3 COMPLETE
    # ids (recent progress) so the OR has both axes of context.
    pending_ids: list[str] = []
    complete_ids: list[str] = []
    for mid, v in items.items():
        st = (v.get("status") or "").upper()
        desc = (v.get("desc", "") or "")[:48]
        if st == "PENDING" and len(pending_ids) < 3:
            pending_ids.append(f"[{mid}] {desc}")
        elif st == "COMPLETE" and len(complete_ids) < 3:
            complete_ids.append(f"[{mid}] {desc}")
    if pending_ids:
        lines.append("Next PENDING MUST:")
        for p in pending_ids:
            lines.append(f"  - {p}")
    if complete_ids:
        lines.append("Recently COMPLETE MUST:")
        for c in complete_ids:
            lines.append(f"  - {c}")
    return lines


def _render_feature_layer() -> list[str] | None:
    s = _safe(state.read_tdd_state, {}) or {}
    fid = s.get("active_feature_id")
    if not fid:
        return None
    feat = s.get("features", {}).get(fid, {}) or {}
    fstate = feat.get("state") or "PENDING"
    return [f"Active feature: {fid} · TDD state: {fstate}"]


def _closing_directive() -> list[str]:
    """The structural reminder that prevents 套娃 误判."""
    return [
        "",
        "phase finish 只标当前 milestone DONE,不结束项目。",
        "唯一项目结束路径: 全部 milestone DONE 后 /superteam:project-complete。",
    ]


# ---------- public API ----------

BANNER_HEADER = "【SuperTeam V5.0 global progress】"


def render_progress_banner() -> str | None:
    """Render the unified progress banner. Returns None when no SuperTeam
    state is present in this directory (non-OR project; hook stays silent).

    Layout:
      header
      milestone layer       (project.md present)
      phase/stage layer     (mode.json or current-run.json present)
      MUST progress layer   (plan-progress.json initialized)
      feature layer         (feature-tdd-state.json has active_feature_id)
      closing directive     (only when at least one layer was rendered)
    """
    sections: list[list[str]] = []
    for renderer in (
        _render_milestone_layer,
        _render_phase_stage_layer,
        _render_must_progress_layer,
        _render_feature_layer,
    ):
        block = _safe(renderer, None)
        if block:
            sections.append(block)

    if not sections:
        return None

    out: list[str] = [BANNER_HEADER]
    for i, block in enumerate(sections):
        out.extend(block)
        if i < len(sections) - 1:
            out.append("")
    out.extend(_closing_directive())
    return "\n".join(out)
