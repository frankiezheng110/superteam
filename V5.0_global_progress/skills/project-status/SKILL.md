---
name: project-status
description: Show project-level progress from .superteam/project.md (V4.7.10). Use when the user asks for project status, milestone overview, or what is left in the multi-milestone roadmap (e.g., "project status", "查看项目进度", "what milestones are left", "next milestone"). Returns a JSON snapshot of frontmatter, milestone counts by status, and the next pending milestone.
disable-model-invocation: true
---

# SuperTeam Project Status

Render `.superteam/project.md` frontmatter and milestones table as a JSON
status snapshot.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" project-status
```

Output fields:

- `frontmatter` — schema_version / project_name / target_release / status /
  current_milestone_slug / created_at / last_updated
- `milestone_count` — total rows in Milestones table
- `milestones_by_status` — counts of DONE / IN_PROGRESS / PENDING
- `next_pending` — first row whose status is PENDING / IN_PROGRESS / TODO
- `is_active` — bool used by stop hook to decide BLOCK / ALLOW

## When NOT To Use

- For a single-phase legacy project without project.md → use
  `/superteam:status` (mode_cli.py status) instead.
