---
name: bypass
description: One-shot escape hatch for SuperTeam V4.7 OR-mode write blocks when the hook misjudges. Use only when gate_main_session_scope blocks a legitimate main-session write that genuinely belongs to OR coordination work but was misclassified. Requires a written reason and is audited.
argument-hint: <reason>
disable-model-invocation: true
---

# SuperTeam Bypass

V4.7 OR mode physically blocks the main session from writing substantive
work files. The intended path is always: spawn a specialist. Bypass exists
only for the case where the hook is **wrong** — never as a shortcut around
the discipline.

## Action

```
python "${CLAUDE_PLUGIN_ROOT}/commands/cli/mode_cli.py" bypass $ARGUMENTS
```

The reason in `$ARGUMENTS` is mandatory and gets written into
`.superteam/state/bypass-log.jsonl` with status `pending`. The very next
blocked write will consume the pending record (status flips to `consumed`)
and proceed without blocking.

## Rules

- **One-shot**: each `/superteam:bypass` allows exactly one bypass. Repeated
  blocks need repeated bypasses, which is the friction.
- **Audited**: every consumed bypass shows up in `bypass-log.jsonl`. The
  `writer` specialist must surface them in `final.md` at finish so the user
  can review whether each was justified.
- **Never use to skip a specialist**: if you find yourself wanting to write
  `review.md` directly because "spawning reviewer would take too long",
  that is the exact scenario V4.7 is built to prevent. Spawn the reviewer.

## When To Use

- The hook blocks a write to a file you believe is on the OR-coordination
  whitelist but the regex misclassified it. Tell the user, get their
  consent, then bypass.
- Recovery from a corrupt `active-subagent.json` — the spawn finished but
  the flag did not clear, so a legitimate main-session coordination write
  is being blocked.

## When NOT To Use

- "I can write this faster than spawning a specialist." No.
- "The plan is small enough I can just edit the file." No.
- "The reviewer would only repeat what I already see." No — reviewer
  independence is the point.

If you cannot articulate why the hook is wrong, the hook is right.
