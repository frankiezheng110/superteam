"""Plan-level MUST progress tracker for interruption resilience.

.superteam/state/plan-progress.json records per-MUST-item status so that
- OR resuming after compaction / session end knows what remains
- Orchestrator Decision Log can only point to PENDING (not COMPLETE) units
- SessionStart can inject a concise remaining-work summary

Lifecycle:
  G3 close → initialize() fills items with status=PENDING and plan_sha256
  executor feature GREEN → mark(item_id, "COMPLETE", evidence)
  user or OR defers   → mark(item_id, "DEFERRED", reason)
  block encountered   → mark(item_id, "BLOCKED", reason)

If plan_sha256 changes (plan.md MUST list edited) → snapshot requires re-init
(supplement_mode=G3-reopen enables that).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import parser, state


def _progress_path() -> Path | None:
    d = state.state_dir()
    return d / "plan-progress.json" if d else None


def _plan_path() -> Path | None:
    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    return rd / "plan.md" if rd else None


def _plan_sha(plan_text: str) -> str:
    must_items = parser.plan_must_items(plan_text)
    joined = "|".join(sorted(must_items))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def read_progress() -> dict[str, Any]:
    p = _progress_path()
    if not p or not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def write_progress(data: dict[str, Any]) -> None:
    p = _progress_path()
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def initialize(plan_text: str | None = None) -> dict[str, Any]:
    """Initialize plan-progress.json from current plan.md (on G3 close)."""
    if plan_text is None:
        pp = _plan_path()
        if not pp or not pp.exists():
            return {}
        plan_text = pp.read_text(encoding="utf-8")
    items_struct = parser.plan_must_items_structured(plan_text)
    items: dict[str, dict[str, Any]] = {}
    for it in items_struct:
        items[it.must_id] = {
            "status": "PENDING",
            "category": it.category,
            "desc": it.desc,
            "initialized_at": datetime.now(timezone.utc).isoformat(),
        }
    data = {
        "plan_sha256": _plan_sha(plan_text),
        "initialized_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }
    write_progress(data)
    return data


def is_initialized() -> bool:
    return bool(read_progress())


def _ensure_initialized() -> dict[str, Any]:
    data = read_progress()
    if data:
        return data
    pp = _plan_path()
    if not pp or not pp.exists():
        return {}
    return initialize(pp.read_text(encoding="utf-8"))


def mark(must_id: str, status: str, **fields: Any) -> bool:
    """Update a MUST item's status. Returns True if updated."""
    if status not in ("PENDING", "COMPLETE", "DEFERRED", "BLOCKED"):
        return False
    data = _ensure_initialized()
    if not data:
        return False
    items = data.setdefault("items", {})
    if must_id not in items:
        return False
    items[must_id]["status"] = status
    items[must_id].update(fields)
    items[must_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["last_updated"] = items[must_id]["updated_at"]
    write_progress(data)
    return True


def item_status(must_id: str) -> str:
    data = read_progress()
    return data.get("items", {}).get(must_id, {}).get("status", "")


def pending_items() -> list[dict[str, Any]]:
    data = read_progress()
    return [
        {"id": k, **v} for k, v in data.get("items", {}).items()
        if v.get("status") == "PENDING"
    ]


def completed_items() -> list[dict[str, Any]]:
    data = read_progress()
    return [
        {"id": k, **v} for k, v in data.get("items", {}).items()
        if v.get("status") == "COMPLETE"
    ]


def summary_for_injection(max_items_per_group: int = 5) -> str:
    """Return a compact (≤500 tokens) summary for SessionStart injection."""
    data = read_progress()
    if not data:
        return ""
    items = data.get("items", {})
    by_status: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for mid, v in items.items():
        by_status.setdefault(v.get("status", "?"), []).append((mid, v))

    lines: list[str] = []
    lines.append(f"Plan Progress ({len(items)} items, plan_sha={data.get('plan_sha256','?')[:8]})")
    order = ("PENDING", "BLOCKED", "COMPLETE", "DEFERRED")
    for st in order:
        group = by_status.get(st, [])
        if not group:
            continue
        lines.append(f"  {st} ({len(group)}):")
        for mid, v in group[:max_items_per_group]:
            desc = (v.get("desc", "") or "")[:50]
            lines.append(f"    - [{mid}] {desc}")
        if len(group) > max_items_per_group:
            lines.append(f"    ... and {len(group) - max_items_per_group} more")
    return "\n".join(lines)


def plan_changed_since_init() -> bool:
    """True if plan.md MUST list changed since initialization (possible supplement)."""
    data = read_progress()
    if not data:
        return False
    pp = _plan_path()
    if not pp or not pp.exists():
        return False
    current_sha = _plan_sha(pp.read_text(encoding="utf-8"))
    return current_sha != data.get("plan_sha256")
