"""A10.1-4 / H10 / H11: git commit/tag/push hard gate.

Blocks commit/tag/push unless:
- verification.md exists with verdict=PASS (A10.1)
- review.md verdict != BLOCK (A10.2)
- activity-trace.md has a section for this commit's checkpoint (A10.3)
- OR environment has ALLOW_UNVERIFIED_COMMIT=1 (A10.4 explicit override)
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from ..lib import parser, state


GIT_COMMIT_RE = re.compile(
    r"""
    ^\s*git\s+
    (?:commit\b|tag\s+-[asm]|push\s+)
    """,
    re.VERBOSE,
)


def _is_git_commit(cmd: str) -> bool:
    if not cmd:
        return False
    return bool(GIT_COMMIT_RE.search(cmd))


def check(tool_input: dict[str, Any]) -> tuple[bool, str]:
    cmd = str(tool_input.get("command", ""))
    if not _is_git_commit(cmd):
        return True, ""

    # A10.4 explicit override
    if os.environ.get("ALLOW_UNVERIFIED_COMMIT") == "1":
        # Log bypass to state/unverified-commits.jsonl (session_end / post_tool will track)
        return True, ""

    # Migration window: if pre-V4.6.0 project without cutover yet, allow
    from ..lib import compat
    if compat.in_tolerant_window():
        return True, ""

    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if not rd:
        # Not inside a superteam run -> allow (project without .superteam/)
        return True, ""

    # A10.1 verification.md PASS
    v = rd / "verification.md"
    if not v.exists():
        return False, "verification.md 不存在 — 必须先 verify PASS 才能 git commit/tag/push (A10.1)"
    verdict = parser.verification_verdict(parser.read_text(v))
    if verdict != "PASS":
        return False, (
            f"verification.md verdict={verdict or 'MISSING'} — 必须先达成 PASS 才能 git commit (A10.1). "
            f"紧急情况可 ALLOW_UNVERIFIED_COMMIT=1 显式覆盖 (留痕)"
        )

    # A10.2 review.md not BLOCK
    r = rd / "review.md"
    if r.exists():
        rv = parser.review_verdict(parser.read_text(r))
        if rv == "BLOCK":
            return False, "review.md verdict=BLOCK — 必须先解决 blocker 才能 commit (A10.2)"

    # A10.3 activity-trace.md has a checkpoint section for current commit
    at = rd / "activity-trace.md"
    if at.exists():
        trace_text = parser.read_text(at)
        # Heuristic: require at least one "## Checkpoint" / "## Commit" / stage boundary after last commit marker
        if not re.search(r"(?im)^##\s+(Checkpoint|Commit|Stage|Gate)", trace_text):
            return False, "activity-trace.md 缺 checkpoint/commit/stage 段 — 必须有对应记录才能 commit (A10.3)"

    return True, ""
