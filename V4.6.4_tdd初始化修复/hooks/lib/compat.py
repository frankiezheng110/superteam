"""Backward compat / migration detection.

When V4.6.0 runs on an existing project that was under V4.5.0 or older,
the state schema and directory layout differ:
- `.superteam/reviewer/` may still exist (pre-swap) -> migrate to inspector/
- `current-run.json` may lack new required fields -> migration mode
- No verifier-verdict / feature-freeze / plan-freeze history -> tolerant window
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import state


def _compat_path() -> Path | None:
    d = state.state_dir()
    return d / "compat.json" if d else None


def read_compat() -> dict[str, Any]:
    p = _compat_path()
    if not p or not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def write_compat(data: dict[str, Any]) -> None:
    p = _compat_path()
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def initialize_cutover() -> None:
    """On first V4.6.0 SessionStart, record cutover date to gate migration mode."""
    compat = read_compat()
    if "cutover_date" not in compat:
        compat["cutover_date"] = datetime.now(timezone.utc).isoformat()
        compat["hook_compat_version"] = "4.6.0"
        write_compat(compat)


def migration_needed() -> bool:
    """True if the project looks like pre-V4.6.0 (no compat record yet)."""
    return "hook_compat_version" not in read_compat()


def legacy_reviewer_dir_exists() -> bool:
    d = state.superteam_dir()
    return bool(d and (d / "reviewer").is_dir())


def migrate_reviewer_to_inspector() -> bool:
    """Move .superteam/reviewer/ -> .superteam/inspector/ (V4.5.0 -> V4.6.0 swap)."""
    d = state.superteam_dir()
    if not d:
        return False
    legacy = d / "reviewer"
    target = d / "inspector"
    if not legacy.is_dir():
        return False
    if target.is_dir():
        # Merge: copy legacy contents into target, skip existing files
        for item in legacy.rglob("*"):
            rel = item.relative_to(legacy)
            dst = target / rel
            if item.is_dir():
                dst.mkdir(parents=True, exist_ok=True)
            else:
                if not dst.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst)
        shutil.rmtree(legacy)
    else:
        shutil.move(str(legacy), str(target))
    return True


def in_tolerant_window() -> bool:
    """True if commits/actions should be lenient (migration not complete)."""
    return migration_needed()
