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

from hooks.lib import mode_state, project_state, state  # noqa: E402


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


# ---------- V4.7.10 project layer ----------

def _bootstrap_superteam_dir() -> Path | None:
    """Create .superteam/state if missing; mirrors cmd_enter's bootstrap path."""
    root = state.find_superteam_root()
    if root is None:
        import os
        base = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
        (base / ".superteam" / "state").mkdir(parents=True, exist_ok=True)
        (base / ".superteam" / "runs").mkdir(parents=True, exist_ok=True)
    return state.superteam_dir()


def cmd_project_init(args: argparse.Namespace) -> int:
    """V4.7.10 — create .superteam/project.md.

    --milestones-file <path> reads a simple TSV/CSV-ish format:
        version<TAB>phase_slug<TAB>status<TAB>notes
    Lines starting with '#' or blank are ignored. status defaults to PENDING.
    """
    name = args.name.strip()
    slug = (args.slug or "").strip() or name.lower().replace(" ", "-")
    target = args.target_release.strip()
    if not name or not target:
        print("error: --name and --target-release required", file=sys.stderr)
        return 2
    _bootstrap_superteam_dir()

    milestones: list[dict[str, str]] = []
    if args.milestones_file:
        mp = Path(args.milestones_file)
        if not mp.exists():
            print(f"error: milestones file not found: {mp}", file=sys.stderr)
            return 2
        for raw in mp.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [c.strip() for c in line.replace("\t", "|").split("|")]
            if len(parts) < 2:
                continue
            milestones.append({
                "version": parts[0],
                "phase_slug": parts[1],
                "status": parts[2] if len(parts) > 2 else "PENDING",
                "notes": parts[3] if len(parts) > 3 else "",
            })

    ok = project_state.init_project(
        name=name, slug=slug, target_release=target, milestones=milestones,
    )
    out = {
        "command": "project-init",
        "ok": ok,
        "project_path": str(project_state.project_path()) if project_state.project_path() else None,
        "milestone_count": len(milestones),
    }
    if not ok:
        out["note"] = "project.md already exists or no .superteam root"
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def cmd_project_status(_args: argparse.Namespace) -> int:
    """V4.7.10 — render project.md frontmatter + milestone summary as JSON."""
    fm = project_state.read_project()
    if not fm:
        out = {
            "command": "project-status",
            "project_present": False,
            "note": ".superteam/project.md missing — use /superteam:project-init to create",
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 1
    rows = project_state.list_milestones()
    nxt = project_state.next_pending_milestone()
    out = {
        "command": "project-status",
        "project_present": True,
        "is_active": project_state.is_project_active(),
        "frontmatter": fm,
        "milestone_count": len(rows),
        "milestones_by_status": {
            s: sum(1 for r in rows if (r.get("status") or "").upper() == s)
            for s in ("DONE", "IN_PROGRESS", "PENDING")
        },
        "next_pending": nxt,
        "current_milestone_slug": project_state.current_milestone_slug() or None,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_project_next(args: argparse.Namespace) -> int:
    """V4.7.10 — advance current_milestone_slug to <slug>; also enter mode for it.

    Sequence:
      1. Verify <slug> exists in project.md milestone table.
      2. Set frontmatter.current_milestone_slug = <slug>.
      3. mode_state.enter(slug) so mode.json points at the new phase.
    Step 3 is best-effort — if a prior phase ended mode but the user is
    just consulting, they can also run mode_cli.py reopen to revive.
    """
    slug = args.slug.strip()
    row = project_state.find_milestone(slug)
    if not row:
        print(json.dumps({
            "command": "project-next", "ok": False,
            "reason": f"slug '{slug}' not in project.md milestones table",
        }, ensure_ascii=False, indent=2))
        return 2
    if not project_state.set_current_milestone(slug):
        print(json.dumps({
            "command": "project-next", "ok": False,
            "reason": "failed to update project.md frontmatter",
        }, ensure_ascii=False, indent=2))
        return 1

    # Best-effort: open a mode session for the new phase. If one is already
    # active for the same slug, mode_state.enter returns ALREADY_ACTIVE which
    # we surface but do not treat as a hard failure.
    enter_ok, enter_reason = mode_state.enter(slug, source="/superteam:project-next")
    out = {
        "command": "project-next",
        "ok": True,
        "slug": slug,
        "milestone": row,
        "mode_enter_ok": enter_ok,
        "mode_enter_reason": enter_reason,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_project_complete(args: argparse.Namespace) -> int:
    """V4.7.10 — mark project.md status=complete and end mode lifecycle.

    Refuses when any milestone is still PENDING / IN_PROGRESS unless --force.
    On success, also calls mode_state.end(reason='project_completion') so
    the V4.7.9 stop-hook fallback path also returns ALLOW.
    """
    if not project_state.read_project():
        print(json.dumps({"command": "project-complete", "ok": False,
                          "reason": "no project.md"}, ensure_ascii=False, indent=2))
        return 1
    rows = project_state.list_milestones()
    pending = [r for r in rows if (r.get("status") or "").upper() not in ("DONE", "")]
    if pending and not args.force:
        print(json.dumps({
            "command": "project-complete", "ok": False,
            "reason": f"{len(pending)} milestone(s) not DONE — pass --force to override",
            "pending": [r.get("phase_slug") for r in pending],
        }, ensure_ascii=False, indent=2))
        return 2

    by = args.by or "user"
    p_ok = project_state.set_project_complete(by=by)
    m_ok = mode_state.end(reason="project_completion")
    out = {
        "command": "project-complete",
        "ok": p_ok,
        "project_marked_complete": p_ok,
        "mode_ended": m_ok,
        "by": by,
    }
    if pending:
        out["forced_over_pending"] = [r.get("phase_slug") for r in pending]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if p_ok else 1


def cmd_reopen(args: argparse.Namespace) -> int:
    """V4.7.10 — revive a project mistakenly marked ended/complete.

    Two-phase: project.md.status → in_progress (if present), and mode.json
    .project_lifecycle → running (via mode_state.resume's underlying write).
    For the mode side we re-enter cleanly to ensure schema-fresh fields.
    """
    reason = (args.reason or "phase-finish-mismark").strip()
    project_ok = project_state.reopen_project(reason=reason)
    md = mode_state.read_mode()
    slug = md.get("active_task_slug") or project_state.current_milestone_slug() or args.slug or ""
    mode_ok = False
    if slug:
        # Reset mode lifecycle without scrubbing audit history — easiest path
        # is to set the field directly via write_mode (the public API V4.7.7
        # provides for migration / pause / resume).
        try:
            md["mode"] = "active"
            md["project_lifecycle"] = "running"
            md["ended_at"] = None
            md["ended_by"] = None
            md["paused_at"] = None
            md["paused_by"] = None
            md["active_task_slug"] = slug
            md["reopened_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            md["reopened_reason"] = reason
            mode_ok = mode_state.write_mode(md)
        except Exception:  # noqa: BLE001
            mode_ok = False

    out = {
        "command": "reopen",
        "project_reopened": project_ok,
        "mode_reopened": mode_ok,
        "anchored_slug": slug or None,
        "reason": reason,
        "ok": project_ok or mode_ok,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if (project_ok or mode_ok) else 1


# ---------- argparse main ----------

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

    # V4.7.10 — project layer
    p_pinit = sub.add_parser("project-init", help="V4.7.10 — create .superteam/project.md.")
    p_pinit.add_argument("--name", required=True, help="Human-readable project name (e.g. SMS).")
    p_pinit.add_argument("--slug", help="project_slug (defaults to slugified name).")
    p_pinit.add_argument("--target-release", required=True, help="e.g. V2.0.0_release")
    p_pinit.add_argument("--milestones-file", help="Optional file with `version|phase_slug|status|notes` rows.")
    p_pinit.set_defaults(func=cmd_project_init)

    p_pstatus = sub.add_parser("project-status", help="V4.7.10 — render project.md as JSON.")
    p_pstatus.set_defaults(func=cmd_project_status)

    p_pnext = sub.add_parser("project-next", help="V4.7.10 — advance current milestone slug.")
    p_pnext.add_argument("slug", help="phase_slug of the milestone to enter.")
    p_pnext.set_defaults(func=cmd_project_next)

    p_pcomplete = sub.add_parser("project-complete", help="V4.7.10 — mark project complete + end mode.")
    p_pcomplete.add_argument("--by", default="user")
    p_pcomplete.add_argument("--force", action="store_true",
                             help="Allow even if some milestones are still PENDING.")
    p_pcomplete.set_defaults(func=cmd_project_complete)

    p_reopen = sub.add_parser("reopen", help="V4.7.10 — revive a project mistakenly ended/complete.")
    p_reopen.add_argument("--reason", default="phase-finish-mismark")
    p_reopen.add_argument("--slug", help="Anchor mode.json to this slug (defaults to current).")
    p_reopen.set_defaults(func=cmd_reopen)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
