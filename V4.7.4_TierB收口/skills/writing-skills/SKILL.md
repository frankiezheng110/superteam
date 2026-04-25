---
name: writing-skills
description: Use when creating a new SuperTeam skill, editing an existing skill, or validating that a skill actually improves agent behavior before release.
argument-hint: [skill need or skill change]
disable-model-invocation: true
---

# SuperTeam Writing Skills

Turn a capability, rule, or recurring workflow into a real SuperTeam skill.

This is a meta skill for product evolution, not a delivery-stage substitute.

It is also the formal sink for reusable workflow improvements captured from `retrospective.md`.

Execution-facing prompt changes should remain English-first unless there is a clear performance reason to localize them.

## Read First

- `framework/skill-common-rules.md`
- `README.md`
- `framework/role-contracts.md`
- `framework/verification-and-fix.md`

## Use This Skill For

- creating a new skill under `skills/<skill-name>/SKILL.md`
- editing or tightening an existing skill
- validating that a skill changes agent behavior in the intended way
- deciding whether a capability should become a stage skill, compatibility wrapper, specialist helper, or meta skill

## Do Not Use This Skill For

- writing feature specs or implementation plans for normal repository work
- replacing `clarify`, `design`, `plan`, or `execute` in the main seven-stage workflow
- documenting one-off project conventions that belong in `CLAUDE.md`

## Core Standard

A SuperTeam skill should improve real operator or agent productivity.

Not every improvement action becomes a skill. If the change belongs in framework contracts or agent prompts instead, route it there explicitly.

Do not add a skill just because the upstream project has one. Add it only when the skill does at least one of these well:

- reduces repeated decision cost
- improves routing or collaboration quality
- makes a recurring workflow easier to trigger correctly
- preserves reusable judgment that should not live only in conversation history

## Skill Design Checklist

Before writing the final skill, decide all of the following:

1. triggering condition - when should the skill be used
2. product role - stage skill, compatibility wrapper, specialist helper, or meta skill
3. productivity gain - what waste or ambiguity it removes
4. boundaries - what it must not replace or silently absorb
5. validation method - how you will know the skill actually helped

If you cannot answer these clearly, do not write the skill yet.

## Skill Writing Rules

- use a lowercase hyphenated name
- write the description as `Use when ...`
- keep the description about triggering conditions, not the whole workflow summary
- match SuperTeam terminology and repository structure
- prefer concise, decision-oriented sections over long essays
- state explicit non-goals when the skill could be misused

## Validation Rule

Do not treat a new skill as complete until you have checked both:

1. structural validity - the skill is discoverable, readable, and matches local conventions
2. behavioral validity - the skill would materially improve agent behavior, routing, or output quality

For behavioral validity, use concrete pressure scenarios when possible:

- what the agent would do without the skill
- what failure or ambiguity appears
- what the skill changes
- what loophole still remains

## Required Output

When this skill is used, produce or update at least:

- `skills/<skill-name>/SKILL.md`

Also update related repository docs when the public skill surface changes, especially:

- `README.md`
- validation docs that describe skill count or command surface

## Recommended Skill Shape

Most SuperTeam skills should include:

- a one-line purpose
- when to use
- when not to use
- read-first references when needed
- concrete rules
- output expectations

Add examples only when they remove ambiguity.

## Fit Check For SuperTeam

Before finalizing a skill, verify that it fits the project's operating model:

- it does not bypass the seven-stage contract without saying so
- it does not create heavier process than the productivity gain justifies
- it respects orchestrator authority and worker boundaries when relevant
- it strengthens the product's reusable capability surface instead of copying upstream for appearance
- it respects the product language boundary: user-facing surfaces may be Chinese-first, execution-facing prompts should usually stay English-first

## Final Gate

Do not ship the skill if any of these are true:

- the trigger is vague
- the capability belongs in a normal stage artifact instead
- the skill duplicates another local skill without a sharper boundary
- the repository docs still describe the old skill surface after your change
