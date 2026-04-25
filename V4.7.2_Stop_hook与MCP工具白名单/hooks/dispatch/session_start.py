#!/usr/bin/env python3
"""SessionStart dispatch entry.

- Initialize compat cutover
- Migrate legacy reviewer/ dir to inspector/
- Rotate trace/report retention
- Inject last-run summary (<=500 tokens)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make hooks/ importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions  # noqa: E402
from hooks.session import session_injection  # noqa: E402


def main() -> None:
    decisions.read_hook_input()  # consume stdin (not strictly needed)
    context = session_injection.run()
    if context.strip():
        decisions.emit_session_context(context)
    else:
        decisions.emit_allow()


if __name__ == "__main__":
    main()
