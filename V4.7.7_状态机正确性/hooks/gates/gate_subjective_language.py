"""A18.1: subjective-language discipline for review.md / verification.md / reports/*.

Blocks Edit/Write introducing 'appears/seems/probably/should/looks fine' into
review/verification/inspector-report files as substantive evidence.
Backtick-quoted occurrences are exempt (quoting someone else's usage).
"""
from __future__ import annotations

import re
from typing import Any

from ..lib import parser


TARGET_PATH_RE = re.compile(
    r"(?i)(review\.md$|verification\.md$|inspector[/\\]reports[/\\].*\.md$)"
)


def check(tool_input: dict[str, Any]) -> tuple[bool, str]:
    fp = str(tool_input.get("file_path", "")).replace("\\", "/")
    if not TARGET_PATH_RE.search(fp):
        return True, ""
    content = tool_input.get("new_string") or tool_input.get("content") or ""
    if not content:
        return True, ""

    violations = parser.find_subjective_violations(content)
    if violations:
        sample = ", ".join(dict.fromkeys(violations[:3]))
        return False, (
            f"检测到主观词 {sample} 出现在 {fp.split('/')[-1]}. "
            f"review/verification/inspector report 禁止主观证据语言 (A18.1). "
            f"改写为具体证据引用 (file:line / trace event / 测试输出)"
        )

    return True, ""
