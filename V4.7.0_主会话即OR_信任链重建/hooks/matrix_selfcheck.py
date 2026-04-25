#!/usr/bin/env python3
"""Matrix self-check: ensure hook-enforcement-matrix.md claims match real files.

Run:
    python hooks/matrix_selfcheck.py

Exits 0 on success, 1 on any missing checker / importable module.
"""
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "framework" / "hook-enforcement-matrix.md"


CHECKER_REF_RE = re.compile(
    r"`(validator_\w+|gate_\w+|observer_\w+|post_agent_\w+|post_executor_\w+|session_\w+|stop_\w+)(?:\.py)?(?:::(\w+))?`"
)


def resolve_module(name: str) -> tuple[Path | None, str | None]:
    """Return (file path, python import path) or (None, None) if not found."""
    candidates = [
        ROOT / "hooks" / "validators" / f"{name}.py",
        ROOT / "hooks" / "gates" / f"{name}.py",
        ROOT / "hooks" / "observers" / f"{name}.py",
        ROOT / "hooks" / "post_agent" / f"{name}.py",
        ROOT / "hooks" / "session" / f"{name}.py",
    ]
    for p in candidates:
        if p.exists():
            module = f"hooks.{p.parent.name}.{name}"
            return p, module
    return None, None


def main() -> int:
    if not MATRIX.exists():
        print(f"FAIL matrix file missing: {MATRIX}")
        return 1
    text = MATRIX.read_text(encoding="utf-8")
    refs = {m.group(1) for m in CHECKER_REF_RE.finditer(text)}
    # Part A3 gate aggregators — conceptually invoked via gate_agent_spawn
    for g in ("gate_1_clarify_to_design", "gate_2_design_to_plan",
              "gate_3_plan_to_execute", "gate_4_execute_to_review",
              "gate_5_review_to_verify", "gate_6_verify_to_finish",
              "gate_7_finish"):
        refs.discard(g)
    # Not actual checker names, but matched by the regex
    refs.discard("gate_check_report")       # trace event name, not a checker
    refs.discard("validator_scorecard")     # merged into validator_current_run_json

    missing: list[str] = []
    unimportable: list[str] = []

    sys.path.insert(0, str(ROOT))
    for name in sorted(refs):
        p, modpath = resolve_module(name)
        if not p:
            missing.append(name)
            continue
        try:
            importlib.import_module(modpath)
        except Exception as e:
            unimportable.append(f"{name}: {type(e).__name__}: {e}")

    if missing:
        print(f"FAIL {len(missing)} checkers missing:")
        for m in missing:
            print(f"  - {m}")
    if unimportable:
        print(f"FAIL {len(unimportable)} checkers unimportable:")
        for m in unimportable:
            print(f"  - {m}")

    if missing or unimportable:
        return 1
    print(f"MATRIX OK · {len(refs)} checkers resolved and importable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
