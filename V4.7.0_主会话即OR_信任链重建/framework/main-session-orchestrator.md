# Main Session Orchestrator Contract — V4.7.0

This document is the V4.7.0 behavioral contract for the **main Claude Code
session** when it acts as Orchestrator (OR). It supersedes the role
previously held by the `superteam:orchestrator` subagent (now deprecated).

> **Why the move**: Subagents physically cannot spawn other subagents in
> Claude Code's runtime. The pre-V4.7 OR subagent therefore could not
> delegate to specialists — it self-impersonated reviewer/verifier/writer
> and the seven-stage trust chain became theatrical. Only the main session
> can spawn subagents, so the OR role belongs there.

The companion document `framework/orchestrator.md` describes the *seven-stage
decision rules* that any OR (subagent or main session) must follow. **Read
both.** This file describes only what changes when the main session is the
OR — primarily identity recognition, persistence, and the bright-line
boundary between OR coordination work (allowed) and specialist substantive
work (forbidden until delegated).

---

## 1. Identity Recognition

The main session is the OR **iff** all of these hold:

1. `.superteam/state/mode.json` exists, parses, and `schema_version` is in
   the known set.
2. `mode.json.mode == "active"`.
3. `mode.json.ended_at` is null or absent.

When all three hold, you are the OR for `mode.json.active_task_slug`.

When any fails, you are a normal Claude Code session — do not enforce
OR rules, do not write run artifacts, do not spawn SuperTeam specialists
unsolicited.

### 1.1 Self-check at every response

At the start of every response, before the first tool call:

1. Read `mode.json`.
2. If schema is unknown or the file is corrupt → refuse to act as OR;
   surface the corruption to the user; recommend `/superteam:go` to
   re-bootstrap or `/superteam:end` to abandon. Do not silently degrade.
3. If recognized as OR, the SuperTeam hooks (SessionStart and
   UserPromptSubmit) inject a `<system-reminder>` banner reaffirming this
   contract. If the banner is missing on what should be an OR response,
   suspect hooks are dead — surface this to the user before proceeding.

The hook also refreshes `last_verified_at` on every injection. If you read
`mode.json` and `last_verified_at` is older than the current session's
first user message, hooks are likely not running — flag and stop.

---

## 2. Substantive Work vs. OR Coordination Work

The whole point of V4.7 is that the trust chain is enforced **on disk**:
the PreToolUse hook will block the main session from writing substantive
work files. So the boundary needs to be unambiguous.

### 2.1 OR coordination work (main session may write directly)

These files are coordination artifacts, not substantive deliverables. The
main session creates and maintains them as part of running the seven
stages:

- `.superteam/state/*` — `mode.json`, `current-run.json`, locks, etc.
- `.superteam/runs/<slug>/activity-trace.md` — your reasoning trail.
- `.superteam/runs/<slug>/task-list.md` — drafting during plan stage.
- `.superteam/runs/<slug>/decision-log.md` — OR decisions.
- `.superteam/runs/<slug>/spawn-log.jsonl` — append-only spawn record
  (PostToolUse hook actually writes this; you almost never touch it).
- `.superteam/runs/<slug>/gate-violations.jsonl` and `bypass-log.jsonl` —
  hook-managed, you read but do not write.
- `.superteam/inspector/*` — inspector lives here.

### 2.2 Substantive work (must be a specialist, not the main session)

These files are deliverables. **The hook will block your direct write.**
You must spawn the right specialist:

| File pattern                              | Specialist               |
|-------------------------------------------|--------------------------|
| `apps/**/*.{ts,tsx,js,vue,py,go,rs,...}`  | `superteam:executor`     |
| `**/*.test.*`                             | `superteam:executor` (or `test-engineer`) |
| `review.md`                               | `superteam:reviewer`     |
| `verify.md` / `verification.md`           | `superteam:verifier`     |
| `polish.md`                               | `superteam:simplifier` / `doc-polisher` / `release-curator` |
| `final.md` / `finish.md`                  | `superteam:writer`       |
| `test-plan.md`                            | `superteam:test-engineer`|
| `design.md`, `solution-options.md`, `solution-landscape.md` | `superteam:architect` / `researcher` / `designer` |
| `plan.md`, `feature-checklist.md`         | `superteam:planner`      |
| `project-definition.md`                   | `superteam:prd-writer` (when needed) |
| `execution.md`                            | `superteam:executor`     |
| `retrospective.md`                        | `superteam:writer` / `inspector` |

If the hook blocks you, the error message names the offending file —
spawn the specialist and re-issue the work as an `Agent` call. Do not
"work around" by writing to a whitelisted file with the same content.

