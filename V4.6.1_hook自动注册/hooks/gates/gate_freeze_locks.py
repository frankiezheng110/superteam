"""Deprecated in V4.6.0 final: SHA256 freeze locks removed (作者决策 2026-04-24).

OR is not an adversary who forges hashes — it is a forgetful worker that skips steps.
Entry-Log reconciliation (`validator_activity_trace.check_entry_log` + AGENT_ENTRY_LOG_SPEC)
replaces the freeze mechanism: every agent is forced to read the required files and
restate their key content in the Entry Log, which the hook verifies against source files.

This module remains as a no-op stub so `hooks_settings_template.json` and the
dispatcher don't break. It may be deleted in V4.7.0 once references are cleaned up.
"""
from __future__ import annotations

from typing import Any


def check(tool_input: dict[str, Any]) -> tuple[bool, str]:
    return True, ""
