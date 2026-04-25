"""Test harness: invoke hook dispatch scripts with simulated Claude JSON payloads.

Each test function:
1. Prepares a fake .superteam/ workspace
2. Builds a Claude hook payload (tool_name, tool_input, tool_response, ...)
3. Runs the dispatch script as subprocess with JSON on stdin
4. Parses stdout JSON -> decision (block / allow / systemMessage / additionalContext)
5. Asserts expected outcome

Also exposes inspect_state() to check files written by hooks (trace, locks, tdd state).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DISPATCH_DIR = ROOT / "hooks" / "dispatch"


@dataclass
class HookResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def decision(self) -> dict[str, Any]:
        """Parsed stdout JSON, or {} on parse failure."""
        try:
            return json.loads(self.stdout) if self.stdout.strip() else {}
        except json.JSONDecodeError:
            return {}

    @property
    def blocked(self) -> bool:
        d = self.decision
        if d.get("decision") == "block":
            return True
        hso = d.get("hookSpecificOutput", {}) or {}
        return hso.get("permissionDecision") == "deny"

    @property
    def reason(self) -> str:
        d = self.decision
        if d.get("reason"):
            return d["reason"]
        hso = d.get("hookSpecificOutput", {}) or {}
        return hso.get("permissionDecisionReason", "") or d.get("systemMessage", "") or hso.get("additionalContext", "")


@dataclass
class Workspace:
    path: Path
    cwd_backup: str = ""

    def enter(self) -> None:
        self.cwd_backup = os.getcwd()
        os.chdir(self.path)

    def exit(self) -> None:
        os.chdir(self.cwd_backup)

    @property
    def superteam(self) -> Path:
        return self.path / ".superteam"

    def init(self, slug: str = "smoke-test", stage: str = "clarify", **extras: Any) -> None:
        (self.superteam / "state").mkdir(parents=True, exist_ok=True)
        (self.superteam / "runs" / slug).mkdir(parents=True, exist_ok=True)
        (self.superteam / "inspector" / "traces").mkdir(parents=True, exist_ok=True)
        (self.superteam / "inspector" / "reports").mkdir(parents=True, exist_ok=True)
        cr = {
            "task_slug": slug,
            "current_stage": stage,
            "last_completed_stage": "",
            "status": "active",
            "repair_cycle_count": 0,
            "plan_quality_gate": "pass",
            "ui_weight": "ui-none",
            "last_updated": "2026-04-24T00:00:00+00:00",
            **extras,
        }
        (self.superteam / "state" / "current-run.json").write_text(
            json.dumps(cr, indent=2), encoding="utf-8"
        )
        (self.superteam / "state" / "compat.json").write_text(
            json.dumps({"hook_compat_version": "4.6.0", "cutover_date": "2026-04-24T00:00:00+00:00"}),
            encoding="utf-8",
        )

    def put(self, relpath: str, content: str) -> None:
        p = self.path / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def read(self, relpath: str) -> str:
        p = self.path / relpath
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def read_json(self, relpath: str) -> dict[str, Any]:
        try:
            return json.loads(self.read(relpath))
        except json.JSONDecodeError:
            return {}


def make_workspace() -> Workspace:
    d = Path(tempfile.mkdtemp(prefix="st_test_"))
    return Workspace(path=d)


def destroy_workspace(ws: Workspace) -> None:
    shutil.rmtree(ws.path, ignore_errors=True)


def invoke(script_name: str, payload: dict[str, Any], *, cwd: Path | None = None) -> HookResult:
    """Run a dispatch/*.py entry script with JSON on stdin, return HookResult.

    script_name examples: 'session_start', 'pre_tool', 'post_tool', 'stop', ...
    """
    script = DISPATCH_DIR / f"{script_name}.py"
    if not script.exists():
        raise FileNotFoundError(script)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(cwd) if cwd else None,
        env=env,
        timeout=30,
    )
    return HookResult(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


# ---- payload builders ----

def pre_tool_edit(file_path: str, new_string: str = "") -> dict[str, Any]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": file_path, "new_string": new_string},
    }


def pre_tool_write(file_path: str, content: str = "") -> dict[str, Any]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
    }


def pre_tool_bash(command: str) -> dict[str, Any]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }


def pre_tool_agent(subagent_type: str, prompt: str = "") -> dict[str, Any]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Agent",
        "tool_input": {"subagent_type": subagent_type, "prompt": prompt},
    }


def post_tool_bash(command: str, stdout: str, exit_code: int = 0) -> dict[str, Any]:
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "tool_response": {"stdout": stdout, "exit_code": exit_code},
    }


def post_tool_agent(subagent_type: str) -> dict[str, Any]:
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": "Agent",
        "tool_input": {"subagent_type": subagent_type, "prompt": ""},
        "tool_response": {"stdout": "", "exit_code": 0},
    }


def post_tool_edit(file_path: str) -> dict[str, Any]:
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": file_path, "new_string": ""},
        "tool_response": {"success": True},
    }


def session_start() -> dict[str, Any]:
    return {"hook_event_name": "SessionStart", "source": "startup"}


def stop_event() -> dict[str, Any]:
    return {"hook_event_name": "Stop", "stop_hook_active": False}
