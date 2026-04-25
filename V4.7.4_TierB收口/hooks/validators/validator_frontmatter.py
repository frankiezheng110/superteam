"""V4.7.3 — validate (and if needed auto-stamp) specialist artifact frontmatter.

The V4.7 trust chain wants `review.md` to be writable only by the reviewer
specialist, `verification.md` only by the verifier, etc. The hook layer
already records every Agent spawn into spawn-log.jsonl; this validator
closes the loop by checking that each substantive artifact carries a
frontmatter block whose agent_id is present in spawn-log and whose
agent_type matches the file's expected role.

Two behaviors:

  - **Missing frontmatter**: auto-stamp using active-subagent.json (if a
    SuperTeam specialist was running when the write happened). This is
    the "auto-补" fallback — it does not destroy the specialist's content,
    it just records who wrote it. If no active subagent context can be
    inferred, only a warning is logged (no destructive action).

  - **Forged frontmatter**: if a frontmatter is present but `agent_id`
    cannot be found in spawn-log.jsonl, or `agent_type` mismatches the
    file's expected role, append a gate_violations record. The file is
    NOT deleted in V4.7.3 — destructive enforcement is reserved for a
    later strict-mode opt-in. Detection alone is enough to surface the
    issue in `/superteam:status` and finish-stage audit.

Files watched (basename match) and their expected agent_type:

  review.md           → reviewer
  verify.md           → verifier
  verification.md     → verifier
  polish.md           → simplifier | doc-polisher | release-curator
  final.md            → writer
  finish.md           → writer
  retrospective.md    → writer | inspector
  execution.md        → executor
  test-plan.md        → test-engineer | planner
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..lib import mode_state
from ..lib import state as _state


# Filename → set of acceptable agent_type values.
EXPECTED_AGENT_TYPES: dict[str, set[str]] = {
    "review.md": {"reviewer"},
    "verify.md": {"verifier"},
    "verification.md": {"verifier"},
    "polish.md": {"simplifier", "doc-polisher", "release-curator"},
    "final.md": {"writer"},
    "finish.md": {"writer"},
    "retrospective.md": {"writer", "inspector"},
    "execution.md": {"executor"},
    "test-plan.md": {"test-engineer", "planner"},
}


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# Match `key: value` lines inside the YAML block. SuperTeam frontmatter is
# intentionally simple — flat string values — so a regex parser is
# sufficient and keeps us off PyYAML.
_KV_RE = re.compile(r"(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$")


def _basename(file_path: str) -> str:
    return file_path.replace("\\", "/").rsplit("/", 1)[-1]


def _is_watched_artifact(file_path: str) -> bool:
    return _basename(file_path) in EXPECTED_AGENT_TYPES


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    body = m.group(1)
    out: dict[str, str] = {}
    for kv in _KV_RE.finditer(body):
        out[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return out


def _spawn_log_index(slug: str) -> dict[str, str]:
    """Return {agent_id: subagent_type_short} from spawn-log.jsonl."""
    p = mode_state.spawn_log_path(slug)
    if not p or not p.exists():
        return {}
    out: dict[str, str] = {}
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            aid = str(rec.get("agent_id", "")).strip()
            st = str(rec.get("subagent_type", "")).strip()
            if aid and st.startswith("superteam:"):
                out[aid] = st.split(":", 1)[1]
    except OSError:
        pass
    return out


def _read_active_subagent_short() -> str:
    """Return the short name (e.g. 'reviewer') of the currently-running specialist, or ''."""
    p = _state.state_dir()
    if not p:
        return ""
    f = p / "active-subagent.json"
    if not f.exists():
        return ""
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    if not isinstance(data, dict):
        return ""
    st = str(data.get("subagent_type", ""))
    return st.split(":", 1)[1] if st.startswith("superteam:") else st


def _stamp_frontmatter(file_path: str, agent_type: str, agent_id: str, slug: str) -> bool:
    """Prepend a fresh YAML frontmatter to file_path. Returns True on success."""
    p = Path(file_path)
    try:
        original = p.read_text(encoding="utf-8")
    except OSError:
        return False
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    block = (
        "---\n"
        f"agent_type: {agent_type}\n"
        f"agent_id: {agent_id}\n"
        f"task_slug: {slug}\n"
        f"stamped_at: {ts}\n"
        "stamped_by: hook_auto_fill\n"
        "---\n"
    )
    try:
        p.write_text(block + original, encoding="utf-8")
        return True
    except OSError:
        return False


def run(file_path: str) -> tuple[bool, list[str]]:
    """Validate (and possibly auto-stamp) frontmatter for a written artifact.

    Return (ok, errors). ok=False signals a forgery (logged but not
    destructive in V4.7.3). Auto-stamp success counts as ok=True.
    """
    if not mode_state.is_or_active():
        return True, []
    if not _is_watched_artifact(file_path):
        return True, []

    p = Path(file_path)
    if not p.exists():
        # Write may have been blocked or rolled back upstream; nothing to do.
        return True, []

    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return True, []

    expected = EXPECTED_AGENT_TYPES.get(_basename(file_path)) or set()
    slug = mode_state.active_task_slug() or _state.current_slug() or ""

    fm = _parse_frontmatter(text)
    if fm is None:
        # Missing frontmatter — try to infer from the running specialist.
        running = _read_active_subagent_short()
        if running and running in expected and slug:
            # Walk recent spawn-log records backwards for the latest match.
            inferred_id = ""
            for rec in reversed(mode_state.read_recent_spawns(limit=20, slug=slug)):
                if rec.get("subagent_type") == f"superteam:{running}":
                    inferred_id = str(rec.get("agent_id", ""))
                    break
            if inferred_id and _stamp_frontmatter(file_path, running, inferred_id, slug):
                return True, [f"frontmatter auto-stamped: agent_type={running}, agent_id={inferred_id}"]
        # Could not infer — log a soft violation but don't destroy content.
        mode_state.append_gate_violation(
            kind="frontmatter_missing",
            file_path=file_path,
            reason=f"no frontmatter and no active superteam:* specialist matching {sorted(expected)}",
            slug=slug,
        )
        return False, ["frontmatter missing and could not be auto-inferred"]

    # Frontmatter present — validate fields.
    agent_type = (fm.get("agent_type") or "").strip()
    agent_id = (fm.get("agent_id") or "").strip()
    fm_slug = (fm.get("task_slug") or "").strip()

    errors: list[str] = []
    if expected and agent_type not in expected:
        errors.append(
            f"agent_type={agent_type!r} not in expected {sorted(expected)} for {_basename(file_path)}"
        )
    if not agent_id:
        errors.append("agent_id is empty in frontmatter")
    elif slug:
        idx = _spawn_log_index(slug)
        if agent_id not in idx:
            errors.append(f"agent_id={agent_id!r} not present in spawn-log.jsonl")
        elif expected and idx.get(agent_id) not in expected:
            errors.append(
                f"spawn-log says agent_id={agent_id!r} ran as {idx.get(agent_id)!r}, "
                f"but {_basename(file_path)} expects {sorted(expected)}"
            )
    if slug and fm_slug and fm_slug != slug:
        errors.append(f"task_slug mismatch: frontmatter={fm_slug!r}, run={slug!r}")

    if errors:
        mode_state.append_gate_violation(
            kind="frontmatter_forged",
            file_path=file_path,
            reason="; ".join(errors),
            slug=slug,
        )
        return False, errors

    return True, []
