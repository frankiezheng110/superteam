"""Mapping of superteam agent types to their legal stages.

Used by gate_agent_spawn.py to reject cross-stage agent spawns (A4.1, A4.9).
Pre-read requirement (A4.5): inspector must read polish.md/execution.md/plan.md
before acting; here encoded as "required artifacts before spawn".
Post V4.6.0 swap: reviewer = review-stage quality gate, inspector = continuity.
"""
from __future__ import annotations

# Agent -> {stages where spawn is legal}. Empty set = no restriction.
AGENT_VALID_STAGES: dict[str, set[str]] = {
    "superteam:orchestrator": set(),  # OR present in every stage
    "superteam:analyst": {"clarify", "plan"},
    "superteam:prd-writer": {"clarify", "plan"},
    "superteam:researcher": {"design", "plan"},
    "superteam:architect": {"design", "plan", "execute"},  # "fix" maps to execute
    "superteam:designer": {"design", "execute", "review"},
    "superteam:planner": {"clarify", "plan", "execute"},
    "superteam:executor": {"execute"},
    "superteam:test-engineer": {"execute", "review", "verify"},
    "superteam:debugger": {"execute"},
    "superteam:reviewer": {"review"},  # audit reviewer (audit code) NOTE post-swap
    "superteam:verifier": {"verify", "finish"},
    "superteam:inspector": {"clarify", "design", "plan", "finish"},  # continuity auditor post-swap
    "superteam:simplifier": {"execute"},
    "superteam:doc-polisher": {"execute", "finish"},
    "superteam:release-curator": {"execute", "finish"},
    "superteam:writer": {"finish"},
}

# Agent -> Gate number whose exit conditions precede spawn.
# e.g. spawning planner requires Gate 2 passed; reviewer requires Gate 4.
AGENT_ENTRY_GATE: dict[str, int] = {
    "superteam:designer": 1,
    "superteam:architect": 1,
    "superteam:researcher": 1,
    "superteam:planner": 2,
    "superteam:executor": 3,
    "superteam:reviewer": 4,  # reviewer = audit-code role post-swap, does review stage
    "superteam:verifier": 5,
    "superteam:inspector": 0,  # continuity audit; no fixed entry gate, present throughout
}

# Agents that MUST have pre-read artifacts available before spawn (A4.5)
AGENT_REQUIRED_PREREAD: dict[str, list[str]] = {
    "superteam:reviewer": ["execution.md", "plan.md"],  # polish.md optional
    "superteam:verifier": ["review.md", "plan.md"],
}

# Workers (non-orchestrator) — they MAY NOT spawn subagents (A4.8)
ORCHESTRATOR_ONLY_SPAWNERS = {
    "superteam:orchestrator",
    "__user__",  # user directly triggers skills
}

# Entry-Log requirements per agent (A5.1 Entry-Log reconciliation — anti-hallucination).
# Each agent's Entry Log in activity-trace.md must:
#   - list the required artifact files (by filename) with their on-disk paths
#   - restate the specified key content (e.g. plan.md MUST items, feature-checklist items)
# Hook verifies every listed path actually exists AND every restated item matches the file.
#
# 'restate' values:
#   "plan-must"         -> list every MUST item from plan.md verbatim
#   "feature-checklist" -> list every feature item from feature-checklist.md verbatim
#   "review-verdict"    -> state review.md verdict value
#   "ui-intent-fonts"   -> list Typography Contract font whitelist
#   "exec-files-changed"-> list files changed section from execution.md
AGENT_ENTRY_LOG_SPEC: dict[str, dict[str, list[str]]] = {
    "superteam:analyst": {
        "files": ["project-definition.md"],
        "restate": [],
    },
    "superteam:researcher": {
        "files": ["project-definition.md"],
        "restate": [],
    },
    "superteam:prd-writer": {
        "files": ["project-definition.md"],
        "restate": [],
    },
    "superteam:architect": {
        "files": ["project-definition.md", "solution-options.md"],
        "restate": [],
    },
    "superteam:designer": {
        "files": ["project-definition.md"],
        "restate": [],
    },
    "superteam:planner": {
        "files": ["design.md", "solution-options.md", "feature-checklist.md"],
        "restate": ["feature-checklist"],
    },
    "superteam:executor": {
        "files": ["plan.md", "feature-checklist.md"],
        "restate": ["plan-must"],
    },
    "superteam:debugger": {
        "files": ["execution.md", "plan.md"],
        "restate": [],
    },
    "superteam:test-engineer": {
        "files": ["plan.md", "feature-checklist.md"],
        "restate": [],
    },
    "superteam:simplifier": {
        "files": ["execution.md"],
        "restate": ["exec-files-changed"],
    },
    "superteam:doc-polisher": {
        "files": ["execution.md"],
        "restate": [],
    },
    "superteam:release-curator": {
        "files": ["plan.md", "execution.md"],
        "restate": [],
    },
    "superteam:reviewer": {  # 审查者 — reads deliverables before judging
        "files": ["execution.md", "plan.md"],
        "restate": ["plan-must"],
    },
    "superteam:verifier": {
        "files": ["review.md", "plan.md", "execution.md"],
        "restate": ["plan-must", "review-verdict"],
    },
    "superteam:inspector": {  # 监察者 — continuity auditor
        "files": ["activity-trace.md"],
        "restate": [],
    },
    "superteam:writer": {
        "files": ["verification.md"],
        "restate": [],
    },
}


def entry_log_spec(agent: str) -> dict[str, list[str]] | None:
    return AGENT_ENTRY_LOG_SPEC.get(agent)


def is_valid_for_stage(agent: str, stage: str) -> bool:
    if agent not in AGENT_VALID_STAGES:
        return True  # unknown agent (project-specific), skip
    valid = AGENT_VALID_STAGES[agent]
    return not valid or stage in valid


def entry_gate(agent: str) -> int:
    return AGENT_ENTRY_GATE.get(agent, 0)


def required_preread(agent: str) -> list[str]:
    return AGENT_REQUIRED_PREREAD.get(agent, [])
