#!/usr/bin/env python3
"""V4.7.0 mode.json CLI — used by /superteam:go, /superteam:end, /superteam:status.

Subcommands:
  enter <slug>            Write mode.json mode=active for given task slug.
                          Fails if a live OR session already exists.
  end                     Set mode=ended, ended_by=user_command. Idempotent.
  end-completion          Set mode=ended, ended_by=project_completion.
  status                  Print mode + spawn log + recent violations as JSON.
  bypass <reason>         Append a one-shot bypass record consumed by the next
                          main-session-write block.

The CLI is intentionally tiny — every write happens through hooks.lib.mode_state
so the slash command path and the hook path share the same atomic-write code.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make hooks/ importable when launched via `python commands/cli/mode_cli.py`
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from hooks.lib import mode_state, state  # noqa: E402


def _ensure_runs_dir(slug: str) -> Path | None:
    runs = state.runs_dir()
    if not runs:
        return None
    target = runs / slug
    target.mkdir(parents=True, exist_ok=True)
    return target


def cmd_enter(args: argparse.Namespace) -> int:
    slug = args.slug.strip()
    if not slug:
        print("error: slug is required", file=sys.stderr)
        return 2
    root = state.find_superteam_root()
    if root is None:
        # No .superteam/ — bootstrap one in CLAUDE_PROJECT_DIR or cwd.
        import os
        base = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
        (base / ".superteam" / "state").mkdir(parents=True, exist_ok=True)
        (base / ".superteam" / "runs").mkdir(parents=True, exist_ok=True)
    _ensure_runs_dir(slug)
    ok, reason = mode_state.enter(slug, source=args.source)
    out: dict = {"command": "enter", "slug": slug, "ok": ok, "reason": reason}
    if ok:
        out["mode_path"] = str(mode_state.mode_path())
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def cmd_end(args: argparse.Namespace) -> int:
    reason = "project_completion" if args.completion else "user_command"
    ok = mode_state.end(reason=reason)
    out: dict = {"command": "end", "ok": ok, "reason": reason}
    if not ok:
        out["note"] = "no mode.json present or already absent"
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def cmd_status(_args: argparse.Namespace) -> int:
    md = mode_state.read_mode()
    cr = state.read_current_run()
    out = {
        "command": "status",
        "health": mode_state.mode_health(),  # V4.7.1 — explicit signal
        "mode_present": bool(md),
        "mode": md.get("mode") if md else None,
        "active_task_slug": md.get("active_task_slug") if md else None,
        "entered_at": md.get("entered_at") if md else None,
        "ended_at": md.get("ended_at") if md else None,
        "ended_by": md.get("ended_by") if md else None,
        "schema_version": md.get("schema_version") if md else None,
        "schema_ok": mode_state.schema_ok(md) if md else None,
        "last_verified_at": md.get("last_verified_at") if md else None,
        "current_stage": cr.get("current_stage") if cr else None,
        "recent_spawns": mode_state.read_recent_spawns(
            limit=5,
            slug=(md.get("active_task_slug") if md else None),
        ),
        "recent_violations": mode_state.read_recent_violations(limit=5),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_bypass(args: argparse.Namespace) -> int:
    reason = args.reason.strip()
    if not reason:
        print("error: bypass reason is required", file=sys.stderr)
        return 2
    mode_state.append_bypass_request(reason)
    out = {"command": "bypass", "ok": True, "reason": reason}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mode_cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_enter = sub.add_parser("enter")
    p_enter.add_argument("slug")
    p_enter.add_argument("--source", default="/superteam:go")
    p_enter.set_defaults(func=cmd_enter)

    p_end = sub.add_parser("end")
    p_end.add_argument("--completion", action="store_true",
                       help="Mark ended_by=project_completion (only via finish stage).")
    p_end.set_defaults(func=cmd_end)

    p_status = sub.add_parser("status")
    p_status.set_defaults(func=cmd_status)

    p_bypass = sub.add_parser("bypass")
    p_bypass.add_argument("reason", nargs="+", help="Why the bypass is needed.")
    p_bypass.set_defaults(func=lambda a: cmd_bypass(argparse.Namespace(reason=" ".join(a.reason))))

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
