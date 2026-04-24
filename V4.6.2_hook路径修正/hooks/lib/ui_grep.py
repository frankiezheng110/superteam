"""CSS/HTML pattern check for project-declared UI contracts (ui-intent.md).

V4.6.0 design: hook does NOT hardcode font/color blacklists. It only reads
the project's `ui-intent.md` and enforces what the project itself declared.
If the project did not declare, hook does not activate.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import parser, state


def is_ui_file(path: str) -> bool:
    lower = path.lower()
    return any(lower.endswith(ext) for ext in (".css", ".scss", ".less", ".sass", ".html", ".htm", ".tsx", ".jsx", ".vue", ".svelte"))


def load_ui_intent() -> str:
    slug = state.current_slug()
    rd = state.run_slug_dir(slug) if slug else None
    if not rd:
        return ""
    p = rd / "ui-intent.md"
    return parser.read_text(p)


def typography_whitelist() -> list[str]:
    text = load_ui_intent()
    if not text:
        return []
    return parser.ui_intent_typography_whitelist(text)


def check_typography_violation(file_content: str, file_path: str) -> str | None:
    """Return first violating font-family value if present; None if clean or inactive."""
    if not is_ui_file(file_path):
        return None
    whitelist = typography_whitelist()
    if not whitelist:
        return None  # project didn't declare; hook stays inactive
    normalized_whitelist = {name.lower().strip() for name in whitelist}
    # Extract every font-family value in file
    for m in re.finditer(r"font-family\s*:\s*([^;{}\n]+)", file_content, re.IGNORECASE):
        stack = m.group(1).strip()
        # Primary font = first token, strip quotes
        primary = stack.split(",")[0].strip().strip('"').strip("'").lower()
        if primary and primary not in normalized_whitelist and not primary.startswith(("var(", "inherit", "initial", "unset")):
            return primary
    return None
