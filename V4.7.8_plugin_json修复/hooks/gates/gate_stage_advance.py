"""V4.7.3 — block illegitimate current_stage advances on disk.

The V4.7.0/V4.7.1/V4.7.2 trust chain made `spawn-log.jsonl` an audit log,
but the log was *recorded* not *consulted*. The main session could still
edit `.superteam/state/current-run.json` and bump `current_stage` from
`execute` to `review` without a reviewer ever having spawned. Hooks said
"recorded" but did not say "no".

This gate inspects writes to `current-run.json`, computes the proposed
new `current_stage` value, and refuses transitions whose preconditions
are not satisfied on disk:

    review  ← execute  : spawn-log must contain superteam:executor
                         AND `.superteam/runs/<slug>/execution.md` exists
    verify  ← review   : spawn-log must contain superteam:reviewer
                         AND `review.md` exists with valid frontmatter
    finish  ← verify   : spawn-log must contain superteam:verifier
                         AND `verification.md` exists with verdict=PASS

The clarify→design→plan→execute transitions are handled by the existing
V4.6 `gate_agent_spawn` + Gate 1/2/3 user-approval flow; this gate
intentionally only covers the post-G3 automated chain that V4.7's main
session OR is supposed to drive without user intervention.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..lib import mode_state
from ..lib import state as _state


# Recognized SuperTeam specialists for spawn-log lookup.
_PREDECESSOR_SPAWN = {
    "review": "executor",
    "verify": "reviewer",
    "finish": "verifier",
}

# Required artifact for each target stage (relative to the run directory).
# V4.7.6 finish 同时接受 verify.md 和 verification.md
# (framework/stage-model.md L38 用 verify.md · V4.7.5 旧标准用 verification.md)
_PREDECESSOR_ARTIFACTS = {
    "review": ["execution.md"],
    "verify": ["review.md"],
    "finish": ["verify.md", "verification.md"],
}


_STAGE_RE = re.compile(r'"current_stage"\s*:\s*"([a-zA-Z_]+)"')


def _extract_new_stage(tool_input: dict[str, Any]) -> str | None:
    """Look at Edit/Write/MultiEdit content for the proposed current_stage value."""
    # Write — full content is in tool_input.content
    content = tool_input.get("content")
    if isinstance(content, str):
        m = _STAGE_RE.search(content)
        if m:
            return m.group(1)
    # Edit — new_string carries the replacement chunk
    new_string = tool_input.get("new_string")
    if isinstance(new_string, str):
        m = _STAGE_RE.search(new_string)
        if m:
            return m.group(1)
    # MultiEdit — edits[] is a list of {old_string, new_string}
    edits = tool_input.get("edits") or []
    if isinstance(edits, list):
        for ed in edits:
            ns = (ed or {}).get("new_string", "") if isinstance(ed, dict) else ""
            if isinstance(ns, str):
                m = _STAGE_RE.search(ns)
                if m:
                    return m.group(1)
    return None


def _is_current_run_json(file_path: str) -> bool:
    norm = file_path.replace("\\", "/")
    return norm.endswith("/.superteam/state/current-run.json") or norm.endswith(
        ".superteam/state/current-run.json"
    )


def _spawn_log_has(slug: str, subagent_short: str) -> bool:
    """True if spawn-log.jsonl contains at least one record matching superteam:<subagent_short>."""
    p = mode_state.spawn_log_path(slug)
    if not p or not p.exists():
        return False
    needle = f"superteam:{subagent_short}"
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("subagent_type") == needle:
                return True
    except OSError:
        return False
    return False


def _verification_verdict_pass(slug: str) -> bool:
    """Read verify.md / verification.md and check for a PASS verdict line.

    V4.7.6 同时检查两种命名 — framework/stage-model.md L38 用 verify.md,
    V4.7.5 旧标准用 verification.md。任一文件含 verdict=PASS 即通过。
    """
    rd = _state.run_slug_dir(slug)
    if not rd:
        return False
    for name in ("verify.md", "verification.md"):
        vf = rd / name
        if not vf.exists():
            continue
        try:
            text = vf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # Match the documented verdict line; lenient on whitespace and case.
        if re.search(r"(?im)^\s*verdict\s*[:：]\s*PASS\b", text):
            return True
    return False


def _artifact_exists(slug: str, names: list[str]) -> bool:
    """V4.7.6 接受多种合法命名 — 任一存在即通过。"""
    rd = _state.run_slug_dir(slug)
    if not rd:
        return False
    return any((rd / n).exists() for n in names)


def check(tool_input: dict[str, Any]) -> tuple[bool, str]:
    """Return (ok, reason). ok=False blocks the tool call."""
    if not mode_state.is_or_active():
        return True, ""

    file_path = str(tool_input.get("file_path", ""))
    if not file_path or not _is_current_run_json(file_path):
        return True, ""

    # If a SuperTeam subagent is currently running, the write may belong to
    # the subagent (specialists are allowed to update state). Don't block.
    if mode_state.is_subagent_running():
        return True, ""

    new_stage = _extract_new_stage(tool_input)
    if not new_stage:
        # No current_stage field in the diff — not a stage advance.
        return True, ""

    if new_stage not in _PREDECESSOR_SPAWN:
        # We only gate the post-G3 automated chain (review/verify/finish).
        # design/plan/execute are governed by the V4.6 G1/G2/G3 user gates.
        return True, ""

    cur = _state.read_current_run() or {}
    old_stage = (cur.get("current_stage") or "").strip()
    if old_stage == new_stage:
        # Same value — not actually a transition.
        return True, ""

    slug = mode_state.active_task_slug() or _state.current_slug() or ""
    if not slug:
        return True, ""  # No task context — leave the write alone.

    needed_spawn = _PREDECESSOR_SPAWN[new_stage]
    needed_artifacts = _PREDECESSOR_ARTIFACTS[new_stage]

    missing: list[str] = []
    if not _spawn_log_has(slug, needed_spawn):
        missing.append(f"spawn-log 缺少 superteam:{needed_spawn} 记录")
    if not _artifact_exists(slug, needed_artifacts):
        if len(needed_artifacts) == 1:
            missing.append(f"产物 {needed_artifacts[0]} 不存在")
        else:
            missing.append(f"产物缺失 (需 {' 或 '.join(needed_artifacts)} 之一)")
    if new_stage == "finish" and not _verification_verdict_pass(slug):
        missing.append("verify.md / verification.md 未携带 verdict=PASS")

    # One-shot bypass support — same valve gate_main_session_scope uses.
    if missing:
        bypass_reason = mode_state.consume_bypass()
        if bypass_reason is not None:
            return True, ""

    if not missing:
        return True, ""

    mode_state.append_gate_violation(
        kind="stage_advance_blocked",
        file_path=file_path,
        reason=f"{old_stage}→{new_stage}: {'; '.join(missing)}",
        slug=slug,
    )
    artifact_hint = (
        needed_artifacts[0]
        if len(needed_artifacts) == 1
        else " 或 ".join(needed_artifacts)
    )
    return False, (
        f"SuperTeam V4.7.3 stage-advance block: 不允许 {old_stage}→{new_stage}。\n"
        f"缺少：{'; '.join(missing)}\n"
        f"正确动作: 先 spawn superteam:{needed_spawn} 完成 {artifact_hint}，"
        f"然后再修改 current_stage。\n"
        "若确认 hook 误判: /superteam:bypass <原因> 后重试一次。"
    )
