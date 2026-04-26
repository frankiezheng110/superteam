---
name: project-next
description: Switch the project's current milestone slug to the next phase and enter mode for it (V4.7.10). Use after a phase finish when the user wants to start the next milestone (e.g., "project next phase-5-desktop", "切换到下一 milestone", "advance to next phase"). Updates project.md.current_milestone_slug and writes mode.json with the new active_task_slug; OR resumes work in the new phase without an additional /superteam:go.
disable-model-invocation: true
---

# SuperTeam Project Next

Advance `current_milestone_slug` in `.superteam/project.md` and enter the
mode session for the next phase.

## Action

The user supplies the phase_slug (must already exist as a row in the
Milestones table):

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" project-next <phase-slug>
```

Effects:

1. `project.md` frontmatter `current_milestone_slug` ← `<phase-slug>`.
2. `mode.json` re-enters with `active_task_slug=<phase-slug>` (best-effort
   — already-active sessions surface but do not fail).
3. The OR continues into the new phase; `clarify` / `design` / `plan` for
   the new phase happen as usual unless the row in project.md notes that
   they are already done from a prior pass.

## When NOT To Use

- The user wants to **end** the entire project — use
  `/superteam:project-complete` instead.
- The phase_slug is not in `project.md` — the CLI returns failure;
  edit project.md to add the row first or use `project-init` with a
  full milestones file.
