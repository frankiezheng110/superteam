"""V4.7.0 mode.json state machine — main session as orchestrator.

Single binary identity switch (active / ended) that drives whether the main
session takes the OR role. Separate from current-run.json (which is the run's
seven-stage progress) so mode flips and run flips don't entangle.

Disk layout:
  .superteam/state/
    mode.json              # this module's primary artifact
    gate-violations.jsonl  # PreToolUse hook block records
    bypass-log.jsonl       # /superteam:bypass user-acknowledged overrides
  .superteam/runs/<slug>/
    spawn-log.jsonl        # PostToolUse hook records every Agent spawn

mode.json schema (v1):
  schema_version: int           — fail-fast if main session sees an unknown version
  mode: "active" | "ended"      — the only identity switch
  entered_at: ISO8601           — when active was entered
  entered_by: "/superteam:go" | "manual"
  active_task_slug: str | null  — task_slug under .superteam/runs/
  last_verified_at: ISO8601     — refreshed by hooks every check, audit signal
  ended_at: ISO8601 | null
  ended_by: "user_command" | "project_completion" | null
  require_hooks: bool           — main session BLOCKs if hooks appear dead
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import state as _state

SCHEMA_VERSION = 1
KNOWN_SCHEMA_VERSIONS = {1}

# Sentinel reasons returned by enter/exit so callers can surface specific user-facing messages.
ENTER_REASON_ALREADY_ACTIVE = "already_active"
ENTER_REASON_OK = "ok"


# ---------- path helpers ----------

def mode_path() -> Path | None:
    d = _state.state_dir()
    return d / "mode.json" if d else None


def gate_violations_path() -> Path | None:
    d = _state.state_dir()
    return d / "gate-violations.jsonl" if d else None


def bypass_log_path() -> Path | None:
    d = _state.state_dir()
    return d / "bypass-log.jsonl" if d else None


def spawn_log_path(slug: str | None = None) -> Path | None:
    if slug is None:
        slug = active_task_slug() or _state.current_slug()
    if not slug:
        return None
    rd = _state.run_slug_dir(slug)
    return rd / "spawn-log.jsonl" if rd else None


# ---------- atomic write ----------

def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON to a temp file in the same dir, then os.replace — never a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


# ---------- read / parse ----------

def read_mode() -> dict[str, Any]:
    """Return the parsed mode.json or {} if missing/corrupt.

    Corrupt files are treated as missing — main session L3 self-check is the
    safety net that surfaces the corruption to the user rather than crashing
    the hook. Never raise from a hook.
    """
    p = mode_path()
    if not p or not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def schema_ok(data: dict[str, Any]) -> bool:
    return int(data.get("schema_version", 0)) in KNOWN_SCHEMA_VERSIONS


def is_or_active() -> bool:
    """True iff mode.json exists, schema is known, mode==active, no ended_at set.

    This is the single source of truth for every hook deciding whether to
    enforce OR-mode behavior on the main session.
    """
    data = read_mode()
    if not data:
        return False
    if not schema_ok(data):
        return False
    if data.get("mode") != "active":
        return False
    if data.get("ended_at"):
        return False
    return True


# Health values for mode_health(). Hooks use this to differentiate "not an OR
# project" (silent skip) from "file is broken and main session must be told"
# (loud warning).
MODE_HEALTH_MISSING = "missing"
MODE_HEALTH_CORRUPT = "corrupt"
MODE_HEALTH_UNKNOWN_SCHEMA = "unknown_schema"
MODE_HEALTH_ACTIVE = "active"
MODE_HEALTH_ENDED = "ended"


def mode_health() -> str:
    """Return one of: missing | corrupt | unknown_schema | active | ended.

    V4.7.1 — V4.7.0 hook injection conflated 'no mode.json' with 'mode.json
    corrupt': both took the silent fall-through. Per PLAN 4.6, a corrupt
    file must surface a loud warning so the main session refuses to act as
    OR until the user repairs it.
    """
    p = mode_path()
    if not p or not p.exists():
        return MODE_HEALTH_MISSING
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return MODE_HEALTH_CORRUPT
    if not isinstance(data, dict):
        return MODE_HEALTH_CORRUPT
    if not schema_ok(data):
        return MODE_HEALTH_UNKNOWN_SCHEMA
    mode = data.get("mode")
    if mode == "ended" or data.get("ended_at"):
        return MODE_HEALTH_ENDED
    if mode == "active":
        return MODE_HEALTH_ACTIVE
    return MODE_HEALTH_CORRUPT


def active_task_slug() -> str | None:
    if not is_or_active():
        return None
    return read_mode().get("active_task_slug") or None


# ---------- writes (four legitimate entry points; see PLAN section 4.3) ----------

def enter(slug: str, *, source: str = "/superteam:go") -> tuple[bool, str]:
    """Entry point #1 — /superteam:go writes mode=active.

    Returns (ok, reason). reason is ENTER_REASON_OK on success, or
    ENTER_REASON_ALREADY_ACTIVE if a live OR session already exists.
    """
    if is_or_active():
        return False, ENTER_REASON_ALREADY_ACTIVE
    p = mode_path()
    if not p:
        return False, "no_superteam_root"
    now = _utcnow_iso()
    data = {
        "schema_version": SCHEMA_VERSION,
        "mode": "active",
        "entered_at": now,
        "entered_by": source,
        "active_task_slug": slug,
        "last_verified_at": now,
        "ended_at": None,
        "ended_by": None,
        "require_hooks": True,
    }
    _atomic_write_json(p, data)
    return True, ENTER_REASON_OK


def end(reason: str = "user_command") -> bool:
    """Entry point #2/#3 — /superteam:end (user_command) or finish-stage user
    confirmation (project_completion). Idempotent: ending an already-ended
    session is a no-op success.
    """
    if reason not in ("user_command", "project_completion"):
        raise ValueError(f"illegal end reason: {reason}")
    p = mode_path()
    if not p or not p.exists():
        return False
    data = read_mode()
    if not data:
        return False
    now = _utcnow_iso()
    data["mode"] = "ended"
    data["ended_at"] = now
    data["ended_by"] = reason
    data["last_verified_at"] = now
    _atomic_write_json(p, data)
    return True


def bump_last_verified() -> None:
    """Entry point #4 — hook-driven heartbeat. Refresh last_verified_at only.

    Cheap; called from SessionStart and UserPromptSubmit. Skips silently when
    no mode.json exists (non-OR project).
    """
    p = mode_path()
    if not p or not p.exists():
        return
    data = read_mode()
    if not data:
        return
    data["last_verified_at"] = _utcnow_iso()
    try:
        _atomic_write_json(p, data)
    except OSError:
        pass


# ---------- spawn log (PostToolUse Agent) ----------

def append_spawn_log(*, subagent_type: str, agent_id: str | None, task_slug: str | None) -> None:
    """Append one spawn record to .superteam/runs/<slug>/spawn-log.jsonl.

    Records every main-session Agent tool call so frontmatter validators and
    /superteam:status can audit "did this specialist actually run?".
    Silent failure is fine — log is best-effort, not a gate.
    """
    if not task_slug:
        task_slug = active_task_slug() or _state.current_slug()
    if not task_slug:
        return
    p = spawn_log_path(task_slug)
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": _utcnow_iso(),
        "subagent_type": subagent_type,
        "agent_id": agent_id or "",
        "task_slug": task_slug,
    }
    try:
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def read_recent_spawns(limit: int = 5, slug: str | None = None) -> list[dict[str, Any]]:
    p = spawn_log_path(slug)
    if not p or not p.exists():
        return []
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# ---------- gate violations (PreToolUse main-session block) ----------

def append_gate_violation(*, kind: str, file_path: str, reason: str, slug: str | None = None) -> None:
    p = gate_violations_path()
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": _utcnow_iso(),
        "kind": kind,
        "file": file_path,
        "reason": reason,
        "task_slug": slug or active_task_slug() or _state.current_slug() or "",
    }
    try:
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def read_recent_violations(limit: int = 5) -> list[dict[str, Any]]:
    p = gate_violations_path()
    if not p or not p.exists():
        return []
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# ---------- bypass (one-shot user override) ----------

def consume_bypass() -> str | None:
    """Return the bypass reason and consume it (one-shot). None if none pending."""
    p = bypass_log_path()
    if not p or not p.exists():
        return None
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    pending: dict[str, Any] | None = None
    pending_idx: int = -1
    for i, line in enumerate(lines):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("status") == "pending":
            pending = rec
            pending_idx = i
    if pending is None:
        return None
    pending["status"] = "consumed"
    pending["consumed_at"] = _utcnow_iso()
    lines[pending_idx] = json.dumps(pending, ensure_ascii=False)
    try:
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        return None
    return pending.get("reason") or ""


def append_bypass_request(reason: str) -> None:
    p = bypass_log_path()
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": _utcnow_iso(),
        "reason": reason,
        "status": "pending",
    }
    try:
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ---------- active subagent transient flag ----------
#
# Hook payloads do not tell us whether a PreToolUse Edit/Write originated from
# the main session or from a running subagent. To distinguish, we maintain a
# transient flag: set on PreToolUse Agent (main session is about to spawn),
# cleared on PostToolUse Agent or SubagentStop. While the flag is set, any
# Edit/Write seen by hooks is presumed to come from inside that subagent and
# is allowed to bypass the main-session-write block.
#
# Limitation: nested or parallel subagent spawns from the main session would
# need a stack here. V4.7.0 keeps the scope to one-spawn-at-a-time which
# matches how main session OR is expected to operate (decide -> spawn -> wait).

def _active_subagent_path() -> Path | None:
    d = _state.state_dir()
    return d / "active-subagent.json" if d else None


def mark_subagent_started(subagent_type: str) -> None:
    p = _active_subagent_path()
    if not p:
        return
    rec = {
        "subagent_type": subagent_type,
        "started_at": _utcnow_iso(),
    }
    try:
        _atomic_write_json(p, rec)
    except OSError:
        pass


def mark_subagent_stopped() -> None:
    p = _active_subagent_path()
    if not p or not p.exists():
        return
    try:
        p.unlink()
    except OSError:
        pass


def is_subagent_running() -> bool:
    p = _active_subagent_path()
    return bool(p and p.exists())