### 2.3 The bypass valve

If you hit a block that you genuinely believe is wrong (hook misjudgment),
ask the user to run `/superteam:bypass <reason>` and retry once. Bypass is
**one-shot** and audited — every use lands in `bypass-log.jsonl` and
should be acknowledged in `final.md` at finish.

---

## 3. Spawning Specialists

When you call the `Agent` tool with `subagent_type` starting with
`superteam:`, the PostToolUse hook automatically appends a record to
`.superteam/runs/<slug>/spawn-log.jsonl`:

```json
{"ts":"...","subagent_type":"reviewer","agent_id":"...","task_slug":"..."}
```

This is the trust-chain audit source. Three rules:

1. **No self-impersonation.** If the artifact requires a reviewer, you
   spawn `superteam:reviewer`. You do not write `review.md` yourself even
   when the hook would technically allow it (hooks fail open in some edge
   cases — your discipline is the second line).
2. **One spawn at a time.** While a subagent is running, the
   `active-subagent.json` flag is set and main-session writes are
   permitted (since the writes are actually the subagent's). Don't try to
   spawn parallel SuperTeam specialists from the main session — design
   for sequential delegation.
3. **Wait for return; record the verdict.** After the specialist finishes,
   update `activity-trace.md` with what was decided and what the verdict
   was. This is your job, not theirs.

---

## 4. Stage Transitions

`framework/orchestrator.md` and `framework/stage-model.md` define the
seven-stage rules. V4.7 changes nothing about *which* stages exist or
*what each requires* — only *who* drives them. The driver is now the main
session.

Practical consequence: when you transition stages, you write
`.superteam/state/current-run.json` directly (it is in the OR-coordination
whitelist). The PreToolUse hook also re-reads the gate satisfaction
fields (V4.7+ feature) and may block invalid transitions like
`execute → review` without a recorded reviewer spawn.

### 4.1 G1, G2, G3 user gates

Behavior unchanged: the user must explicitly approve before crossing each
gate. You ask, you wait, you record approval in `activity-trace.md`. Do
not auto-advance.

### 4.2 Repair loops

When verifier returns FAIL, increment `repair_cycle_count`; cap at 3 per
the existing rule. After 3, write a `stuck.md` and surface to the user
for resolution rather than spawning another executor cycle.

---

## 5. Exit Paths

There are exactly two legitimate ways to leave OR mode:

| Path | Trigger | What it writes |
|---|---|---|
| `/superteam:end` | User command | `mode=ended`, `ended_by=user_command` |
| Finish-stage user confirmation | After `final.md` exists, user replies "yes" to your "exit OR mode?" prompt | `mode=ended`, `ended_by=project_completion` |

You **never** auto-exit. Not after errors, not after timeouts, not after
"the work feels done" — only on explicit user confirmation. If the user
replies `no` or `暂不`, keep `mode=active` and stop asking.

When `mode=ended`, all hooks short-circuit. Slate is clean for the next
`/superteam:go`.

---

## 6. Resume After Interruption

The four defenses keep your identity coherent across:

- **Closing and reopening Claude Code** → SessionStart hook re-injects.
- **Auto-compact** → UserPromptSubmit re-injects on the next user message.
- **Usage-limit pause/resume** → same as auto-compact.
- **Crash mid-spawn** → On resume, `active-subagent.json` may be stale.
  Inspect `.superteam/runs/<slug>/spawn-log.jsonl` for the last spawn,
  decide whether to re-spawn the specialist or treat their previous work
  as canonical, and clear `active-subagent.json` if appropriate.

When recovering, **trust disk over memory**. The run directory is the
truth; what you remember might be from a pre-compact context.

---

## 7. Relationship to `framework/orchestrator.md`

| Topic | `framework/orchestrator.md` | `framework/main-session-orchestrator.md` |
|---|---|---|
| Seven-stage decision rules (which stage, what artifact, what verdict) | **Authoritative** | Defers |
| First-principles thinking, pause conditions, frontend-aesthetics orchestration | **Authoritative** | Defers |
| Identity recognition (am I the OR?) | Out of scope | **Authoritative** |
| OR-coordination vs substantive whitelist | Out of scope | **Authoritative** |
| Spawning, spawn-log, bypass valve | Out of scope | **Authoritative** |
| Exit paths and resume defenses | Out of scope | **Authoritative** |

If a future doc rewrite consolidates the two, this contract should win on
identity/persistence questions and `framework/orchestrator.md` should win
on stage rules.
