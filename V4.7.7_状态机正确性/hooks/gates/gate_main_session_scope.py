"""V4.7.5 — block main-session Edit/Write on substantive work files AND on
state-machine control files.

When mode.json mode==active and no subagent is currently running, the main
session is acting as Orchestrator and must delegate substantive work to a
specialist subagent. Direct writes to code, review.md, verify.md, polish.md,
final.md, or test-plan.md are blocked.

V4.7.5 — additionally protect the state machine itself. The Stop hook is
state-machine-driven (mode.json + current-run.json + active-subagent.json),
so any path that lets the main session edit those files would let it forge
the state machine and bypass the Stop guard. Hook control files are now
written *only* through the Python API (mode_state.enter / end / mark_*),
never via Edit/Write — so blocking Edit/Write on them costs us nothing and
seals the loophole.

Allowed direct writes (OR coordination only, not substantive work):
  .superteam/runs/<slug>/activity-trace.md — run coordination log
  .superteam/runs/<slug>/task-list.md      — plan-stage drafting
  .superteam/runs/<slug>/decision-log.md   — OR decision records
  .superteam/inspector/*                   — inspector domain (its own gate)

Blocked state-machine control files:
  .superteam/state/mode.json               — OR identity switch
  .superteam/state/current-run.json        — seven-stage state
  .superteam/state/active-subagent.json    — subagent-running flag
  .superteam/state/turn.json               — turn boundary marker
  .superteam/state/subagent-stop-log.jsonl
  .superteam/state/gate-violations.jsonl
  .superteam/state/bypass-log.jsonl
  .superteam/runs/<slug>/spawn-log.jsonl

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
# V4.7.5 — state/* is no longer wholesale whitelisted. The state machine is
# maintained through the Python API (mode_state.enter / end / mark_*),
# never via Edit/Write, so the OR has no legitimate reason to write those
# files directly. Same for spawn-log.jsonl which the PostToolUse hook owns.
_WHITELIST_RE = re.compile(
    r"(?:^|[/\\])\.superteam[/\\](?:"
    r"runs[/\\][^/\\]+[/\\](?:"
    r"activity-trace\.md"
    r"|task-list\.md"
    r"|decision-log\.md"
    r")"
    r"|inspector[/\\][^/\\]+(?:[/\\].+)?"
    r")$"
)


# V4.7.5 — explicit BLOCK for hook-owned control files. The state machine
# itself (mode.json / current-run.json) has its own legitimate write paths
# and is *not* in this list:
#   - mode.json               → updated only via Python API
#                                (mode_state.enter / end / bump)
#   - current-run.json        → main session legitimately Edit/Writes here
#                                to advance stages, validated by
#                                gate_stage_advance.py
#
# What *is* blocked are the hook-internal log/marker files. These are
# written exclusively through the Python API by hook code, so no agent of
# any kind has a legitimate reason to Edit/Write them. Forging them would
# let an OR fake a subagent-running flag, fake spawn records, or skip the
# turn boundary, all of which break Stop-hook reasoning.
_STATE_MACHINE_BLOCK_RE = re.compile(
    r"(?:^|[/\\])\.superteam[/\\](?:"
    r"state[/\\](?:"
    r"active-subagent\.json"
    r"|turn\.json"
    r"|gate-violations\.jsonl"
    r"|bypass-log\.jsonl"
    r"|subagent-stop-log\.jsonl"
    r"|mode\.json"
    r")"
    r"|runs[/\\][^/\\]+[/\\]spawn-log\.jsonl"
    r")$"
)


def _is_whitelisted(file_path: str) -> bool:
    norm = file_path.replace("\\", "/")
    return bool(_WHITELIST_RE.search(norm))


def _is_state_machine_file(file_path: str) -> bool:
    norm = file_path.replace("\\", "/")
    return bool(_STATE_MACHINE_BLOCK_RE.search(norm))


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

    file_path = str(tool_input.get("file_path", ""))
    if not file_path:
        return True, ""

    # V4.7.5 — state-machine control files are blocked unconditionally,
    # even from inside a subagent. Specialists have no business writing
    # mode.json / current-run.json / active-subagent.json / etc; those are
    # owned by the Python API and the hook layer. Bypass is *not* honored
    # here because forging the state machine breaks every other guard.
    if _is_state_machine_file(file_path):
        mode_state.append_gate_violation(
            kind="state_machine_write_blocked",
            file_path=file_path,
            reason="state-machine control file (mode.json / current-run.json / "
            "active-subagent.json / turn.json / *-log.jsonl) is hook-owned",
        )
        return False, (
            "SuperTeam V4.7.5 state-machine block: 状态机控制文件由 hook 维护，"
            "任何 agent (含 main session 与 specialist) 都不得直接 Edit/Write。\n"
            f"file: {file_path}\n"
            "状态推进只能通过合法路径触发：\n"
            "  - mode.json: /superteam:go (enter) / /superteam:end (exit)\n"
            "  - current-run.json: gate_stage_advance.py (spawn + artifact 后)\n"
            "  - active-subagent.json / turn.json / *-log.jsonl: hook 自动维护"
        )

    if mode_state.is_subagent_running():
        # The write is happening inside a specialist subagent; the
        # substantive-file gate does not apply (specialists are the
        # legitimate writers).
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
