#!/usr/bin/env python3
"""V4.7.x mode.json CLI — used by every /superteam:* slash command.

Subcommands:
  enter <slug>            Write mode.json mode=active for given task slug.
                          Fails if a live OR session already exists.
  end                     Set mode=ended, ended_by=user_command. Idempotent.
  status                  Print mode + spawn log + recent violations as JSON.
  bypass <reason>         Append a one-shot bypass record consumed by the next
                          main-session-write block.
  debug                   V4.7.4 — dump recent spawn-log / gate-violations /
                          bypass-log entries for triage.
  repair [--slug X]       V4.7.4 — back up corrupt/stale mode.json and rewrite
                          a fresh schema-valid one (anchored to slug X if given,
                          else the salvaged value from the broken file).
  doctor                  V4.7.4 — comprehensive trust-chain health check
                          (mode.json schema, last_verified_at staleness,
                          spawn-log vs current_stage, bypass volume,
                          stale active-subagent flag).

The CLI is intentionally tiny — every write goes through hooks.lib.mode_state
so the slash command path and the hook path share the same atomic-write code.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
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


def cmd_pause(_args: argparse.Namespace) -> int:
    """V4.7.7 — pause running project. project_lifecycle: running → paused."""
    ok = mode_state.pause(by="user")
    out: dict = {
        "command": "pause",
        "ok": ok,
        "project_lifecycle": "paused" if ok else None,
    }
    if not ok:
        out["note"] = "no mode.json present"
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def cmd_resume(_args: argparse.Namespace) -> int:
    """V4.7.7 — resume paused project. project_lifecycle: paused → running."""
    ok = mode_state.resume()
    out: dict = {
        "command": "resume",
        "ok": ok,
        "project_lifecycle": "running" if ok else None,
    }
    if not ok:
        out["note"] = "no mode.json present"
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


def cmd_debug(args: argparse.Namespace) -> int:
    """V4.7.4 — output recent spawn-log + gate-violations + bypass-log for triage."""
    limit = int(getattr(args, "limit", 10) or 10)
    md = mode_state.read_mode()
    slug = md.get("active_task_slug") if md else None
    out = {
        "command": "debug",
        "health": mode_state.mode_health(),
        "active_task_slug": slug,
        "recent_spawns": mode_state.read_recent_spawns(limit=limit, slug=slug),
        "recent_violations": mode_state.read_recent_violations(limit=limit),
        "violations_in_60s": mode_state.violations_in_window(seconds=60),
    }
    bp = mode_state.bypass_log_path()
    if bp and bp.exists():
        try:
            tail = bp.read_text(encoding="utf-8").splitlines()[-limit:]
            out["recent_bypasses"] = [json.loads(x) for x in tail if x.strip()]
        except (OSError, json.JSONDecodeError):
            out["recent_bypasses"] = []
    else:
        out["recent_bypasses"] = []
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    """V4.7.4 — back up corrupt mode.json and rewrite a fresh schema-valid one.

    Preserves active_task_slug if recoverable so the run directory is not
    orphaned. Run history (spawn-log, violations, run artifacts) is left
    untouched.
    """
    p = mode_state.mode_path()
    if not p:
        print(json.dumps({"command": "repair", "ok": False,
                          "reason": "no .superteam/state directory"}, ensure_ascii=False, indent=2))
        return 1
    health = mode_state.mode_health()

    # Try to salvage active_task_slug from old file or args.
    salvaged_slug = ""
    if p.exists():
        try:
            raw = p.read_text(encoding="utf-8")
            try:
                old = json.loads(raw)
                if isinstance(old, dict):
                    salvaged_slug = str(old.get("active_task_slug") or "")
            except json.JSONDecodeError:
                pass
            # Always back up the file before rewrite.
            backup = p.with_suffix(p.suffix + f".bak.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}")
            backup.write_text(raw, encoding="utf-8")
        except OSError:
            pass

    target_slug = (getattr(args, "slug", None) or salvaged_slug or "").strip()
    if not target_slug:
        print(json.dumps({
            "command": "repair", "ok": False,
            "reason": "no slug to anchor (use --slug <task-slug>); previous mode.json had none",
            "prior_health": health,
        }, ensure_ascii=False, indent=2))
        return 2

    # Force-end any prior session, then re-enter cleanly so schema is fresh.
    if p.exists():
        try:
            p.unlink()
        except OSError:
            pass
    ok, reason = mode_state.enter(target_slug, source="/superteam:repair")
    out = {
        "command": "repair",
        "ok": ok,
        "reason": reason,
        "prior_health": health,
        "anchored_slug": target_slug,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def cmd_doctor(_args: argparse.Namespace) -> int:
    """V4.7.4 — comprehensive health check across the V4.7 trust chain."""
    md = mode_state.read_mode()
    cr = state.read_current_run()
    health = mode_state.mode_health()
    slug = md.get("active_task_slug") if md else None

    findings: list[dict] = []

    # 1. mode.json health
    if health == mode_state.MODE_HEALTH_CORRUPT:
        findings.append({"severity": "high", "check": "mode.json", "msg": "corrupt — run /superteam:repair"})
    elif health == mode_state.MODE_HEALTH_UNKNOWN_SCHEMA:
        findings.append({"severity": "high", "check": "mode.json",
                         "msg": "schema_version not in known set — plugin upgrade may be required"})

    # 2. last_verified_at staleness — hooks may be dead.
    if md and md.get("last_verified_at"):
        from datetime import datetime, timezone, timedelta
        try:
            ts = datetime.fromisoformat(md["last_verified_at"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - ts
            if age > timedelta(minutes=30) and md.get("mode") == "active":
                findings.append({
                    "severity": "medium", "check": "hook heartbeat",
                    "msg": f"last_verified_at is {age.total_seconds():.0f}s old — hooks may not be running",
                })
        except ValueError:
            pass

    # 3. spawn-log vs current_stage consistency
    if md and md.get("mode") == "active" and slug and cr:
        cs = (cr.get("current_stage") or "").strip()
        if cs in ("review", "verify", "finish"):
            spawns = {r.get("subagent_type", "") for r in mode_state.read_recent_spawns(limit=200, slug=slug)}
            need = {"review": "superteam:executor", "verify": "superteam:reviewer", "finish": "superteam:verifier"}[cs]
            if need not in spawns:
                findings.append({
                    "severity": "high", "check": "stage prerequisites",
                    "msg": f"current_stage={cs} but spawn-log lacks {need} — stage was advanced without prerequisite",
                })

    # 4. bypass log volume
    bp = mode_state.bypass_log_path()
    if bp and bp.exists():
        try:
            consumed = sum(1 for line in bp.read_text(encoding="utf-8").splitlines()
                           if line.strip() and json.loads(line).get("status") == "consumed")
            if consumed >= 3:
                findings.append({
                    "severity": "low", "check": "bypass usage",
                    "msg": f"{consumed} consumed bypasses in this run — review whether the gate rules need adjustment",
                })
        except (OSError, json.JSONDecodeError):
            pass

    # 5. recent violation cluster
    if mode_state.is_or_active():
        recent = mode_state.violations_in_window(seconds=60)
        if len(recent) >= 3:
            findings.append({
                "severity": "medium", "check": "block clustering",
                "msg": f"{len(recent)} blocks in last 60s — see /superteam:debug for details",
            })

    # 6. corrupt active-subagent.json (stale flag)
    p_state = state.state_dir()
    if p_state:
        asf = p_state / "active-subagent.json"
        if asf.exists():
            try:
                rec = json.loads(asf.read_text(encoding="utf-8"))
                ts_raw = rec.get("started_at", "")
                from datetime import datetime, timezone, timedelta
                try:
                    ts = datetime.fromisoformat(ts_raw)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    age = datetime.now(timezone.utc) - ts
                    if age > timedelta(minutes=15):
                        findings.append({
                            "severity": "medium", "check": "active-subagent.json",
                            "msg": f"flag set {age.total_seconds():.0f}s ago but no SubagentStop — clear with `rm` or wait for next spawn cycle to overwrite",
                        })
                except ValueError:
                    pass
            except (OSError, json.JSONDecodeError):
                pass

    out = {
        "command": "doctor",
        "health": health,
        "active_task_slug": slug,
        "current_stage": cr.get("current_stage") if cr else None,
        "findings": findings,
        "ok": all(f["severity"] != "high" for f in findings),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["ok"] else 1


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

    p_pause = sub.add_parser("pause", help="V4.7.7 — set project_lifecycle=paused.")
    p_pause.set_defaults(func=cmd_pause)

    p_resume = sub.add_parser("resume", help="V4.7.7 — set project_lifecycle=running.")
    p_resume.set_defaults(func=cmd_resume)

    p_status = sub.add_parser("status")
    p_status.set_defaults(func=cmd_status)

    p_bypass = sub.add_parser("bypass")
    p_bypass.add_argument("reason", nargs="+", help="Why the bypass is needed.")
    p_bypass.set_defaults(func=lambda a: cmd_bypass(argparse.Namespace(reason=" ".join(a.reason))))

    p_debug = sub.add_parser("debug", help="V4.7.4 — recent spawn / violation / bypass log dump.")
    p_debug.add_argument("--limit", type=int, default=10)
    p_debug.set_defaults(func=cmd_debug)

    p_repair = sub.add_parser("repair", help="V4.7.4 — back up and rewrite mode.json with fresh schema.")
    p_repair.add_argument("--slug", help="Task slug to anchor the repaired mode.json to (defaults to salvaged value).")
    p_repair.set_defaults(func=cmd_repair)

    p_doctor = sub.add_parser("doctor", help="V4.7.4 — comprehensive trust-chain health check.")
    p_doctor.set_defaults(func=cmd_doctor)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
