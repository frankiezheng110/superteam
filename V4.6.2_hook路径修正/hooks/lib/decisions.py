"""Unified hook decision emitters with token budget enforcement.

Every hook returns JSON on stdout. This module enforces:
- block reasons <= 200 tokens (~600 chars)
- systemMessage <= 100 tokens (~300 chars)
- SessionStart additionalContext <= 500 tokens (~1500 chars)

Over-budget content is truncated with a trailing marker so runtime never
explodes Claude's context.
"""
from __future__ import annotations

import json
import sys
from typing import Any

# Rough char budgets (token x 3 heuristic; Chinese-heavy text biased)
MAX_BLOCK_REASON = 600
MAX_SYSTEM_MESSAGE = 300
MAX_SESSION_CONTEXT = 1500

_TRUNCATE_MARK = "… [truncated by hook budget]"


def _truncate(text: str, limit: int) -> str:
    if not text:
        return text
    if len(text) <= limit:
        return text
    return text[: limit - len(_TRUNCATE_MARK)] + _TRUNCATE_MARK


def emit_allow() -> None:
    """No-op; hook is silent and tool proceeds."""
    print(json.dumps({}, ensure_ascii=False))
    sys.exit(0)


def emit_block(reason: str, *, extra: dict[str, Any] | None = None) -> None:
    """Block the tool call. Claude sees the reason and should adjust."""
    reason = _truncate(reason, MAX_BLOCK_REASON)
    payload: dict[str, Any] = {
        "decision": "block",
        "reason": reason,
    }
    if extra:
        payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)


def emit_deny(reason: str) -> None:
    """PreToolUse permission-level deny (cannot retry without different input)."""
    reason = _truncate(reason, MAX_BLOCK_REASON)
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)


def emit_system_message(message: str, *, hook_event: str | None = None) -> None:
    """Non-blocking hint injected as systemMessage."""
    message = _truncate(message, MAX_SYSTEM_MESSAGE)
    payload: dict[str, Any] = {"systemMessage": message}
    if hook_event:
        payload["hookSpecificOutput"] = {"hookEventName": hook_event}
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)


def emit_session_context(context: str) -> None:
    """SessionStart additionalContext injection."""
    context = _truncate(context, MAX_SESSION_CONTEXT)
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)


def read_hook_input() -> dict[str, Any]:
    """Parse the hook JSON payload from stdin. Returns {} on empty/invalid."""
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def log_internal(event: str, detail: dict[str, Any], log_path: str) -> None:
    """Append hook internal event to .superteam/state/hook-log.jsonl.

    Internal log is for debugging hook behavior; does NOT go to Claude context.
    """
    from datetime import datetime, timezone
    from pathlib import Path

    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **detail,
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
