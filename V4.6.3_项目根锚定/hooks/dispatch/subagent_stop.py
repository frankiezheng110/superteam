#!/usr/bin/env python3
"""SubagentStop dispatch.

Redundant with PostToolUse(Agent) for agent-stop tracking, but Claude Code
fires both, so we emit a clean stage snapshot here regardless.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, state, trace  # noqa: E402


def main() -> None:
    payload = decisions.read_hook_input()
    # SubagentStop payload may include final text + stop_reason
    trace.emit(
        "subagent_stop",
        stop_reason=payload.get("stop_reason", ""),
        stage=state.current_stage(),
    )
    decisions.emit_allow()


if __name__ == "__main__":
    main()
