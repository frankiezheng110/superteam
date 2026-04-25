"""A7.3: solution-landscape.md — external search evidence with URL + date."""
from __future__ import annotations

import re
from pathlib import Path

from ..lib import parser, state


URL_RE = re.compile(r"https?://\S+")
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2}|20\d{2}/\d{1,2}/\d{1,2})\b")


def run(path: Path | str | None = None) -> tuple[bool, list[str]]:
    if path is None:
        slug = state.current_slug()
        rd = state.run_slug_dir(slug) if slug else None
        if not rd:
            return True, []
        path = rd / "solution-landscape.md"
    text = parser.read_text(path)
    if not text:
        return False, ["solution-landscape.md 不存在或为空"]
    errs: list[str] = []

    if len(URL_RE.findall(text)) < 2:
        errs.append("缺少足够外部搜索证据: 至少需要 2 个 URL 引用")
    if not DATE_RE.search(text):
        errs.append("缺少日期标注 (至少一个 YYYY-MM-DD 格式的参考日期)")

    return not errs, errs
