---
name: project-init
description: Create the .superteam/project.md file that tracks a multi-milestone delivery (V4.7.10 project layer). Use when the user wants to establish project-level scope spanning multiple SuperTeam workflow runs (e.g., "init project SMS V2.0.0", "建立 project.md", "set up multi-milestone tracking"). Each milestone in project.md corresponds to one phase = one SuperTeam workflow loop.
disable-model-invocation: true
---

# SuperTeam Project Init

Create `.superteam/project.md` so phase-finish marks a milestone DONE
without ending the project lifecycle.

## Action

Ask the user for: project name, target release version, optional initial milestone list.
Then run:

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" project-init \
  --name <NAME> --target-release <VERSION> [--slug <SLUG>] [--milestones-file <PATH>]
```

When `--milestones-file` is provided, the file contains one row per
milestone, pipe- or tab-separated:

```
# version | phase_slug | status | notes
V1.0.0_foundation | foundation-bootstrap | DONE | repo init
V1.5.0_desktop    | phase-5-desktop      | PENDING | Tauri integration
```

## After Init

- `.superteam/project.md` is created with frontmatter (`schema_version: 1`,
  `status: in_progress`, `current_milestone_slug` = first milestone) and a
  Milestones table seeded from the file.
- Subsequent SessionStart hooks inject the project banner so the OR
  context begins with project-wide visibility.
- Phase finish (Stop hook with current_stage=finish + valid artifacts)
  marks the active milestone DONE in the table.

## When NOT To Use

- A project.md already exists — edit by hand or use `project-next` /
  `mark-milestone-done` flows.
- The repo is a single-phase delivery — V4.7.9 mode-only behavior is
  enough; introducing project.md adds noise.
