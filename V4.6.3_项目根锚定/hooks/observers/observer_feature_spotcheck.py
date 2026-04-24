"""V3: track that verifier actually spot-checked each feature during verify stage.

Maintains `.superteam/state/verifier-spotcheck.json` keyed by feature_id with
Bash commands executed while verifier was the active spawner. Used by
validator_verification to ensure per-feature spot checks actually ran.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..lib import state


def _spotcheck_path() -> Path | None:
    d = state.state_dir()
    return d / "verifier-spotcheck.json" if d else None


def run(tool_input: dict[str, Any], tool_response: dict[str, Any]) -> None:
    if state.current_stage() != "verify":
        return
    cmd = str(tool_input.get("command", ""))
    if not cmd:
        return
    p = _spotcheck_path()
    if not p:
        return
    data: dict[str, Any] = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    fid, _ = state.get_active_feature()
    key = fid or "_global"
    data.setdefault(key, []).append({
        "command": cmd[:160],
        "exit_code": tool_response.get("exit_code", 0),
        "ts": datetime.now(timezone.utc).isoformat(),
    })
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
