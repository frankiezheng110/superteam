---
name: superteam:strategic-compact
description: Suggest manual context compaction at logical phase boundaries. Use when a long session reaches a natural checkpoint between workflow phases or after a major milestone.
argument-hint: [phase or milestone optional]
disable-model-invocation: true
---

# SuperTeam Strategic Compact

Use this skill to recommend manual context compaction at good workflow boundaries.

## Read First

- `framework/skill-common-rules.md`
- `framework/state-and-resume.md`

## Purpose

This skill helps long runs preserve clarity across phase changes.

It is advisory only.

## Trigger Rules

- suggest after `clarify`, `design`, or `plan` closes
- suggest after a major milestone or after a failed debugging branch ends
- suggest before switching to a clearly different task cluster
- suggest only when the session is long, context is getting stale, or the user explicitly wants a checkpoint
- avoid suggesting compaction in the middle of tightly coupled implementation unless context quality is obviously degrading

## Rules

- anchor every recommendation to a logical checkpoint, not an arbitrary token threshold alone
- point the user back to `.superteam/` artifacts as the durable source of truth
- keep the recommendation short and stage-aware
- do not force compaction; recommend it
- do not become a second context-management system beyond the existing artifact-driven resume model

## Suggested Message Shape

When you recommend compaction, state:

- current stage or just-closed stage
- why this is a clean checkpoint
- which artifacts already preserve the important context
