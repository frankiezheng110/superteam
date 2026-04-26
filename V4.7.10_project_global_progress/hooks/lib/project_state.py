"""V4.7.10 — project layer state machine.

A *project* is a multi-milestone delivery; each milestone is one phase
(one SuperTeam workflow run). project.md lives at the project root
(`.superteam/project.md`, sibling of `state/`) and persists across sessions
and across phases.

V4.7.9 had only one layer: `mode.json.project_lifecycle ∈ {running, paused,
ended}`, which conflated phase-finish with project-end. SMS phase-4-s3-module
walking through `finish` flipped lifecycle=ended even though SMS still has
V1.5+ → V2.0.0 milestones to ship. V4.7.10 introduces the project layer
above mode.json so phase-finish marks one milestone DONE without ending the
project.

Stop hook decision precedence:
    1. project.md present → consult `is_project_active()` (this module)
    2. project.md absent  → fall back to V4.7.9 `mode_state.is_project_alive()`

Schema (project.md):

    ---
    schema_version: 1
    project_name: SMS
    project_slug: store-management-system
    target_release: V2.0.0_release
    status: in_progress | complete
    current_milestone_slug: phase-5-desktop
    created_at: ISO8601
    last_updated: ISO8601
    ---

    # Project: <human name>

    ## Milestones

    | # | Version | Phase Slug | Status | Started | Completed | Notes |
    |---|---------|------------|--------|---------|-----------|-------|
    | 1 | V1.0.0  | foundation | DONE   | ...     | ...       | ...   |
    ...

    ## Decision Log
    ...

    ## Pending Cross-Milestone Items
    ...

The frontmatter is the structured truth; the body's tables and logs are
human-readable annotations the OR / inspector / writer maintain.

Frontmatter parser is line-based (no YAML dependency) — keys at the top
level, simple `key: value` form. Sufficient for the V1 schema; if the
schema grows nested fields, switch to a real YAML parser.
"""
from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import state as _state


PROJECT_FILE_NAME = "project.md"
SCHEMA_VERSION = 1

# ---------- path / time helpers ----------

def project_path() -> Path | None:
    d = _state.superteam_dir()
    return d / PROJECT_FILE_NAME if d else None


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------- frontmatter ----------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(?P<fm>.*?)\n---\s*\n?", re.DOTALL)


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse a leading `---\\n...\\n---` block as flat key:value pairs.

    Returns {} when no frontmatter or on parse error. Values are kept as
    strings — schema_version is coerced to int by callers that need it.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    body = m.group("fm")
    out: dict[str, Any] = {}
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def _format_frontmatter(data: dict[str, Any]) -> str:
    # Stable key order so diff stays small across writes.
    ordered_keys = [
        "schema_version", "project_name", "project_slug", "target_release",
        "status", "current_milestone_slug", "created_at", "last_updated",
    ]
    seen: set[str] = set()
    lines = ["---"]
    for k in ordered_keys:
        if k in data:
            lines.append(f"{k}: {data[k]}")
            seen.add(k)
    for k, v in data.items():
        if k in seen:
            continue
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def read_project_text() -> str:
    """Full project.md text, or '' when missing."""
    p = project_path()
    if not p or not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def read_project() -> dict[str, Any]:
    """Frontmatter as a dict; {} when missing / unreadable / no frontmatter."""
    return _parse_frontmatter(read_project_text())


