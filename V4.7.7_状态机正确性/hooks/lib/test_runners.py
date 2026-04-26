"""Test command recognition + output parsing for TDD red/green detection.

Supports the mainstream runners out of the box; project can extend via
`.superteam/config/test-commands.json`.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import state

# Default runners: command-prefix regex -> family name
DEFAULT_RUNNERS: dict[str, str] = {
    r"\bpytest\b": "pytest",
    r"\bpython\s+-m\s+pytest\b": "pytest",
    r"\bjest\b": "jest",
    r"\bnpx\s+jest\b": "jest",
    r"\bvitest\b": "vitest",
    r"\bnpx\s+vitest\b": "vitest",
    r"\bnpm\s+(run\s+)?test\b": "npm-test",
    r"\byarn\s+(run\s+)?test\b": "npm-test",
    r"\bpnpm\s+(run\s+)?test\b": "npm-test",
    r"\bcargo\s+test\b": "cargo-test",
    r"\bcargo\s+nextest\b": "cargo-test",
    r"\bgo\s+test\b": "go-test",
    r"\bmvn\s+(test|verify)\b": "mvn-test",
    r"\bgradle\s+test\b": "gradle-test",
    r"\bdotnet\s+test\b": "dotnet-test",
    r"\brspec\b": "rspec",
    r"\bphpunit\b": "phpunit",
    r"\bcypress\s+run\b": "cypress",
    r"\bplaywright\s+test\b": "playwright",
    r"\bdeno\s+test\b": "deno-test",
    r"\bflutter\s+test\b": "flutter-test",
}

# Build-only commands (NOT tests) — used by observer_build_only
BUILD_ONLY_RUNNERS: dict[str, str] = {
    r"\bcargo\s+check\b": "cargo-check",
    r"\btsc\s+--noEmit\b": "tsc-noemit",
    r"\btsc\b\s*$": "tsc",
    r"\beslint\b": "eslint",
    r"\bmypy\b": "mypy",
    r"\bflutter\s+analyze\b": "flutter-analyze",
    r"\bcargo\s+build\b": "cargo-build",
}


def load_project_runners() -> dict[str, str]:
    d = state.superteam_dir()
    if not d:
        return {}
    p = d.parent / ".superteam" / "config" / "test-commands.json"
    if not p.exists():
        p = Path(state.find_superteam_root() or ".") / ".superteam" / "config" / "test-commands.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def classify_command(cmd: str) -> tuple[str | None, str]:
    """Return (family, category) where category ∈ {'test','build','other'}."""
    for pattern, family in DEFAULT_RUNNERS.items():
        if re.search(pattern, cmd, re.IGNORECASE):
            return family, "test"
    for pattern, family in BUILD_ONLY_RUNNERS.items():
        if re.search(pattern, cmd, re.IGNORECASE):
            return family, "build"
    for pattern, family in load_project_runners().items():
        if re.search(pattern, cmd, re.IGNORECASE):
            return family, "test"
    return None, "other"


# ---------- output parsers ----------

PYTEST_SUMMARY_RE = re.compile(
    r"=+\s*(\d+)\s+failed[,\s]*(\d+)?\s*passed|(\d+)\s+passed\b|(\d+)\s+failed\b",
    re.IGNORECASE,
)
JEST_SUMMARY_RE = re.compile(r"Tests?:\s+(?:(\d+)\s+failed,\s*)?(\d+)\s+passed", re.IGNORECASE)
CARGO_SUMMARY_RE = re.compile(
    r"test result:\s+(ok|FAILED)\.\s+(\d+)\s+passed;\s+(\d+)\s+failed",
    re.IGNORECASE,
)
GO_SUMMARY_RE = re.compile(r"^(FAIL|PASS|ok)\s+\S+", re.MULTILINE)


def parse_test_output(family: str, stdout: str) -> tuple[int, int]:
    """Return (passed_count, failed_count). -1,-1 if unable to parse."""
    if not stdout:
        return -1, -1
    lower = stdout.lower()
    if family == "pytest":
        m = re.search(r"(\d+)\s+failed[,\s]+(\d+)\s+passed", stdout, re.IGNORECASE)
        if m:
            return int(m.group(2)), int(m.group(1))
        mf = re.search(r"(\d+)\s+failed", stdout, re.IGNORECASE)
        mp = re.search(r"(\d+)\s+passed", stdout, re.IGNORECASE)
        failed = int(mf.group(1)) if mf else 0
        passed = int(mp.group(1)) if mp else 0
        return passed, failed
    if family in ("jest", "vitest", "npm-test"):
        m = re.search(r"(?:(\d+)\s+failed,\s*)?(\d+)\s+passed", stdout, re.IGNORECASE)
        if m:
            failed = int(m.group(1) or 0)
            passed = int(m.group(2))
            return passed, failed
        if "FAIL" in stdout:
            return 0, 1
        if "PASS" in stdout:
            return 1, 0
    if family in ("cargo-test",):
        m = CARGO_SUMMARY_RE.search(stdout)
        if m:
            return int(m.group(2)), int(m.group(3))
    if family == "go-test":
        fail = stdout.count("--- FAIL")
        p = stdout.count("--- PASS")
        return p, fail
    # generic keyword fallback
    has_fail = "failed" in lower or "fail" in lower or "error" in lower
    has_pass = "passed" in lower or "ok" in lower
    if has_fail and not has_pass:
        return 0, 1
    if has_pass and not has_fail:
        return 1, 0
    if has_fail and has_pass:
        return 1, 1  # mixed — unreliable; treat as still-red
    return -1, -1


def looks_like_test_error(stdout: str) -> bool:
    """Distinguish test-framework error (syntax/import) from real test failure.

    Used by A6.4: RED must be a real test failure, not an import error.
    """
    s = stdout or ""
    return bool(
        re.search(
            r"(ImportError|ModuleNotFoundError|SyntaxError|cannot find module|"
            r"TS\d{4,}|compilation error|FAILED\s+\[\s+error\s+\])",
            s,
            re.IGNORECASE,
        )
    )
