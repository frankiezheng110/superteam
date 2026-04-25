#!/usr/bin/env python3
"""PreCompact dispatch — snapshot critical state before context compaction."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, state  # noqa: E402


def main() -> None:
    decisions.read_hook_input()
    d = state.state_dir()
    if d:
        snaps = d / "snapshots"
        snaps.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        from hooks.lib import plan_progress
        snapshot = {
            "ts": ts,
            "current_run": state.read_current_run(),
            "tdd_state": state.read_tdd_state(),
            "plan_progress": plan_progress.read_progress(),
        }
        (snaps / f"{ts}.json").write_text(
            json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    decisions.emit_allow()


if __name__ == "__main__":
    main()
