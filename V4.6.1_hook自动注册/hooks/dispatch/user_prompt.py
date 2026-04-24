#!/usr/bin/env python3
"""UserPromptSubmit dispatch.

A23: detect supplement-mode re-entry ('reopen G1/G2/G3') in user text and set
`supplement_mode` flag in current-run.json so downstream freeze locks relax.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions, state  # noqa: E402


REOPEN_RE = re.compile(
    r"(?i)(reopen|重新打开|补充|supplement)\s*G\s*([123])"
    r"|G\s*([123])\s*(reopen|重开|补充)"
)


def main() -> None:
    payload = decisions.read_hook_input()
    prompt = payload.get("prompt", "") or payload.get("user_prompt", "")
    m = REOPEN_RE.search(str(prompt))
    if m:
        gate = m.group(2) or m.group(3)
        state.update_current_run(supplement_mode=f"G{gate}-reopen")
    decisions.emit_allow()


if __name__ == "__main__":
    main()
