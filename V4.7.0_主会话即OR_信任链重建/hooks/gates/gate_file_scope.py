"""A9.*: PreToolUse(Edit/Write) — stage-scoped file-write permission.

Each stage has an allow-list of writable artifact paths. Writes outside the
allow-list are blocked unless explicitly overridden.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..lib import state


STAGE_ALLOWED_RUN_ARTIFACTS: dict[str, set[str]] = {
    "clarify": {"project-definition.md", "activity-trace.md"},
    "design": {
        "solution-options.md", "solution-landscape.md", "design.md",
        "ui-intent.md", "feature-checklist.md", "activity-trace.md",
    },
    "plan": {"plan.md", "activity-trace.md", "scorecard.md"},
    "execute": {"execution.md", "activity-trace.md", "polish.md", "scorecard.md"},
    "review": {"review.md", "activity-trace.md"},
    "verify": {"verification.md", "activity-trace.md"},
    "finish": {"finish.md", "retrospective.md", "activity-trace.md", "scorecard.md"},
}

RUN_ARTIFACT_RE = re.compile(r"(?i)\.superteam[/\\]runs[/\\][^/\\]+[/\\](?P<file>[^/\\]+)$")
INSPECTOR_DIR_RE = re.compile(r"(?i)\.superteam[/\\]inspector[/\\]")
STATE_DIR_RE = re.compile(r"(?i)\.superteam[/\\]state[/\\]")


def check(tool_input: dict[str, Any]) -> tuple[bool, str]:
    fp = str(tool_input.get("file_path", ""))
    if not fp:
        return True, ""
    cs = state.current_stage()
    if not cs:
        return True, ""

    # Run-artifact writes must match stage allow-list
    m = RUN_ARTIFACT_RE.search(fp)
    if m:
        fname = m.group("file")
        allowed = STAGE_ALLOWED_RUN_ARTIFACTS.get(cs, set())
        # handoffs/** is always allowed (internal handoff folder)
        if "handoffs" in fp.replace("\\", "/").split("/"):
            return True, ""
        if fname not in allowed:
            return False, (
                f"当前 stage={cs} 禁止写入 {fname} "
                f"(允许的文件: {sorted(allowed)}) — A9 violation"
            )

    # Inspector/ reports/ are only written during finish stage
    if INSPECTOR_DIR_RE.search(fp):
        if cs not in ("finish", "clarify", "design", "plan"):
            # inspector also writes during first 3 stages (checkpoints) and finish (report)
            return False, f"当前 stage={cs} 不应写入 .superteam/inspector/ 路径下文件"

    # State-dir writes are internal to hooks only; agents must not write here
    if STATE_DIR_RE.search(fp):
        return False, ".superteam/state/ 由 hook 内部维护，禁止 agent 手动写入"

    return True, ""
