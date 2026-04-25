"""V4.7.0 — block main-session Edit/Write on substantive work files.

When mode.json mode==active and no subagent is currently running, the main
session is acting as Orchestrator and must delegate substantive work to a
specialist subagent. Direct writes to code, review.md, verify.md, polish.md,
final.md, or test-plan.md are blocked.

Whitelist (main session may write directly — these are OR coordination
artifacts, not substantive work):
  .superteam/state/*                       — state machine maintenance
  .superteam/runs/<slug>/activity-trace.md — run coordination log
  .superteam/runs/<slug>/task-list.md      — plan-stage drafting
  .superteam/runs/<slug>/decision-log.md   — OR decision records
  .superteam/runs/<slug>/spawn-log.jsonl
  .superteam/runs/<slug>/gate-violations.jsonl
  .superteam/runs/<slug>/bypass-log.jsonl

Bypass: /superteam:bypass writes a one-shot pending record consumed here.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import mode_state

# Substantive work files that demand a specialist subagent. Match by basename
# OR by extension. Anything under tests/ or apps/ that ends in a code suffix
# also triggers — covers languages we have not enumerated.
_BLOCKED_BASENAMES = {
    "review.md",
    "verify.md",
    "verification.md",
    "polish.md",
    "final.md",
    "test-plan.md",
    "design.md",
    "solution-options.md",
    "solution-landscape.md",
    "ui-intent.md",
    "feature-checklist.md",
    "plan.md",
    "execution.md",
    "project-definition.md",
    "retrospective.md",
}

_CODE_SUFFIXES = (
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".vue", ".svelte",
    ".py",
    ".go",
    ".rs",
    ".java", ".kt", ".scala",
    ".cs", ".cpp", ".cc", ".c", ".h", ".hpp",
    ".rb",
    ".php",
    ".swift",
    ".sql",
    ".css", ".scss", ".sass", ".less",
    ".html", ".htm",
)

# Whitelist patterns (regex). Anchored to the path *after* `.superteam/`.
_WHITELIST_RE = re.compile(
    r"(?:^|[/\\])\.superteam[/\\](?:"
    r"state[/\\][^/\\]+"
    r"|runs[/\\][^/\\]+[/\\](?:"
    r"activity-trace\.md"
    r"|task-list\.md"
    r"|decision-log\.md"
    r"|spawn-log\.jsonl"
    r"|gate-violations\.jsonl"
    r"|bypass-log\.jsonl"
    r")"
    r"|inspector[/\\][^/\\]+(?:[/\\].+)?"
    r")$"
)


def _is_whitelisted(file_path: str) -> bool:
    norm = file_path.replace("\\", "/")
    return bool(_WHITELIST_RE.search(norm))


def _is_blocked_target(file_path: str) -> bool:
    if not file_path:
        return False
    norm = file_path.replace("\\", "/")
    base = norm.rsplit("/", 1)[-1].lower()
    if base in _BLOCKED_BASENAMES:
        return True
    suffix_idx = base.rfind(".")
    if suffix_idx >= 0:
        suffix = base[suffix_idx:]
        if suffix in _CODE_SUFFIXES:
            return True
    return False


def check(tool_input: dict) -> tuple[bool, str]:
    """Return (ok, reason). ok=False blocks the tool call."""
    if not mode_state.is_or_active():
        return True, ""
    if mode_state.is_subagent_running():
        # The write is happening inside a specialist subagent; the gate does
        # not apply (specialists are the legitimate writers).
        return True, ""

    file_path = str(tool_input.get("file_path", ""))
    if not file_path:
        return True, ""

    if _is_whitelisted(file_path):
        return True, ""

    if not _is_blocked_target(file_path):
        return True, ""

    # Check for an outstanding /superteam:bypass record before blocking.
    bypass_reason = mode_state.consume_bypass()
    if bypass_reason is not None:
        return True, ""

    reason = (
        "SuperTeam V4.7 OR-mode block: 主会话不得直接写实质工作文件 — "
        f"必须 spawn 对应 specialist subagent。\n"
        f"file: {file_path}\n"
        "正确动作: 用 Agent 工具调用 superteam:executor / reviewer / verifier / "
        "writer 等专家完成此次写入。\n"
        "若确认 hook 误判: /superteam:bypass <原因> 后重试一次。"
    )
    mode_state.append_gate_violation(
        kind="main_session_write_blocked",
        file_path=file_path,
        reason="not in whitelist; no active subagent",
    )
    return False, reason