def _split_frontmatter_and_body(text: str) -> tuple[str, str]:
    """Return (fm_block_text_with_delims, body_after_fm). Empty fm if absent."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    return m.group(0), text[m.end():]


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_project_frontmatter(updates: dict[str, Any]) -> bool:
    """Merge `updates` into the existing frontmatter and rewrite atomically.

    Body (markdown content after the frontmatter) is preserved byte-for-byte.
    `last_updated` is always refreshed. Returns False when project.md is
    absent — callers must `init_project()` first.
    """
    p = project_path()
    if not p or not p.exists():
        return False
    text = read_project_text()
    fm = _parse_frontmatter(text) or {}
    fm.update(updates)
    fm["last_updated"] = _utcnow_iso()
    _, body = _split_frontmatter_and_body(text)
    new_text = _format_frontmatter(fm) + body
    try:
        _atomic_write(p, new_text)
    except OSError:
        return False
    return True


# ---------- public read accessors ----------

def project_status() -> str:
    """'in_progress' / 'complete' / '' (when project.md missing)."""
    return read_project().get("status", "")


def is_project_active() -> bool:
    """V4.7.10 — single boolean stop hook reads when project.md is present.

    True  ⇔ project.md exists AND status != 'complete'
    False ⇔ project.md missing (no project layer in this directory)
            OR status == 'complete'

    Fail-closed mirroring V4.7.9 mode_state.is_project_alive: any unexpected
    read failure → treat as active (OR cannot self-stop).
    """
    try:
        p = project_path()
        if p is None or not p.exists():
            return False
        return project_status() != "complete"
    except Exception:  # noqa: BLE001 — defense-in-depth fail-closed
        return True


def current_milestone_slug() -> str:
    return read_project().get("current_milestone_slug", "")


def project_name() -> str:
    return read_project().get("project_name", "") or read_project().get("project_slug", "")


# ---------- milestone table ----------

# Match a row in the milestones markdown table:
# | # | Version | Phase Slug | Status | Started | Completed | Notes |
# Captures the leading `| <n> | <ver> | <slug> |` and the cells after slug.
_MILESTONE_ROW_RE = re.compile(
    r"^(?P<prefix>\|\s*\d+\s*\|[^|]*\|\s*)(?P<slug>[^|]+?)(?P<after>\s*\|\s*)"
    r"(?P<status>[^|]*?)(?P<rest>\s*\|.*\|)\s*$",
    re.MULTILINE,
)


def list_milestones() -> list[dict[str, str]]:
    """Parse the Milestones table; return a list of dicts keyed by slug.

    Best-effort: returns [] when no table is found or it is malformed.
    Each entry contains: number, version, phase_slug, status, started,
    completed, notes (each may be empty string).
    """
    text = read_project_text()
    if not text:
        return []
    # Limit search to the body (after frontmatter)
    _, body = _split_frontmatter_and_body(text)
    out: list[dict[str, str]] = []
    in_table = False
    header_cols: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not in_table:
            # First table row is the header; second is `|---|---|...`
            if any(c.lower() in ("phase slug", "phase_slug") for c in cells):
                header_cols = [c.lower() for c in cells]
                in_table = True
            continue
        if all(set(c) <= set("- :") for c in cells if c):
            # Separator row — skip
            continue
        row = dict(zip(header_cols, cells))
        slug = row.get("phase slug") or row.get("phase_slug") or ""
        if not slug or slug.startswith("---"):
            continue
        out.append({
            "number": row.get("#", ""),
            "version": row.get("version", ""),
            "phase_slug": slug,
            "status": row.get("status", ""),
            "started": row.get("started", ""),
            "completed": row.get("completed", ""),
            "notes": row.get("notes", ""),
        })
    return out


def find_milestone(slug: str) -> dict[str, str] | None:
    for row in list_milestones():
        if row["phase_slug"] == slug:
            return row
    return None


def next_pending_milestone() -> dict[str, str] | None:
    """Return the first row with status PENDING / IN_PROGRESS, else None."""
    for row in list_milestones():
        s = (row.get("status") or "").upper()
        if s in ("PENDING", "IN_PROGRESS", "TODO"):
            return row
    return None


def mark_milestone_done(slug: str, *, completed_at: str | None = None) -> bool:
    """Update milestone row `phase_slug=slug` Status → DONE, fill Completed.

    Idempotent: rerunning on an already-DONE row is a no-op success.
    Returns False when project.md missing or row not found.
    """
    p = project_path()
    if not p or not p.exists():
        return False
    text = read_project_text()
    if not text:
        return False

    completed = completed_at or _utcnow_iso()[:10]  # YYYY-MM-DD

    # Walk the milestone table line-by-line to avoid clobbering similar
    # text outside the table.
    lines = text.splitlines(keepends=True)
    in_table = False
    header_cols: list[str] = []
    changed = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        cells_raw = stripped.strip("|").split("|")
        cells = [c.strip() for c in cells_raw]
        if not in_table:
            if any(c.lower() in ("phase slug", "phase_slug") for c in cells):
                header_cols = [c.lower() for c in cells]
                in_table = True
            continue
        if all(set(c) <= set("- :") for c in cells if c):
            continue
        row = dict(zip(header_cols, cells))
        row_slug = row.get("phase slug") or row.get("phase_slug") or ""
        if row_slug != slug:
            continue

        # Found the row — rebuild it preserving widths and order.
        idx_status = None
        idx_completed = None
        for j, h in enumerate(header_cols):
            if h == "status":
                idx_status = j
            elif h == "completed":
                idx_completed = j
        if idx_status is not None:
            cells_raw[idx_status] = f" DONE "
        if idx_completed is not None:
            cells_raw[idx_completed] = f" {completed} "
        rebuilt = "|" + "|".join(cells_raw) + "|"
        # Preserve original line ending
        ending = line[len(line.rstrip("\r\n")):]
        lines[i] = rebuilt + ending
        changed = True
        break

    if not changed:
        return False

    new_text = "".join(lines)

    # Also bump frontmatter last_updated (write_project_frontmatter handles)
    fm = _parse_frontmatter(text) or {}
    fm["last_updated"] = _utcnow_iso()
    _, body_after = _split_frontmatter_and_body(new_text)
    final_text = _format_frontmatter(fm) + body_after
    try:
        _atomic_write(p, final_text)
    except OSError:
        return False
    return True


def set_current_milestone(slug: str) -> bool:
    """Update `current_milestone_slug` in frontmatter."""
    return write_project_frontmatter({"current_milestone_slug": slug})


def set_project_complete(by: str = "user") -> bool:
    """Set status=complete in frontmatter. Recorded `completed_by` field."""
    return write_project_frontmatter({"status": "complete", "completed_by": by})


def reopen_project(reason: str = "phase-finish-mismark") -> bool:
    """Force project.md status back to in_progress.

    Use case: V4.7.9 misclassified a phase finish as project end and the
    operator needs to revive the project to continue subsequent milestones.
    Records `reopened_at` + `reopened_reason` for audit.
    """
    if not project_path() or not project_path().exists():
        return False
    return write_project_frontmatter({
        "status": "in_progress",
        "reopened_at": _utcnow_iso(),
        "reopened_reason": reason,
    })


# ---------- creation ----------

def init_project(
    *,
    name: str,
    slug: str,
    target_release: str,
    milestones: list[dict[str, str]] | None = None,
) -> bool:
    """Create `.superteam/project.md` with a minimal scaffold.

    `milestones`: optional list of {version, phase_slug, status, notes} dicts
    used to seed the Milestones table. When None, a single placeholder row
    is emitted.
    Returns False when no .superteam root or the file already exists.
    """
    p = project_path()
    if not p:
        return False
    if p.exists():
        return False  # don't overwrite — operator must edit by hand or use the CLI updaters

    now = _utcnow_iso()
    fm = {
        "schema_version": SCHEMA_VERSION,
        "project_name": name,
        "project_slug": slug,
        "target_release": target_release,
        "status": "in_progress",
        "current_milestone_slug": (milestones[0]["phase_slug"] if milestones else ""),
        "created_at": now,
        "last_updated": now,
    }

    rows: list[str] = []
    rows.append("| # | Version | Phase Slug | Status | Started | Completed | Notes |")
    rows.append("|---|---------|------------|--------|---------|-----------|-------|")
    if milestones:
        for i, m in enumerate(milestones, start=1):
            rows.append(
                f"| {i} | {m.get('version','')} | {m.get('phase_slug','')} | "
                f"{m.get('status','PENDING')} | {m.get('started','-')} | "
                f"{m.get('completed','-')} | {m.get('notes','')} |"
            )
    else:
        rows.append("| 1 | (placeholder) | (set by operator) | PENDING | - | - | - |")

    body = (
        f"\n# Project: {name}\n\n"
        "## Milestones\n\n"
        + "\n".join(rows)
        + "\n\n## Decision Log\n\n"
        "(Cross-milestone decisions go here. Append; do not delete history.)\n\n"
        "## Pending Cross-Milestone Items\n\n"
        "- (operator-edited)\n"
    )

    text = _format_frontmatter(fm) + body
    try:
        _atomic_write(p, text)
    except OSError:
        return False
    return True
