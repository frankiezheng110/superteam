"""A7.5 / Gate 2 check 8 / B5: ui-intent.md — 7 aesthetic contract sections."""
from __future__ import annotations

from pathlib import Path

from ..lib import parser, state


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    # Only active when ui_weight is standard/critical
    uw = state.ui_weight()
    if uw not in ("ui-standard", "ui-critical"):
        return True, []
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "ui-intent.md"
    text = parser.read_text(path)
    if not text:
        return False, ["ui-intent.md 不存在或为空 (ui-standard/critical 必需)"]

    missing = parser.ui_intent_missing_sections(text)
    errs = [f"ui-intent.md 缺少必需段: {s}" for s in missing]

    # B5: design thinking 4 pillars (Purpose/Tone/Constraints/Differentiation)
    for pillar in ("Purpose", "Tone", "Constraints", "Differentiation"):
        if not parser.has_section(text, pillar):
            errs.append(f"缺少 Design Thinking pillar: {pillar}")

    # Each contract section must have non-trivial content (> 50 chars)
    for sect in (
        r"Aesthetic\s+Direction",
        r"Typography\s+Contract",
        r"Color\s+Contract",
        r"Motion\s+Contract",
        r"Spatial\s+Contract",
        r"Visual\s+Detail\s+Contract",
        r"Anti[-\s]Pattern\s+Exclusions",
    ):
        body = parser.extract_section(text, sect)
        if 0 < len(body.strip()) < 50:
            errs.append(f"段 {sect.replace(chr(92)+'s+',' ')} 存在但内容太空 (< 50 字符)")

    return not errs, errs
