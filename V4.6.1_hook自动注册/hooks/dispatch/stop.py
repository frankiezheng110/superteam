#!/usr/bin/env python3
"""Stop dispatch — enforce Gate 7 inspector-report existence before Stop."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions  # noqa: E402
from hooks.session import stop_finish_guard  # noqa: E402


def main() -> None:
    decisions.read_hook_input()
    ok, reason = stop_finish_guard.check()
    if not ok:
        decisions.emit_block(reason)
    decisions.emit_allow()


if __name__ == "__main__":
    main()
