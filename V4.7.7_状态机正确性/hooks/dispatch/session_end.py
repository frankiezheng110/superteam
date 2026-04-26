#!/usr/bin/env python3
"""SessionEnd dispatch — lightweight persistence; non-blocking."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, state  # noqa: E402


def main() -> None:
    decisions.read_hook_input()
    # Just bump last_updated; don't overwrite other fields
    cr = state.read_current_run()
    if cr:
        state.update_current_run(**{k: cr[k] for k in cr if k != "last_updated"})
    decisions.emit_allow()


if __name__ == "__main__":
    main()
