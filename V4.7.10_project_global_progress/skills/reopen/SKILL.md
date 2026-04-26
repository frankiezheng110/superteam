---
name: reopen
description: Revive a project that was mistakenly marked ended/complete (V4.7.10). Use when a phase finish was misread as a project end and the user needs to continue with subsequent milestones (e.g., "reopen project", "撤销 ended", "phase finish 不应该 end project", "redo project-complete"). Sets project.md.status=in_progress and mode.json.project_lifecycle=running so OR can resume the next milestone. Records reopened_at + reopened_reason for audit.
disable-model-invocation: true
---

# SuperTeam Reopen

Restore a project that was prematurely terminated. Common trigger: a pre-
V4.7.10 release auto-flipped lifecycle=ended at phase finish even though
more milestones remained.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" reopen \
  [--reason "phase-finish-mismark"] [--slug <phase-slug>]
```

Effects:

- `project.md.status` → `in_progress` (if project.md present); records
  `reopened_at` + `reopened_reason` in frontmatter.
- `mode.json.project_lifecycle` → `running`, clears `ended_at` /
  `ended_by`, anchors `active_task_slug` to the supplied `--slug` (or the
  current_milestone_slug from project.md, or the prior mode.json value).

## When NOT To Use

- The project genuinely is complete — leave it complete; create a new
  project for follow-on work.
- mode.json is corrupt — use `/superteam:repair` first to write a fresh
  schema-valid file, then `reopen`.

## After Reopen

- Stop hook resumes BLOCKing OR self-stop until the next legitimate
  exit (`/superteam:project-complete` or `/superteam:end`).
- All audit history (spawn-log, gate-violations, run artifacts) is
  preserved untouched.
