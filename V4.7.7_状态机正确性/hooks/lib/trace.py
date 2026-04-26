"""Inspector trace JSONL writer (post reviewer/inspector swap).

The inspector (监察者) owns `.superteam/inspector/traces/<slug>.jsonl`.
Hooks auto-emit minimum event coverage so that inspector agent does not have
to self-write every event — this is a key V4.6.0 guarantee that H22
(reviewer/inspector continuity) is physically enforced.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import state


def trace_path(slug: str | None = None) -> Path | None:
    s = slug or state.current_slug()
    d = state.inspector_dir()
    if not d or not s:
        return None
    return d / "traces" / f"{s}.jsonl"


def emit(event_type: str, **fields: Any) -> None:
    """Append a JSONL event to the inspector trace."""
    p = trace_path()
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_id": str(uuid.uuid4())[:8],
        **fields,
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def read_events(slug: str | None = None) -> list[dict[str, Any]]:
    p = trace_path(slug)
    if not p or not p.exists():
        return []
    events: list[dict[str, Any]] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def has_event(event_type: str, *, stage: str | None = None, since_ts: str | None = None) -> bool:
    for evt in read_events():
        if evt.get("event_type") != event_type:
            continue
        if stage and evt.get("stage") != stage:
            continue
        if since_ts and evt.get("timestamp", "") < since_ts:
            continue
        return True
    return False


def count_events(event_type: str | None = None, stage: str | None = None) -> int:
    n = 0
    for evt in read_events():
        if event_type and evt.get("event_type") != event_type:
            continue
        if stage and evt.get("stage") != stage:
            continue
        n += 1
    return n


# Common event emitters for hook use

def emit_agent_spawn(agent: str, spawner: str = "orchestrator") -> None:
    emit("agent_spawn", agent=agent, spawner=spawner, stage=state.current_stage())


def emit_agent_stop(agent: str) -> None:
    emit("agent_stop", agent=agent, stage=state.current_stage())


def emit_gate_check_report(gate: int, results: list[dict[str, Any]], source: str = "hook") -> None:
    emit(
        "gate_check_report",
        gate=f"gate_{gate}",
        source=source,
        check_results=results,
        stage=state.current_stage(),
    )


def emit_stage_enter(stage: str) -> None:
    emit("stage_enter", stage=stage)


def emit_stage_exit(stage: str) -> None:
    emit("stage_exit", stage=stage)


def emit_decision_made(what: str, rationale: str = "") -> None:
    emit("decision_made", what=what, rationale=rationale, stage=state.current_stage())


def emit_gate_decision_observed(
    gate: int, decision: str, *, discrepancy: bool = False, detail: str = ""
) -> None:
    emit(
        "gate_decision_observed",
        gate=f"gate_{gate}",
        or_decision=decision,
        discrepancy=discrepancy,
        discrepancy_detail=detail,
        stage=state.current_stage(),
    )


def emit_discrepancy(rule_id: str, detail: str, severity: str = "medium") -> None:
    emit(
        "discrepancy_observed",
        rule_id=rule_id,
        detail=detail,
        severity=severity,
        stage=state.current_stage(),
    )


def emit_override_recorded(gate: int, reason: str, authorized_by: str = "orchestrator") -> None:
    emit(
        "override_recorded",
        gate=f"gate_{gate}",
        reason=reason,
        authorized_by=authorized_by,
        stage=state.current_stage(),
    )
