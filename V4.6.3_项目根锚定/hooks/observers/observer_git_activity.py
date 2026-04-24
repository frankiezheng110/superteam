"""A10.3 / H11: record git commit activity to state/commit-log.jsonl.

Enables later audit of which commits had their verification + activity-trace
continuity satisfied at commit time.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from ..lib import state


GIT_COMMIT_RE = re.compile(r"^\s*git\s+commit\b")
GIT_TAG_RE = re.compile(r"^\s*git\s+tag\s+-")
GIT_PUSH_RE = re.compile(r"^\s*git\s+push\b")


def run(tool_input: dict[str, Any], tool_response: dict[str, Any]) -> None:
    cmd = str(tool_input.get("command", ""))
    kind = None
    if GIT_COMMIT_RE.search(cmd):
        kind = "commit"
    elif GIT_TAG_RE.search(cmd):
        kind = "tag"
    elif GIT_PUSH_RE.search(cmd):
        kind = "push"
    if not kind:
        return

    d = state.state_dir()
    if not d:
        return
    log = d / "commit-log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "kind": kind,
        "command": cmd[:200],
        "stage": state.current_stage(),
        "slug": state.current_slug(),
        "ts": datetime.now(timezone.utc).isoformat(),
        "exit_code": tool_response.get("exit_code", 0),
    }
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
