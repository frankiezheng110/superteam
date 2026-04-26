---
name: project-complete
description: Mark the entire project complete after all milestones are DONE (V4.7.10). Use only when the user has finished every milestone and wants to fully end the project (e.g., "project complete", "全部 milestone 完成", "wrap up project", "release V2.0.0"). Sets project.md.status=complete and ends mode lifecycle so OR can finally self-stop. Refuses (without --force) when any milestone is still PENDING.
disable-model-invocation: true
---

# SuperTeam Project Complete

End the project: project.md.status → `complete`, mode.json.lifecycle →
`ended`. Stop hook will then ALLOW the OR to stop.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" project-complete
```

Optional flags:

- `--force` — proceed even if milestones are still PENDING. Use only when
  the user explicitly accepts an early termination.
- `--by user_command|project_completion|migration` — recorded in
  frontmatter `completed_by` (default: `user`).

## After Complete

- `.superteam/project.md` shows `status: complete` + `completed_by` set.
- `mode.json.project_lifecycle = ended` and `ended_by = project_completion`.
- The next Stop event passes `_or_self_stop_check` (project not active +
  mode not alive) and the OR can finally yield.

## When NOT To Use

- Any milestone still PENDING / IN_PROGRESS without explicit user
  approval — the CLI refuses by default. Use `/superteam:project-next`
  to advance milestones one at a time.
- The user only wants to pause (not end) — use `/superteam:pause`
  instead. Pause keeps the project alive but lets OR stop temporarily.

## When To Use

- All milestones are DONE in the table.
- The user has explicitly confirmed "we are done with this project".
