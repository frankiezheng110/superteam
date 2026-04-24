#!/usr/bin/env python3
"""Merge hooks_settings_template.json into target Claude settings.json.

Called by install.ps1 / install.sh. Does a structural merge — existing user
hooks are preserved; SuperTeam hooks are appended per event. If the exact
command already exists under an event, it is NOT duplicated.

Usage:
    python install_merge.py <template_path> <target_settings_path>

Exits 0 on success.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def merge_event_entries(existing: list, new_entries: list) -> list:
    """Merge hook entries for a single event. Dedupe by exact command string."""
    existing_cmds: set[str] = set()
    for entry in existing:
        for h in entry.get("hooks", []) or []:
            existing_cmds.add(h.get("command", ""))
    merged = list(existing)
    for entry in new_entries:
        wanted = [h for h in entry.get("hooks", []) or [] if h.get("command") not in existing_cmds]
        if wanted:
            # Keep matcher if present
            new_entry = {k: v for k, v in entry.items() if k != "hooks"}
            new_entry["hooks"] = wanted
            merged.append(new_entry)
    return merged


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: install_merge.py <template> <target>")
        return 2
    tpl = Path(sys.argv[1])
    tgt = Path(sys.argv[2])
    if not tpl.exists():
        print(f"template missing: {tpl}")
        return 1
    template = json.loads(tpl.read_text(encoding="utf-8"))
    template_hooks = template.get("hooks", {}) or {}

    target: dict = {}
    if tgt.exists():
        try:
            target = json.loads(tgt.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            backup = tgt.with_suffix(tgt.suffix + ".bak")
            tgt.rename(backup)
            print(f"target was invalid JSON; backed up to {backup}")
            target = {}

    target.setdefault("hooks", {})
    for event, new_entries in template_hooks.items():
        existing = target["hooks"].get(event, []) or []
        target["hooks"][event] = merge_event_entries(existing, new_entries)

    tgt.parent.mkdir(parents=True, exist_ok=True)
    tgt.write_text(json.dumps(target, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"merged SuperTeam hooks into {tgt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
