#!/usr/bin/env python3
"""PostToolUse dispatch — runs validators, observers, post-agent chain."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))

from hooks.lib import decisions  # noqa: E402
from hooks.observers import (  # noqa: E402
    observer_build_only,
    observer_feature_spotcheck,
    observer_git_activity,
    observer_test_runner,
)
from hooks.post_agent import (  # noqa: E402
    post_agent_entry_log,
    post_agent_trace_writer,
    post_executor_chain,
)
from hooks.validators import (  # noqa: E402
    validator_activity_trace,
    validator_current_run_json,
    validator_design,
    validator_execution,
    validator_feature_checklist,
    validator_plan,
    validator_polish,
    validator_project_definition,
    validator_review,
    validator_solution_landscape,
    validator_solution_options,
    validator_ui_intent,
    validator_verification,
)
from hooks.lib import trace  # noqa: E402


# Artifact filename -> validator module
ARTIFACT_VALIDATORS = {
    "project-definition.md": validator_project_definition,
    "solution-options.md": validator_solution_options,
    "solution-landscape.md": validator_solution_landscape,
    "design.md": validator_design,
    "ui-intent.md": validator_ui_intent,
    "feature-checklist.md": validator_feature_checklist,
    "plan.md": validator_plan,
    "execution.md": validator_execution,
    "polish.md": validator_polish,
    "review.md": validator_review,
    "verification.md": validator_verification,
    "activity-trace.md": validator_activity_trace,
    "current-run.json": validator_current_run_json,
}


def _run_artifact_validator(file_path: str) -> None:
    fname = file_path.replace("\\", "/").rsplit("/", 1)[-1]
    mod = ARTIFACT_VALIDATORS.get(fname)
    if not mod:
        return
    ok, errs = mod.run()
    if not ok:
        for e in errs[:3]:
            trace.emit_discrepancy(f"post_write_{fname}", e, severity="medium")


def main() -> None:
    payload = decisions.read_hook_input()
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    tool_response = payload.get("tool_response", {}) or {}

    if tool == "Agent":
        post_agent_trace_writer.run(tool_input, tool_response)
        post_agent_entry_log.run(tool_input, tool_response)
        msg = post_executor_chain.run(tool_input, tool_response)
        if msg:
            decisions.emit_system_message(msg, hook_event="PostToolUse")

    elif tool in ("Edit", "Write", "MultiEdit"):
        fp = str(tool_input.get("file_path", ""))
        if fp:
            _run_artifact_validator(fp)

    elif tool == "Bash":
        observer_test_runner.run(tool_input, tool_response)
        observer_build_only.run(tool_input, tool_response)
        observer_git_activity.run(tool_input, tool_response)
        observer_feature_spotcheck.run(tool_input, tool_response)

    decisions.emit_allow()


if __name__ == "__main__":
    main()
