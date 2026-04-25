"""SuperTeam runtime state access with concurrency-safe read/write.

Paths follow V4.6.0 convention (post reviewer/inspector swap):
  .superteam/
    runs/<slug>/
      project-definition.md, activity-trace.md, plan.md, execution.md, ...
    inspector/
      traces/<slug>.jsonl
      reports/<slug>-report.md / .html
      health.json, insights.md, improvement-backlog.md
    state/
      current-run.json
      feature-tdd-state.json
      feature-freeze.lock.json
      plan-freeze.lock.json
      verdict-signatures.jsonl
      hook-log.jsonl
      compat.json
      snapshots/<ts>.json
"""
from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any

try:
    import msvcrt  # Windows file locking
except ImportError:
    msvcrt = None

try:
    import fcntl  # POSIX file locking
except ImportError:
    fcntl = None


# ---------- path helpers ----------

def find_superteam_root(start: str | Path | None = None) -> Path | None:
    """Walk up from project dir (or given start) until a .superteam/ directory found.

    Priority: explicit `start` arg > $CLAUDE_PROJECT_DIR env > os.getcwd().
    Using CLAUDE_PROJECT_DIR anchors hook resolution to the session's true
    project root — os.getcwd() is unreliable because it reflects wherever the
    last Bash tool invocation left the process, which may be a clone dir or
    temp folder unrelated to the current session's project.
    """
    if start is None:
        start = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    p = Path(start).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / ".superteam").is_dir():
            return candidate
    return None


def superteam_dir() -> Path | None:
    root = find_superteam_root()
    return root / ".superteam" if root else None


def current_run_path() -> Path | None:
    d = superteam_dir()
    return d / "state" / "current-run.json" if d else None


def runs_dir() -> Path | None:
    d = superteam_dir()
    return d / "runs" if d else None


def inspector_dir() -> Path | None:
    """Note: post V4.6.0 swap, traces/reports live under .superteam/inspector/."""
    d = superteam_dir()
    return d / "inspector" if d else None


def state_dir() -> Path | None:
    d = superteam_dir()
    return d / "state" if d else None


def run_slug_dir(slug: str) -> Path | None:
    r = runs_dir()
    return r / slug if r else None


# ---------- file locking ----------

@contextmanager
def _locked(path: Path, mode: str = "r+"):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() and "r" in mode and "+" not in mode:
        yield None
        return
    if not path.exists():
        path.touch()
    f = path.open(mode, encoding="utf-8")
    try:
        if msvcrt is not None:
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
            except OSError:
                pass
        elif fcntl is not None:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        yield f
    finally:
        try:
            if msvcrt is not None:
                try:
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            elif fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        finally:
            f.close()


# ---------- current-run.json ----------

def read_current_run() -> dict[str, Any]:
    p = current_run_path()
    if not p or not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def write_current_run(data: dict[str, Any]) -> None:
    p = current_run_path()
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    with _locked(p, "w") as f:
        if f is not None:
            json.dump(data, f, ensure_ascii=False, indent=2)


def update_current_run(**updates: Any) -> dict[str, Any]:
    data = read_current_run()
    data.update(updates)
    from datetime import datetime, timezone
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    write_current_run(data)
    return data


def current_stage() -> str:
    return read_current_run().get("current_stage", "")


def current_slug() -> str:
    return read_current_run().get("task_slug", "")


def plan_quality_gate() -> str:
    return read_current_run().get("plan_quality_gate", "")


def repair_cycle_count() -> int:
    return int(read_current_run().get("repair_cycle_count", 0))


def supplement_mode() -> str:
    """'' / 'G1-reopen' / 'G2-reopen' / 'G3-reopen'"""
    return read_current_run().get("supplement_mode", "") or ""


def ui_weight() -> str:
    return read_current_run().get("ui_weight", "ui-none")


# ---------- feature TDD state ----------

def tdd_state_path() -> Path | None:
    d = state_dir()
    return d / "feature-tdd-state.json" if d else None


def read_tdd_state() -> dict[str, Any]:
    p = tdd_state_path()
    if not p or not p.exists():
        return {"active_feature_id": None, "features": {}}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"active_feature_id": None, "features": {}}


def write_tdd_state(data: dict[str, Any]) -> None:
    p = tdd_state_path()
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    with _locked(p, "w") as f:
        if f is not None:
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_active_feature() -> tuple[str | None, dict[str, Any]]:
    s = read_tdd_state()
    fid = s.get("active_feature_id")
    if not fid:
        return None, {}
    return fid, s.get("features", {}).get(fid, {})


def set_feature_state(feature_id: str, **fields: Any) -> None:
    s = read_tdd_state()
    features = s.setdefault("features", {})
    feat = features.setdefault(feature_id, {"state": "PENDING"})
    feat.update(fields)
    s["active_feature_id"] = feature_id
    write_tdd_state(s)


# ---------- hook log ----------

def hook_log_path() -> Path | None:
    d = state_dir()
    return d / "hook-log.jsonl" if d else None
